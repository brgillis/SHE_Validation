""" @file config_utility.py

    Created 29 July 2021

    Utility functions related to configuration.
"""

__updated__ = "2021-08-27"

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

from typing import Dict, Any, Type

from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import ValidationConfigKeys, convert_config_types

from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
import numpy as np

from .constants.default_config import FailSigmaScaling
from .constants.test_info import BinParameters, D_BIN_PARAMETER_META

logger = getLogger(__name__)

# Set up the common types and enum types for configs
COMMON_VAL_TYPES = {ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA: float,
                    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA: float,
                    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: FailSigmaScaling}
for bin_parameter in BinParameters:
    bin_limits_key = D_BIN_PARAMETER_META[bin_parameter].config_key
    COMMON_VAL_TYPES[bin_limits_key] = np.ndarray


def get_d_bin_limits(pipeline_config: Dict[str, Any]) -> Dict[BinParameters, np.ndarray]:
    """ Convert the bin limits in a pipeline_config (after type conversion) into a dict of arrays.
    """

    d_bin_limits = {}
    for bin_parameter in BinParameters:
        bin_limits_key = D_BIN_PARAMETER_META[bin_parameter].config_key
        if bin_limits_key is None or bin_limits_key not in pipeline_config:
            # This signifies not relevant to this test or not yet set up. Fill in with the default limits just in case
            d_bin_limits[bin_parameter] = DEFAULT_BIN_LIMITS
            continue
        d_bin_limits[bin_parameter] = pipeline_config[bin_limits_key]

    return d_bin_limits


def convert_val_config_types(pipeline_config: Dict[str, str],
                             d_types: Dict[str, Type],) -> Dict[str, Any]:
    """ Converts values in the pipeline config to the proper types. Common values for the validation pipeline
        don't need to be supplied.
    """

    # Add common types and enum_types to the dicts
    d_types = {**COMMON_VAL_TYPES, **d_types}

    return convert_config_types(pipeline_config=pipeline_config,
                                d_types=d_types,)
