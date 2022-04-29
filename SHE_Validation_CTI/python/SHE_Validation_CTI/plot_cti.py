""" @file plot_cti.py

    Created 3 Nov 2021

    Code to make plots for CTI-related validation tests.
"""

__updated__ = "2021-08-30"

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

from typing import Dict, Optional, Sequence, Union

import numpy as np
from astropy.table import Row, Table
from matplotlib import pyplot as plt

from SHE_PPT.logging import getLogger
from SHE_PPT.math import LinregressResults, linregress_with_errors
from SHE_PPT.table_formats.she_star_catalog import TF as SHE_STAR_CAT_TF
from SHE_PPT.utility import coerce_to_list
from SHE_Validation.binning.bin_constraints import get_table_of_ids
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.plotting import ValidationPlotter
from .file_io import CtiPlotFileNamer
from .table_formats.cti_gal_object_data import TF as CGOD_TF

logger = getLogger(__name__)


class CtiPlotter(ValidationPlotter):
    """ Class to handle plotting for CTI-related validation tests (CTI-Gal and CTI-PSF).
    """

    # Class constants

    SLOPE_DIGITS = 7
    INTERCEPT_DIGITS = 5
    SIGMA_DIGITS = 1

    # Attributes set directly at init
    _object_table: Table
    bin_limits: np.ndarray
    l_ids_in_bin: Sequence[int]

    # Attributes determined at init
    method_name: Optional[str] = None
    _t_good: Union[Sequence[Row], Table]
    _g1_colname: str
    _g1_err_colname: Optional[str] = None
    _weight_colname: Optional[str] = None

    def __init__(self,
                 object_table: Table,
                 file_namer: CtiPlotFileNamer,
                 bin_limits: Sequence[float],
                 l_ids_in_bin: Sequence[int], ):

        super().__init__(file_namer = file_namer)

        # Set attrs directly
        self.object_table = object_table
        self.bin_limits = bin_limits
        self.l_ids_in_bin = l_ids_in_bin

        # Determine attrs from kwargs
        if self.method is None:
            self._g1_colname = SHE_STAR_CAT_TF.e1
            self._g1_err_colname = SHE_STAR_CAT_TF.e1_err
        else:
            self.method_name = self.method.value
            self._g1_colname = getattr(CGOD_TF, f"g1_image_{self.method_name}")
            self._weight_colname = getattr(CGOD_TF, f"weight_{self.method_name}")

        self._t_good = get_table_of_ids(t = self.object_table,
                                        l_ids = self.l_ids_in_bin, )

    # Property getters and setters

    @property
    def object_table(self) -> Table:
        return self._object_table

    @object_table.setter
    def object_table(self, object_table: Table):
        self._object_table = object_table

    @property
    def t_good(self) -> Union[Sequence[Row], Table]:
        return self._t_good

    @property
    def g1_colname(self) -> str:
        return self._g1_colname

    @property
    def g1_err_colname(self) -> Optional[str]:
        return self._g1_err_colname

    @property
    def weight_colname(self) -> Optional[str]:
        return self._weight_colname

    # Callable methods

    def plot(self) -> None:
        """ Plot CTI validation test data.
        """

        l_rr_dist: Sequence[float] = np.array(coerce_to_list(self.t_good[CGOD_TF.readout_dist]))
        l_g1: Sequence[float] = np.array(coerce_to_list(self.t_good[self.g1_colname]))

        if self.g1_err_colname is not None:
            l_g1_err: Sequence[float] = np.array(coerce_to_list(self.g1_err_colname))
        else:
            l_g1_err: Sequence[float] = np.array(coerce_to_list(1 / np.sqrt(self.t_good[self.weight_colname])))

        if self.method_name is None:
            opt_method_str: str = ""
            plot_title: str = f"CTI-PSF Validation - {self.bin_parameter.value}"
        else:
            opt_method_str = f"method {self.method_name}, "
            plot_title: str = f"{self.method_name} CTI-Gal Validation - {self.bin_parameter.value}"

        # Append note of exposure or observation
        exp_index = self.file_namer.exp_index
        if exp_index is None:
            plot_title += "- Full Observation"
        else:
            plot_title += f"- Exposure {exp_index}"

        # Check if there's any valid data for this bin
        if len(l_rr_dist) <= 1:
            # We'll always make the tot plot for testing purposes, but log a warning if no data
            if self.bin_parameter == BinParameters.TOT:
                logger.warning(f"Insufficient valid data to plot for {opt_method_str}and test case "
                               f"{self.bin_parameter.value}, but making plot anyway for testing purposes.")
            else:
                logger.debug(f"Insufficient valid valid data to plot for {opt_method_str}test case "
                             f"{self.bin_parameter.value}, bin {self.bin_limits}, so skipping plot.")
                return

        # Perform the linear regression, calculate bias, and save it in the bias dict
        linregress_results: LinregressResults = linregress_with_errors(x = l_rr_dist,
                                                                       y = l_g1,
                                                                       y_err = l_g1_err)

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Linear regression for {opt_method_str}test case {self.bin_parameter.value}, "
                    f"bin {self.bin_limits}:")
        d_linregress_strings: Dict[str, str] = {}
        for a, d in (("slope", self.SLOPE_DIGITS),
                     ("intercept", self.INTERCEPT_DIGITS)):

            val = getattr(linregress_results, a)
            val_err = getattr(linregress_results, f'{a}_err')
            val_sigma = getattr(linregress_results, f'{a}_sigma')

            d_linregress_strings[f"{a}"] = (f"{a} = {val:.{d}f} +/- "
                                            f"{val_err:.{d}f} "
                                            f"({val_sigma:.{self.SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(d_linregress_strings[f"{a}"])

        # Make a plot of the data and bestfit line

        # Set up the figure, with a density scatter as a base

        self.subplots_adjust()

        self.density_scatter(l_rr_dist, l_g1, sort = True, bins = 200, colorbar = False, s = 4)

        if self.bin_parameter != BinParameters.TOT:
            plot_title += f" {self.bin_limits}"
        self.set_title(plot_title)

        self.set_xy_labels(x_label = f"Readout Register Distance (pix)",
                           y_label = f"e1 (detector coordinates)")

        # Draw the x axis
        self.draw_x_axis()

        # Draw the line of best-fit
        self.draw_bestfit_line(linregress_results)

        # Reset the axes, in case they changed after drawing the axes or bestfit line
        self.reset_axes()

        # Write the m and c bias on the plot
        self.summary_text([d_linregress_strings[f"slope"], d_linregress_strings[f"intercept"]])

        # Save the plot (which generates a filename) and log it
        super()._save_plot()
        logger.info(f"Saved {self.method_name} CTI plot to {self.qualified_plot_filename}")

        plt.close()
