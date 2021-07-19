""" @file shear_bias_test_info.py

    Created 15 July 2021

    Constants relating to CTI-Gal test and test case
"""

__updated__ = "2021-07-19"

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

from SHE_PPT.pipeline_utility import AnalysisValidationConfigKeys
from SHE_Validation.constants.default_config import FailSigmaScaling

PROFILING_FILENAME = "validate_shear_bias.prof"

# Config keys and default values
SHEAR_BIAS_DEFAULT_CONFIG = {AnalysisValidationConfigKeys.SBV_M_FAIL_SIGMA.value: 5.,
                             AnalysisValidationConfigKeys.SBV_C_FAIL_SIGMA.value: 5.,
                             AnalysisValidationConfigKeys.SBV_FAIL_SIGMA_SCALING.value: FailSigmaScaling.TEST_CASE_SCALE.value,
                             AnalysisValidationConfigKeys.PIP_PROFILE.value: "False",
                             }

# Execution mode options
LOCAL_MODE = "local"
GLOBAL_MODE = "global"
