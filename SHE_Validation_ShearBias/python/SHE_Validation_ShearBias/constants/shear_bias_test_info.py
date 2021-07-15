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


# Metadata about the requirement
SHEAR_BIAS_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-140",
                                              description=("Residual of CTI to galaxy multiplicative bias mu <5x10-4 " +
                                                           "(1-sigma)."),
                                              parameter=("Z-value for slope of g1_image versus distance from readout " +
                                                         "register compared to expectation of zero."))

# Metadata about the test
SHEAR_BIAS_TEST_INFO = TestInfo(test_id="T-SHE-000010-CTI-gal",
                                description=("Linear dependence of galaxy ellipticity with read-out register distance " +
                                             "(slope)."))


class ShearBiasTestCases(Enum):
    """ Enum of test cases for this test.
    """
    GLOBAL = "global"
    SNR = "snr"
    BG = "bg"
    COLOUR = "colour"
    SIZE = "size"
    EPOCH = "epoch"


SHEAR_BIAS_TEST_CASE_GLOBAL_INFO = TestCaseInfo(test_case_id="T-SHE-000010-CTI-gal",
                                                description=("Linear dependence of " +
                                                             "residual galaxy ellipticity with read-out " +
                                                             "register distance (slope) unbinned."),
                                                bins_cline_arg=None,
                                                bins_config_key=None,
                                                name=ShearBiasTestCases.GLOBAL.value,
                                                comment=None,)
SHEAR_BIAS_TEST_CASE_SNR_INFO = TestCaseInfo(test_case_id="TC-SHE-100028-CTI-gal-SNR",
                                             description=("Linear dependence of " +
                                                          "residual galaxy ellipticity with read-out register " +
                                                          "distance (slope) in bins of SNR of galaxies."),
                                             bins_cline_arg="snr_bin_limits",
                                             bins_config_key=AnalysisConfigKeys.CGV_SNR_BIN_LIMITS.value,
                                             name=ShearBiasTestCases.SNR.value,
                                             comment=None,)
SHEAR_BIAS_TEST_CASE_BG_INFO = TestCaseInfo(test_case_id="TC-SHE-100029-CTI-gal-bg",
                                            description=("Linear dependence of residual galaxy ellipticity " +
                                                         "with read-out register distance (slope) in bins of " +
                                                         "sky background levels."),
                                            bins_cline_arg="bg_bin_limits",
                                            bins_config_key=AnalysisConfigKeys.CGV_BG_BIN_LIMITS.value,
                                            name=ShearBiasTestCases.BG.value,
                                            comment=BACKGROUND_LEVEL_UNITS)
SHEAR_BIAS_TEST_CASE_COLOUR_INFO = TestCaseInfo(test_case_id="TC-SHE-100030-CTI-gal-col",
                                                description=("Linear dependence of residual galaxy " +
                                                             "ellipticity with read-out register distance " +
                                                             "(slope) in bins of colour of galaxies."),
                                                bins_cline_arg="colour_bin_limits",
                                                bins_config_key=AnalysisConfigKeys.CGV_COLOUR_BIN_LIMITS.value,
                                                name=ShearBiasTestCases.COLOUR.value,
                                                comment=COLOUR_DEFINITION)
SHEAR_BIAS_TEST_CASE_SIZE_INFO = TestCaseInfo(test_case_id="TC-SHE-100031-CTI-gal-size",
                                              description=("Linear dependence of residual galaxy ellipticity " +
                                                           "with read-out register distance (slope) in bins " +
                                                           "of size of galaxies."),
                                              bins_cline_arg="size_bin_limits",
                                              bins_config_key=AnalysisConfigKeys.CGV_SIZE_BIN_LIMITS.value,
                                              name=ShearBiasTestCases.SIZE.value,
                                              comment=SIZE_DEFINITION)
SHEAR_BIAS_TEST_CASE_EPOCH_INFO = TestCaseInfo(test_case_id="TC-SHE-100032-CTI-gal-epoch",
                                               description=("Linear dependence of residual galaxy " +
                                                            "ellipticity with read-out register distance " +
                                                            "(slope) in bins of observation epoch"),
                                               bins_cline_arg=None,
                                               bins_config_key=None,
                                               name=ShearBiasTestCases.EPOCH.value,
                                               comment=None)

# Create a dict of the test case info
D_SHEAR_BIAS_TEST_CASE_INFO = {ShearBiasTestCases.GLOBAL: SHEAR_BIAS_TEST_CASE_GLOBAL_INFO,
                               ShearBiasTestCases.SNR: SHEAR_BIAS_TEST_CASE_SNR_INFO,
                               ShearBiasTestCases.BG: SHEAR_BIAS_TEST_CASE_BG_INFO,
                               ShearBiasTestCases.COLOUR: SHEAR_BIAS_TEST_CASE_COLOUR_INFO,
                               ShearBiasTestCases.SIZE: SHEAR_BIAS_TEST_CASE_SIZE_INFO,
                               ShearBiasTestCases.EPOCH: SHEAR_BIAS_TEST_CASE_EPOCH_INFO, }

SHEAR_BIAS_TEST_CASES = D_SHEAR_BIAS_TEST_CASE_INFO.keys()

NUM_SHEAR_BIAS_TEST_CASES = len(ShearBiasTestCases)

NUM_METHOD_SHEAR_BIAS_TEST_CASES = NUM_SHEAR_ESTIMATION_METHODS * NUM_SHEAR_BIAS_TEST_CASES
