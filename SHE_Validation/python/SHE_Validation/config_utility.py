"""
:file: python/SHE_Validation/config_utility.py

:date: 29 July 2021
:author: Bryan Gillis

Utility functions related to configuration
"""

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

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import ValidationConfigKeys
from .constants.default_config import FailSigmaScaling
from .constants.test_info import BinParameters, D_BIN_PARAMETER_META

logger = getLogger(__name__)

# Set up the common types and enum types for configs
COMMON_VAL_TYPES = {ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA: float,
                    ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA: float,
                    ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING: FailSigmaScaling}
for _bin_parameter in BinParameters:
    _bin_limits_key = D_BIN_PARAMETER_META[_bin_parameter].config_key
    COMMON_VAL_TYPES[_bin_limits_key] = np.ndarray
