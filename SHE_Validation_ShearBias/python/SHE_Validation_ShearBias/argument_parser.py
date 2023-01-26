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
from SHE_PPT.argument_parser import ClineArgType
from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_Validation.argument_parser import ValidationArgumentParser
from .constants.shear_bias_default_config import D_SHEAR_BIAS_CONFIG_CLINE_ARGS

CA_MAX_G_IN = D_SHEAR_BIAS_CONFIG_CLINE_ARGS[ValidationConfigKeys.SBV_MAX_G_IN]
CA_BOOTSTRAP_ERRORS = D_SHEAR_BIAS_CONFIG_CLINE_ARGS[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS]
CA_REQ_FITCLASS_ZERO = D_SHEAR_BIAS_CONFIG_CLINE_ARGS[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO]


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
        self.add_arg_with_type(f'--{CA_MAX_G_IN}', type=float, default=None, arg_type=ClineArgType.OPTION,
                               help='Maximum value of input shear to allow.')
        self.add_arg_with_type(f'--{CA_BOOTSTRAP_ERRORS}', type=bool, default=None, arg_type=ClineArgType.OPTION,
                               help='If set to True, will use bootstrap calculation for errors.')
        self.add_arg_with_type(f'--{CA_REQ_FITCLASS_ZERO}', type=bool, default=None, arg_type=ClineArgType.OPTION,
                               help='If set to true, will only include objects identified as galaxies ('
                                    'FITCLASS==0) in analysis.')
