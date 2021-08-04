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
from typing import Iterable, List, Union

from SHE_PPT.constants.shear_estimation_methods import METHODS as SHEAR_ESTIMATION_METHODS
from SHE_PPT.utility import coerce_to_list

from SHE_Validation.constants.test_info import BinParameterMeta

from .constants.test_info import BinParameters, TestCaseInfo, D_BIN_PARAMETER_META


def add_bin_limits_cline_args(parser: argparse.ArgumentParser,
                              l_bin_parameters: Iterable[BinParameters] = BinParameters):
    """ Adds bin limits arguments to an argument parser.
    """

    for bin_parameter in l_bin_parameters:
        bin_parameter_meta: BinParameterMeta = D_BIN_PARAMETER_META[bin_parameter]
        parser.add_argument('--' + bin_parameter_meta.cline_arg, type=str, default=None,
                            help=bin_parameter_meta.help_text)


def make_test_case_info_for_bins(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                 l_bin_parameters: Iterable[BinParameters] = BinParameters) -> List[TestCaseInfo]:
    """ Takes as input a test case or list of test cases, then creates versions of it for each bin parameter in the provided
        list.
    """

    # Silently coerce test_case_info into a list
    l_test_case_info: List[TestCaseInfo] = coerce_to_list(test_case_info)

    l_bin_test_case_info: List[TestCaseInfo] = []

    for test_case_info in l_test_case_info:
        for bin_parameter in l_bin_parameters:

            # Copy the test case info and modify the bins attribute of it
            bin_test_case_info: TestCaseInfo = deepcopy(test_case_info)
            bin_test_case_info.bins = bin_parameter

            l_bin_test_case_info.append(bin_test_case_info)

    return l_bin_test_case_info


def make_test_case_info_for_methods(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                    l_methods: Iterable[str] = SHEAR_ESTIMATION_METHODS):
    """ Takes as input a test case or list of test cases, then creates versions of it for each shear estimation method
        in the provided list.
    """

    # Silently coerce test_case_info into a list
    l_test_case_info: List[TestCaseInfo] = coerce_to_list(test_case_info)

    l_method_test_case_info: List[TestCaseInfo] = []

    for test_case_info in l_test_case_info:
        for method in l_methods:

            # Copy the test case info and modify the bins attribute of it
            method_test_case_info: TestCaseInfo = deepcopy(test_case_info)
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


def find_test_case_info(l_test_case_info: List[TestCaseInfo],
                        methods: Union[None, str, List[str]] = None,
                        bin_parameters:  Union[None, BinParameters, List[BinParameters]] = None,
                        return_one=False) -> Union[List[TestCaseInfo], TestCaseInfo]:
    """ Finds all test_case_info in the provided list matching the method and bin_parameter provided, and returns as a
        list.

        If return_one is set to True, will check if the list contains only one element. If so, returns that element.
        If it contains more than one element, will raise a ValueError.
    """

    # Make sure methods and bin_parameters input are always lists if they aren't None
    l_methods: List[str] = coerce_to_list(methods, keep_none=True)
    l_bin_parameters: List[BinParameters] = coerce_to_list(bin_parameters, keep_none=True)

    # Init list which will store all matching test cases
    l_matching_test_case_info: List[TestCaseInfo] = []

    for test_case_info in l_test_case_info:
        # Check both methods and bin_parameters, and continue if we don't have a match
        if l_methods and not test_case_info.method in l_methods:
            continue
        if l_bin_parameters and not test_case_info.bins in l_bin_parameters:
            continue
        l_matching_test_case_info.append(test_case_info)

    # If we're not asked to return just one, we can return now
    if not return_one:
        return l_matching_test_case_info

    # Check we have just one matching test case, and raise a ValueError if not
    if len(l_matching_test_case_info) == 1:
        return l_matching_test_case_info[0]

    raise ValueError(f"More than one TestCaseInfo in l_test_case_info ({l_test_case_info}) matches the criteria:\n"
                     f"methods = {methods}\n"
                     f"bin_parameters = {bin_parameters}\n"
                     f"Matching TestCaseInfo are: {l_matching_test_case_info}")
