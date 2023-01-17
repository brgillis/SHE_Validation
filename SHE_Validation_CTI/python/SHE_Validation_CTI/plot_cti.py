"""
:file: python/SHE_Validation_CTI/plot_cti.py

:date: 3 November 2021
:author: Bryan Gillis

Code to make plots for CTI-related validation tests
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

from typing import Dict, List, Optional, Sequence, Union

import numpy as np
from astropy.table import Row, Table

from SHE_PPT.logging import getLogger
from SHE_PPT.math import LinregressResults, linregress_with_errors
from SHE_PPT.table_formats.she_star_catalog import TF as SHE_STAR_CAT_TF
from SHE_PPT.utility import coerce_to_list
from SHE_Validation.binning.bin_constraints import get_table_of_ids
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.plotting import ValidationPlotter
from .table_formats.cti_gal_object_data import TF as CGOD_TF

logger = getLogger(__name__)


class CtiPlotter(ValidationPlotter):
    """ Class to handle plotting for CTI-related validation tests (CTI-Gal and CTI-PSF).
    """

    # Class constants

    SLOPE_DIGITS = 7
    INTERCEPT_DIGITS = 5
    SIGMA_DIGITS = 1

    # Overridden parent attributes
    _x_label = f"Readout Register Distance (pix)"
    _y_label = f"e1 (detector coordinates)"

    # Attributes set directly at init
    _object_table: Table
    l_ids_in_bin: Sequence[int]

    # Attributes determined at init
    method_name: Optional[str] = None
    _t_good: Union[Sequence[Row], Table]
    _g1_colname: str
    _g1_err_colname: Optional[str] = None
    _weight_colname: Optional[str] = None

    # Attributes determined while plotting
    l_rr_distarray: Optional[np.ndarray] = None
    l_g1: Optional[np.ndarray] = None
    l_g1_err: Optional[np.ndarray] = None
    opt_method_str: str = ""
    exp_index: Optional[int] = None
    linregress_results: Optional[LinregressResults] = None
    d_linregress_strings: Optional[Dict[str, str]] = None

    def __init__(self,
                 object_table: Table,
                 l_ids_in_bin: Sequence[int],
                 *args,
                 **kwargs):

        super().__init__(*args, **kwargs)

        # Set attrs directly
        self.object_table = object_table
        self.l_ids_in_bin = l_ids_in_bin

        # Determine attrs from kwargs
        if self.method is None:
            self._g1_colname = SHE_STAR_CAT_TF.e1
            self._g1_err_colname = SHE_STAR_CAT_TF.e1_err
        else:
            self.method_name = self.method.value
            self._g1_colname = getattr(CGOD_TF, f"g1_image_{self.method_name}")
            self._weight_colname = getattr(CGOD_TF, f"weight_{self.method_name}")

        self._t_good = get_table_of_ids(t=self.object_table,
                                        l_ids=self.l_ids_in_bin, )

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

    # Protected method overrides

    def _get_plot_title(self) -> str:
        """ Overridable method to get the plot title
        """

        if self.method_name is None:
            plot_title: str = f"CTI-PSF Validation"
        else:
            plot_title: str = f"{self.method_name} CTI-Gal Validation"

        # Append note of exposure or observation
        if self.exp_index is None:
            plot_title += " - Full Observation"
        else:
            plot_title += f" - Exposure {self.exp_index}"

        # Add bin info
        plot_title += self._get_bin_info_str()

        return plot_title

    def _get_l_summary_text(self) -> List[str]:
        """ Override parent method to get summary text.
        """

        return [self.d_linregress_strings[f"slope"],
                self.d_linregress_strings[f"intercept"]]

    def _get_msg_plot_saved(self) -> str:
        """ Override parent method to get the method to print to log that a plot has been saved
        """
        return f"Saved {self.method_name} CTI plot to {self.qualified_plot_filename}"

    def _calc_plotting_data(self):
        """ Override parent method to get all the data we want to plot.
        """

        self.l_rr_distarray = np.array(coerce_to_list(self.t_good[CGOD_TF.readout_dist]))
        self.l_g1 = np.array(coerce_to_list(self.t_good[self.g1_colname]))

        if self.g1_err_colname is not None:
            self.l_g1_err: Sequence[float] = np.array(coerce_to_list(self.g1_err_colname))
        else:
            self.l_g1_err: Sequence[float] = np.array(coerce_to_list(1 / np.sqrt(self.t_good[self.weight_colname])))

        if self.method_name is not None:
            self.opt_method_str = f"method {self.method_name}, "

        self.exp_index = self.file_namer.exp_index

        # Check if there's any valid data for this bin
        if len(self.l_rr_distarray) <= 1:
            # We'll always make the tot plot for testing purposes, but log a warning if no data
            if self.bin_parameter == BinParameters.TOT:
                logger.warning(f"Insufficient valid data to plot for {self.opt_method_str}and test case "
                               f"{self.bin_parameter.value}, but making plot anyway for testing purposes.")
            else:
                logger.debug(f"Insufficient valid valid data to plot for {self.opt_method_str}test case "
                             f"{self.bin_parameter.value}, bin {self.bin_limits}, so skipping plot.")
                return True

        # Perform the linear regression, calculate bias, and save it in the bias dict
        self.linregress_results = linregress_with_errors(x=self.l_rr_distarray,
                                                         y=self.l_g1,
                                                         y_err=self.l_g1_err)

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Linear regression for {self.opt_method_str}test case {self.bin_parameter.value}, "
                    f"bin {self.bin_limits}:")

        self.d_linregress_strings: Dict[str, str] = {}
        for a, d in (("slope", self.SLOPE_DIGITS),
                     ("intercept", self.INTERCEPT_DIGITS)):

            val = getattr(self.linregress_results, a)
            val_err = getattr(self.linregress_results, f'{a}_err')
            val_sigma = getattr(self.linregress_results, f'{a}_sigma')

            self.d_linregress_strings[f"{a}"] = (f"{a} = {val:.{d}f} +/- "
                                                 f"{val_err:.{d}f} "
                                                 f"({val_sigma:.{self.SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(self.d_linregress_strings[f"{a}"])

        return False

    def _draw_plot(self):
        """ Override parent method for drawing the plot.
        """

        # Draw the plot as a density scatter plot
        self._density_scatter(self.l_rr_distarray, self.l_g1, sort=True, bins=200, colorbar=False, s=4)

        # Draw the x axis
        self._draw_x_axis()

        # Draw the line of best-fit
        self._draw_bestfit_line(self.linregress_results)

        # Reset the axes, in case they changed after drawing the axes or bestfit line
        self._reset_axes()
