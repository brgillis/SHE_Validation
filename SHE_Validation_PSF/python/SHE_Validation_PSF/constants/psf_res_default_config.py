""" @file psf_res_default_config.py

    Created 08 March 2022 by Bryan Gillis

    Constants relating to PSF-Res configuration
"""

__updated__ = "2022-04-08"

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

from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_Validation.constants.default_config import (CA_P_FAIL, D_VALIDATION_CONFIG_CLINE_ARGS,
                                                     D_VALIDATION_CONFIG_DEFAULTS,
                                                     D_VALIDATION_CONFIG_TYPES, )

DEFAULT_P_FAIL = 0.05

# Create the default config dicts for this task by extending the tot default config dicts
D_PSF_RES_CONFIG_DEFAULTS = {**D_VALIDATION_CONFIG_DEFAULTS,
                             ValidationConfigKeys.PRSP_P_FAIL        : DEFAULT_P_FAIL,
                             ValidationConfigKeys.PRSP_SNR_BIN_LIMITS: D_VALIDATION_CONFIG_DEFAULTS[
                                 ValidationConfigKeys.VAL_SNR_BIN_LIMITS]}
D_PSF_RES_CONFIG_TYPES = {**D_VALIDATION_CONFIG_TYPES,
                          ValidationConfigKeys.PRSP_P_FAIL        : float,
                          ValidationConfigKeys.PRSP_SNR_BIN_LIMITS: D_VALIDATION_CONFIG_TYPES[
                              ValidationConfigKeys.VAL_SNR_BIN_LIMITS]}
D_PSF_RES_CONFIG_CLINE_ARGS = {**D_VALIDATION_CONFIG_CLINE_ARGS,
                               ValidationConfigKeys.PRSP_P_FAIL        : CA_P_FAIL,
                               ValidationConfigKeys.PRSP_SNR_BIN_LIMITS: D_VALIDATION_CONFIG_CLINE_ARGS[
                                   ValidationConfigKeys.VAL_SNR_BIN_LIMITS]}
