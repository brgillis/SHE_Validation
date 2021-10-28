""" @file argument_parser.py

    Created 29 July 2021

    Base class for an argument parser for SHE Validation executables.
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

from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_Validation.argument_parser import ValidationArgumentParser
from .constants.shear_bias_default_config import D_SHEAR_BIAS_CONFIG_CLINE_ARGS


class ShearValidationArgumentParser(ValidationArgumentParser):
    """ Argument parser specialized for SHE Validation executables.
    """

    def __init__(self):
        super().__init__()

        # Input filenames
        self.add_bin_parameter_args()

        # Output filenames
        self.add_test_result_arg()

        # Options
        self.add_argument(f'--{D_SHEAR_BIAS_CONFIG_CLINE_ARGS[ValidationConfigKeys.SBV_MAX_G_IN]}',
                          type = float, default = None,
                          help = 'OPTION: Maximum value of input shear to allow.')
        self.add_argument(f'--{D_SHEAR_BIAS_CONFIG_CLINE_ARGS[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS]}',
                          type = bool, default = None,
                          help = 'OPTION: If set to True, will use bootstrap calculation for errors.')
        self.add_argument(f'--{D_SHEAR_BIAS_CONFIG_CLINE_ARGS[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO]}',
                          type = bool, default = None,
                          help = 'OPTION: If set to true, will only include objects identified as galaxies ('
                                 'FITCLASS==0) in analysis.')
