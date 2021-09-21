""" @file shear_bias_test_info.py

    Created 15 July 2021

    Constants relating to CTI-Gal test and test case
"""

__updated__ = "2021-08-03"

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
from SHE_Validation.constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                                     D_VALIDATION_CONFIG_TYPES, )

LOCAL_PROFILING_FILENAME = "validate_local_shear_bias.prof"
GLOBAL_PROFILING_FILENAME = "validate_global_shear_bias.prof"

# Create the default config dicts for this task by extending the global default config dicts
D_SHEAR_BIAS_CONFIG_DEFAULTS = {ValidationConfigKeys.SBV_MAX_G_IN             : 0.99,
                                ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS     : True,
                                ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO: False,
                                **D_VALIDATION_CONFIG_DEFAULTS}
D_SHEAR_BIAS_CONFIG_TYPES = {ValidationConfigKeys.SBV_MAX_G_IN             : float,
                             ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS     : bool,
                             ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO: bool,
                             **D_VALIDATION_CONFIG_TYPES}
D_SHEAR_BIAS_CONFIG_CLINE_ARGS = {ValidationConfigKeys.SBV_MAX_G_IN             : "max_g_in",
                                  ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS     : "bootstrap_errors",
                                  ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO: "require_fitclass_zero",
                                  **D_VALIDATION_CONFIG_CLINE_ARGS}
