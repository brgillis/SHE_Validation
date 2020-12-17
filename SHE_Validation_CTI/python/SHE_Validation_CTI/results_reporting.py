""" @file input_data.py

    Created 17 December 2020

    Utility functions for CTI-Gal validation, for reporting results.
"""

__updated__ = "2020-12-17"

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

from astropy import table

from SHE_PPT.logging import getLogger
from SHE_Validation_CTI import constants
from SHE_Validation_CTI.table_formats.regression_results import tf as rr_tf
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
import numpy as np


logger = getLogger(__name__)


def report_test_not_run(requirement_object,
                        reason="Unspecified reason."):
    """ Fills in the data model with the fact that a test was not run and the reason.
    """

    requirement_object.MeasuredValue.Parameter = 0.
    requirement_object.ValidationResult = "PASSED"
    requirement_object.Comment = "WARNING: Test not run."

    supplementary_info_parameter = requirement_object.SupplementaryInformation.Parameter[0]
    supplementary_info_parameter.Key = "REASON"
    supplementary_info_parameter.Description = "Why the test was not run."
    supplementary_info_parameter.StringValue = reason

    return


def add_supplementary_info(requirement_object,
                           slope: float,
                           slope_err: float,
                           slope_z: float,
                           slope_result: float,
                           intercept: float,
                           intercept_err: float,
                           intercept_result: float,
                           extra_slope_message: str ="",
                           extra_intercept_message: str =""):

    # Check the extra messages and make sure they end in a linebreak
    if extra_slope_message != "" and extra_slope_message[-2:] != "\n":
        extra_slope_message = extra_slope_message + "\n"
    if extra_intercept_message != "" and extra_intercept_message[-2:] != "\n":
        extra_intercept_message = extra_intercept_message + "\n"

    slope_supplementary_info_parameter = requirement_object.SupplementaryInformation.Parameter[0]
    intercept_supplementary_info_parameter = deepcopy(slope_supplementary_info_parameter)
    requirement_object.SupplementaryInformation.Parameter[0].append(
        intercept_supplementary_info_parameter)

    slope_supplementary_info_parameter.Key = "SLOPE_INFO"
    slope_supplementary_info_parameter.Description = ("Information about the test on slope of g1_image " +
                                                      "versus readout distance.")
    slope_supplementary_info_parameter.StringValue = (extra_slope_message +
                                                      f"slope = {slope}\n" +
                                                      f"slope_err = {slope_err}\n" +
                                                      f"slope_z = {slope_z}\n" +
                                                      f"Maximum allowed slope_z = {constants.slope_fail_sigma}\n" +
                                                      f"Result: {slope_result}\n")

    intercept_supplementary_info_parameter.Key = "INTERCEPT_INFO"
    intercept_supplementary_info_parameter.Description = ("Information about the test on intercept of " +
                                                          "g1_image versus readout distance.")
    intercept_supplementary_info_parameter.StringValue = (extra_intercept_message +
                                                          f"intercept = {intercept}\n" +
                                                          f"intercept_err = {intercept_err}\n" +
                                                          f"intercept_z = {intercept_z}\n" +
                                                          f"Maximum allowed intercept_z = " +
                                                          f"{constants.intercept_fail_sigma}\n" +
                                                          f"Result: {intercept_result}\n")


def report_bad_data(requirement_object,
                    slope=slope,
                    slope_err=slope_err,
                    intercept=intercept,
                    intercept_err=intercept_err,):

    # Calculate slope_z and intercept_z - one or both might be NaN, but try anyway in case we get something
    slope_z = np.abs(slope / slope_err)
    intercept_z = np.abs(intercept / intercept_err)

    # Report -1 as the measured value for this test
    requirement_object.MeasuredValue.Parameter = -1

    intercept_pass = intercept_z < constants.intercept_fail_sigma

    # Report the result as failed
    slope_result = "FAILED"
    requirement_object.ValidationResult = slope_result

    # Also record whether or not the intercept test passed
    if intercept_pass:
        intercept_result = "PASSED"
    else:
        intercept_result = "FAILED"

    requirement_object.Comment = "WARNING: Multiple notes; see SupplementaryInformation."

    # Add a supplementary info key for each of the slope and intercept, reporting details

    add_supplementary_info(requirement_object,
                           slope=slope,
                           slope_err=slope_err,
                           slope_z=slope_z,
                           slope_result=slope_result,
                           intercept=intercept,
                           intercept_err=intercept_err,
                           intercept_result=intercept_result,
                           extra_slope_message="Test failed due to NaN regression results for slope.\n",
                           extra_intercept_message="")

    return


def report_zero_slope_err(requirement_object,
                          slope: float,
                          intercept: float,
                          intercept_err: float,):

    # Calculate slope_z and intercept_z - one or both might be NaN, but try anyway in case we get something
    slope_err = 0
    slope_z = np.inf
    intercept_z = np.abs(intercept / intercept_err)

    # Report -2 as the measured value for this test
    requirement_object.MeasuredValue.Parameter = -2

    intercept_pass = intercept_z < constants.intercept_fail_sigma

    # Report the result as failed
    slope_result = "FAILED"
    requirement_object.ValidationResult = slope_result

    # Also record whether or not the intercept test passed
    if intercept_pass:
        intercept_result = "PASSED"
    else:
        intercept_result = "FAILED"

    requirement_object.Comment = "WARNING: Multiple notes; see SupplementaryInformation."

    # Add a supplementary info key for each of the slope and intercept, reporting details

    add_supplementary_info(requirement_object,
                           slope=slope,
                           slope_err=slope_err,
                           slope_z=slope_z,
                           slope_result=slope_result,
                           intercept=intercept,
                           intercept_err=intercept_err,
                           intercept_result=intercept_result,
                           extra_slope_message="Test failed due to zero slope error.\n",
                           extra_intercept_message="")

    return


def report_good_data(requirement_object,
                     slope=slope,
                     slope_err=slope_err,
                     intercept=intercept,
                     intercept_err=intercept_err,):

    # Calculate if it passes or fails
    slope_z = np.abs(slope / slope_err)
    intercept_z = np.abs(intercept / intercept_err)

    # Report the slope_z as the measured value for this test
    requirement_object.MeasuredValue.Parameter = slope_z

    slope_pass = slope_z < constants.slope_fail_sigma
    intercept_pass = intercept_z < constants.intercept_fail_sigma

    # Report the result based on whether or not the slope passed.
    if slope_pass:
        slope_result = "PASSED"
    else:
        slope_result = "FAILED"
    requirement_object.ValidationResult = slope_result

    # Also record whether or not the intercept test passed
    if intercept_pass:
        intercept_result = "PASSED"
    else:
        intercept_result = "FAILED"

    # If the slope passes but the intercept doesn't, we should raise a warning
    if slope_pass and not intercept_pass:
        comment_level = "WARNING"
    else:
        comment_level = "INFO"

    requirement_object.Comment = f"{comment_level}: Multiple notes; see SupplementaryInformation."

    # Add a supplementary info key for each of the slope and intercept, reporting details

    add_supplementary_info(requirement_object,
                           slope=slope,
                           slope_err=slope_err,
                           slope_z=slope_z,
                           slope_result=slope_result,
                           intercept=intercept,
                           intercept_err=intercept_err,
                           intercept_result=intercept_result,
                           extra_slope_message="",
                           extra_intercept_message="")

    return


def fill_cti_gal_validation_results(test_result_product: dpdSheValidationTestResults,
                                    regression_results_row: table.Row,
                                    method_data_exists: bool = True):
    """ Interprets the results in the regression_results_row and other provided data to fill out the provided
        test_result_product with the results of this validation test.
    """

    # The results of this each test will be stored in an item of the ValidationTestList.
    # We'll iterate over the methods and test cases and fill in each in turn

    test_case_index = 0

    for method in constants.methods:
        for test_case in constants.cti_gal_test_cases:
            test_object = test_result_product.Data.ValidationTestList[test_case_index]

            # Fill in metadata about the test
            test_object.TestId = constants.cti_gal_test_id
            test_object.TestDescription = constants.cti_gal_test_description

            requirement_object = test_object.ValidatedRequirements.Requirement[0]

            requirement_object.Id = constants.cti_gal_requirement_id

            requirement_object.MeasuredValue.Parameter = constants.cti_gal_parameter

            if test_case == "Global" and method_data_exists:
                # Get the required info for this test
                slope = regression_results_row[getattr(rr_tf, f"slope_{method}")]
                slope_err = regression_results_row[getattr(rr_tf, f"slope_err_{method}")]
                intercept = regression_results_row[getattr(rr_tf, f"intercept_{method}")]
                intercept_err = regression_results_row[getattr(rr_tf, f"intercept_err_{method}")]

                # Check for data quality issues
                if (np.isnan([slope, slope_err]).any() or np.isinf([slope, slope_err]).any()):
                    report_bad_data(requirement_object,
                                    slope=slope,
                                    slope_err=slope_err,
                                    intercept=intercept,
                                    intercept_err=intercept_err,)
                elif slope_err == 0.:
                    report_zero_slope(requirement_object,
                                      slope=slope,
                                      slope_err=slope_err,
                                      intercept=intercept,
                                      intercept_err=intercept_err,)
                else:
                    report_good_data(requirement_object,
                                     slope=slope,
                                     slope_err=slope_err,
                                     intercept=intercept,
                                     intercept_err=intercept_err,)

            elif test_case == "Global" and not method_data_exists:
                # Report that the test wasn't run due to a lack of data
                report_test_not_run(requirement_object,
                                    reason="No data is available for this test.")

            else:
                # Report that the test wasn't run due to it not yet being implemented
                report_test_not_run(requirement_object,
                                    reason="This test has not yet been implemented.")

            test_object.GlobalResult = requirement_object.ValidationResult

            test_case_index += 1

    return
