""" @file shear_bias_test_info.py

    Created 15 July 2021

    Default values for information about tests and test cases.
"""

__updated__ = "2021-07-15"

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

from SHE_PPT.constants.shear_estimation_methods import NUM_METHODS as NUM_SHEAR_ESTIMATION_METHODS
from SHE_PPT.pipeline_utility import AnalysisConfigKeys

from SHE_Validation.test_info import RequirementInfo, TestInfo, TestCaseInfo
from SHE_Validation_CTI.constants.shear_bias_default_config import (BACKGROUND_LEVEL_UNITS,
                                                                    COLOUR_DEFINITION, SIZE_DEFINITION)


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


SHEAR_BIAS_TEST_CASE_M_INFO = TestCaseInfo(test_case_id="TC-SHE-100017-shear-bias-m",
                                           description=("Multiplicative shear bias."),
                                           name=ShearBiasTestCases.M.value,
                                           comment=None,)
SHEAR_BIAS_TEST_CASE_C_INFO = TestCaseInfo(test_case_id="TC-SHE-100018-shear-bias-c",
                                           description=("Additive shear bias."),
                                           name=ShearBiasTestCases.C.value,
                                           comment=None,)

# Create a dict of the test case info
D_SHEAR_BIAS_TEST_CASE_INFO = {ShearBiasTestCases.M: SHEAR_BIAS_TEST_CASE_M_INFO,
                               ShearBiasTestCases.C: SHEAR_BIAS_TEST_CASE_C_INFO, }

SHEAR_BIAS_TEST_CASES = D_SHEAR_BIAS_TEST_CASE_INFO.keys()

NUM_SHEAR_BIAS_TEST_CASES = len(ShearBiasTestCases)

NUM_METHOD_SHEAR_BIAS_TEST_CASES = NUM_SHEAR_ESTIMATION_METHODS * NUM_SHEAR_BIAS_TEST_CASES
