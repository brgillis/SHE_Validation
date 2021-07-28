""" @file shear_bias_test_info.py

    Created 15 July 2021

    Constants relating to CTI-Gal test and test case
"""

__updated__ = "2021-07-28"

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

from SHE_PPT.pipeline_utility import ValidationConfigKeys
from SHE_Validation.constants.default_config import VALIDATION_DEFAULT_CONFIG

PROFILING_FILENAME = "validate_shear_bias.prof"

# Config keys and default values
SHEAR_BIAS_DEFAULT_CONFIG = {ValidationConfigKeys.SBV_MAX_G_IN.value: 0.99,
                             ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS.value: True,
                             ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO.value: False,
                             **VALIDATION_DEFAULT_CONFIG}
