""" @file plot_cti_gal.py

    Created 8 July 2021

    Code to make plots for CTI-Gal Validation test.
"""

__updated__ = "2021-08-04"

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
from typing import Dict, Iterable, Optional

from SHE_PPT import file_io
from SHE_PPT.logging import getLogger
from SHE_PPT.math import linregress_with_errors, LinregressResults
from astropy.table import Table, Row
from matplotlib import pyplot as plt

import SHE_Validation
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.plotting import ValidationPlotter
import numpy as np

from .data_processing import get_rows_in_bin
from .table_formats.cti_gal_object_data import TF as CGOD_TF


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
    _object_table: Table
    method: str
    bin_parameter: BinParameters
    bin_index: int
    workdir: str

    # Attributes calculated at init
    bin_limits: np.ndarray
    l_rows_in_bin: Iterable[Row]
    _l_good_rows: Iterable[Row]
    _g1_colname: str
    _weight_colname: str

    # Attributes calculated when plotting methods are called
    _cti_gal_plot_filename: Optional[str] = None

    def __init__(self,
                 object_table: Table,
                 method: str,
                 bin_parameter: BinParameters,
                 d_bin_limits: Dict[str, float],
                 bin_index: int,
                 workdir: str,):

        super().__init__()

        # Set attrs directly
        self.object_table = object_table
        self.method = method
        self.bin_parameter = bin_parameter
        self.bin_index = bin_index
        self.workdir = workdir

        # Determine attrs from kwargs
        self._g1_colname = getattr(CGOD_TF, f"g1_image_{method}")
        self._weight_colname = getattr(CGOD_TF, f"weight_{method}")

        self.bin_limits = d_bin_limits[bin_parameter][bin_index:bin_index + 2]
        self.l_rows_in_bin = get_rows_in_bin(self.object_table, self.bin_parameter, self.bin_limits)

        weight = self.object_table[self.weight_colname][self.l_rows_in_bin]
        self._l_good_rows = weight > 0

        # Set as None attributes to be set when plotting methods are called
        self._cti_gal_plot_filename = None

    # Property getters and setters

    @property
    def object_table(self) -> Table:
        return self._object_table

    @object_table.setter
    def object_table(self, object_table: Table):
        self._object_table = object_table

    @property
    def l_good_rows(self) -> Iterable[Row]:
        return self._l_good_rows

    @property
    def g1_colname(self) -> str:
        return self._g1_colname

    @property
    def weight_colname(self) -> str:
        return self._weight_colname

    @property
    def cti_gal_plot_filename(self) -> Optional[str]:
        return self._cti_gal_plot_filename

    @cti_gal_plot_filename.setter
    def cti_gal_plot_filename(self, cti_gal_plot_filename: Optional[str]):
        self._cti_gal_plot_filename = cti_gal_plot_filename

    # Callable methods

    def plot_cti_gal(self) -> None:
        """ Plot CTI-Gal validation test data.
        """

        l_rr_dist: Iterable[float] = self.object_table[CGOD_TF.readout_dist][self.l_rows_in_bin][self.l_good_rows]
        l_g1: Iterable[float] = self.object_table[self.g1_colname][self.l_rows_in_bin][self.l_good_rows]
        l_g1_err: Iterable[float] = 1 / np.sqrt(self.object_table[self.weight_colname]
                                                [self.l_rows_in_bin][self.l_good_rows])

        # Check if there's any valid data for this bin
        if len(l_rr_dist) <= 1:
            # We'll always make the global plot for testing purposes, but log a warning if no data
            if self.bin_parameter == BinParameters.GLOBAL:
                logger.warning(f"Insufficient valid data to plot for method {self.method} and test case "
                               f"{self.bin_parameter.value}, but making plot anyway for testing purposes.")
            else:
                logger.debug(f"Insufficient valid valid data to plot for method {self.method}, test case "
                             f"{self.bin_parameter.value}, bin {self.bin_limits}, so skipping plot.")
                return

        # Perform the linear regression, calculate bias, and save it in the bias dict
        linregress_results: LinregressResults = linregress_with_errors(x=l_rr_dist,
                                                                       y=l_g1,
                                                                       y_err=l_g1_err)

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Linear regression for method {self.method}, test case {self.bin_parameter.value}, "
                    f"bin {self.bin_limits}:")
        d_linregress_strings: Dict[str, str] = {}
        for a, d in ("slope", SLOPE_DIGITS), ("intercept", INTERCEPT_DIGITS):
            d_linregress_strings[f"{a}"] = (f"{a} = {getattr(linregress_results,a):.{d}f} +/- "
                                            f"{getattr(linregress_results,f'{a}_err'):.{d}f} "
                                            f"({getattr(linregress_results,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(d_linregress_strings[f"{a}"])

        # Make a plot of the data and bestfit line

        # Set up the figure, with a density scatter as a base

        self.fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

        self.density_scatter(l_rr_dist, l_g1, sort=True, bins=200, colorbar=False, s=4)

        plot_title: str = f"{self.method} CTI-Gal Validation - {self.bin_parameter.value} {self.bin_limits}"
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
        instance_id: str = f"{self.method}-{self.bin_parameter.value}-{self.bin_index}-{os.getpid()}".upper()
        plot_filename: str = file_io.get_allowed_filename(type_name="CTI-GAL-VAL",
                                                          instance_id=instance_id,
                                                          extension=PLOT_FORMAT,
                                                          version=SHE_Validation.__version__)
        qualified_plot_filename: str = os.path.join(self.workdir, plot_filename)

        # Save the figure and close it
        plt.savefig(qualified_plot_filename, format=PLOT_FORMAT,
                    bbox_inches="tight", pad_inches=0.05)
        logger.info(f"Saved {self.method} CTI-Gal plot to {qualified_plot_filename}")
        plt.close()

        # Record the filename for this plot in the filenams dict
        self.cti_gal_plot_filename = plot_filename
