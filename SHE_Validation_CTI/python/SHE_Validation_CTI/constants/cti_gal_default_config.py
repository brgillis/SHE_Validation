""" @file cti_gal_test_info.py

    Created 15 Dec 2020

    Constants relating to CTI-Gal test and test case
"""

__updated__ = "2021-03-15"

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

from SHE_PPT.pipeline_utility import AnalysisConfigKeys
from SHE_PPT.utility import AllowedEnum

BACKGROUND_LEVEL_UNITS = "ADU/pixel"
COLOUR_DEFINITION = "2.5*log10(FLUX_VIS_APER/FLUX_NIR_STACK_APER)"
SIZE_DEFINITION = "Area of segmentation map (pixels)"


class FailSigmaScaling(AllowedEnum):
    """ Enum to list allowed command-line values to describe how to scale failure threshold. All values are
        case-insensitive

        none: Use failure thresholds without any modification
        bins: Scale failure thresholds based on the number of bins for each test case individually
        test_cases: Scale failure thresholds based on the number of test cases
        test_case_bins: Scale failure thresholds based on the total number of bins, across all test cases
    """
    NO_SCALE = "none"
    BIN_SCALE = "bins"
    TEST_CASE_SCALE = "test_cases"
    TEST_CASE_BINS_SCALE = "test_case_bins"


# Config keys and default values
CTI_GAL_DEFAULT_CONFIG = {AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value: 5.,
                          AnalysisConfigKeys.CGV_INTERCEPT_FAIL_SIGMA.value: 5.,
                          AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value: FailSigmaScaling.TEST_CASE_BINS_SCALE.value,
                          AnalysisConfigKeys.CGV_SNR_BIN_LIMITS.value: "0 5 10 30 100 1e99",
                          AnalysisConfigKeys.CGV_BG_BIN_LIMITS.value: "0 30 35 40 45 50 55 60 65 100 150 200 400 1e99",
                          AnalysisConfigKeys.CGV_COLOUR_BIN_LIMITS.value: "-1e99 -4 -3 -2 -1 0 1 2 3 4 1e99",
                          AnalysisConfigKeys.CGV_SIZE_BIN_LIMITS.value: "0 10 30 100 300 1000 1e99",
                          }

DEFAULT_BIN_LIMIT_MIN = -1e99
DEFAULT_BIN_LIMIT_MAX = 1e99
DEFAULT_BIN_LIMITS = (DEFAULT_BIN_LIMIT_MIN, DEFAULT_BIN_LIMIT_MAX)
FAILSAFE_BIN_LIMITS = f"{DEFAULT_BIN_LIMIT_MIN} {DEFAULT_BIN_LIMIT_MAX}"
