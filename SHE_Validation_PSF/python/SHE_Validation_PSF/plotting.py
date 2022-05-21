""" @file plotting.py

    Created 28 April 2022

    Classes and functions to perform plotting for PSF validation tests.
"""

__updated__ = "2022-04-28"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

import abc
from typing import List, Optional, Sequence

import numpy as np
from astropy.table import Table
from matplotlib import pyplot as plt

from SHE_PPT import logging
from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.utility import is_inf_nan_or_masked
from SHE_Validation.binning.bin_constraints import get_table_of_ids
from SHE_Validation.plotting import ValidationPlotter
from SHE_Validation_PSF.file_io import PsfResSPPlotFileNamer
from SHE_Validation_PSF.utility import KsResult, calculate_p_values

logger = logging.getLogger(__name__)


class PsfResSPPlotter(ValidationPlotter, abc.ABC):
    """Abstract plotting class for plots generated by the PSF Residual (Star Positions) validation test.
    """

    # Class constants
    TEST_CAT_LEGEND_NAME = "Test"
    REF_CAT_LEGEND_NAME = "Reference"

    STR_KS_P_LABEL = r"$p_{\rm KS}$: "
    KS_P_DIGITS = 2

    # Fixed attributes which can be overridden by child classes
    plot_format: str = "png"
    group_mode: bool = False

    def __init__(self,
                 star_cat: Table,
                 file_namer: PsfResSPPlotFileNamer,
                 bin_limits: Sequence[float],
                 l_ids_in_bin: Sequence[int],
                 ks_test_result: KsResult,
                 ref_star_cat: Optional[Table] = None,
                 l_ref_ids_in_bin: Optional[Sequence[int]] = None,
                 group_mode: Optional[bool] = None, ):
        super().__init__(file_namer = file_namer)

        # Set attrs directly
        self.star_cat = star_cat
        self.bin_limits = bin_limits
        self.l_ids_in_bin = l_ids_in_bin
        self.ks_test_result = ks_test_result
        self.ref_star_cat = ref_star_cat
        self.l_ref_ids_in_bin = l_ref_ids_in_bin
        self.group_mode = group_mode if group_mode is not None else self.group_mode

        # Determine attrs from kwargs

        self.t_good = get_table_of_ids(t = self.star_cat,
                                       l_ids = self.l_ids_in_bin, )
        if self.ref_star_cat is not None:
            # Ensure we have reference IDs supplied
            if self.l_ref_ids_in_bin is None:
                raise ValueError("self.l_ref_ids_in_bin must be supplied if ref_star_cat is supplied.")
            self.two_sample_mode = True
            self.ref_t_good = get_table_of_ids(t = self.ref_star_cat,
                                               l_ids = self.l_ref_ids_in_bin, )
        else:
            self.two_sample_mode = False
            self.ref_t_good = None

        # Declare instance attributes which will be calculated later
        self.base_plot_title: Optional[str] = None


class PsfResSPHistPlotter(PsfResSPPlotter):
    """ Plotter for a histogram of PSF Residual (Star Pos) log10(p_chisq) values.
    """

    # Class constants

    STR_HIST_TEST_P_MED_LABEL = r"Median test $p(\chi^2,{\rm d.o.f.})$: "
    STR_HIST_REF_P_MED_LABEL = r"Median ref. $p(\chi^2,{\rm d.o.f.})$: "
    P_MED_DIGITS = 2

    HIST_TYPE = 'step'
    HIST_NUM_BINS = 20

    STR_HIST_BASE_TITLE = "PSF Res. (Star Pos.) p"
    STR_HIST_BASE_TITLE_LOG = "PSF Res. (Star Pos.) log(p)"
    STR_HIST_TITLE_CUMULATIVE_TAIL = " (cumulative)"

    STR_HIST_Y_LABEL_CUMULATIVE_TAIL = " (cumulative)"
    STR_HIST_Y_LABEL_BASE = r"$n$"

    STR_HIST_X_LABEL = r"$p(\chi^2,{\rm d.o.f.})$"
    STR_HIST_X_LABEL_LOG = r"${\rm log}_{10}(p(\chi^2,{\rm d.o.f.}))$"

    # Class attributes

    cumulative: bool = False

    def __init__(self,
                 *args,
                 cumulative: Optional[bool] = None,
                 **kwargs):
        """ Init that allows the user to specify here whether to plot a cumulative hist or not, or else go with the
            default.
        """

        super().__init__(*args, **kwargs)

        self.cumulative = cumulative if cumulative is not None else self.cumulative

        # Declare instance attributes which will be calculated later
        self.l_p: Optional[np.ndarray] = None
        self.l_p_trimmed: Optional[np.ndarray] = None
        self.l_p_to_plot: Optional[np.ndarray] = None
        self.l_ref_p: Optional[np.ndarray] = None
        self.l_ref_p_trimmed: Optional[np.ndarray] = None
        self.l_ref_logp: Optional[np.ndarray] = None

    # Protected method overrides

    def _get_x_label(self) -> str:
        """ Override parent method to get the label for the X axis.
        """
        if self.two_sample_mode:
            return self.STR_HIST_X_LABEL_LOG
        else:
            return self.STR_HIST_X_LABEL

    def _get_y_label(self) -> str:
        """ Override parent method to get the label for the Y axis.
        """

        y_label = self.STR_HIST_Y_LABEL_BASE
        if self.cumulative:
            y_label += self.STR_HIST_Y_LABEL_CUMULATIVE_TAIL

        return y_label

    def _get_plot_title(self) -> str:
        """ Overridable method to get the plot title
        """
        if self.two_sample_mode:
            plot_title = self.STR_HIST_BASE_TITLE_LOG
        else:
            plot_title = self.STR_HIST_BASE_TITLE

        if self.cumulative:
            plot_title += self.STR_HIST_TITLE_CUMULATIVE_TAIL

        plot_title += self.bin_parameter.name

        if self.bin_parameter != BinParameters.TOT:
            plot_title += f" {self.bin_limits}"

        return plot_title

    def _get_legend_loc(self) -> Optional[str]:
        """ Override parent method to get location of the legend (None = don't display legend)
        """
        if self.two_sample_mode:
            return "lower right"
        return None

    def _get_l_summary_text(self) -> List[str]:
        """ Override parent method to get summary text.
        """

        # Add a line for the median p value of test data
        p_median = np.median(self.l_p_trimmed)
        l_summary_text = [self.STR_HIST_TEST_P_MED_LABEL + f"{p_median:.{self.P_MED_DIGITS}e}"]

        # Optionally add a line for the median p value of reference data
        if self.two_sample_mode:
            ref_p_median = np.median(self.l_ref_p_trimmed)
            l_summary_text.append(self.STR_HIST_REF_P_MED_LABEL + f"{ref_p_median:.{self.P_MED_DIGITS}e}")

        # Add a line for the p value from the KS test
        l_summary_text.append(self.STR_KS_P_LABEL + f"{self.ks_test_result.pvalue:.{self.KS_P_DIGITS}f}")

        return l_summary_text

    def _get_msg_plot_saved(self) -> str:
        """ Override parent method to get the method to print to log that a plot has been saved
        """
        return (f"Saved {self.bin_parameter} {self.bin_limits} PSF Res (Star Pos.) histogram to"
                f" {self.qualified_plot_filename}")

    def _calc_plotting_data(self):
        """ Override parent method to get all the data we want to plot.
        """

        self.l_p: Sequence[float] = calculate_p_values(cat = self.t_good,
                                                       group_mode = self.group_mode)

        # Remove any bad values from the data
        self.l_p_trimmed = np.array([x for x in self.l_p if x > 0 and not is_inf_nan_or_masked(x)])
        l_logp = np.log10(self.l_p_trimmed)

        # Check if there's any valid data for this bin
        if len(l_logp) <= 1:
            # We'll always make the tot plot for testing purposes, but log a warning if no data
            if self.bin_parameter == BinParameters.TOT:
                logger.warning(self.MSG_INSUFFICIENT_DATA_TOT, self.bin_parameter.value)
            else:
                logger.debug(self.MSG_INSUFFICIENT_DATA, self.bin_parameter.value, self.bin_limits)
                return True

        # Determine whether we'll plot log or not depending on comparison mode
        if self.two_sample_mode:
            self.l_p_to_plot = l_logp

            # Get data for the reference catalog here
            self.l_ref_p = calculate_p_values(cat = self.ref_t_good,
                                              group_mode = self.group_mode)
            self.l_ref_p_trimmed = np.array([x for x in self.l_ref_p if x > 0 and not is_inf_nan_or_masked(x)])

            self.l_ref_logp = np.log10(self.l_ref_p_trimmed)
        else:
            self.l_p_to_plot = self.l_p_trimmed
            self.l_ref_p = None
            self.l_ref_p_trimmed = None
            self.l_ref_logp = None

        return False

    def _draw_plot(self):
        """ Override parent method for drawing the plot.
        """
        # Plot the histogram for both test and reference catalogs
        plt.hist(self.l_p_to_plot,
                 bins = self.HIST_NUM_BINS,
                 density = True,
                 cumulative = self.cumulative,
                 histtype = self.HIST_TYPE,
                 label = self.TEST_CAT_LEGEND_NAME,
                 linestyle = '-')
        if self.two_sample_mode:
            # Add the other histogram, plus a legend to differentiate them
            plt.hist(self.l_ref_logp,
                     bins = self.HIST_NUM_BINS,
                     density = True,
                     cumulative = self.cumulative,
                     histtype = self.HIST_TYPE,
                     label = self.REF_CAT_LEGEND_NAME,
                     linestyle = '--')
