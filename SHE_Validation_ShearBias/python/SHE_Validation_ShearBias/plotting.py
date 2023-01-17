""" @file plotting.py

    Created 8 July 2021

    Code to make plots for shear bias validation test
"""

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

from typing import Dict, List, Optional, Sequence

import numpy as np

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
    component_index: Optional[int] = None
    g_in: Optional[np.ndarray] = None
    g_out: Optional[np.ndarray] = None
    linregress_results: Optional[LinregressResults] = None
    d_bias_strings: Optional[Dict[str, str]] = None

    def __init__(self,
                 data_processor: ShearBiasTestCaseDataProcessor,
                 bin_index: int,
                 *args,
                 **kwargs,
                 ) -> None:

        file_namer = ShearBiasPlotFileNamer(workdir=data_processor.workdir,
                                            method=data_processor.method,
                                            bin_parameter=data_processor.bin_parameter,
                                            bin_index=bin_index)

        super().__init__(*args, file_namer=file_namer, **kwargs)

        # Set attrs directly
        self.data_processor = data_processor
        self.data_processor.calc()

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

    # Protected method overrides

    def _get_x_label(self) -> str:
        """ Override parent method to get the label for the X axis.
        """
        return f"True g{self.component_index}"

    def _get_y_label(self) -> str:
        """ Override parent method to get the label for the Y axis.
        """

        return f"Estimated g{self.component_index}"

    def _get_plot_title(self) -> str:
        """ Overridable method to get the plot title
        """

        plot_title = f"{self.method.value} Shear Estimates: g{self.component_index} {self._get_bin_info_str()}"

        return plot_title

    def _get_l_summary_text(self) -> List[str]:
        """ Override parent method to get summary text.
        """

        return [self.d_bias_strings[f"c{self.component_index}"],
                self.d_bias_strings[f"m{self.component_index}"]]

    def _calc_plotting_data(self):
        """ Override parent method to get all the data we want to plot.
        """

        i = self.component_index

        # Get the needed data from the data_processor
        self.g_in = self.data_processor.d_g_in[i]
        self.g_out = self.data_processor.d_g_out[i]
        self.linregress_results: LinregressResults = self.data_processor.l_d_linregress_results[self.bin_index][i]
        self.d_bias_strings = self.data_processor.l_d_bias_strings[self.bin_index]

        return False

    def _draw_plot(self):
        """ Override parent method for drawing the plot.
        """

        # Plot data as a density scatter plot
        self._density_scatter(self.g_in, self.g_out, s=1)

        # Draw the zero-axes
        self._draw_axes()

        # Draw the line of best-fit
        self._draw_bestfit_line(self.linregress_results)

        # Reset the axes, in case they changed after drawing the axes or bestfit line
        self._reset_axes()

    def _save_plot(self) -> None:
        """ Override parent method to set up different name for each component plot and store results in dict.
        """

        # Set the instance id for this component
        self.file_namer.instance_id_tail = f"g{self.component_index}"

        # Use the parent method to save the plot and get the filename of it
        bias_plot_filename = super()._save_plot()

        # Record the filename for this plot in the filenames dict
        self.d_bias_plot_filename[self.component_index] = bias_plot_filename

    def plot(self, show: bool = False) -> None:
        """ Override parent plot, and call it for both components
        """

        for self.component_index in (1, 2):
            super().plot(show=show)
            self._clear_plots()
