""" @file results_reporting.py

    Created 15 July 2021

    Utility functions for Shear Bias validation, for reporting results.
"""

__updated__ = "2021-07-19"

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

from copy import deepcopy
from typing import Dict, List,  Any, Callable, Union

from SHE_PPT.constants.shear_estimation_methods import METHODS, NUM_METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements
from SHE_PPT.pipeline_utility import AnalysisValidationConfigKeys
import scipy.stats

from SHE_Validation.results_writer import (SupplementaryInfo, RequirementWriter, AnalysisWriter,
                                           TestCaseWriter, ValidationResultsWriter, RESULT_PASS, RESULT_FAIL,
                                           WARNING_MULTIPLE, MSG_NO_DATA)
from SHE_Validation.test_info import TestCaseInfo
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
import numpy as np

from .constants.shear_bias_default_config import FailSigmaScaling
from .constants.shear_bias_test_info import (D_SHEAR_BIAS_REQUIREMENT_INFO,
                                             ShearBiasTestCases,
                                             D_SHEAR_BIAS_TEST_CASE_INFO,
                                             SHEAR_BIAS_TEST_CASE_M_INFO,
                                             SHEAR_BIAS_TEST_CASE_C_INFO)
from .constants.shear_bias_test_info import NUM_METHOD_SHEAR_BIAS_TEST_CASES

logger = getLogger(__name__)

# Define constants for various messages

KEY_G1_INFO = "G1_INFO"
KEY_G2_INFO = "G2_INFO"

DESC_INFO_BASE = "Information about the test on REPLACEME_PROP bias in component REPLACEME_COMPONENT."

D_DESC_INFO = {}
for prop, name in ("m", "multiplicative"), ("c", "additive"):
    for i in (1, 2):
        D_DESC_INFO[f"{prop}{i}"] = DESC_INFO_BASE.replace(
            "REPLACEME_PROP", name).replace("REPLACEME_COMPONENT", f"{i}")

MSG_NAN_VAL = "Test failed due to NaN regression results."
MSG_ZERO_ERR = "Test failed due to zero error."

SHEAR_BIAS_DIRECTORY_FILENAME = "SheShearBiasResultsDirectory.txt"
SHEAR_BIAS_DIRECTORY_HEADER = "### OU-SHE CTI-Gal Analysis Results File Directory ###"


class FailSigmaCalculator():
    """Class to calculate the fail sigma, scaling properly for number of bins and/or/nor test cases.
    """

    def __init__(self,
                 pipeline_config: Dict[str, str]):

        self.m_fail_sigma = pipeline_config[AnalysisValidationConfigKeys.SBV_M_FAIL_SIGMA.value]
        self.c_fail_sigma = pipeline_config[AnalysisValidationConfigKeys.SBV_C_FAIL_SIGMA.value]
        self.fail_sigma_scaling = pipeline_config[AnalysisValidationConfigKeys.SBV_FAIL_SIGMA_SCALING.value]

        self.num_test_cases = NUM_METHOD_SHEAR_BIAS_TEST_CASES

        self._d_scaled_m_sigma = None
        self._d_scaled_c_sigma = None

    @property
    def d_scaled_m_sigma(self):
        if self._d_scaled_m_sigma is None:
            self._d_scaled_m_sigma = self._calc_d_scaled_sigma(self.m_fail_sigma)
        return self._d_scaled_m_sigma

    @property
    def d_scaled_c_sigma(self):
        if self._d_scaled_c_sigma is None:
            self._d_scaled_c_sigma = self._calc_d_scaled_sigma(self.c_fail_sigma)
        return self._d_scaled_c_sigma

    def _calc_d_scaled_sigma(self, base_sigma: float) -> Dict[str, float]:

        d_scaled_sigma = {}

        for test_case in ShearBiasTestCases:

            # Get the number of tries depending on scaling type
            if self.fail_sigma_scaling == FailSigmaScaling.NO_SCALE.value:
                num_tries = 1
            elif self.fail_sigma_scaling == FailSigmaScaling.TEST_CASE_SCALE.value:
                num_tries = self.num_test_cases
            else:
                raise ValueError("Unexpected fail sigma scaling: " + self.fail_sigma_scaling)

            d_scaled_sigma[test_case] = self._calc_scaled_sigma_from_tries(base_sigma=base_sigma,
                                                                           num_tries=num_tries)

        return d_scaled_sigma

    @classmethod
    def _calc_scaled_sigma_from_tries(cls,
                                      base_sigma: float,
                                      num_tries: int) -> float:
        # To avoid numeric error, don't calculate if num_tries==1
        if num_tries == 1:
            return base_sigma

        p_good = (1 - 2 * scipy.stats.norm.cdf(-base_sigma))
        return -scipy.stats.norm.ppf((1 - p_good**(1 / num_tries)) / 2)


class ShearBiasRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    prop = None
    val = None
    val_err = None
    val_target = None
    val_z = None
    fail_sigma = None
    test_pass = None
    result = None
    good_data = None

    def _get_supplementary_info(self,
                                extra_g1_message: str = "",
                                extra_g2_message: str = "",) -> SupplementaryInfo:

        # Check the extra messages and make sure they end in a linebreak
        if extra_g1_message != "" and extra_g1_message[-1:] != "\n":
            extra_g1_message = extra_g1_message + "\n"
        if extra_g2_message != "" and extra_g2_message[-1:] != "\n":
            extra_g2_message = extra_g2_message + "\n"

        # Set up result messages for each component
        messages = {1: extra_g1_message + "\n",
                    2: extra_g2_message + "\n"}
        for i in (1, 2):

            messages[i] += (f"{self.prop}{i} = {self.val[i]}\n" +
                            f"{self.prop}{i}_err = {self.val_err[i]}\n" +
                            f"{self.prop}{i}_z = {self.val_z[i]}\n" +
                            f"Maximum allowed {self.prop}_z = {self.fail_sigma}\n" +
                            f"Result: {self.result[i]}\n\n")

        supplementary_info = (SupplementaryInfo(key=KEY_G1_INFO,
                                                description=D_DESC_INFO[f"{self.prop}1"],
                                                message=messages[1]),
                              SupplementaryInfo(key=KEY_G2_INFO,
                                                description=D_DESC_INFO[f"{self.prop}2"],
                                                message=messages[2]))

        return supplementary_info

    def report_bad_data(self):

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_supplementary_info(extra_g1_message=MSG_NAN_VAL,
                                                            extra_g2_message=MSG_NAN_VAL,)
        super().report_bad_data(l_supplementary_info)

    def report_zero_err(self):

        # Report -2 as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = -2.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_supplementary_info(extra_g1_message=MSG_ZERO_ERR,
                                                            extra_g2_message=MSG_ZERO_ERR,)
        self.add_supplementary_info(l_supplementary_info)

    def report_good_data(self,
                         measured_value: float):

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_supplementary_info()
        super().report_good_data(measured_value=measured_value,
                                 warning=False,
                                 l_supplementary_info=l_supplementary_info)

    def _calc_test_results(self,
                           i: int):
        """ Calculate the test results for either component
        """

        # Init each of pass and result as empty dicts
        self.test_pass = {}
        self.result = {}
        self.good_data = {}
        some_good_data = False

        for i in (1, 2):
            if (np.isnan(self.val[i]) or np.isnan(self.val_err[i])):
                self.test_pass[i] = False
                self.good_data[i] = False
            else:
                self.test_pass[i] = self.val_z[i] < self.fail_sigma
                self.good_data[i] = True
                some_good_data = True
            if self.test_pass[i]:
                self.result[i] = RESULT_PASS
            else:
                self.result[i] = RESULT_FAIL

        # Pass if there's at least some good data, and all good data passes
        if (not some_good_data) or ((self.test_pass[1] or not self.good_data[1]) and
                                    (self.test_pass[2] or not self.good_data[2])):
            setattr(self, f"{prop}_pass", True)
            setattr(self, f"{prop}_result", RESULT_PASS)
        else:
            setattr(self, f"{prop}_pass", False)
            setattr(self, f"{prop}_result", RESULT_FAIL)

    def write(self,
              report_method: Callable[[Any], None] = None,
              have_data: bool = False,
              prop: Dict[int, float] = None,
              val: Dict[int, float] = None,
              val_err: Dict[int, float] = None,
              val_target: float = None,
              val_z: Dict[int, float] = None,
              fail_sigma: float = None,
              report_kwargs: Dict[str, Any] = None) -> str:

        self.prop = prop
        self.val = val
        self.val_err = val_err
        self.val_target = val_target
        self.val_z = val_z
        self.fail_sigma = fail_sigma

        # Default to reporting good data if we're not told otherwise
        if report_method is None:
            report_method = self.report_good_data

        # Default to empty dict for report_kwargs
        if report_kwargs is None:
            report_kwargs = {}

        # If we don't have data, report with the provided method and return
        if not have_data:
            report_method(**report_kwargs)
            return RESULT_PASS

        # Calculate test results for both components
        for i in (1, 2):
            self._calc_test_results(i)

        # Report the result based on whether or not bothc components passed
        test_pass = self.test_pass[1] and self.test_pass[2]
        if test_pass:
            result = RESULT_PASS
        else:
            result = RESULT_FAIL
        self.requirement_object.ValidationResult = result

        parameter = D_SHEAR_BIAS_REQUIREMENT_INFO[ShearBiasTestCases(self.prop)].parameter

        self.requirement_object.MeasuredValue[0].Parameter = parameter

        # Check for data quality issues and report as proper if found
        if self.val_err[1] == 0 or self.val_err[2] == 0:
            report_method = self.report_zero_err
            extra_report_kwargs = {}
        elif ((np.isnan(self.val[1]) or np.isnan(self.val_err[1]) or
               np.isinf(self.val[1]) or np.isinf(self.val_err[1])) and
              (np.isnan(self.val[2]) or np.isnan(self.val_err[2]) or
               np.isinf(self.val[1]) or np.isinf(self.val_err[1]))):
            report_method = self.report_bad_data
            extra_report_kwargs = {}
        else:
            report_method = self.report_good_data

            # Report the maximum z as the measured value for this test
            extra_report_kwargs = {"measured_value": np.nanmax((self.val_z[1], self.val_z[2]))}

        return super().write(result=result,
                             report_method=report_method,
                             report_kwargs={**report_kwargs, **extra_report_kwargs},)


class ShearBiasAnalysisWriter(AnalysisWriter):
    """ Subclass of AnalysisWriter, to handle some changes specific for this test.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(product_type="CTI-GAL-ANALYSIS-FILES",
                         *args, **kwargs)

    def _generate_directory_filename(self):
        """ Overriding method to generate a filename for a directory file.
        """
        self.directory_filename = SHEAR_BIAS_DIRECTORY_FILENAME

    def _get_directory_header(self):
        """ Overriding method to get the desired header for a directory file.
        """
        return SHEAR_BIAS_DIRECTORY_HEADER


class ShearBiasTestCaseWriter(TestCaseWriter):

    def __init__(self,
                 parent_validation_writer: "ShearBiasValidationResultsWriter",
                 test_case_object,
                 test_case_info: TestCaseInfo,
                 *args, **kwargs):
        """ We override __init__ since we'll be using a known set of requirement info.
        """

        # Get whether we're doing m or c from the last letter of the test case id
        prop = test_case_info.test_case_id[-1]
        requirement_info = D_SHEAR_BIAS_REQUIREMENT_INFO[ShearBiasTestCases(prop)]

        super().__init__(parent_validation_writer,
                         test_case_object,
                         test_case_info,
                         l_requirement_info=requirement_info,
                         *args, **kwargs)

    def _init_requirement_writer(self, **kwargs) -> ShearBiasRequirementWriter:
        """ We override the _init_requirement_writer method to create a writer of the inherited type.
        """
        return ShearBiasRequirementWriter(self, **kwargs)

    def _init_analysis_writer(self, **kwargs) -> ShearBiasAnalysisWriter:
        """ We override the _init_analysis_writer method to create a writer of the inherited type.
        """
        return ShearBiasAnalysisWriter(self, **kwargs)


class ShearBiasValidationResultsWriter(ValidationResultsWriter):
    def __init__(self,
                 test_object: dpdSheValidationTestResults,
                 workdir: str,
                 d_bias_measurements: Dict[str, Dict[int, BiasMeasurements]],
                 fail_sigma_calculator: FailSigmaCalculator,
                 data_exists: bool = True,
                 *args, **kwargs):

        # Initialise a list of test case info. We'll have one m for each method, and one c for each method
        l_test_case_info = [SHEAR_BIAS_TEST_CASE_M_INFO] * NUM_METHODS + [SHEAR_BIAS_TEST_CASE_C_INFO] * NUM_METHODS

        super().__init__(test_object=test_object,
                         workdir=workdir,
                         num_test_cases=None,
                         l_test_case_info=l_test_case_info, *args, **kwargs)

        self.d_bias_measurements = d_bias_measurements
        self.fail_sigma_calculator = fail_sigma_calculator
        self.data_exists = data_exists

    def _init_test_case_writer(self, **kwargs):
        """ Override _init_test_case_writer to create a ShearBiasTestCaseWriter
        """
        return ShearBiasTestCaseWriter(self, **kwargs)

    def write_test_case_objects(self):
        """ Writes all data for each requirement subobject, modifying self._test_object.
        """
        # The results of this each test will be stored in an item of the ValidationTestList.
        # We'll iterate over the methods, test cases, and bins, and fill in each in turn

        test_case_index = 0

        for test_case in ShearBiasTestCases:

            # Get whether this relates to m or c from the test case info's test_case_id's last letter
            test_case_info = D_SHEAR_BIAS_TEST_CASE_INFO[test_case]
            prop = test_case_info.test_case_id[-1]

            fail_sigma = getattr(self.fail_sigma_calculator, f"d_scaled_{prop}_sigma")[test_case]

            for method in METHODS:

                test_case_writer = self.l_test_case_writers[test_case_index]

                # Use a modified test case info object to describe this test, clarifying it's
                # just for this method
                method_test_case_info = deepcopy(test_case_info)
                method_test_case_info._test_case_id = method_test_case_info.id + "-" + method

                test_case_writer._test_case_info = method_test_case_info

                # Fill in metadata about the test

                requirement_writer = test_case_writer.l_requirement_writers[0]

                if method in self.d_bias_measurements:
                    d_method_bias_measurements = self.d_bias_measurements[method]
                    method_data_exists = True
                else:
                    method_data_exists = False

                if self.data_exists and method_data_exists:

                    val = {1: getattr(d_method_bias_measurements[1], prop),
                           2: getattr(d_method_bias_measurements[2], prop)}
                    val_err = {1: getattr(d_method_bias_measurements[1], f"{prop}_err"),
                               2: getattr(d_method_bias_measurements[2], f"{prop}_err")}
                    val_target = getattr(d_method_bias_measurements[1], f"{prop}_target")
                    val_z = {1: getattr(d_method_bias_measurements[1], f"{prop}_sigma"),
                             2: getattr(d_method_bias_measurements[2], f"{prop}_sigma")}

                    report_method = None
                    report_kwargs = {}
                    write_kwargs = {"have_data": True,
                                    "prop": prop,
                                    "val": val,
                                    "val_err": val_err,
                                    "val_target": val_target,
                                    "val_z": val_z,
                                    "fail_sigma": fail_sigma}

                else:
                    # Report that the test wasn't run due to a lack of data
                    report_method = requirement_writer.report_test_not_run
                    report_kwargs = {"reason": MSG_NO_DATA}
                    write_kwargs = {}

                write_kwargs["report_method"] = report_method
                write_kwargs["report_kwargs"] = report_kwargs

                test_case_writer.write(requirements_kwargs=write_kwargs,)

                test_case_index += 1


def fill_shear_bias_validation_results(test_result_product: dpdSheValidationTestResults,
                                       d_bias_measurements: Dict[str, Dict[int, BiasMeasurements]],
                                       pipeline_config: Dict[str, Any],
                                       workdir: str,
                                       figures: Union[Dict[str, Union[Dict[str, str], List[str]]],
                                                      List[Union[Dict[str, str], List[str]]], ] = None,
                                       data_exists: bool = True):
    """ Interprets the bias measurements and writes out the results of the test and figures to the data product.
    """

    # Set up a calculator object for scaled fail sigmas
    fail_sigma_calculator = FailSigmaCalculator(pipeline_config=pipeline_config)

    # Initialize a test results writer
    test_results_writer = ShearBiasValidationResultsWriter(test_object=test_result_product,
                                                           workdir=workdir,
                                                           d_bias_measurements=d_bias_measurements,
                                                           fail_sigma_calculator=fail_sigma_calculator,
                                                           data_exists=data_exists,
                                                           figures=figures)

    test_results_writer.write()
