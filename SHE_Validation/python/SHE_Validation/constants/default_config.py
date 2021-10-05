""" @file default_config.py

    Created 15 July 2021

    Constants relating default configurations for validation tests
"""

__updated__ = "2021-08-05"

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

from enum import EnumMeta
from typing import Any, Dict, Tuple, Type, Union

import numpy as np

from SHE_PPT.constants.classes import AllowedEnum
from SHE_PPT.pipeline_utility import ConfigKeys, GlobalConfigKeys, ValidationConfigKeys
from SHE_Validation.constants.test_info import BinParameters, D_BIN_PARAMETER_META


class ExecutionMode(AllowedEnum):
    """ Execution mode options - whether an executable operates on individual observation or tile (local) or
        all that are available (global).
    """
    LOCAL = "local"
    GLOBAL = "global"


class FailSigmaScaling(AllowedEnum):
    """ Enum to list allowed command-line values to describe how to scale failure threshold. All values are
        case-insensitive

        none: Use failure thresholds without any modification
        bins: Scale failure thresholds based on the number of bins for each test case individually
        test_cases: Scale failure thresholds based on the number of test cases
        test_case_bins: Scale failure thresholds based on the total number of bins, across all test cases
    """
    NONE = "none"
    BINS = "bins"
    TEST_CASES = "test_cases"
    TEST_CASE_BINS = "test_case_bins"


# Config keys, default values, types, and associated cline-args

# Default values
D_VALIDATION_CONFIG_DEFAULTS: Dict[ConfigKeys, Any] = {
    ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA : 2.,
    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA  : 5.,
    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: FailSigmaScaling.TEST_CASE_BINS,
    ValidationConfigKeys.VAL_SNR_BIN_LIMITS    : "0 5 10 30 100 1e99",
    ValidationConfigKeys.VAL_BG_BIN_LIMITS     : "0 30 35 40 45 50 55 60 65 100 150 200 400 1e99",
    ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS : "-1e99 -4 -3 -2 -1 0 1 2 3 4 1e99",
    ValidationConfigKeys.VAL_SIZE_BIN_LIMITS   : "0 10 30 100 300 1000 1e99",
    GlobalConfigKeys.PIP_PROFILE               : "False",
    }

DEFAULT_BIN_LIMIT_MIN: float = -1e99
DEFAULT_BIN_LIMIT_MAX: float = 1e99
DEFAULT_BIN_LIMITS: Tuple[float, float] = (DEFAULT_BIN_LIMIT_MIN, DEFAULT_BIN_LIMIT_MAX)
DEFAULT_BIN_LIMITS_STR: str = f"{DEFAULT_BIN_LIMIT_MIN} {DEFAULT_BIN_LIMIT_MAX}"

# Types
D_VALIDATION_CONFIG_TYPES: Dict[ConfigKeys, Union[Type, EnumMeta]] = {
    ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA : float,
    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA  : float,
    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: FailSigmaScaling,
    ValidationConfigKeys.VAL_SNR_BIN_LIMITS    : np.ndarray,
    ValidationConfigKeys.VAL_BG_BIN_LIMITS     : np.ndarray,
    ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS : np.ndarray,
    ValidationConfigKeys.VAL_SIZE_BIN_LIMITS   : np.ndarray,
    GlobalConfigKeys.PIP_PROFILE               : bool,
    }

# Command-line arguments
D_VALIDATION_CONFIG_CLINE_ARGS: Dict[ConfigKeys, str] = {
    ValidationConfigKeys.VAL_SNR_BIN_LIMITS   : D_BIN_PARAMETER_META[BinParameters.SNR].cline_arg,
    ValidationConfigKeys.VAL_BG_BIN_LIMITS    : D_BIN_PARAMETER_META[BinParameters.BG].cline_arg,
    ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS: D_BIN_PARAMETER_META[BinParameters.COLOUR].cline_arg,
    ValidationConfigKeys.VAL_SIZE_BIN_LIMITS  : D_BIN_PARAMETER_META[BinParameters.SIZE].cline_arg,
    }
