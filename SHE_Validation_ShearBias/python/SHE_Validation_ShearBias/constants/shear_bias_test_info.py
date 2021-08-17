""" @file shear_bias_test_info.py

    Created 15 July 2021

    Default values for information about tests and test cases.
"""

__updated__ = "2021-08-11"

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

from enum import Enum

from SHE_Validation.constants.test_info import RequirementInfo, TestInfo, TestCaseInfo
from SHE_Validation.test_info_utility import make_test_case_info_for_bins_and_methods


# Metadata about the requirements
SHEAR_BIAS_M_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-070",
                                                description=("Multiplicative bias mu of shear measurement "
                                                             "<2x10^-3."),
                                                parameter=("Z-value for measured multiplicative bias compared to "
                                                           "target value of <2x10^-3."))
SHEAR_BIAS_C_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-080",
                                                description=("Additive bias c of shear measurement "
                                                             "<1x10^-4"),
                                                parameter=("Z-value for measured additive bias compared to "
                                                           "target value of <1x10^-4."))

# Metadata about the test
SHEAR_BIAS_TEST_INFO = TestInfo(test_id="T-SHE-000006-shear-bias",
                                description=("Multiplicative and additive bias of shear estimation."))


class ShearBiasTestCases(Enum):
    """ Enum of test cases for this test.
    """
    M = "m"
    C = "c"


M_TEST_CASE_ID = "TC-SHE-100017-shear-bias-m"
BASE_SHEAR_BIAS_TEST_CASE_M_INFO = TestCaseInfo(base_test_case_id=M_TEST_CASE_ID,
                                                base_description=("Multiplicative shear bias."),)
C_TEST_CASE_ID = "TC-SHE-100018-shear-bias-c"
BASE_SHEAR_BIAS_TEST_CASE_C_INFO = TestCaseInfo(base_test_case_id=C_TEST_CASE_ID,
                                                base_description=("Additive shear bias."),)

# Create lists of the test case info for just m, just c, and combined
L_SHEAR_BIAS_TEST_CASE_M_INFO = make_test_case_info_for_bins_and_methods([BASE_SHEAR_BIAS_TEST_CASE_M_INFO])
L_SHEAR_BIAS_TEST_CASE_C_INFO = make_test_case_info_for_bins_and_methods([BASE_SHEAR_BIAS_TEST_CASE_C_INFO])
L_SHEAR_BIAS_TEST_CASE_INFO = [*L_SHEAR_BIAS_TEST_CASE_M_INFO, *L_SHEAR_BIAS_TEST_CASE_C_INFO]

NUM_SHEAR_BIAS_M_TEST_CASES = len(L_SHEAR_BIAS_TEST_CASE_M_INFO)
NUM_SHEAR_BIAS_M_TEST_CASES = len(L_SHEAR_BIAS_TEST_CASE_C_INFO)
NUM_SHEAR_BIAS_TEST_CASES = len(L_SHEAR_BIAS_TEST_CASE_INFO)


def get_prop_from_id(test_case_id: str):
    """ Utility function to determine whether a test case refers to M or C from the test case ID.
    """
    if M_TEST_CASE_ID in test_case_info.id:
        return ShearBiasTestCases.M
    elif C_TEST_CASE_ID in test_case_info.id:
        return ShearBiasTestCases.C
    else:
        raise ValueError(f"Unrecognized test case ID: {test_case_id}")


# Create a dict of the requirement info
D_L_SHEAR_BIAS_REQUIREMENT_INFO = {}
for test_case_info in L_SHEAR_BIAS_TEST_CASE_INFO:
    prop = get_prop_from_id(test_case_info.id)
    if prop == ShearBiasTestCases.M:
        D_L_SHEAR_BIAS_REQUIREMENT_INFO[test_case_info.name] = SHEAR_BIAS_M_REQUIREMENT_INFO
    else:
        D_L_SHEAR_BIAS_REQUIREMENT_INFO[test_case_info.name] = SHEAR_BIAS_C_REQUIREMENT_INFO
