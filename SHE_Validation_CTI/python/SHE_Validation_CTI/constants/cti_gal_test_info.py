""" @file cti_gal_test_info.py

    Created 15 Dec 2020

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

from SHE_Validation.constants.test_info import RequirementInfo, TestInfo, TestCaseInfo
from SHE_Validation.test_info_utility import make_test_case_info_for_bins_and_methods


# Metadata about the requirement
CTI_GAL_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-140",
                                           description=("Residual of CTI to galaxy multiplicative bias mu <5x10-4 " +
                                                        "(1-sigma)."),
                                           parameter=("Z-value for slope of g1_image versus distance from readout " +
                                                      "register compared to expectation of zero."))

# Metadata about the test
CTI_GAL_TEST_INFO = TestInfo(test_id="T-SHE-000010-CTI-gal",
                             description=("Linear dependence of galaxy ellipticity with read-out register distance " +
                                          "(slope)."))


BASE_CTI_GAL_TEST_CASE_INFO = TestCaseInfo(base_test_case_id="T-SHE-000010-CTI-gal",
                                           base_description=("Linear dependence of " +
                                                             "residual galaxy ellipticity with read-out " +
                                                             "register distance (slope)."),)

# Create a dict of the test case info
L_CTI_GAL_TEST_CASE_INFO = make_test_case_info_for_bins_and_methods(BASE_CTI_GAL_TEST_CASE_INFO)

NUM_CTI_GAL_TEST_CASES = len(L_CTI_GAL_TEST_CASE_INFO)

# Create a dict of the requirement info
D_L_CTI_GAL_REQUIREMENT_INFO = {}
for test_case_info in L_CTI_GAL_TEST_CASE_INFO:
    D_L_CTI_GAL_REQUIREMENT_INFO[test_case_info.name] = CTI_GAL_REQUIREMENT_INFO
