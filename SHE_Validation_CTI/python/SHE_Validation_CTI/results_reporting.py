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

            requirement_object = test_object.ValidatedRequirements[0]

            requirement_object.Id = constants.cti_gal_requirement_id

            requirement_object.MeasuredValue.Parameter = constants.cti_gal_parameter

            if test_case == "Global" and method_data_exists:
                # Get the required info for this test
                slope = regression_results_row[get_attr(rr_tf, f"slope_{method}")]
                slope_err = regression_results_row[get_attr(rr_tf, f"slope_err_{method}")]
                intercept = regression_results_row[get_attr(rr_tf, f"intercept_{method}")]
                intercept_err = regression_results_row[get_attr(rr_tf, f"intercept_err_{method}")]

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

                slope_supplementary_info_parameter = requirement_object.SupplementaryInformation.Parameter[0]
                intercept_supplementary_info_parameter = deepcopy(slope_supplementary_info_parameter)
                requirement_object.SupplementaryInformation.Parameter[0].append(intercept_supplementary_info_parameter)

                slope_supplementary_info_parameter.Key = "SLOPE_INFO"
                slope_supplementary_info_parameter.Description = ("Information about the test on slope of g1_image " +
                                                                  "versus readout distance.")
                slope_supplementary_info_parameter.StringValue = (f"slope = {slope}" +
                                                                  f"slope_err = {slope_err}" +
                                                                  f"slope_z = {slope_z}" +
                                                                  f"Result: {slope_result}")

                intercept_supplementary_info_parameter.Key = "INTERCEPT_INFO"
                intercept_supplementary_info_parameter.Description = ("Information about the test on intercept of " +
                                                                      "g1_image versus readout distance.")
                intercept_supplementary_info_parameter.StringValue = (f"intercept = {intercept}" +
                                                                      f"intercept_err = {intercept_err}" +
                                                                      f"intercept_z = {intercept_z}" +
                                                                      f"Result: {intercept_result}")

                # Report the results of the global test for this method
                requirement_object.MeasuredValue.Parameter = slope_z
                requirement_object.ValidationResult = "PASSED"

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
