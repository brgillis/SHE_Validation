""" @file psf_res_test_info.py

    Created 08 March 2022 by Bryan Gillis

    Default values for information about tests and test cases.
"""

__updated__ = "2022-04-08"

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

from SHE_Validation.constants.test_info import (BinParameters, ID_NUMBER_REPLACE_TAG, NAME_REPLACE_TAG, RequirementInfo,
                                                TestCaseInfo,
                                                TestInfo, )
from SHE_Validation.test_info_utility import make_test_case_info_for_bins

# Metadata about the requirement
PSF_RES_REQUIREMENT_INFO = RequirementInfo(requirement_id = "R-SHE-PRD-F-100",
                                           description = ("The distribution of chi-squared (chi-squared) values for "
                                                          "each star with respect to the model, over the population "
                                                          "of stars, shall be consistent (TBD) with the chi-squared "
                                                          "distribution."),
                                           parameter = ("TBD - Statistic representing how well PSF residual "
                                                        "chi-squared statistics match expected distributions."))

# Metadata about the test
PSF_RES_TEST_INFO = TestInfo(test_id = "T-SHE-000001-PSF-res-star-pos",
                             description = ("Consistency of PSF residual chi-squared values with expected "
                                            "distributions."))

BASE_PSF_RES_TEST_CASE_INFO = TestCaseInfo(base_test_case_id = f"TC-SHE-{ID_NUMBER_REPLACE_TAG}-PSF-res-star-"
                                                               f"{NAME_REPLACE_TAG}",
                                           base_name = f"PR-{NAME_REPLACE_TAG}",
                                           base_description = PSF_RES_TEST_INFO.description,
                                           base_id_number = 100001)

# Create a dict of the test case info

L_PSF_RES_BIN_PARAMETERS = (BinParameters.TOT, BinParameters.SNR)

L_PSF_RES_TEST_CASE_INFO = make_test_case_info_for_bins(BASE_PSF_RES_TEST_CASE_INFO,
                                                        l_bin_parameters = L_PSF_RES_BIN_PARAMETERS)

NUM_PSF_RES_TEST_CASES = len(L_PSF_RES_TEST_CASE_INFO)

# Create a dict of the requirement info
D_L_PSF_RES_REQUIREMENT_INFO = {}
for test_case_info in L_PSF_RES_TEST_CASE_INFO:
    D_L_PSF_RES_REQUIREMENT_INFO[test_case_info.name] = PSF_RES_REQUIREMENT_INFO
