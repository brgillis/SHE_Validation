""" @file plot_cti_gal.py

    Created 8 July 2021

    Code to make plots for CTI-Gal Validation test.
"""

__updated__ = "2021-07-14"

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from SHE_PPT import file_io
from SHE_PPT.logging import getLogger
from SHE_PPT.math import linregress_with_errors
from astropy import table
from matplotlib import pyplot as plt

import SHE_Validation
from SHE_Validation.plotting import ValidationPlotter
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF
import numpy as np


logger = getLogger(__name__)


TITLE_FONTSIZE = 12
AXISLABEL_FONTSIZE = 12
TEXT_SIZE = 12
PLOT_FORMAT = "png"
SLOPE_DIGITS = 7
INTERCEPT_DIGITS = 5
SIGMA_DIGITS = 1


class CtiGalPlotter(ValidationPlotter):

    # Attributes set directly at init
    _l_object_data_table = None
    _object_table = None
    method = None
    workdir = None

    # Attributes calculated at init
    _good_rows = None
    _g1_colname = None
    _weight_colname = None

    # Attributes calculated when plotting methods are called
    _cti_gal_plot_filename = None

    def __init__(self, l_object_data_table, object_table, method, workdir):

        super().__init__()

        # Set attrs directly
        self.l_object_data_table = l_object_data_table
        if object_table is not None:
            self.object_table = object_table
        else:
            self.object_table = table.vstack(tables=self.l_object_data_table)
        self.method = method
        self.workdir = workdir

        # Determine attrs from kwargs
        self._g1_colname = getattr(CGOD_TF, f"g1_image_{method}")
        self._weight_colname = getattr(CGOD_TF, f"weight_{method}")

        weight = self.object_table[self.weight_colname]
        self._good_rows = weight > 0

        # Set as None attributes to be set when plotting methods are called
        self._cti_gal_plot_filename = None

    # Property getters and setters

    @property
    def l_object_data_table(self):
        return self._l_object_data_table

    @l_object_data_table.setter
    def l_object_data_table(self, l_object_data_table):
        if l_object_data_table is None:
            self._l_object_data_table = []
        else:
            self._l_object_data_table = l_object_data_table

    @property
    def object_table(self):
        return self._object_table

    @object_table.setter
    def object_table(self, object_table):
        self._object_table = object_table

    @property
    def good_rows(self):
        return self._good_rows

    @property
    def g1_colname(self):
        return self._g1_colname

    @property
    def weight_colname(self):
        return self._weight_colname

    @property
    def cti_gal_plot_filename(self):
        return self._cti_gal_plot_filename

    @cti_gal_plot_filename.setter
    def cti_gal_plot_filename(self, cti_gal_plot_filename):
        self._cti_gal_plot_filename = cti_gal_plot_filename

    # Callable methods

    def plot_cti_gal(self):
        """ Plot CTI-Gal validation test data.
        """

        rr_dist = self.object_table[CGOD_TF.readout_dist][self._good_rows]
        g1 = self.object_table[self.g1_colname][self._good_rows]
        g1_err = 1 / np.sqrt(self.object_table[self.weight_colname][self._good_rows])

        # Perform the linear regression, calculate bias, and save it in the bias dict
        linregress_results = linregress_with_errors(x=rr_dist,
                                                    y=g1,
                                                    y_err=g1_err)

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Global linear regression for method {self.method}:")
        d_linregress_strings = {}
        for a, d in ("slope", SLOPE_DIGITS), ("intercept", INTERCEPT_DIGITS):
            d_linregress_strings[f"{a}"] = (f"{a} = {getattr(linregress_results,a):.{d}f} +/- "
                                            f"{getattr(linregress_results,f'{a}_err'):.{d}f} "
                                            f"({getattr(linregress_results,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(d_linregress_strings[f"{a}"])

        # Make a plot of the data and bestfit line

        # Set up the figure, with a density scatter as a base

        self.fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

        self.density_scatter(rr_dist, g1, sort=True, bins=200, colorbar=False, s=4)

        plot_title = f"{self.method} g1 v. Readout Register Distance"
        plt.title(plot_title, fontsize=TITLE_FONTSIZE)

        self.ax.set_xlabel(f"Readout Register Distance (pix)", fontsize=AXISLABEL_FONTSIZE)
        self.ax.set_ylabel(f"g1 (detector coordinates)", fontsize=AXISLABEL_FONTSIZE)

        # Draw the x axis
        self.draw_x_axis()

        # Draw the line of best-fit
        self.draw_bestfit_line(linregress_results)

        # Reset the axes
        self.reset_axes()

        # Write the bias
        self.ax.text(0.02, 0.98, d_linregress_strings[f"slope"], horizontalalignment='left', verticalalignment='top',
                     transform=self.ax.transAxes, fontsize=TEXT_SIZE)
        self.ax.text(0.02, 0.93, d_linregress_strings[f"intercept"], horizontalalignment='left', verticalalignment='top',
                     transform=self.ax.transAxes, fontsize=TEXT_SIZE)

        # Save the plot

        # Get the filename to save to
        plot_filename = file_io.get_allowed_filename(type_name="CTI-GAL-VAL",
                                                     instance_id=f"{self.method}-{os.getpid()}".upper(),
                                                     extension=PLOT_FORMAT,
                                                     version=SHE_Validation.__version__)
        qualified_plot_filename = os.path.join(self.workdir, plot_filename)

        # Save the figure and close it
        plt.savefig(qualified_plot_filename, format=PLOT_FORMAT,
                    bbox_inches="tight", pad_inches=0.05)
        logger.info(f"Saved {self.method} CTI-Gal plot to {qualified_plot_filename}")
        plt.close()

        # Record the filename for this plot in the filenams dict
        self.cti_gal_plot_filename = plot_filename
