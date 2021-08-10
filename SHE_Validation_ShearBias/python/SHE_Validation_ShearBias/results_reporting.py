""" @file results_reporting.py

    Created 15 July 2021

    Utility functions for Shear Bias validation, for reporting results.
"""
from copy import deepcopy
from typing import Dict, List,  Any, Callable, Union

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods, NUM_METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements

from SHE_Validation.constants.default_config import ExecutionMode
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.results_writer import (SupplementaryInfo, RequirementWriter, AnalysisWriter,
                                           TestCaseWriter, ValidationResultsWriter, RESULT_PASS, RESULT_FAIL,
                                           WARNING_MULTIPLE, MSG_NO_DATA, FailSigmaCalculator)
from SHE_Validation_ShearBias.constants.shear_bias_test_info import get_prop_from_id
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
import numpy as np

from .constants.shear_bias_test_info import (ShearBiasTestCases,
                                             L_SHEAR_BIAS_TEST_CASE_INFO,
                                             D_L_SHEAR_BIAS_REQUIREMENT_INFO,)


__updated__ = "2021-08-10"

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
SHEAR_BIAS_DIRECTORY_HEADER = "### OU-SHE Shear Bias Analysis Results File Directory ###"


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

    def _calc_test_results(self):
        """ Calculate the test results
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
        self._calc_test_results()

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

    method = None

    def __init__(self, method, *args, **kwargs):
        super().__init__(product_type="SHEAR-BIAS-ANALYSIS-FILES",
                         *args, **kwargs)

        self.method = method

    def _get_filename_tag(self):
        """ Overriding method to get a tag to add to figure/textfile filenames with method name.
        """
        return self.method

    def _generate_directory_filename(self):
        """ Overriding method to generate a filename for a directory file.
        """
        self.directory_filename = SHEAR_BIAS_DIRECTORY_FILENAME

    def _get_directory_header(self):
        """ Overriding method to get the desired header for a directory file.
        """
        return SHEAR_BIAS_DIRECTORY_HEADER


class ShearBiasTestCaseWriter(TestCaseWriter):

    method = None

    def __init__(self,
                 parent_validation_writer: "ShearBiasValidationResultsWriter",
                 test_case_object,
                 test_case_info: TestCaseInfo,
                 method=None,
                 *args, **kwargs):
        """ We override __init__ since we'll be using a known set of requirement info.
        """

        # Get whether we're doing m or c from the last letter of the test case id
        prop = test_case_info.test_case_id[-1]
        requirement_info = D_SHEAR_BIAS_REQUIREMENT_INFO[ShearBiasTestCases(prop)]

        self.method = method

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
        return ShearBiasAnalysisWriter(parent_test_case_writer=self, method=self.method, **kwargs)

    def write(self, *args, **kwargs):
        """ Need to override write here to make sure that 'method' is properly set up for each analysis writer.
        """

        self.analysis_writer.method = self.method
        super().write(*args, **kwargs)


class ShearBiasValidationResultsWriter(ValidationResultsWriter):

    # Types of child classes
    test_case_writer_type = ShearBiasTestCaseWriter

    def __init__(self,
                 test_object: dpdSheValidationTestResults,
                 workdir: str,
                 d_bias_measurements: Dict[str, Dict[int, BiasMeasurements]],
                 fail_sigma_calculator: FailSigmaCalculator,
                 method_data_exists: bool = True,
                 mode: ExecutionMode = ExecutionMode,
                 *args, **kwargs):

        super().__init__(test_object=test_object,
                         workdir=workdir,
                         l_test_case_info=L_SHEAR_BIAS_TEST_CASE_INFO,
                         dl_l_requirement_info=D_L_SHEAR_BIAS_REQUIREMENT_INFO,
                         *args, **kwargs)

        self.d_bias_measurements = d_bias_measurements
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

            # Get whether this relates to m or c from the test case info's test_case_id's last letter
            prop = get_prop_from_id(test_case_info.id)

            fail_sigma = getattr(self.fail_sigma_calculator, f"d_scaled_{self.mode}_sigma")[test_case_info.name]

            # Fill in metadata about the test

            requirement_writer = test_case_writer.l_requirement_writers[0]

            if self.data_exists and test_case_info.bins != BinParameters.EPOCH:

                d_test_case_bias_measurements = self.d_bias_measurements[test_case_name]

                val = {1: getattr(d_test_case_bias_measurements[1], prop),
                       2: getattr(d_test_case_bias_measurements[2], prop)}
                val_err = {1: getattr(d_test_case_bias_measurements[1], f"{prop}_err"),
                           2: getattr(d_test_case_bias_measurements[2], f"{prop}_err")}
                val_target = getattr(d_test_case_bias_measurements[1], f"{prop}_target")
                val_z = {1: getattr(d_test_case_bias_measurements[1], f"{prop}_sigma"),
                         2: getattr(d_test_case_bias_measurements[2], f"{prop}_sigma")}

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


def fill_shear_bias_validation_results(test_result_product: dpdSheValidationTestResults,
                                       d_bias_measurements: Dict[str, Dict[int, BiasMeasurements]],
                                       pipeline_config: Dict[str, Any],
                                       d_bin_limits: Dict[BinParameters, np.ndarray],
                                       workdir: str,
                                       dl_l_figures: Union[Dict[str, Union[Dict[str, str], List[str]]],
                                                           List[Union[Dict[str, str], List[str]]], ] = None,
                                       method_data_exists: bool = True,
                                       mode: ExecutionMode = ExecutionMode.LOCAL):
    """ Interprets the bias measurements and writes out the results of the test and figures to the data product.
    """

    # Set up a calculator object for scaled fail sigmas
    fail_sigma_calculator = FailSigmaCalculator(pipeline_config=pipeline_config,
                                                l_test_case_info=L_SHEAR_BIAS_TEST_CASE_INFO,
                                                d_bin_limits=d_bin_limits,
                                                mode=mode)

    # Initialize a test results writer
    test_results_writer = ShearBiasValidationResultsWriter(test_object=test_result_product,
                                                           workdir=workdir,
                                                           d_bias_measurements=d_bias_measurements,
                                                           fail_sigma_calculator=fail_sigma_calculator,
                                                           method_data_exists=method_data_exists,
                                                           dl_l_figures=dl_l_figures,
                                                           mode=mode)

    test_results_writer.write()
