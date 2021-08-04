""" @file test_info_utility.py

    Created 27 July 2021

    Utility functions related to requirement, test, and test case info.
"""

__updated__ = "2021-08-04"

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

import argparse
from copy import deepcopy
from typing import Iterable, Union, List

from SHE_PPT.constants.shear_estimation_methods import METHODS as SHEAR_ESTIMATION_METHODS

from .constants.test_info import BinParameters, TestCaseInfo, D_BIN_PARAMETER_META


def add_bin_limits_cline_args(parser: argparse.ArgumentParser,
                              l_bin_parameters: Iterable[BinParameters] = BinParameters):
    """ Adds bin limits arguments to an argument parser.
    """

    for bin_parameter in l_bin_parameters:
        bin_parameter_meta = D_BIN_PARAMETER_META[bin_parameter]
        parser.add_argument('--' + bin_parameter_meta.cline_arg, type=str, default=None,
                            help=bin_parameter_meta.help_text)


def make_test_case_info_for_bins(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                 l_bin_parameters: Iterable[BinParameters] = BinParameters):
    """ Takes as input a test case or list of test cases, then creates versions of it for each bin parameter in the provided
        list.
    """

    # Silently coerce test_case_info into a list
    if isinstance(test_case_info, TestCaseInfo):
        l_test_case_info = [test_case_info]
    else:
        l_test_case_info = test_case_info

    l_bin_test_case_info = {}

    for test_case_info in l_test_case_info:
        for bin_parameter in l_bin_parameters:

            # Copy the test case info and modify the bins attribute of it
            bin_test_case_info = deepcopy(test_case_info)
            bin_test_case_info.bins = bin_parameter

            l_bin_test_case_info.append(bin_test_case_info)

    return l_bin_test_case_info


def make_test_case_info_for_methods(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                    l_methods: Iterable[str] = SHEAR_ESTIMATION_METHODS):
    """ Takes as input a test case or list of test cases, then creates versions of it for each shear estimation method
        in the provided list.
    """

    # Silently coerce test_case_info into a list
    if isinstance(test_case_info, TestCaseInfo):
        l_test_case_info = [test_case_info]
    else:
        l_test_case_info = test_case_info

    l_method_test_case_info = {}

    for test_case_info in l_test_case_info:
        for method in l_methods:

            # Copy the test case info and modify the bins attribute of it
            method_test_case_info = deepcopy(test_case_info)
            method_test_case_info.method = method

            l_method_test_case_info.append(method_test_case_info)

    return l_method_test_case_info


def make_test_case_info_for_bins_and_methods(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                             l_bin_parameters: Iterable[BinParameters] = BinParameters,
                                             l_methods: Iterable[str] = SHEAR_ESTIMATION_METHODS):
    """ Takes as input a test case or list of test cases, then creates versions of it for each bin parameter in the
        provided list, for each shear estimation method in the provided list.
    """

    return make_test_case_info_for_methods(make_test_case_info_for_bins(test_case_info, l_bin_parameters), l_methods)
