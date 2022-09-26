"""
:file: python/SHE_Validation_DataQuality/constants/sed_exist_config.py

:date: 09/21/22
:author: Bryan Gillis

Constants relating to SED-Exist validation test configuration
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
from SHE_PPT.constants.config import AnalysisConfigKeys
from SHE_Validation.constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                                     D_VALIDATION_CONFIG_TYPES, )

# Create the default config dicts for this task by extending the tot default config dicts
D_SED_EXIST_CONFIG_DEFAULTS = {**D_VALIDATION_CONFIG_DEFAULTS,
                               AnalysisConfigKeys.PSF_NUM_STARS: 200}
D_SED_EXIST_CONFIG_TYPES = {**D_VALIDATION_CONFIG_TYPES,
                            AnalysisConfigKeys.PSF_NUM_STARS: int}
D_SED_EXIST_CONFIG_CLINE_ARGS = {**D_VALIDATION_CONFIG_CLINE_ARGS,
                                 AnalysisConfigKeys.PSF_NUM_STARS: None}
