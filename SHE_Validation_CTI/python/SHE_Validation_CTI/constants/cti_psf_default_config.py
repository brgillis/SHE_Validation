""" @file cti_psf_default_config.py

    Created 28 Octo 2021

    Constants relating to CTI-PSF configuration
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

from SHE_Validation.constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                                     D_VALIDATION_CONFIG_TYPES, )

# Create the default config dicts for this task by extending the global default config dicts
D_CTI_PSF_CONFIG_DEFAULTS = {**D_VALIDATION_CONFIG_DEFAULTS}
D_CTI_PSF_CONFIG_TYPES = {**D_VALIDATION_CONFIG_TYPES}
D_CTI_PSF_CONFIG_CLINE_ARGS = {**D_VALIDATION_CONFIG_CLINE_ARGS}