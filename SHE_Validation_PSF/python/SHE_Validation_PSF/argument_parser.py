""" @file argument_parser.py

    Created 08 March 2022 by Bryan Gillis

    Classes for argument parsers for SHE PSF Validation executables.
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

from SHE_Validation.argument_parser import ValidationArgumentParser
from SHE_Validation_PSF.constants.psf_res_test_info import L_PSF_RES_BIN_PARAMETERS


class PsfResArgumentParser(ValidationArgumentParser):
    """ Argument parser specialized for SHE CTI-Gal Validation executables.
    """

    def __init__(self):
        super().__init__()

        # Input filename arguments

        self.add_star_catalog_arg()

        # Output filename arguments

        self.add_test_result_arg()

        # Optional arguments

        self.add_bin_parameter_args(l_bin_parameters = L_PSF_RES_BIN_PARAMETERS)
