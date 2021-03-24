""" @file results_reporting.py

    Created 17 December 2020

    Utility functions for CTI-Gal validation, for reporting results.
"""

__updated__ = "2021-03-24"

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
from typing import Dict, Any, List

from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import AnalysisConfigKeys
from astropy import table
import scipy.stats

from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
import numpy as np

from .constants.cti_gal_default_config import FailSigmaScaling
from .constants.cti_gal_test_info import (CTI_GAL_REQUIREMENT_INFO,
                                          CTI_GAL_TEST_CASES, CtiGalTestCases,
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


class FailSigmaCalculator():
    """Class to calculate the fail sigma, scaling properly for number of bins and/or/nor test cases.
    """

    def __init__(self,
                 pipeline_config: Dict[str, str],
                 d_bin_limits: Dict[str, str]):

        self.slope_fail_sigma = pipeline_config[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value]
        self.intercept_fail_sigma = pipeline_config[AnalysisConfigKeys.CGV_INTERCEPT_FAIL_SIGMA.value]
        self.fail_sigma_scaling = pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value]

        self.num_test_cases = len(d_bin_limits)
        self.d_num_bins = {}
        self.num_test_case_bins = 0
        for test_case in d_bin_limits:
            self.d_num_bins[test_case] = len(d_bin_limits[test_case]) - 1
            self.num_test_case_bins += self.d_num_bins[test_case]

        self._d_scaled_slope_sigma = None
        self._d_scaled_intercept_sigma = None

    @property
    def d_scaled_slope_sigma(self):
        if self._d_scaled_slope_sigma is None:
            self._d_scaled_slope_sigma = self._calculate_d_scaled_sigma(self.slope_fail_sigma)
        return self._d_scaled_slope_sigma

    @property
    def d_scaled_intercept_sigma(self):
        if self._d_scaled_intercept_sigma is None:
            self._d_scaled_intercept_sigma = self._calculate_d_scaled_sigma(self.intercept_fail_sigma)
        return self._d_scaled_intercept_sigma

    def _calculate_d_scaled_sigma(self, base_sigma: float):

        d_scaled_sigma = {}

        for test_case in self.d_num_bins:

            # Get the number of tries depending on scaling type
            if self.fail_sigma_scaling == FailSigmaScaling.NO_SCALE.value:
                num_tries = 1
            elif self.fail_sigma_scaling == FailSigmaScaling.BIN_SCALE.value:
                num_tries = self.d_num_bins[test_case]
            elif self.fail_sigma_scaling == FailSigmaScaling.TEST_CASE_SCALE.value:
                num_tries = self.num_test_cases
            elif self.fail_sigma_scaling == FailSigmaScaling.TEST_CASE_BINS_SCALE.value:
                num_tries = self.num_test_case_bins
            else:
                raise ValueError("Unexpected fail sigma scaling: " + self.fail_sigma_scaling)

            d_scaled_sigma[test_case] = self._calculate_scaled_sigma_from_tries(base_sigma=base_sigma,
                                                                                num_tries=num_tries)

        return d_scaled_sigma

    @classmethod
    def _calculate_scaled_sigma_from_tries(cls,
                                           base_sigma: float,
                                           num_tries: int):
        # To avoid numeric error, don't calculate if num_tries==1
        if num_tries == 1:
            return base_sigma

        p_good = (1 - 2 * scipy.stats.norm.cdf(-base_sigma))
        return -scipy.stats.norm.ppf((1 - p_good**(1 / num_tries)) / 2)


def report_test_not_run(requirement_object,
                        reason="Unspecified reason."):
    """ Fills in the data model with the fact that a test was not run and the reason.
    """

    requirement_object.MeasuredValue[0].Parameter = WARNING_TEST_NOT_RUN
    requirement_object.ValidationResult = RESULT_PASS
    requirement_object.Comment = WARNING_TEST_NOT_RUN

    supplementary_info_parameter = requirement_object.SupplementaryInformation.Parameter[0]
    supplementary_info_parameter.Key = KEY_REASON
    supplementary_info_parameter.Description = DESC_REASON
    supplementary_info_parameter.StringValue = reason


class CTIGalRequirementWriter():
    """ Class for managing reporting of results for a single CTI-Gal test case.
    """

    def __init__(self,
                 requirement_object,
                 l_slope: List[float],
                 l_slope_err: List[float],
                 l_intercept: List[float],
                 l_intercept_err: List[float],
                 l_bin_limits: List[float],
                 slope_fail_sigma: float,
                 intercept_fail_sigma: float):

        self.requirement_object = requirement_object
        self.l_slope = np.array(l_slope)
        self.l_slope_err = np.array(l_slope_err)
        self.l_intercept = np.array(l_intercept)
        self.l_intercept_err = np.array(l_intercept_err)
        if l_bin_limits is None:
            self.l_bin_limits = None
        else:
            self.l_bin_limits = np.array(l_bin_limits)
        self.slope_fail_sigma = slope_fail_sigma
        self.intercept_fail_sigma = intercept_fail_sigma

        self.num_bins = len(l_slope)

        # Calculate some values for both the slope and intercept
        for prop in "slope", "intercept":

            # Init each z, pass, and result as empy lists

            l_prop_z = np.empty(self.num_bins, dtype=float)
            setattr(self, f"l_{prop}_z", l_prop_z)

            l_prop_pass = np.empty(self.num_bins, dtype=bool)
            setattr(self, f"l_{prop}_pass", l_prop_pass)

            l_prop_result = np.empty(self.num_bins, dtype='<U' + str(np.max([len(RESULT_PASS), len(RESULT_FAIL)])))
            setattr(self, f"l_{prop}_result", l_prop_result)

            l_prop_good_data = np.empty(self.num_bins, dtype=bool)

            for bin_index in range(self.num_bins):
                if (np.isnan(getattr(self, f"l_{prop}")[bin_index]) or
                        np.isnan(getattr(self, f"l_{prop}_err")[bin_index])):
                    l_prop_z[bin_index] = np.NaN
                    l_prop_pass[bin_index] = False
                    l_prop_good_data[bin_index] = False
                else:
                    if getattr(self, f"l_{prop}_err")[bin_index] != 0.:
                        l_prop_z[bin_index] = np.abs(getattr(self, f"l_{prop}")[bin_index] /
                                                     getattr(self, f"l_{prop}_err")[bin_index])
                    else:
                        l_prop_z[bin_index] = np.NaN
                    l_prop_pass[bin_index] = l_prop_z[bin_index] < getattr(self, f"{prop}_fail_sigma")
                    l_prop_good_data[bin_index] = True

                if l_prop_pass[bin_index]:
                    l_prop_result[bin_index] = RESULT_PASS
                else:
                    l_prop_result[bin_index] = RESULT_FAIL

            # Pass if there's at least some good data, and all good data passes
            if (np.all(np.logical_or(l_prop_pass, ~l_prop_good_data)) and
                    not np.all(~l_prop_good_data)):
                setattr(self, f"{prop}_pass", True)
                setattr(self, f"{prop}_result", RESULT_PASS)
            else:
                setattr(self, f"{prop}_pass", False)
                setattr(self, f"{prop}_result", RESULT_FAIL)

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

        # Set up result messages for each bin, for both the slope and intercept
        messages = {"slope": extra_slope_message + "\n",
                    "intercept": extra_intercept_message + "\n"}
        for prop in messages:
            for bin_index in range(self.num_bins):

                if self.l_bin_limits is not None:
                    messages[prop] += (f"bin_min = {self.l_bin_limits[bin_index][0]}\n" +
                                       f"bin_max = {self.l_bin_limits[bin_index][1]}\n")

                messages[prop] += (f"{prop} = {getattr(self,f'l_{prop}')[bin_index]}\n" +
                                   f"{prop}_err = {getattr(self,f'l_{prop}_err')[bin_index]}\n" +
                                   f"{prop}_z = {getattr(self,f'l_{prop}_z')[bin_index]}\n" +
                                   f"Maximum allowed {prop}_z = {getattr(self,f'{prop}_fail_sigma')}\n" +
                                   f"Result: {getattr(self,f'l_{prop}_result')[bin_index]}\n\n")

        slope_supplementary_info_parameter.Key = KEY_SLOPE_INFO
        slope_supplementary_info_parameter.Description = DESC_SLOPE_INFO
        slope_supplementary_info_parameter.StringValue = messages["slope"]

        intercept_supplementary_info_parameter.Key = KEY_INTERCEPT_INFO
        intercept_supplementary_info_parameter.Description = DESC_INTERCEPT_INFO
        intercept_supplementary_info_parameter.StringValue = messages["intercept"]

    def report_bad_data(self):

        # Report -1 as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = -1.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details
        self.add_supplementary_info(extra_slope_message=MSG_NAN_SLOPE)

    def report_zero_slope_err(self):

        # Report -2 as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = -2.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details

        self.add_supplementary_info(extra_slope_message=MSG_ZERO_SLOPE_ERR,)

    def report_good_data(self):

        # Report the maximum slope_z as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = np.nanmax(self.l_slope_z)

        # If the slope passes but the intercept doesn't, we should raise a warning
        if self.slope_pass and not self.intercept_pass:
            comment_level = COMMENT_LEVEL_WARNING
        else:
            comment_level = COMMENT_LEVEL_INFO

        self.requirement_object.Comment = f"{comment_level}: " + COMMENT_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details

        self.add_supplementary_info()

    def report_data(self):

        # Report the result based on whether or not the slope passed.
        self.requirement_object.ValidationResult = self.slope_result
        self.requirement_object.MeasuredValue[0].Parameter = CTI_GAL_REQUIREMENT_INFO.parameter

        # Check for data quality issues and report as proper if found
        if np.all(self.l_slope_err == 0.):
            self.report_zero_slope_err()
        elif np.logical_or.reduce((np.isnan(self.l_slope),
                                   np.isinf(self.l_slope),
                                   np.isnan(self.l_slope_err),
                                   np.isinf(self.l_slope_err),
                                   self.l_slope_err == 0.)).all():
            self.report_bad_data()
        else:
            self.report_good_data()


def fill_cti_gal_validation_results(test_result_product: dpdSheValidationTestResults,
                                    regression_results_row_index: int,
                                    d_regression_results_tables: Dict[str, List[table.Table]],
                                    pipeline_config: Dict[str, Any],
                                    d_bin_limits: Dict[str, np.ndarray],
                                    method_data_exists: bool = True):
    """ Interprets the results in the regression_results_row and other provided data to fill out the provided
        test_result_product with the results of this validation test.
    """

    # Set up a calculator object for scaled fail sigmas
    fail_sigma_calculator = FailSigmaCalculator(pipeline_config=pipeline_config,
                                                d_bin_limits=d_bin_limits)

    # The results of this each test will be stored in an item of the ValidationTestList.
    # We'll iterate over the methods, test cases, and bins, and fill in each in turn

    test_case_index = 0

    for method in METHODS:
        for test_case in CTI_GAL_TEST_CASES:

            l_test_case_bins = d_bin_limits[test_case]
            num_bins = len(l_test_case_bins) - 1

            slope_fail_sigma = fail_sigma_calculator.d_scaled_slope_sigma[test_case]
            intercept_fail_sigma = fail_sigma_calculator.d_scaled_intercept_sigma[test_case]

            test_object = test_result_product.Data.ValidationTestList[test_case_index]

            l_test_case_regression_results_tables = d_regression_results_tables[test_case]

            # Fill in metadata about the test
            test_object.TestId = D_CTI_GAL_TEST_CASE_INFO[test_case].id + "-" + method
            test_object.TestDescription = D_CTI_GAL_TEST_CASE_INFO[test_case].description

            requirement_object = test_object.ValidatedRequirements.Requirement[0]

            requirement_object.Id = CTI_GAL_REQUIREMENT_INFO.id

            requirement_object.MeasuredValue[0].Parameter = CTI_GAL_REQUIREMENT_INFO.parameter

            if method_data_exists and test_case != CtiGalTestCases.EPOCH:

                # Sort the data out from the tables

                l_slope = [None] * num_bins
                l_slope_err = [None] * num_bins
                l_intercept = [None] * num_bins
                l_intercept_err = [None] * num_bins
                l_bin_limits = [None] * num_bins

                for (bin_index,
                     bin_test_case_regression_results_table) in enumerate(l_test_case_regression_results_tables):

                    regression_results_row = bin_test_case_regression_results_table[regression_results_row_index]

                    l_slope[bin_index] = regression_results_row[getattr(RR_TF, f"slope_{method}")]
                    l_slope_err[bin_index] = regression_results_row[getattr(RR_TF, f"slope_err_{method}")]
                    l_intercept[bin_index] = regression_results_row[getattr(RR_TF, f"intercept_{method}")]
                    l_intercept_err[bin_index] = regression_results_row[getattr(RR_TF, f"intercept_err_{method}")]
                    l_bin_limits[bin_index] = l_test_case_bins[bin_index:bin_index + 2]

                # For the global case, override the bin limits with None
                if test_case == CtiGalTestCases.GLOBAL:
                    l_bin_limits = None

                requirement_writer = CTIGalRequirementWriter(requirement_object,
                                                             l_slope=l_slope,
                                                             l_slope_err=l_slope_err,
                                                             l_intercept=l_intercept,
                                                             l_intercept_err=l_intercept_err,
                                                             l_bin_limits=l_bin_limits,
                                                             slope_fail_sigma=slope_fail_sigma,
                                                             intercept_fail_sigma=intercept_fail_sigma)

                requirement_writer.report_data()

            elif test_case == CtiGalTestCases.EPOCH:
                # Report that the test wasn't run due to it not yet being implemented
                report_test_not_run(requirement_object,
                                    reason=MSG_NOT_IMPLEMENTED)
            else:
                # Report that the test wasn't run due to a lack of data
                report_test_not_run(requirement_object,
                                    reason=MSG_NO_DATA)

            test_object.GlobalResult = requirement_object.ValidationResult

            test_case_index += 1
