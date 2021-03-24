""" @file cti_gal_test_info.py

    Created 15 Dec 2020

    Default values for information about tests and test cases.
"""

__updated__ = "2021-03-03"

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

from SHE_Validation.test_info import TestCaseInfo
from SHE_Validation_CTI.constants.cti_gal_default_config import BACKGROUND_LEVEL_UNITS, \
    COLOUR_DEFINITION, SIZE_DEFINITION


# Metadata about the requirement
CTI_GAL_REQUIREMENT_ID = "R-SHE-CAL-F-140"
CTI_GAL_REQUIREMENT_DESCRIPTION = "Residual of CTI to galaxy multiplicative bias mu <5x10-4 (1-sigma)."
CTI_GAL_PARAMETER = ("Z-value for slope of g1_image versus distance from readout register compared to expectation " +
                     "of zero.")

# Metadata about the test
CTI_GAL_TEST_ID = "T-SHE-000010-CTI-gal"
CTI_GAL_TEST_DESCRIPTION = "Linear dependence of galaxy ellipticity with read-out register distance (slope)."


class CtiGalTestCases(Enum):
    """ Enum of test cases for this test.
    """
    GLOBAL = "Global"
    SNR = "SNR"
    BG = "Background level"
    COLOUR = "Colour"
    SIZE = "Size"
    EPOCH = "Epoch"


CTI_GAL_TEST_CASE_GLOBAL_INFO = TestCaseInfo(test_case_id="T-SHE-000010-CTI-gal",
                                             description=("Linear dependence of " +
                                                          "residual galaxy ellipticity with read-out " +
                                                          "register distance (slope) unbinned."),
                                             bins_cline_arg=None,
                                             bins_config_key=None,
                                             name="global",
                                             comment=None,)
CTI_GAL_TEST_CASE_SNR_INFO = TestCaseInfo(test_case_id="TC-SHE-100028-CTI-gal-SNR",
                                          description=("Linear dependence of " +
                                                       "residual galaxy ellipticity with read-out register " +
                                                       "distance (slope) in bins of SNR of galaxies."),
                                          bins_cline_arg="snr_bin_limits",
                                          bins_config_key=AnalysisConfigKeys.CGV_SNR_BIN_LIMITS.value,
                                          name="snr",
                                          comment=None,)
CTI_GAL_TEST_CASE_BG_INFO = TestCaseInfo(test_case_id="TC-SHE-100029-CTI-gal-bg",
                                         description=("Linear dependence of residual galaxy ellipticity " +
                                                      "with read-out register distance (slope) in bins of " +
                                                      "sky background levels."),
                                         bins_cline_arg="bg_bin_limits",
                                         bins_config_key=AnalysisConfigKeys.CGV_BG_BIN_LIMITS.value,
                                         name="bg",
                                         comment=BACKGROUND_LEVEL_UNITS)
CTI_GAL_TEST_CASE_COLOUR_INFO = TestCaseInfo(test_case_id="TC-SHE-100030-CTI-gal-col",
                                             description=("Linear dependence of residual galaxy " +
                                                          "ellipticity with read-out register distance " +
                                                          "(slope) in bins of colour of galaxies."),
                                             bins_cline_arg="colour_bin_limits",
                                             bins_config_key=AnalysisConfigKeys.CGV_COLOUR_BIN_LIMITS.value,
                                             name="colour",
                                             comment=COLOUR_DEFINITION)
CTI_GAL_TEST_CASE_SIZE_INFO = TestCaseInfo(test_case_id="TC-SHE-100031-CTI-gal-size",
                                           description=("Linear dependence of residual galaxy ellipticity " +
                                                        "with read-out register distance (slope) in bins " +
                                                        "of size of galaxies."),
                                           bins_cline_arg="size_bin_limits",
                                           bins_config_key=AnalysisConfigKeys.CGV_SIZE_BIN_LIMITS.value,
                                           name="size",
                                           comment=SIZE_DEFINITION)
CTI_GAL_TEST_CASE_EPOCH_INFO = TestCaseInfo(test_case_id="TC-SHE-100032-CTI-gal-epoch",
                                            description=("Linear dependence of residual galaxy " +
                                                         "ellipticity with read-out register distance " +
                                                         "(slope) in bins of observation epoch"),
                                            bins_cline_arg=None,
                                            bins_config_key=None,
                                            name="epoch",
                                            comment=None)

# Create a dict of the test case info
D_CTI_GAL_TEST_CASE_INFO = {CtiGalTestCases.GLOBAL: CTI_GAL_TEST_CASE_GLOBAL_INFO,
                            CtiGalTestCases.SNR: CTI_GAL_TEST_CASE_SNR_INFO,
                            CtiGalTestCases.BG: CTI_GAL_TEST_CASE_BG_INFO,
                            CtiGalTestCases.COLOUR: CTI_GAL_TEST_CASE_COLOUR_INFO,
                            CtiGalTestCases.SIZE: CTI_GAL_TEST_CASE_SIZE_INFO,
                            CtiGalTestCases.EPOCH: CTI_GAL_TEST_CASE_EPOCH_INFO, }

CTI_GAL_TEST_CASES = D_CTI_GAL_TEST_CASE_INFO.keys()

NUM_CTI_GAL_TEST_CASES = len(CtiGalTestCases)

NUM_METHOD_CTI_GAL_TEST_CASES = NUM_SHEAR_ESTIMATION_METHODS * NUM_CTI_GAL_TEST_CASES
