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
from typing import Dict, List, Sequence, Type

from astropy.table import Table

from SHE_PPT import logging as log
from SHE_PPT.table_formats.she_star_catalog import SheStarCatalogFormat, SheStarCatalogMeta
from SHE_PPT.table_utility import SheTableMeta
from SHE_Validation.binning.bin_constraints import get_ids_for_test_cases, get_table_of_ids
from SHE_Validation_PSF.constants.psf_res_test_info import L_PSF_RES_TEST_CASE_INFO

logger = log.getLogger(__name__)


# We'll be modifying the star catalog table a bit, so define an extended table format for the new columns

class SheExtStarCatalogMeta(SheStarCatalogMeta):

    def __init__(self):
        super().__init__()

        self.bin_parameter = "BIN_PAR"
        self.bin_limits = "BIN_LIMS"


class SheExtStarCatalogFormat(SheStarCatalogFormat):
    meta_type: Type[SheTableMeta] = SheExtStarCatalogMeta

    def __init__(self):
        super().__init__()

        self.group_p = self.set_column_properties("SHE_STARCAT_GROUP_P", dtype = ">f4", fits_dtype = "E",
                                                  comment = "p-value for a Chi-squared test on this group")

        self._finalize_init()


TF = SheExtStarCatalogFormat()


def test_psf_res(star_cat: Table,
                 d_l_bin_limits = Dict[Sequence[float]]) -> Dict[List[Table]]:
    """ Calculates results of the PSF residual validation test for all bin parameters and bins.
    """

    # Create a dict of lists of tables for results
    d_l_psf_res_results: Dict[List[Table]] = {}

    # Get lists of IDs in each bin
    d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = L_PSF_RES_TEST_CASE_INFO,
                                                        d_bin_limits = d_l_bin_limits,
                                                        detections_table = star_cat, )

    # Loop over bin parameters first, then over bin limits, and test for each
    for bin_parameter in d_l_bin_limits:

        # Create a list for the results of each set of bin limits
        l_psf_res_results: List[Table] = []

        # Get data for this bin parameter
        l_l_test_case_object_ids = d_l_l_test_case_object_ids[bin_parameter]
        l_bin_limits = d_l_bin_limits[bin_parameter]
        num_bins = len(l_bin_limits) - 1

        # Loop over bins now
        for bin_index in range(num_bins):
            # Get data for these bin limits
            l_test_case_object_ids = l_l_test_case_object_ids[bin_index]
            bin_limits = l_bin_limits[bin_index:bin_index + 2]

            # Get a table with only data in this bin
            table_in_bin = get_table_of_ids(star_cat, l_test_case_object_ids, id_colname = TF.id)

        # Add the list of results to the output dict
        d_l_psf_res_results[bin_parameter] = l_psf_res_results

    return d_l_psf_res_results
