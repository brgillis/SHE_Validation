""" @file cti_psf_test_info.py

    Created 3 Nov 2021

    Default values for information about tests and test cases.
"""

__updated__ = "2021-08-09"

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
CTI_PSF_REQUIREMENT_INFO = RequirementInfo(requirement_id = "R-SHE-CAL-F-020",
                                           description = "CTI correction residuals in the PSF.",
                                           parameter = ("Z-values of differences in slope of g1_image versus distance "
                                                        "from readout register between bins, compared to expectation "
                                                        "of zero."))

# Metadata about the test
CTI_PSF_TEST_INFO = TestInfo(test_id = "T-SHE-000009-CTI-PSF",
                             description = ("Linear dependence of PSF ellipticity with read-out register  distance ("
                                            "slope)."))

BASE_CTI_PSF_TEST_CASE_INFO = TestCaseInfo(base_test_case_id = f"TC-SHE-{ID_NUMBER_REPLACE_TAG}-CTI-PSF-"
                                                               f"{NAME_REPLACE_TAG}",
                                           base_name = f"CG-{NAME_REPLACE_TAG}",
                                           base_description = ("Linear dependence of PSF ellipticity with read-out "
                                                               "register  distance (slope)."),
                                           base_id_number = 100024)

# Create a list and dict of the test case info for each bin parameter
CTI_PSF_BIN_PARAMETERS = [BinParameters.SNR,
                          BinParameters.BG,
                          BinParameters.COLOUR,
                          BinParameters.EPOCH]

L_CTI_PSF_TEST_CASE_INFO = make_test_case_info_for_bins(BASE_CTI_PSF_TEST_CASE_INFO,
                                                        l_bin_parameters = CTI_PSF_BIN_PARAMETERS)

NUM_CTI_PSF_TEST_CASES = len(L_CTI_PSF_TEST_CASE_INFO)

# Create a dict of the requirement info
D_L_CTI_PSF_REQUIREMENT_INFO = {}
for test_case_info in L_CTI_PSF_TEST_CASE_INFO:
    D_L_CTI_PSF_REQUIREMENT_INFO[test_case_info.name] = CTI_PSF_REQUIREMENT_INFO
