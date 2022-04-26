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
from SHE_PPT.constants.config import D_GLOBAL_CONFIG_CLINE_ARGS, D_GLOBAL_CONFIG_DEFAULTS, D_GLOBAL_CONFIG_TYPES
from SHE_PPT.pipeline_utility import ConfigKeys, ValidationConfigKeys
from ..binning.utility import DEFAULT_AUTO_BIN_LIMITS
from ..constants.test_info import BinParameters, D_BIN_PARAMETER_META


class ExecutionMode(AllowedEnum):
    """ Execution mode options - whether an executable operates on individual observation or tile (local) or
        all that are available (tot).
    """
    LOCAL = "local"
    TOT = "tot"


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

DEFAULT_P_FAIL = 0.05
DEFAULT_GLOBAL_FAIL_SIGMA = 2.
DEFAULT_LOCAL_FAIL_SIGMA = 5.
DEFAULT_FAIL_SIGMA_SCALING = FailSigmaScaling.TEST_CASE_BINS

DEFAULT_BIN_LIMIT_MIN: float = -1e99
DEFAULT_BIN_LIMIT_MAX: float = 1e99
TOT_BIN_LIMITS: Tuple[float, float] = (DEFAULT_BIN_LIMIT_MIN, DEFAULT_BIN_LIMIT_MAX)
TOT_BIN_LIMITS_STR: str = f"{DEFAULT_BIN_LIMIT_MIN} {DEFAULT_BIN_LIMIT_MAX}"

D_VALIDATION_CONFIG_DEFAULTS: Dict[ConfigKeys, Any] = {
    **D_GLOBAL_CONFIG_DEFAULTS,
    ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA : DEFAULT_GLOBAL_FAIL_SIGMA,
    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA  : DEFAULT_LOCAL_FAIL_SIGMA,
    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: DEFAULT_FAIL_SIGMA_SCALING,
    ValidationConfigKeys.VAL_SNR_BIN_LIMITS    : DEFAULT_AUTO_BIN_LIMITS,
    ValidationConfigKeys.VAL_BG_BIN_LIMITS     : DEFAULT_AUTO_BIN_LIMITS,
    ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS : DEFAULT_AUTO_BIN_LIMITS,
    ValidationConfigKeys.VAL_SIZE_BIN_LIMITS   : DEFAULT_AUTO_BIN_LIMITS,
    ValidationConfigKeys.VAL_EPOCH_BIN_LIMITS  : DEFAULT_AUTO_BIN_LIMITS,
    }

# Types
D_VALIDATION_CONFIG_TYPES: Dict[ConfigKeys, Union[Type, EnumMeta]] = {
    **D_GLOBAL_CONFIG_TYPES,
    ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA : float,
    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA  : float,
    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: FailSigmaScaling,
    ValidationConfigKeys.VAL_SNR_BIN_LIMITS    : np.ndarray,
    ValidationConfigKeys.VAL_BG_BIN_LIMITS     : np.ndarray,
    ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS : np.ndarray,
    ValidationConfigKeys.VAL_SIZE_BIN_LIMITS   : np.ndarray,
    ValidationConfigKeys.VAL_EPOCH_BIN_LIMITS  : np.ndarray,
    }

# Command-line arguments

CA_P_FAIL = "p_fail"
CA_GLOBAL_FAIL_SIGMA = "global_fail_sigma"
CA_LOCAL_FAIL_SIGMA = "local_fail_sigma"
CA_FAIL_SIGMA_SCALING = "fail_sigma_scaling"

D_VALIDATION_CONFIG_CLINE_ARGS: Dict[ConfigKeys, str] = {
    **D_GLOBAL_CONFIG_CLINE_ARGS,
    ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA : CA_GLOBAL_FAIL_SIGMA,
    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA  : CA_LOCAL_FAIL_SIGMA,
    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: CA_FAIL_SIGMA_SCALING,
    ValidationConfigKeys.VAL_SNR_BIN_LIMITS    : D_BIN_PARAMETER_META[BinParameters.SNR].cline_arg,
    ValidationConfigKeys.VAL_BG_BIN_LIMITS     : D_BIN_PARAMETER_META[BinParameters.BG].cline_arg,
    ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS : D_BIN_PARAMETER_META[BinParameters.COLOUR].cline_arg,
    ValidationConfigKeys.VAL_SIZE_BIN_LIMITS   : D_BIN_PARAMETER_META[BinParameters.SIZE].cline_arg,
    ValidationConfigKeys.VAL_EPOCH_BIN_LIMITS  : D_BIN_PARAMETER_META[BinParameters.EPOCH].cline_arg,
    }
