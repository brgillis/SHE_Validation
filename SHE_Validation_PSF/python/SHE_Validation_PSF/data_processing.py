""" @file data_processing.py

    Created 23 March 2022 by Bryan Gillis

    Functions for data processing in PSF Residual validation test
"""

__updated__ = "2022-04-23"

#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
from typing import Dict, List, Optional, Sequence

import numpy as np
from astropy.table import Table
from scipy.stats import ks_2samp, kstest, uniform
from scipy.stats.stats import KstestResult

from SHE_PPT import logging as log
from SHE_PPT.utility import is_inf_or_nan, is_nan_or_masked
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint, get_ids_for_test_cases
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation_PSF.constants.psf_res_sp_test_info import L_PSF_RES_SP_TEST_CASE_INFO
from SHE_Validation_PSF.file_io import PsfResSPPlotFileNamer
from SHE_Validation_PSF.plotting import PsfResSPHistPlotter
from SHE_Validation_PSF.utility import (KsResult, add_snr_column_to_star_cat, calculate_p_values,
                                        get_table_in_bin, getitem_or_none, )

logger = log.getLogger(__name__)


def run_psf_res_val_test(star_cat: Table,
                         d_l_bin_limits: Dict[BinParameters, Sequence[float]],
                         ref_star_cat: Optional[Table] = None) -> Dict[str, List[KsResult]]:
    """ Calculates results of the PSF residual validation test for all bin parameters and bins.

        Returns a Dict of Lists of log(p) values for each test case and bin.
    """

    # Add the necessary SNR column to the star_cat and ref_star_cat so we can bin with it
    add_snr_column_to_star_cat(star_cat)
    if ref_star_cat is not None:
        add_snr_column_to_star_cat(ref_star_cat)

    # Get lists of IDs in each bin, in both the test and reference star catalogs
    d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = L_PSF_RES_SP_TEST_CASE_INFO,
                                                        d_bin_limits = d_l_bin_limits,
                                                        detections_table = star_cat,
                                                        bin_constraint_type = BinParameterBinConstraint)

    d_l_l_ref_test_case_object_ids: Optional[Dict[str, List[Sequence[int]]]]
    if ref_star_cat is not None:
        d_l_l_ref_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = L_PSF_RES_SP_TEST_CASE_INFO,
                                                                d_bin_limits = d_l_bin_limits,
                                                                detections_table = ref_star_cat,
                                                                bin_constraint_type = BinParameterBinConstraint)
    else:
        d_l_l_ref_test_case_object_ids = None

    # Init a dict of list of results
    d_l_psf_res_result_ps: Dict[str, List[KsResult]] = {}

    # Loop over bin parameters first, then over bin limits, and test for each
    for test_case in L_PSF_RES_SP_TEST_CASE_INFO:

        bin_parameter = test_case.bin_parameter

        group_mode = (bin_parameter == BinParameters.TOT)

        # Get data for this bin parameter
        l_l_test_case_object_ids = d_l_l_test_case_object_ids[test_case.name]
        l_l_ref_test_case_object_ids = getitem_or_none(d_l_l_ref_test_case_object_ids, test_case.name)

        l_bin_limits = d_l_bin_limits[bin_parameter]
        num_bins = len(l_bin_limits) - 1

        # Create a list for the results of each set of bin limits
        l_psf_res_result_ps: List[KsResult] = [KstestResult(np.nan, np.nan)] * num_bins

        # Loop over bins now
        for bin_index in range(num_bins):
            # Get data for these bin limits
            l_test_case_object_ids = l_l_test_case_object_ids[bin_index]
            l_ref_test_case_object_ids = getitem_or_none(l_l_ref_test_case_object_ids, bin_index)

            # Get tables with only data in this bin
            table_in_bin = get_table_in_bin(cat = star_cat,
                                            bin_parameter = bin_parameter,
                                            bin_index = bin_index,
                                            l_bin_limits = l_bin_limits,
                                            l_test_case_object_ids = l_test_case_object_ids)
            ref_table_in_bin = get_table_in_bin(cat = ref_star_cat,
                                                bin_parameter = bin_parameter,
                                                bin_index = bin_index,
                                                l_bin_limits = l_bin_limits,
                                                l_test_case_object_ids = l_ref_test_case_object_ids)

            # Run the test on this table and store the result
            l_psf_res_result_ps[bin_index] = run_psf_res_val_test_for_bin(star_cat = table_in_bin,
                                                                          ref_star_cat = ref_table_in_bin,
                                                                          group_mode = group_mode)

            # Create plots for this bin
            hist_plotter = PsfResSPHistPlotter(star_cat = star_cat,
                                               file_namer = PsfResSPPlotFileNamer(bin_parameter = bin_parameter,
                                                                                  bin_index = bin_index),
                                               bin_limits = l_bin_limits[bin_index:bin_index + 1],
                                               l_ids_in_bin = l_test_case_object_ids,
                                               ks_test_result = l_psf_res_result_ps[bin_index],
                                               group_mode = group_mode)
            hist_plotter.plot()

            # Add the list of results to the output dict
            d_l_psf_res_result_ps[test_case.name] = l_psf_res_result_ps

    return d_l_psf_res_result_ps


def run_psf_res_val_test_for_bin(star_cat: Table,
                                 ref_star_cat: Optional[Table] = None,
                                 group_mode: bool = False) -> KsResult:
    """ Runs the PSF Residual test, taking as input a table in format ExtSheStarCatalogFormat.

        If group_mode is set to True, will do the test on groups rather than individual stars

        Returns log(p) for the set of tests (sum of log(p) for each group or individual star).
    """

    l_ps = calculate_p_values(star_cat, group_mode)
    l_ref_ps = calculate_p_values(ref_star_cat, group_mode)

    # Check if we have any valid data
    l_ps_trimmed = [x for x in l_ps if not is_inf_or_nan(x)]
    if l_ref_ps is not None:
        l_ref_ps_trimmed = [x for x in l_ref_ps if not is_inf_or_nan(x)]
    else:
        l_ref_ps_trimmed = None

    # Raise an exception of reference data is provided but it's invalid

    # Warn if there's no valid test data for this bin and return a NaN result
    if (log_if_no_valid_data(l_ref_ps, l_ref_ps_trimmed) or
            log_if_no_valid_data(l_ps, l_ps_trimmed, )):

        # Return a NaN test result
        return KstestResult(np.nan, np.nan)

    # Now, we take these various p values and test that this set of p values is reasonable to be obtained,
    # using a KS test.

    ks_test_result: KsResult
    if ref_star_cat is None:
        # If no reference star catalog is provided, do a one-sample test comparing against a uniform distribution of
        # p values
        ks_test_result = kstest(rvs = l_ps_trimmed, cdf = uniform.cdf)
    else:
        # If a reference star catalog is provided, test that this catalog is consistent with it or better using a
        # two-sample test.

        ks_test_result = ks_2samp(data1 = l_ps_trimmed, data2 = l_ref_ps_trimmed,
                                  alternative = 'greater')

    return ks_test_result


def log_if_no_valid_data(l_ps: List[float], l_ps_trimmed: List[float]) -> bool:
    """If the provided data is invalid, log a warning with the provided method
    """
    if l_ps_trimmed is not None and len(l_ps_trimmed) == 0:
        logger.warning("No valid data present in execution of run_psf_res_val_test_for_bin. \n"
                       f"Total data length: {len(l_ps)}\n"
                       f"Number of NaN results: {np.sum(is_nan_or_masked(l_ps))}\n"
                       f"Number of Inf results: {np.sum(np.isinf(l_ps))}\n")
        return True
    return False
