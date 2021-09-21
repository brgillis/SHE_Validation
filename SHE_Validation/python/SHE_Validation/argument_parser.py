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

from SHE_PPT.argument_parser import SheArgumentParser
from .test_info_utility import add_bin_limits_cline_args


class ValidationArgumentParser(SheArgumentParser):
    """ Argument parser specialized for SHE Validation executables.
    """

    def __init__(self,
                 bin_parameter_args: bool = True):
        super().__init__()

        if bin_parameter_args:
            add_bin_limits_cline_args(self)
