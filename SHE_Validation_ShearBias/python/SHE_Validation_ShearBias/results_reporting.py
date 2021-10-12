""" @file results_reporting.py

    Created 15 July 2021

    Utility functions for Shear Bias validation, for reporting results.
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

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union

import numpy as np

from SHE_PPT.constants.config import ConfigKeys
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements
from SHE_PPT.utility import is_inf_or_nan, is_zero
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS, ExecutionMode
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.results_writer import (AnalysisWriter, FailSigmaCalculator, MSG_NO_DATA, RESULT_PASS,
                                           RequirementWriter, SupplementaryInfo, TestCaseWriter,
                                           ValidationResultsWriter, WARNING_MULTIPLE, check_test_pass,
                                           check_test_pass_if_data, get_result_string, )
from SHE_Validation_ShearBias.constants.shear_bias_test_info import get_prop_from_id
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
from .constants.shear_bias_test_info import (D_L_SHEAR_BIAS_REQUIREMENT_INFO, L_SHEAR_BIAS_TEST_CASE_INFO,
                                             ShearBiasTestCases, )

logger = getLogger(__name__)

# Define constants for various messages

KEY_G1_INFO = "G1_INFO"
KEY_G2_INFO = "G2_INFO"

DESC_INFO_BASE = "Information about the test on REPLACEME_PROP bias in component REPLACEME_COMPONENT."

D_DESC_INFO = {}
for _prop, _name in ("m", "multiplicative"), ("c", "additive"):
    for _comp in (1, 2):
        D_DESC_INFO[f"{_prop}{_comp}"] = DESC_INFO_BASE.replace(
            "REPLACEME_PROP", _name).replace("REPLACEME_COMPONENT", f"{_comp}")

MSG_NAN_VAL = "Test failed due to NaN regression results."
MSG_ZERO_ERR = "Test failed due to zero error."

SHEAR_BIAS_DIRECTORY_FILENAME = "SheShearBiasResultsDirectory.txt"
SHEAR_BIAS_DIRECTORY_HEADER = "### OU-SHE Shear Bias Analysis Results File Directory ###"

REPORT_DIGITS = 8

# Type definitions for types used here
TK = TypeVar('TK')
TV = TypeVar('TV')
TIn = TypeVar('TIn')
TOut = TypeVar('TOut')
Number = TypeVar('Number', float, int)
ComponentDict = Dict[int, Number]


def get_l_of_component(l_d_x: Sequence[Dict[TK, TV]], i: TK) -> List[TV]:
    l_xi: List[TV] = [d_x[i] for d_x in l_d_x]
    return l_xi


def get_t_l_of_components_1_2(l_d_x: Sequence[Dict[int, TV]]) -> Tuple[List[TV], List[TV]]:
    l_x1: List[TV] = get_l_of_component(l_d_x, 1)
    l_x2: List[TV] = get_l_of_component(l_d_x, 2)
    return l_x1, l_x2


def map_for_1_2(f: Callable[[TIn], TOut], *l_l_d_x: Sequence[Dict[int, TIn]]) -> List[Dict[int, TOut]]:
    """ Maps a function to lists of components 1 and 2.
    """

    l_l_x1: List[Optional[Sequence[TIn]]] = [None] * len(l_l_d_x)
    l_l_x2: List[Optional[Sequence[TIn]]] = [None] * len(l_l_d_x)
    for i, l_d_x in enumerate(l_l_d_x):
        l_l_x1[i], l_l_x2[i] = get_t_l_of_components_1_2(l_d_x)

    l_y1, l_y2 = list(map(f, *l_l_x1)), list(map(f, *l_l_x2))
    l_d_y = [{1: y1, 2: y2} for y1, y2 in zip(l_y1, l_y2)]

    return l_d_y


# Utility function to simplify tests on values that have components 1 and 2
def f_for_1_or_2(f: Callable[[Number], bool], d_x: ComponentDict):
    return f(d_x[1]) or f(d_x[2])


# Utility function to simplify tests on values that have components 1 and 2
def f_for_1_and_2(f: Callable[[Number], bool], d_x: ComponentDict):
    return f(d_x[1]) and f(d_x[2])


# Utility function to simplify tests on values that have components 1 and 2
def l_f_for_1_or_2(f: Callable[[Number], bool], l_d_x: Sequence[ComponentDict]) -> np.ndarray:
    l_x1, l_x2 = get_t_l_of_components_1_2(l_d_x)
    l_b1, l_b2 = list(map(f, l_x1)), list(map(f, l_x2))
    return np.array(np.logical_or(l_b1, l_b2))


# Utility function to simplify tests on values that have components 1 and 2
def l_f_for_1_and_2(f: Callable[[Number], bool], l_d_x: Sequence[ComponentDict]) -> np.ndarray:
    l_x1, l_x2 = get_t_l_of_components_1_2(l_d_x)
    l_b1, l_b2 = list(map(f, l_x1)), list(map(f, l_x2))
    return np.array(np.logical_and(l_b1, l_b2))


class ShearBiasRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    # Attributes set and used while writing
    _prop: Optional[ShearBiasTestCases] = None

    l_d_val: Optional[Sequence[Dict[int, float]]] = None
    l_d_val_err: Optional[Sequence[Dict[int, float]]] = None
    l_d_val_target: Optional[Sequence[Dict[int, float]]] = None
    l_d_val_z: Optional[Sequence[Dict[int, float]]] = None
    l_d_fail_sigma: Optional[List[Dict[int, float]]] = None

    fail_sigma: Optional[float] = None

    method: ShearEstimationMethods

    bin_parameter: BinParameters
    l_bin_limits: Sequence[float]
    num_bins: int

    # Which component(s) have at least some good data / pass / result?
    d_good_data: Optional[Dict[int, bool]] = None
    d_test_pass: Optional[Dict[int, bool]] = None
    d_result: Optional[Dict[int, str]] = None

    # Which bin(s) have at least some good data / pass / result?
    l_good_data: Optional[Sequence[bool]] = None
    l_test_pass: Optional[Sequence[bool]] = None
    l_result: Optional[Sequence[str]] = None

    # Which bin(s) for which component(s) have good data / pass / result?
    l_d_good_data: Optional[Sequence[Dict[int, bool]]] = None
    l_d_test_pass: Optional[Sequence[Dict[int, bool]]] = None
    l_d_result: Optional[Sequence[Dict[int, str]]] = None

    # Is there any good data?
    good_data: Optional[bool] = None

    def _get_supplementary_info(self,
                                extra_g1_message: str = "",
                                extra_g2_message: str = "", ) -> Sequence[SupplementaryInfo]:

        # Check the extra messages and make sure they end in a linebreak
        if extra_g1_message != "" and extra_g1_message[-1:] != "\n":
            extra_g1_message = extra_g1_message + "\n"
        if extra_g2_message != "" and extra_g2_message[-1:] != "\n":
            extra_g2_message = extra_g2_message + "\n"

        method_bin_message: str = (f"Test results for method {self.method.value}, with {self.bin_parameter.value} "
                                   f"bins.\n")

        # Set up result messages for each component
        d_messages: Dict[int, str] = {1: method_bin_message + extra_g1_message + "\n",
                                      2: method_bin_message + extra_g2_message + "\n"}

        # Report results for each bin of each component

        for bin_index in range(self.num_bins):

            d_val = self.l_d_val[bin_index]
            d_val_err = self.l_d_val_err[bin_index]
            d_val_z = self.l_d_val_z[bin_index]
            d_result = self.l_d_result[bin_index]

            bin_min: float = 0.
            bin_max: float = 0.
            if self.l_bin_limits is not None:
                bin_min = self.l_bin_limits[bin_index]
                bin_max = self.l_bin_limits[bin_index + 1]

            for component_index in (1, 2):

                val = d_val[component_index]
                val_err = d_val_err[component_index]
                val_z = d_val_z[component_index]
                result = d_result[component_index]

                if self.l_bin_limits is not None:
                    d_messages[component_index] += (f"Results for bin {bin_index}, for values from {bin_min} to"
                                                    f" {bin_max}:")

                d_messages[component_index] += (
                        f"{self.prop}{component_index} = {val:.{REPORT_DIGITS}f}\n" +
                        f"{self.prop}{component_index}_err = {val_err:.{REPORT_DIGITS}f}\n" +
                        f"{self.prop}{component_index}_z = {val_z:.{REPORT_DIGITS}f}\n" +
                        f"Maximum allowed {self.prop}_z = {self.fail_sigma:.{REPORT_DIGITS}f}\n" +
                        f"Result: {result}\n\n")

        l_supplementary_info = (SupplementaryInfo(key = KEY_G1_INFO,
                                                  description = D_DESC_INFO[f"{self.prop}1"],
                                                  message = d_messages[1]),
                                SupplementaryInfo(key = KEY_G2_INFO,
                                                  description = D_DESC_INFO[f"{self.prop}2"],
                                                  message = d_messages[2]))

        return l_supplementary_info

    def report_bad_shear_bias_data(self):

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_supplementary_info(extra_g1_message = MSG_NAN_VAL,
                                                            extra_g2_message = MSG_NAN_VAL, )
        super().report_bad_data(l_supplementary_info)

    def report_zero_err(self):

        # Report -2 as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = -2.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details
        self.add_supplementary_info(self._get_supplementary_info(extra_g1_message = MSG_ZERO_ERR,
                                                                 extra_g2_message = MSG_ZERO_ERR, ))

    def report_good_shear_bias_data(self,
                                    measured_value: float):

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info: Sequence[SupplementaryInfo] = self._get_supplementary_info()
        super().report_good_data(measured_value = measured_value,
                                 warning = False,
                                 l_supplementary_info = l_supplementary_info)

    def _calc_test_results(self):
        """ Calculate the test results
        """

        # Map the test check function to get the test pass results
        self.l_d_test_pass = map_for_1_2(check_test_pass, self.l_d_val, self.l_d_val_err, self.l_d_val_z,
                                         self.l_d_fail_sigma)
        l_d_test_pass_if_data = map_for_1_2(check_test_pass_if_data, self.l_d_val, self.l_d_val_err, self.l_d_val_z,
                                            self.l_d_fail_sigma, self.l_d_good_data)
        self.d_test_pass = {1: np.all(get_l_of_component(l_d_test_pass_if_data, 1)),
                            2: np.all(get_l_of_component(l_d_test_pass_if_data, 2))}
        self.l_test_pass = list(map((lambda d_x: d_x[1] and d_x[2]), l_d_test_pass_if_data))
        self.test_pass = self.d_test_pass[1] and self.d_test_pass[2]

        # Map the get_result_string function to get result strings
        self.l_d_result = map_for_1_2(get_result_string, self.l_d_test_pass)
        self.d_result = {1: get_result_string(self.d_test_pass[1]),
                         2: get_result_string(self.d_test_pass[2]), }
        self.l_result = list(map(get_result_string, self.l_test_pass))
        self.result = get_result_string(self.test_pass)

    def write(self,
              report_method: Callable[[Any], None] = None,
              have_data: bool = False,
              prop: Optional[ShearBiasTestCases] = None,
              l_d_val: Optional[List[Dict[int, float]]] = None,
              l_d_val_err: Optional[List[Dict[int, float]]] = None,
              l_d_val_target: Optional[List[Dict[int, float]]] = None,
              l_d_val_z: Optional[List[Dict[int, float]]] = None,
              fail_sigma: Optional[float] = None,
              method: Optional[ShearEstimationMethods] = None,
              bin_parameter: Optional[BinParameters] = None,
              l_bin_limits: Optional[Sequence[float]] = None,
              report_kwargs: Optional[Dict[str, Any]] = None) -> str:

        # Set attributes from input kwargs
        self.prop = prop
        self.l_d_val = l_d_val
        self.l_d_val_err = l_d_val_err
        self.l_d_val_target = l_d_val_target
        self.l_d_val_z = l_d_val_z
        self.fail_sigma = fail_sigma
        self.method = method
        self.bin_parameter = bin_parameter
        self.l_bin_limits = l_bin_limits
        if self.l_bin_limits is not None:
            self.num_bins = len(self.l_bin_limits) - 1
            if not self.num_bins >= 1:
                raise ValueError(f"Too few bins in bin limits: {self.l_bin_limits}.")
        else:
            self.num_bins = 1
            self.l_bin_limits = DEFAULT_BIN_LIMITS

        # Check the number of bins is right for all input data, if it's not None
        def none_or_match_len(l_x: Optional[List[Any]]):
            if l_x is None:
                return True
            return self.num_bins == len(l_x)

        if not (none_or_match_len(self.l_d_val) and none_or_match_len(self.l_d_val_err) and
                none_or_match_len(self.l_d_val_target) and none_or_match_len(self.l_d_val_z)):
            raise ValueError(f"Inconsistent array lengths in Shear Bias test results writing.")

        # Fill out the fail sigma list of dicts, to help with mapping function calls
        self.l_d_fail_sigma = [{1: fail_sigma, 2: fail_sigma}] * self.num_bins

        # If report method is supplied, go with that rather than figuring it out
        if report_method:
            return super().write(report_method = report_method,
                                 report_kwargs = report_kwargs, )

        # Default to reporting good data
        if report_method is None:
            report_method = self.report_good_shear_bias_data

        # Default to empty dict for report_kwargs
        if report_kwargs is None:
            report_kwargs = {}

        # If we don't have data, report with the provided method and return
        if not have_data:
            report_method(**report_kwargs)
            return RESULT_PASS

        # Check for data quality issues and report as proper if found

        # Check for data quality issues in each bin, and each bin for each component separately
        l_d_zero_err: List[Dict[int, bool]] = map_for_1_2(is_zero, self.l_d_val_err)
        l_zero_err: np.ndarray = l_f_for_1_or_2(is_zero, self.l_d_val_err)

        l_d_bad_val: List[Dict[int, bool]] = map_for_1_2(is_inf_or_nan, self.l_d_val)
        l_bad_val: np.ndarray = l_f_for_1_or_2(is_inf_or_nan, self.l_d_val)

        l_d_bad_val_err: List[Dict[int, bool]] = map_for_1_2(is_inf_or_nan, self.l_d_val_err)
        l_bad_val_err: np.ndarray = l_f_for_1_or_2(is_inf_or_nan, self.l_d_val_err)

        def logical_not_a_b_or_c(a, b, c):
            return np.logical_not(np.logical_or(a, np.logical_or(b, c)))

        # Mark which bins/components have good data
        self.l_good_data = logical_not_a_b_or_c(l_zero_err, l_bad_val, l_bad_val_err)
        self.l_d_good_data = map_for_1_2(logical_not_a_b_or_c, l_d_zero_err, l_d_bad_val, l_d_bad_val_err)
        self.d_good_data = {1: np.any(get_l_of_component(self.l_d_good_data, 1)),
                            2: np.any(get_l_of_component(self.l_d_good_data, 2))}
        self.good_data = np.any(self.l_good_data)

        # Calculate test results for both components
        self._calc_test_results()

        # Report the result based on whether or not both components passed wherever there's good data
        self.requirement_object.ValidationResult = self.result

        parameter: str = self.requirement_info.parameter

        self.requirement_object.MeasuredValue[0].Parameter = parameter

        # Choose report method depending on data quality issues

        # Check if all bins have zero error
        if np.all(l_zero_err):
            report_method = self.report_zero_err
            extra_report_kwargs = {}

        # Check there isn't any good data
        elif not np.any(self.good_data):
            report_method = self.report_bad_shear_bias_data
            extra_report_kwargs = {}

        # Otherwise, we have at least one bin with good data
        else:
            report_method = self.report_good_shear_bias_data

            # Report the maximum z across both components as the measured value for this test

            l_val_z1: List[float] = get_l_of_component(l_d_val_z, 1)
            l_val_z2: List[float] = get_l_of_component(l_d_val_z, 2)

            extra_report_kwargs = {"measured_value": np.nanmax((*l_val_z1, *l_val_z2))}

        return super().write(result = self.result,
                             report_method = report_method,
                             report_kwargs = {**report_kwargs, **extra_report_kwargs}, )


class ShearBiasAnalysisWriter(AnalysisWriter):
    """ Subclass of AnalysisWriter, to handle some changes specific for this test.
    """

    method: ShearEstimationMethods

    def __init__(self,
                 *args, **kwargs):
        super().__init__(product_type = "SHEAR-BIAS-ANALYSIS-FILES",
                         *args, **kwargs)

        # Get the shear estimation method from the parent's test case info
        self.method = self.parent_test_case_writer.test_case_info.method

    def _get_filename_tag(self):
        """ Overriding method to get a tag to add to figure/textfile filenames with method name.
        """
        return self.method.value

    def _generate_directory_filename(self):
        """ Overriding method to generate a filename for a directory file.
        """
        self.directory_filename = SHEAR_BIAS_DIRECTORY_FILENAME

    def _get_directory_header(self):
        """ Overriding method to get the desired header for a directory file.
        """
        return SHEAR_BIAS_DIRECTORY_HEADER


class ShearBiasTestCaseWriter(TestCaseWriter):
    # Class members

    # Types of child objects, overriding those in base class
    requirement_writer_type: Type = ShearBiasRequirementWriter
    analysis_writer_type: Type = ShearBiasAnalysisWriter


class ShearBiasValidationResultsWriter(ValidationResultsWriter):
    # Types of child classes
    test_case_writer_type = ShearBiasTestCaseWriter

    def __init__(self, test_object: dpdSheValidationTestResults, workdir: str,
                 d_l_d_bias_measurements: Dict[str, List[Dict[int, BiasMeasurements]]],
                 d_l_bin_limits: Dict[BinParameters, np.ndarray],
                 fail_sigma_calculator: FailSigmaCalculator, method_data_exists: bool = True,
                 mode: ExecutionMode = ExecutionMode, *args, **kwargs):

        super().__init__(test_object = test_object,
                         workdir = workdir,
                         l_test_case_info = L_SHEAR_BIAS_TEST_CASE_INFO,
                         dl_l_requirement_info = D_L_SHEAR_BIAS_REQUIREMENT_INFO,
                         *args, **kwargs)

        self.d_l_d_bias_measurements = d_l_d_bias_measurements
        self.d_l_bin_limits = d_l_bin_limits
        self.fail_sigma_calculator = fail_sigma_calculator
        self.method_data_exists = method_data_exists
        self.mode = mode

    def write_test_case_objects(self):
        """ Writes all data for each requirement subobject, modifying self._test_object.
        """
        # The results of this each test will be stored in an item of the ValidationTestList.
        # We'll iterate over the methods, test cases, and bins, and fill in each in turn

        for test_case_info, test_case_writer in zip(self.l_test_case_info, self.l_test_case_writers):

            test_case_name = test_case_info.name
            l_bin_limits = self.d_l_bin_limits[test_case_info.bins]

            # Get whether this relates to m or c from the test case info's test_case_id's last letter
            prop = get_prop_from_id(test_case_info.id).value

            fail_sigma = getattr(self.fail_sigma_calculator, f"d_scaled_{self.mode.value}_sigma")[test_case_info.name]

            # Fill in metadata about the test

            requirement_writer = test_case_writer.l_requirement_writers[0]

            if (self.method_data_exists and test_case_info.bins != BinParameters.EPOCH and
                    test_case_name in self.d_l_d_bias_measurements):

                num_bins = len(l_bin_limits) - 1

                l_d_val: List[Optional[Dict[int, float]]] = [None] * num_bins
                l_d_val_err: List[Optional[Dict[int, float]]] = [None] * num_bins
                l_d_val_target: List[Optional[Dict[int, float]]] = [None] * num_bins
                l_d_val_z: List[Optional[Dict[int, float]]] = [None] * num_bins

                l_d_bias_measurements = self.d_l_d_bias_measurements[test_case_name]

                for bin_index in range(num_bins):

                    d_test_case_bias_measurements = l_d_bias_measurements[bin_index]

                    l_d_val[bin_index] = {1: getattr(d_test_case_bias_measurements[1], prop),
                                          2: getattr(d_test_case_bias_measurements[2], prop)}
                    l_d_val_err[bin_index] = {1: getattr(d_test_case_bias_measurements[1], f"{prop}_err"),
                                              2: getattr(d_test_case_bias_measurements[2], f"{prop}_err")}
                    l_d_val_target[bin_index] = {1: getattr(d_test_case_bias_measurements[1], f"{prop}_target"),
                                                 2: getattr(d_test_case_bias_measurements[2], f"{prop}_target")}
                    l_d_val_z[bin_index] = {1: getattr(d_test_case_bias_measurements[1], f"{prop}_sigma"),
                                            2: getattr(d_test_case_bias_measurements[2], f"{prop}_sigma")}

                report_method = None
                report_kwargs = {}
                write_kwargs = {"have_data"     : True,
                                "prop"          : prop,
                                "l_d_val"       : l_d_val,
                                "l_d_val_err"   : l_d_val_err,
                                "l_d_val_target": l_d_val_target,
                                "l_d_val_z"     : l_d_val_z,
                                "fail_sigma"    : fail_sigma,
                                "method"        : test_case_info.method,
                                "bin_parameter" : test_case_info.bin_parameter,
                                "l_bin_limits"  : self.d_l_bin_limits[test_case_info.bins]}

            else:
                # Report that the test wasn't run due to a lack of data
                report_method = requirement_writer.report_test_not_run
                report_kwargs = {"reason": MSG_NO_DATA}
                write_kwargs = {}

            write_kwargs["report_method"] = report_method
            write_kwargs["report_kwargs"] = report_kwargs

            test_case_writer.write(requirements_kwargs = write_kwargs, )


def fill_shear_bias_test_results(test_result_product: dpdSheValidationTestResults,
                                 d_l_d_bias_measurements: Dict[str, List[Dict[int, BiasMeasurements]]],
                                 pipeline_config: Dict[ConfigKeys, Any],
                                 d_l_bin_limits: Dict[BinParameters, np.ndarray], workdir: str,
                                 dl_dl_plot_filenames: Union[Dict[str, Union[Dict[str, str], List[str]]],
                                                             List[Union[Dict[str, str], List[str]]]] = None,
                                 method_data_exists: bool = True, mode: ExecutionMode = ExecutionMode.LOCAL):
    """ Interprets the bias measurements and writes out the results of the test and figures to the data product.
    """

    # Set up a calculator object for scaled fail sigmas
    fail_sigma_calculator = FailSigmaCalculator(pipeline_config = pipeline_config,
                                                l_test_case_info = L_SHEAR_BIAS_TEST_CASE_INFO,
                                                d_bin_limits = d_l_bin_limits,
                                                mode = mode)

    # Initialize a test results writer
    test_results_writer = ShearBiasValidationResultsWriter(test_object = test_result_product,
                                                           workdir = workdir,
                                                           d_l_d_bias_measurements = d_l_d_bias_measurements,
                                                           d_l_bin_limits = d_l_bin_limits,
                                                           fail_sigma_calculator = fail_sigma_calculator,
                                                           method_data_exists = method_data_exists,
                                                           mode = mode,
                                                           dl_l_figures = dl_dl_plot_filenames)

    test_results_writer.write()
