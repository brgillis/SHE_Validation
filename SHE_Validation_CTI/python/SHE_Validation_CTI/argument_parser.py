""" @file argument_parser.py

    Created 28 Oct 2021

    Base class for an argument parser for SHE CTI Validation executables.
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

from SHE_Validation.argument_parser import ValidationArgumentParser


class CtiGalArgumentParser(ValidationArgumentParser):
    """ Argument parser specialized for SHE CTI-Gal Validation executables.
    """

    def __init__(self):
        super().__init__()

        # Input filename arguments

        self.add_calibrated_frame_arg()
        self.add_final_catalog_arg()
        self.add_measurements_arg()
        self.add_mdb_arg()

        # Output filename arguments

        self.add_obs_test_result_arg()
        self.add_exp_test_result_listfile_arg()

        # Optional arguments

        self.add_bin_parameter_args()


class CtiPsfArgumentParser(ValidationArgumentParser):
    """ Argument parser specialized for SHE CTI-PSF Validation executables.
    """

    def __init__(self):
        super().__init__()

        # Input filename arguments

        self.add_argument("--star_catalog_listfile", type = str,
                          help = "INPUT: .json listfile containing filenames of .xml data products for SHE star "
                                 "catalogs for each exposure.")

        self.add_mdb_arg()

        # Output filename arguments

        self.add_obs_test_result_arg()
        self.add_exp_test_result_listfile_arg()

        # Optional arguments

        self.add_bin_parameter_args()
