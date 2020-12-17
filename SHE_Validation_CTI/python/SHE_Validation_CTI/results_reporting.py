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

from copy import deepcopy

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

    requirement_object.MeasuredValue.Parameter = "WARNING: Test not run."
    requirement_object.ValidationResult = "PASSED"
    requirement_object.Comment = "WARNING: Test not run."

    supplementary_info_parameter = requirement_object.SupplementaryInformation.Parameter[0]
    supplementary_info_parameter.Key = "REASON"
    supplementary_info_parameter.Description = "Why the test was not run."
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
                 intercept_err: float,):

        self.requirement_object = requirement_object
        self.slope = slope
        self.slope_err = slope_err
        self.intercept = intercept
        self.intercept_err = intercept_err

        # Calculate some values for both the slope and intercept
        for attr in ("slope", "intercept"):
            if np.isnan(getattr(self, attr)) or np.isnan(getattr(self, f"{attr}_err")):
                setattr(self, f"{attr}_z", np.NaN)
                setattr(self, f"{attr}_pass", False)
                setattr(self, f"{attr}_result", "FAILED")
            elif getattr(self, f"{attr}_err") == 0.:
                setattr(self, f"{attr}_z", np.NaN)
                setattr(self, f"{attr}_pass", False)
            else:
                setattr(self, f"{attr}_z", np.abs(getattr(self, attr) / getattr(self, f"{attr}_err")))
                setattr(self, f"{attr}_pass", getattr(self, f"{attr}_z") < constants.slope_fail_sigma)

            if getattr(self, f"{attr}_pass"):
                setattr(self, f"{attr}_result", "PASSED")
            else:
                setattr(self, f"{attr}_result", "FAILED")

        return

    def add_supplementary_info(self,
                               extra_slope_message: str ="",
                               extra_intercept_message: str =""):

        # Check the extra messages and make sure they end in a linebreak
        if extra_slope_message != "" and extra_slope_message[-2:] != "\n":
            extra_slope_message = extra_slope_message + "\n"
        if extra_intercept_message != "" and extra_intercept_message[-2:] != "\n":
            extra_intercept_message = extra_intercept_message + "\n"

        slope_supplementary_info_parameter = self.requirement_object.SupplementaryInformation.Parameter[0]
        intercept_supplementary_info_parameter = deepcopy(slope_supplementary_info_parameter)

        self.requirement_object.SupplementaryInformation.Parameter = [slope_supplementary_info_parameter,
                                                                      intercept_supplementary_info_parameter]

        slope_supplementary_info_parameter.Key = "self.slope_INFO"
        slope_supplementary_info_parameter.Description = ("Information about the test on self.slope of g1_image " +
                                                          "versus readout distance.")
        slope_supplementary_info_parameter.StringValue = (extra_slope_message +
                                                          f"self.slope = {self.slope}\n" +
                                                          f"self.slope_err = {self.slope_err}\n" +
                                                          f"self.slope_z = {self.slope_z}\n" +
                                                          f"Maximum allowed self.slope_z = {constants.slope_fail_sigma}\n" +
                                                          f"Result: {self.slope_result}\n")

        intercept_supplementary_info_parameter.Key = "self.intercept_INFO"
        intercept_supplementary_info_parameter.Description = ("Information about the test on self.intercept of " +
                                                              "g1_image versus readout distance.")
        intercept_supplementary_info_parameter.StringValue = (extra_intercept_message +
                                                              f"self.intercept = {self.intercept}\n" +
                                                              f"self.intercept_err = {self.intercept_err}\n" +
                                                              f"self.intercept_z = {self.intercept_z}\n" +
                                                              f"Maximum allowed self.intercept_z = " +
                                                              f"{constants.intercept_fail_sigma}\n" +
                                                              f"Result: {self.intercept_result}\n")

        return

    def report_bad_data(self):

        # Report -1 as the measured value for this test
        self.requirement_object.MeasuredValue.Parameter = "-1"

        self.requirement_object.Comment = "WARNING: Multiple notes; see SupplementaryInformation."

        # Add a supplementary info key for each of the self.slope and self.intercept, reporting details

        self.add_supplementary_info(extra_slope_message="Test failed due to NaN regression results for self.slope.\n")

        return

    def report_zero_slope_err(self):

        # Report -2 as the measured value for this test
        self.requirement_object.MeasuredValue.Parameter = "ERROR: Zero slope"

        self.requirement_object.Comment = "WARNING: Multiple notes; see SupplementaryInformation."

        # Add a supplementary info key for each of the self.slope and self.intercept, reporting details

        self.add_supplementary_info(extra_slope_message="Test failed due to zero self.slope error.\n",)

        return

    def report_good_data(self):

        # Report the self.slope_z as the measured value for this test
        self.requirement_object.MeasuredValue.Parameter = str(self.slope_z)

        # If the slope passes but the intercept doesn't, we should raise a warning
        if self.slope_pass and not self.intercept_pass:
            comment_level = "WARNING"
        else:
            comment_level = "INFO"

        self.requirement_object.Comment = f"{comment_level}: Multiple notes; see SupplementaryInformation."

        # Add a supplementary info key for each of the self.slope and self.intercept, reporting details

        self.add_supplementary_info()

        return

    def report_data(self):

        # Report the result based on whether or not the slope passed.
        self.requirement_object.ValidationResult = self.slope_result

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
            test_object.TestId = constants.cti_gal_test_case_info[test_case].id
            test_object.TestDescription = constants.cti_gal_test_case_info[test_case].description

            requirement_object = test_object.ValidatedRequirements.Requirement[0]

            requirement_object.Id = constants.cti_gal_requirement_id

            requirement_object.MeasuredValue.Parameter = constants.cti_gal_parameter

            if test_case == "Global" and method_data_exists:

                requirement_writer = CTIGalRequirementWriter(requirement_object,
                                                             slope=regression_results_row[getattr(
                                                                 rr_tf, f"slope_{method}")],
                                                             slope_err=regression_results_row[getattr(
                                                                 rr_tf, f"slope_err_{method}")],
                                                             intercept=regression_results_row[getattr(
                                                                 rr_tf, f"intercept_{method}")],
                                                             intercept_err=regression_results_row[getattr(
                                                                 rr_tf, f"intercept_err_{method}")])

                requirement_writer.report_data()

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
