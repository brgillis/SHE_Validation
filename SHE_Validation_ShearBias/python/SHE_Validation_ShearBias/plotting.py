""" @file plotting.py

    Created 8 July 2021

    Code to make plots for shear bias validation test.
"""

__updated__ = "2021-08-23"

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
from typing import Dict, Sequence

from SHE_PPT import file_io
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from matplotlib import pyplot as plt

import SHE_Validation
from SHE_Validation.plotting import ValidationPlotter
from .data_processing import ShearBiasTestCaseDataProcessor


logger = getLogger(__name__)

# Plotting constants
TITLE_FONTSIZE: float = 12
AXISLABEL_FONTSIZE: float = 12
TEXT_SIZE: float = 12
PLOT_FORMAT: str = "png"


class ShearBiasPlotter(ValidationPlotter):

    # Attributes set directly at init
    data_processor: ShearBiasTestCaseDataProcessor

    # Attributes determined at init
    method: ShearEstimationMethods

    # Attributes calculated when plotting
    _d_g_in = Dict[int, Sequence[float]]
    _d_g_out = Dict[int, Sequence[float]]
    _d_g_out_err = Dict[int, Sequence[float]]

    # Attributes calculated when plotting methods are called
    _d_bias_plot_filename: Dict[int, str]

    def __init__(self,
                 data_processor: ShearBiasTestCaseDataProcessor,
                 ) -> None:

        super().__init__()

        # Set attrs directly
        self.data_processor = data_processor

        # Get attrs from the data processor
        self.method = self.data_processor.method

        # Init empty dicts for intermediate data used when plotting
        self._d_bias_plot_filename = {}

    # Property getters and setters

    @property
    def d_bias_measurements(self):
        if not self._d_bias_measurements:
            self._d_bias_measurements = self.data_processor.d_bias_measurements

    @property
    def d_bias_plot_filename(self):
        return self._d_bias_plot_filename

    @d_bias_plot_filename.setter
    def d_bias_plot_filename(self, d_bias_plot_filename):
        if d_bias_plot_filename is None:
            self._d_bias_plot_filename = {}
        else:
            self._d_bias_plot_filename = d_bias_plot_filename

    # Private methods

    def _save_component_plot(self, i):
        """ Save the plot for bias component i.
        """

        # Get the filename to save to
        bias_plot_filename = file_io.get_allowed_filename(type_name="SHEAR-BIAS-VAL",
                                                          instance_id=f"{self.method.value}-g{i}-{os.getpid()}".upper(),
                                                          extension=PLOT_FORMAT,
                                                          version=SHE_Validation.__version__)
        qualified_bias_plot_filename = os.path.join(self.workdir, bias_plot_filename)

        # Save the figure and close it
        plt.savefig(qualified_bias_plot_filename, format=PLOT_FORMAT,
                    bbox_inches="tight", pad_inches=0.05)
        logger.info(f"Saved {self.method} g{i} bias plot to {qualified_bias_plot_filename}")

        # Record the filename for this plot in the filenams dict
        self.d_bias_plot_filename[i] = bias_plot_filename

    def _plot_component_shear_bias(self,
                                   i: int,):
        """ Plot shear bias for an individual component.
        """

        # Get the needed data from the data_processor
        g_in = self.data_processor.d_g_in[i]
        g_out = self.data_processor.d_g_out[i]
        linregress_results = self.data_processor.d_linregress_results[i]
        d_bias_strings = self.data_processor.d_bias_strings

        # Make a plot of the shear estimates

        # Set up the figure, with a density scatter as a base

        self.fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

        self.density_scatter(g_in, g_out, sort=True, bins=20, colorbar=False, s=1)

        plot_title = f"{self.method} Shear Estimates: g{i}"
        plt.title(plot_title, fontsize=TITLE_FONTSIZE)

        self.ax.set_xlabel(f"True g{i}", fontsize=AXISLABEL_FONTSIZE)
        self.ax.set_ylabel(f"Estimated g{i}", fontsize=AXISLABEL_FONTSIZE)

        # Draw the zero-axes
        self.draw_axes()

        # Draw the line of best-fit
        self.draw_bestfit_line(linregress_results)

        # Reset the axes
        self.reset_axes()

        # Write the bias
        self.ax.text(0.02, 0.98, d_bias_strings[f"c{i}"], horizontalalignment='left', verticalalignment='top',
                     transform=self.ax.transAxes, fontsize=TEXT_SIZE)
        self.ax.text(0.02, 0.93, d_bias_strings[f"m{i}"], horizontalalignment='left', verticalalignment='top',
                     transform=self.ax.transAxes, fontsize=TEXT_SIZE)

        # Save the plot
        self._save_component_plot(i)

        # Clear the plot to make way for future plots
        self.clear_plots()

    def plot_shear_bias(self):
        """ Plot shear bias for both components.
        """

        self.data_processor.calc()

        for i in (1, 2):
            self.plot_component_shear_bias(i)
