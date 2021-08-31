""" @file plotting.py

    Created 8 July 2021

    Code to make plots for shear bias validation test.
"""

__updated__ = "2021-08-31"

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

from typing import Dict, Sequence

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, LinregressResults
from matplotlib import pyplot as plt

from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.plotting import ValidationPlotter

from .data_processing import ShearBiasTestCaseDataProcessor
from .file_io import ShearBiasPlotFileNamer


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
    bin_parameter: BinParameters

    # Attributes overriding parent to use specific values
    _short_test_case_name: str = "SHEAR-BIAS"

    # Attributes used when plotting
    _instance_id_tail: str

    # Attributes calculated when plotting
    _d_g_in = Dict[int, Sequence[float]]
    _d_g_out = Dict[int, Sequence[float]]
    _d_g_out_err = Dict[int, Sequence[float]]

    # Attributes calculated when plotting methods are called
    _d_bias_plot_filename: Dict[int, str]

    def __init__(self,
                 data_processor: ShearBiasTestCaseDataProcessor,
                 ) -> None:

        file_namer = ShearBiasPlotFileNamer(workdir=data_processor.workdir,
                                            method=data_processor.method,
                                            bin_parameter=data_processor.bin_parameter,
                                            bin_index=data_processor.bin_index)

        super().__init__(file_namer=file_namer)

        # Set attrs directly
        self.data_processor = data_processor

        # Init empty dicts for intermediate data used when plotting
        self._d_bias_plot_filename = {}

    # Property getters and setters

    @property
    def d_bias_measurements(self) -> Dict[int, BiasMeasurements]:
        if not self._d_bias_measurements:
            self._d_bias_measurements = self.data_processor.d_bias_measurements

    @property
    def d_bias_plot_filename(self) -> Dict[int, str]:
        return self._d_bias_plot_filename

    @d_bias_plot_filename.setter
    def d_bias_plot_filename(self, d_bias_plot_filename: Dict[int, str]):
        if d_bias_plot_filename is None:
            self._d_bias_plot_filename = {}
        else:
            self._d_bias_plot_filename = d_bias_plot_filename

    # Private methods

    def _save_component_plot(self, i: int) -> None:
        """ Save the plot for bias component i.
        """

        # Set the instance id for this component
        self.file_namer.instance_id_tail = f"g{i}"

        # Use the parent method to save the plot and get the filename of it
        bias_plot_filename = super()._save_plot()

        # Record the filename for this plot in the filenams dict
        self.d_bias_plot_filename[i] = bias_plot_filename

    def _plot_component_shear_bias(self,
                                   i: int,) -> None:
        """ Plot shear bias for an individual component.
        """

        # Get the needed data from the data_processor
        g_in = self.data_processor.d_g_in[i]
        g_out = self.data_processor.d_g_out[i]
        linregress_results: LinregressResults = self.data_processor.d_linregress_results[i]
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

    def plot(self) -> None:
        """ Plot shear bias for both components.
        """

        self.data_processor.calc()

        for i in (1, 2):
            self._plot_component_shear_bias(i)