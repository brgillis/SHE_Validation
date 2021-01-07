""" @file input_data.py

    Created 17 December 2020

    Utility functions for CTI-Gal validation, for reporting results.
"""

__updated__ = "2021-01-07"

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

from astropy import table

from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
import numpy as np

from .constants.cti_gal_test_info import (CTI_GAL_REQUIREMENT_ID, CTI_GAL_PARAMETER,
                                          CTI_GAL_TEST_CASES, CTI_GAL_TEST_CASE_GLOBAL,
                                          D_CTI_GAL_TEST_CASE_INFO,)
from .table_formats.regression_results import TF as RR_TF


logger = getLogger(__name__)

# Define constants for various messages

RESULT_PASS = "PASSED"
RESULT_FAIL = "FAILED"

COMMENT_LEVEL_INFO = "INFO"
COMMENT_LEVEL_WARNING = "WARNING"
COMMENT_MULTIPLE = "Multiple notes; see SupplementaryInformation."

INFO_MULTIPLE = COMMENT_LEVEL_INFO + ": " + COMMENT_MULTIPLE

WARNING_TEST_NOT_RUN = "WARNING: Test not run."
WARNING_MULTIPLE = COMMENT_LEVEL_WARNING + ": " + COMMENT_MULTIPLE

KEY_REASON = "REASON"
KEY_SLOPE_INFO = "SLOPE_INFO"
KEY_INTERCEPT_INFO = "INTERCEPT_INFO"

DESC_REASON = "Why the test was not run."
DESC_SLOPE_INFO = "Information about the test on slope of g1_image versus readout distance."
DESC_INTERCEPT_INFO = "Information about the test on intercept of g1_image versus readout distance."

MSG_NAN_SLOPE = "Test failed due to NaN regression results for slope."
MSG_ZERO_SLOPE_ERR = "Test failed due to zero slope error."
MSG_NO_DATA = "No data is available for this test."
MSG_NOT_IMPLEMENTED = "This test has not yet been implemented."


def report_test_not_run(requirement_object,
                        reason="Unspecified reason."):
    """ Fills in the data model with the fact that a test was not run and the reason.
    """

    requirement_object.MeasuredValue.Parameter = WARNING_TEST_NOT_RUN
    requirement_object.ValidationResult = RESULT_PASS
    requirement_object.Comment = WARNING_TEST_NOT_RUN

    supplementary_info_parameter = requirement_object.SupplementaryInformation.Parameter[0]
    supplementary_info_parameter.Key = KEY_REASON
    supplementary_info_parameter.Description = DESC_REASON
    supplementary_info_parameter.StringValue = reason

    return


class CTIGalRequirementWriter():
    """ Class for managing reporting of results for a single CTI-Gal test case.
    """

    def __init__(self,
                 requirement_object,
                 slope: float,
                 slope_err: float,
                 intercept: float,
                 intercept_err: float,
                 slope_fail_sigma: float,
                 intercept_fail_sigma: float):

        self.requirement_object = requirement_object
        self.slope = slope
        self.slope_err = slope_err
        self.intercept = intercept
        self.intercept_err = intercept_err
        self.slope_fail_sigma = slope_fail_sigma
        self.intercept_fail_sigma = intercept_fail_sigma

        # Calculate some values for both the slope and intercept
        for prop in ("slope", "intercept"):
            if np.isnan(getattr(self, prop)) or np.isnan(getattr(self, f"{prop}_err")):
                setattr(self, f"{prop}_z", np.NaN)
                setattr(self, f"{prop}_pass", False)
                setattr(self, f"{prop}_result", RESULT_FAIL)
            elif getattr(self, f"{prop}_err") == 0.:
                setattr(self, f"{prop}_z", np.NaN)
                setattr(self, f"{prop}_pass", False)
            else:
                setattr(self, f"{prop}_z", np.abs(getattr(self, prop) / getattr(self, f"{prop}_err")))
                setattr(self, f"{prop}_pass", getattr(self, f"{prop}_z") < getattr(self, f"{prop}_fail_sigma"))

            if getattr(self, f"{prop}_pass"):
                setattr(self, f"{prop}_result", RESULT_PASS)
            else:
                setattr(self, f"{prop}_result", RESULT_FAIL)

        return

    def add_supplementary_info(self,
                               extra_slope_message: str ="",
                               extra_intercept_message: str =""):

        # Check the extra messages and make sure they end in a linebreak
        if extra_slope_message != "" and extra_slope_message[-1:] != "\n":
            extra_slope_message = extra_slope_message + "\n"
        if extra_intercept_message != "" and extra_intercept_message[-1:] != "\n":
            extra_intercept_message = extra_intercept_message + "\n"

        slope_supplementary_info_parameter = self.requirement_object.SupplementaryInformation.Parameter[0]
        intercept_supplementary_info_parameter = deepcopy(slope_supplementary_info_parameter)

        self.requirement_object.SupplementaryInformation.Parameter = [slope_supplementary_info_parameter,
                                                                      intercept_supplementary_info_parameter]

        slope_supplementary_info_parameter.Key = KEY_SLOPE_INFO
        slope_supplementary_info_parameter.Description = DESC_SLOPE_INFO
        slope_supplementary_info_parameter.StringValue = (extra_slope_message +
                                                          f"slope = {self.slope}\n" +
                                                          f"slope_err = {self.slope_err}\n" +
                                                          f"slope_z = {self.slope_z}\n" +
                                                          f"Maximum allowed slope_z = {self.slope_fail_sigma}\n" +
                                                          f"Result: {self.slope_result}\n")

        intercept_supplementary_info_parameter.Key = KEY_INTERCEPT_INFO
        intercept_supplementary_info_parameter.Description = DESC_INTERCEPT_INFO
        intercept_supplementary_info_parameter.StringValue = (extra_intercept_message +
                                                              f"intercept = {self.intercept}\n" +
                                                              f"intercept_err = {self.intercept_err}\n" +
                                                              f"intercept_z = {self.intercept_z}\n" +
                                                              f"Maximum allowed intercept_z = " +
                                                              f"{self.intercept_fail_sigma}\n" +
                                                              f"Result: {self.intercept_result}\n")

        return

    def report_bad_data(self):

        # Report -1 as the measured value for this test
        self.requirement_object.MeasuredValue.Value.FloatValue = -1.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details
        self.add_supplementary_info(extra_slope_message=MSG_NAN_SLOPE)

        return

    def report_zero_slope_err(self):

        # Report -2 as the measured value for this test
        self.requirement_object.MeasuredValue.Value.FloatValue = -2.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details

        self.add_supplementary_info(extra_slope_message=MSG_ZERO_SLOPE_ERR,)

        return

    def report_good_data(self):

        # Report the self.slope_z as the measured value for this test
        self.requirement_object.MeasuredValue.Value.FloatValue = self.slope_z

        # If the slope passes but the intercept doesn't, we should raise a warning
        if self.slope_pass and not self.intercept_pass:
            comment_level = COMMENT_LEVEL_WARNING
        else:
            comment_level = COMMENT_LEVEL_INFO

        self.requirement_object.Comment = f"{comment_level}: " + COMMENT_MULTIPLE

        # Add a supplementary info key for each of the self.slope and self.intercept, reporting details

        self.add_supplementary_info()

        return

    def report_data(self):

        # Report the result based on whether or not the slope passed.
        self.requirement_object.ValidationResult = self.slope_result
        self.requirement_object.MeasuredValue.Parameter = CTI_GAL_PARAMETER

        # Check for data quality issues and report as proper if found
        if (np.isnan([self.slope, self.slope_err]).any() or
                np.isinf([self.slope, self.slope_err]).any()):
            self.report_bad_data()
        elif self.slope_err == 0.:
            self.report_zero_slope_err()
        else:
            self.report_good_data()

        return


def fill_cti_gal_validation_results(test_result_product: dpdSheValidationTestResults,
                                    regression_results_row: table.Row,
                                    pipeline_config: Dict[str, Any],
                                    method_data_exists: bool = True):
    """ Interprets the results in the regression_results_row and other provided data to fill out the provided
        test_result_product with the results of this validation test.
    """

    # The results of this each test will be stored in an item of the ValidationTestList.
    # We'll iterate over the methods and test cases and fill in each in turn

    test_case_index = 0

    for method in METHODS:
        for test_case in CTI_GAL_TEST_CASES:
            test_object = test_result_product.Data.ValidationTestList[test_case_index]

            # Fill in metadata about the test
            test_object.TestId = D_CTI_GAL_TEST_CASE_INFO[test_case].id + "-" + method
            test_object.TestDescription = D_CTI_GAL_TEST_CASE_INFO[test_case].description

            requirement_object = test_object.ValidatedRequirements.Requirement[0]

            requirement_object.Id = CTI_GAL_REQUIREMENT_ID

            requirement_object.MeasuredValue.Parameter = CTI_GAL_PARAMETER

            if test_case == CTI_GAL_TEST_CASE_GLOBAL and method_data_exists:

                requirement_writer = CTIGalRequirementWriter(requirement_object,
                                                             slope=regression_results_row[getattr(
                                                                 RR_TF, f"slope_{method}")],
                                                             slope_err=regression_results_row[getattr(
                                                                 RR_TF, f"slope_err_{method}")],
                                                             intercept=regression_results_row[getattr(
                                                                 RR_TF, f"intercept_{method}")],
                                                             intercept_err=regression_results_row[getattr(
                                                                 RR_TF, f"intercept_err_{method}")],
                                                             slope_fail_sigma=pipeline_config[
                                                                 AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value],
                                                             intercept_fail_sigma=pipeline_config[
                                                                 AnalysisConfigKeys.CGV_INTERCEPT_FAIL_SIGMA.value])

                requirement_writer.report_data()

            elif test_case == CTI_GAL_TEST_CASE_GLOBAL and not method_data_exists:
                # Report that the test wasn't run due to a lack of data
                report_test_not_run(requirement_object,
                                    reason=MSG_NO_DATA)

            else:
                # Report that the test wasn't run due to it not yet being implemented
                report_test_not_run(requirement_object,
                                    reason=MSG_NOT_IMPLEMENTED)

            test_object.GlobalResult = requirement_object.ValidationResult

            test_case_index += 1

    return
