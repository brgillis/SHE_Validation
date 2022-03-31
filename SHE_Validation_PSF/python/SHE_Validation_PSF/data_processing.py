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
from copy import deepcopy
from typing import Dict, List, Optional, Sequence, Type, Union

import numpy as np
from astropy.table import Row, Table
from scipy.stats import chi2, kstest, uniform
from scipy.stats.stats import KstestResult

from SHE_PPT import logging as log
from SHE_PPT.table_formats.she_star_catalog import SheStarCatalogFormat, SheStarCatalogMeta
from SHE_PPT.table_utility import SheTableMeta
from SHE_PPT.utility import is_inf_or_nan
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint, get_ids_for_test_cases, get_table_of_ids
from SHE_Validation.binning.bin_data import BIN_TF
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation_PSF.constants.psf_res_test_info import L_PSF_RES_TEST_CASE_INFO

logger = log.getLogger(__name__)


# We'll be modifying the star catalog table a bit, so define an extended table format for the new columns

class SheExtStarCatalogMeta(SheStarCatalogMeta):
    """ Modified star catalog metadata format which adds some meta values.
    """

    def __init__(self):
        super().__init__()

        self.bin_parameter = "BIN_PAR"
        self.bin_limits = "BIN_LIMS"


class SheExtStarCatalogFormat(SheStarCatalogFormat):
    """ Modified star catalog table format which adds a few extra columns and some metadata values.
    """
    meta_type: Type[SheTableMeta] = SheExtStarCatalogMeta
    meta: SheExtStarCatalogMeta
    m: SheExtStarCatalogMeta

    def __init__(self):
        super().__init__()

        self.snr = self.set_column_properties(BIN_TF.snr, dtype = BIN_TF.dtypes[BIN_TF.snr],
                                              fits_dtype = BIN_TF.fits_dtypes[BIN_TF.snr],
                                              is_optional = True)

        self.group_p = self.set_column_properties("SHE_STARCAT_GROUP_P", dtype = ">f4", fits_dtype = "E",
                                                  comment = "p-value for a Chi-squared test on this group",
                                                  is_optional = True)

        self.star_p = self.set_column_properties("SHE_STARCAT_STAR_P", dtype = ">f4", fits_dtype = "E",
                                                 comment = "p-value for a Chi-squared test on this star",
                                                 is_optional = True)

        self._finalize_init()


ESC_TF = SheExtStarCatalogFormat()


def run_psf_res_val_test(star_cat: Table,
                         d_l_bin_limits = Dict[BinParameters, Sequence[float]]) -> Dict[str, List[KstestResult]]:
    """ Calculates results of the PSF residual validation test for all bin parameters and bins.

        Returns a Dict of Lists of log(p) values for each test case and bin.
    """

    # Add the necessary SNR column to the star_cat so we can bin with it
    add_snr_column_to_star_cat(star_cat)

    # Get lists of IDs in each bin
    d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = L_PSF_RES_TEST_CASE_INFO,
                                                        d_bin_limits = d_l_bin_limits,
                                                        detections_table = star_cat,
                                                        bin_constraint_type = BinParameterBinConstraint)

    # Init a dict of list of results
    d_l_psf_res_result_ps: Dict[str, List[KstestResult]] = {}

    # Loop over bin parameters first, then over bin limits, and test for each
    for test_case in L_PSF_RES_TEST_CASE_INFO:

        bin_parameter = test_case.bin_parameter

        # Get data for this bin parameter
        l_l_test_case_object_ids = d_l_l_test_case_object_ids[test_case.name]
        l_bin_limits = d_l_bin_limits[bin_parameter]
        num_bins = len(l_bin_limits) - 1

        # Create a list for the results of each set of bin limits
        l_psf_res_result_ps: List[KstestResult] = [KstestResult(np.nan, np.nan)] * num_bins

        # Loop over bins now
        for bin_index in range(num_bins):
            # Get data for these bin limits
            l_test_case_object_ids = l_l_test_case_object_ids[bin_index]

            # Get a table with only data in this bin
            table_in_bin = deepcopy(get_table_of_ids(star_cat, l_test_case_object_ids, id_colname = ESC_TF.id))

            # Save the info about bin_parameter and bin_limits in the table's metadata
            table_in_bin.meta[ESC_TF.m.bin_parameter] = bin_parameter.value
            table_in_bin.meta[ESC_TF.m.bin_limits] = str(l_bin_limits[bin_index:bin_index + 2])

            # Run the test on this table and store the result
            l_psf_res_result_ps[bin_index] = run_psf_res_val_test_for_bin(star_cat = table_in_bin,
                                                                          group_mode = (
                                                                                  bin_parameter == BinParameters.TOT))

        # Add the list of results to the output dict
        d_l_psf_res_result_ps[test_case.name] = l_psf_res_result_ps

    return d_l_psf_res_result_ps


def add_snr_column_to_star_cat(star_cat: Table) -> None:
    """Adds the SNR column to the star catalog if not already present.
    """
    if ESC_TF.snr not in star_cat.colnames:
        star_cat[ESC_TF.snr] = star_cat[ESC_TF.flux] / star_cat[ESC_TF.flux_err]


def add_p_columns_to_star_cat(star_cat: Table) -> None:
    """ Adds columns for star and group p-values to the table if not already present. The new columns will initially
        be filled with np.NaN to indicate it has not yet been calculated.
    """
    len_star_cat = len(star_cat)
    if ESC_TF.group_p not in star_cat.colnames:
        star_cat[ESC_TF.group_p] = np.NaN * np.ones(len_star_cat, dtype = ESC_TF.dtypes[ESC_TF.group_p])
    if ESC_TF.star_p not in star_cat.colnames:
        star_cat[ESC_TF.star_p] = np.NaN * np.ones(len_star_cat, dtype = ESC_TF.dtypes[ESC_TF.star_p])


def run_psf_res_val_test_for_bin(star_cat: Table,
                                 group_mode: bool = False) -> KstestResult:
    """ Runs the PSF Residual test, taking as input a table in format ExtSheStarCatalogFormat.

        If group_mode is set to True, will do the test on groups rather than individual stars

        Returns log(p) for the set of tests (sum of log(p) for each group or individual star).
    """

    # Select the ID column based on the mode
    if group_mode:
        id_colname = ESC_TF.group_id
        chisq_colname = ESC_TF.group_chisq
        num_pix_colname = ESC_TF.group_unmasked_pix
        num_fitted_params_colname: Optional[str] = ESC_TF.group_num_fitted_params
        p_colname = ESC_TF.group_p
    else:
        id_colname = ESC_TF.id
        chisq_colname = ESC_TF.star_chisq
        num_pix_colname = ESC_TF.star_unmasked_pix
        num_fitted_params_colname: Optional[str] = None
        p_colname = ESC_TF.star_p

    # We'll just use one row from each group, or each individual star, for the test
    l_unique_ids: Sequence[int] = np.unique(star_cat[id_colname])
    num_groups = len(l_unique_ids)

    l_ps = np.ones(num_groups, dtype = float)

    # Run the test for each group
    star_cat.add_index(id_colname)
    for i, group_id in enumerate(l_unique_ids):
        # Extract just the first row of each group
        table_or_row_in_group: Union[Table, Row] = star_cat.loc[group_id]
        if isinstance(table_or_row_in_group, Table):
            # Multiple rows are in this group, so just get the first
            data_row: Row = table_or_row_in_group[0]
        elif isinstance(table_or_row_in_group, Row):
            data_row: Row = table_or_row_in_group
        else:
            raise TypeError(f"Type of object returned by Table.loc is not recognized: {type(table_or_row_in_group)}")

        # Check if the p value has already been calculated, and use that if so
        if not np.isnan(data_row[p_colname]):
            l_ps[i] = data_row[p_colname]
            continue

        # Run the test on this row

        # Get the number of fitted params - if the colname is None, that means we have 0 fitted params
        if num_fitted_params_colname is not None:
            num_fitted_params = data_row[num_fitted_params_colname]
        else:
            num_fitted_params = 0

        l_ps[i] = chi2.sf(x = data_row[chisq_colname],
                          df = data_row[num_pix_colname] - num_fitted_params)

        # Save this value in the initial data table
        table_or_row_in_group[p_colname] = l_ps[i]

    # Check if we have any valid data
    l_ps_trimmed = [x for x in l_ps if not is_inf_or_nan(x)]
    if len(l_ps_trimmed) == 0:

        logger.warning("No valid data present in execution of run_psf_res_val_test_for_bin. \n"
                       f"Total data length: {len(l_ps)}\n"
                       f"Number of NaN results: {np.sum(np.isnan(l_ps))}\n"
                       f"Number of Inf results: {np.sum(np.isinf(l_ps))}\n")

        # Return a NaN test result
        ks_test_result: KstestResult = KstestResult(np.nan, np.nan)

    else:

        # Now, we take these various p values and test that this set of p values is reasonable to be obtained,
        # using a KS test and assuming that ideally, these would come from a uniform distribution from 0 to 1.
        ks_test_result: KstestResult = kstest(rvs = l_ps, cdf = uniform.cdf)

    return ks_test_result
