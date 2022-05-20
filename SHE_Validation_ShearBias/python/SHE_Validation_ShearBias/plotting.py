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
from SHE_PPT.math import LinregressResults
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.plotting import ValidationPlotter
from .data_processing import ShearBiasTestCaseDataProcessor
from .file_io import ShearBiasPlotFileNamer

logger = getLogger(__name__)


class ShearBiasPlotter(ValidationPlotter):
    """ Class to handle plotting for Shear Bias validation tests.
    """

    # Attributes set directly at init
    data_processor: ShearBiasTestCaseDataProcessor
    bin_index: int

    # Attributes determined at init
    method: ShearEstimationMethods
    bin_parameter: BinParameters

    # Attributes overriding parent to use specific values
    _short_test_case_name: str = "SB"

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
                 bin_index: int,
                 ) -> None:

        file_namer = ShearBiasPlotFileNamer(workdir = data_processor.workdir,
                                            method = data_processor.method,
                                            bin_parameter = data_processor.bin_parameter,
                                            bin_index = bin_index)

        super().__init__(file_namer = file_namer)

        # Set attrs directly
        self.data_processor = data_processor

        # Init empty dicts for intermediate data used when plotting
        self._d_bias_plot_filename = {}

    # Property getters and setters

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
        bias_plot_filename = super().__save_plot()

        # Record the filename for this plot in the filenames dict
        self.d_bias_plot_filename[i] = bias_plot_filename

    def _plot_component_shear_bias(self,
                                   i: int, ) -> None:
        """ Plot shear bias for an individual component.
        """

        # Get the needed data from the data_processor
        g_in = self.data_processor.d_g_in[i]
        g_out = self.data_processor.d_g_out[i]
        linregress_results: LinregressResults = self.data_processor.l_d_linregress_results[self.bin_index][i]
        d_bias_strings = self.data_processor.l_d_bias_strings[self.bin_index]

        # Make a plot of the shear estimates

        # Set up the figure, with a density scatter as a base

        self.__subplots_adjust()

        self._density_scatter(g_in, g_out, sort = True, bins = 20, colorbar = False, s = 1)

        plot_title = f"{self.method} Shear Estimates: g{i}"
        self.__set_title(plot_title)

        self.__set_xy_labels(x_label = f"True g{i}",
                             y_label = f"Estimated g{i}")

        # Draw the zero-axes
        self._draw_axes()

        # Draw the line of best-fit
        self._draw_bestfit_line(linregress_results)

        # Reset the axes, in case they changed after drawing the axes or bestfit line
        self._reset_axes()

        # Write the m and c bias on the plot
        self.__write_summary_text([d_bias_strings[f"c{i}"], d_bias_strings[f"m{i}"]])

        # Save the plot
        self._save_component_plot(i)

        # Clear the plot to make way for future plots
        self._clear_plots()

    def plot(self) -> None:
        """ Plot shear bias for both components.
        """

        self.data_processor.calc()

        for i in (1, 2):
            self._plot_component_shear_bias(i)
