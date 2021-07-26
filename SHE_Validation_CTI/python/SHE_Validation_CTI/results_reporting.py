""" @file results_reporting.py

    Created 17 December 2020

    Utility functions for CTI-Gal validation, for reporting results.
"""

__updated__ = "2021-07-15"

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
from typing import Dict, List,  Any, Callable, Tuple, Union

from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import ValidationConfigKeys
from astropy import table
import scipy.stats

from SHE_Validation.results_writer import (SupplementaryInfo, RequirementWriter, AnalysisWriter,
                                           TestCaseWriter, ValidationResultsWriter, RESULT_PASS, RESULT_FAIL,
                                           WARNING_MULTIPLE, MSG_NOT_IMPLEMENTED, MSG_NO_DATA)
from SHE_Validation.test_info import TestCaseInfo
from SHE_Validation_CTI.constants.cti_gal_test_info import NUM_METHOD_CTI_GAL_TEST_CASES
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
import numpy as np

from .constants.cti_gal_default_config import FailSigmaScaling
from .constants.cti_gal_test_info import (CTI_GAL_REQUIREMENT_INFO,
                                          CtiGalTestCases,
                                          D_CTI_GAL_TEST_CASE_INFO)
from .table_formats.regression_results import TF as RR_TF

logger = getLogger(__name__)

# Define constants for various messages

KEY_SLOPE_INFO = "SLOPE_INFO"
KEY_INTERCEPT_INFO = "INTERCEPT_INFO"

DESC_SLOPE_INFO = "Information about the test on slope of g1_image versus readout distance."
DESC_INTERCEPT_INFO = "Information about the test on intercept of g1_image versus readout distance."

MSG_NAN_SLOPE = "Test failed due to NaN regression results for slope."
MSG_ZERO_SLOPE_ERR = "Test failed due to zero slope error."

CTI_GAL_DIRECTORY_FILENAME = "SheCtiGalResultsDirectory.txt"
CTI_GAL_DIRECTORY_HEADER = "### OU-SHE CTI-Gal Analysis Results File Directory ###"


class FailSigmaCalculator():
    """Class to calculate the fail sigma, scaling properly for number of bins and/or/nor test cases.
    """

    def __init__(self,
                 pipeline_config: Dict[str, str],
                 d_bin_limits: Dict[str, str]):

        self.slope_fail_sigma = pipeline_config[ValidationConfigKeys.VAL_SLOPE_FAIL_SIGMA.value]
        self.intercept_fail_sigma = pipeline_config[ValidationConfigKeys.VAL_INTERCEPT_FAIL_SIGMA.value]
        self.fail_sigma_scaling = pipeline_config[ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING.value]

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
            self._d_scaled_slope_sigma = self._calc_d_scaled_sigma(self.slope_fail_sigma)
        return self._d_scaled_slope_sigma

    @property
    def d_scaled_intercept_sigma(self):
        if self._d_scaled_intercept_sigma is None:
            self._d_scaled_intercept_sigma = self._calc_d_scaled_sigma(self.intercept_fail_sigma)
        return self._d_scaled_intercept_sigma

    def _calc_d_scaled_sigma(self, base_sigma: float) -> Dict[str, float]:

        d_scaled_sigma = {}

        for test_case in CtiGalTestCases:

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


class CtiGalRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single CTI-Gal requirement
    """

    def _get_slope_intercept_info(self,
                                  extra_slope_message: str = "",
                                  extra_intercept_message: str = "") -> Tuple[SupplementaryInfo, SupplementaryInfo]:

        # Check the extra messages and make sure they end in a linebreak
        if extra_slope_message != "" and extra_slope_message[-1:] != "\n":
            extra_slope_message = extra_slope_message + "\n"
        if extra_intercept_message != "" and extra_intercept_message[-1:] != "\n":
            extra_intercept_message = extra_intercept_message + "\n"

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

        slope_supplementary_info = SupplementaryInfo(key=KEY_SLOPE_INFO,
                                                     description=DESC_SLOPE_INFO,
                                                     message=messages["slope"])

        intercept_supplementary_info = SupplementaryInfo(key=KEY_INTERCEPT_INFO,
                                                         description=DESC_INTERCEPT_INFO,
                                                         message=messages["intercept"])

        return slope_supplementary_info, intercept_supplementary_info

    def report_bad_data(self):

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_slope_intercept_info(extra_slope_message=MSG_NAN_SLOPE)
        super().report_bad_data(l_supplementary_info)

    def report_zero_slope_err(self):

        # Report -2 as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = -2.0

        self.requirement_object.Comment = WARNING_MULTIPLE

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_slope_intercept_info(extra_slope_message=MSG_ZERO_SLOPE_ERR)
        self.add_supplementary_info(l_supplementary_info)

    def report_good_data(self,
                         measured_value: float):

        # If the slope passes but the intercept doesn't, we should raise a warning
        if self.slope_pass and not self.intercept_pass:
            warning = True
        else:
            warning = False

        # Add a supplementary info key for each of the slope and intercept, reporting details
        l_supplementary_info = self._get_slope_intercept_info()
        super().report_good_data(measured_value=measured_value,
                                 warning=warning,
                                 l_supplementary_info=l_supplementary_info)

    def _calc_test_results(self,
                           prop: str):
        """ Calculate the test results for either the slope or intercept.
        """

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
                    l_prop_z[bin_index] = np.abs(
                        getattr(self, f"l_{prop}")[bin_index] / getattr(self, f"l_{prop}_err")[bin_index])
                else:
                    l_prop_z[bin_index] = np.NaN
                l_prop_pass[bin_index] = l_prop_z[bin_index] < getattr(self, f"{prop}_fail_sigma")
                l_prop_good_data[bin_index] = True
            if l_prop_pass[bin_index]:
                l_prop_result[bin_index] = RESULT_PASS
            else:
                l_prop_result[bin_index] = RESULT_FAIL

        # Pass if there's at least some good data, and all good data passes
        if (np.all(np.logical_or(l_prop_pass, ~l_prop_good_data)) and not np.all(~l_prop_good_data)):
            setattr(self, f"{prop}_pass", True)
            setattr(self, f"{prop}_result", RESULT_PASS)
        else:
            setattr(self, f"{prop}_pass", False)
            setattr(self, f"{prop}_result", RESULT_FAIL)

    def write(self,
              report_method: Callable[[Any], None] = None,
              have_data: bool = False,
              l_slope: List[float] = None,
              l_slope_err: List[float] = None,
              l_intercept: List[float] = None,
              l_intercept_err: List[float] = None,
              l_bin_limits: List[float] = None,
              slope_fail_sigma: float = None,
              intercept_fail_sigma: float = None,
              report_kwargs: Dict[str, Any] = None) -> str:

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

        # Calculate test results for both the slope and intercept
        for prop in "slope", "intercept":
            self._calc_test_results(prop)

        # Report the result based on whether or not the slope passed.
        self.requirement_object.ValidationResult = self.slope_result
        self.requirement_object.MeasuredValue[0].Parameter = CTI_GAL_REQUIREMENT_INFO.parameter

        # Check for data quality issues and report as proper if found
        if np.all(self.l_slope_err == 0.):
            report_method = self.report_zero_slope_err
            extra_report_kwargs = {}
        elif np.logical_or.reduce((np.isnan(self.l_slope),
                                   np.isinf(self.l_slope),
                                   np.isnan(self.l_slope_err),
                                   np.isinf(self.l_slope_err),
                                   self.l_slope_err == 0.)).all():
            report_method = self.report_bad_data
            extra_report_kwargs = {}
        else:
            report_method = self.report_good_data

            # Report the maximum slope_z as the measured value for this test
            extra_report_kwargs = {"measured_value": np.nanmax(self.l_slope_z)}

        return super().write(result=self.slope_result,
                             report_method=report_method,
                             report_kwargs={**report_kwargs, **extra_report_kwargs},)


class CtiGalAnalysisWriter(AnalysisWriter):
    """ Subclass of AnalysisWriter, to handle some changes specific for this test.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(product_type="CTI-GAL-ANALYSIS-FILES",
                         *args, **kwargs)

    def _generate_directory_filename(self):
        """ Overriding method to generate a filename for a directory file.
        """
        self.directory_filename = CTI_GAL_DIRECTORY_FILENAME

    def _get_directory_header(self):
        """ Overriding method to get the desired header for a directory file.
        """
        return CTI_GAL_DIRECTORY_HEADER


class CtiGalTestCaseWriter(TestCaseWriter):

    def __init__(self,
                 parent_validation_writer: "CtiGalValidationResultsWriter",
                 test_case_object,
                 test_case_info: TestCaseInfo,
                 *args, **kwargs):
        """ We override __init__ since we'll be using a known set of requirement info.
        """

        super().__init__(parent_validation_writer,
                         test_case_object,
                         test_case_info,
                         l_requirement_info=CTI_GAL_REQUIREMENT_INFO,
                         *args, **kwargs)

    def _init_requirement_writer(self, **kwargs) -> CtiGalRequirementWriter:
        """ We override the _init_requirement_writer method to create a writer of the inherited type.
        """
        return CtiGalRequirementWriter(self, **kwargs)

    def _init_analysis_writer(self, **kwargs) -> CtiGalAnalysisWriter:
        """ We override the _init_analysis_writer method to create a writer of the inherited type.
        """
        return CtiGalAnalysisWriter(self, **kwargs)


class CtiGalValidationResultsWriter(ValidationResultsWriter):

    def __init__(self,
                 test_object: dpdSheValidationTestResults,
                 workdir: str,
                 regression_results_row_index: int,
                 d_regression_results_tables: Dict[str, List[table.Table]],
                 fail_sigma_calculator: FailSigmaCalculator,
                 d_bin_limits: Dict[str, np.ndarray],
                 method_data_exists: bool = True,
                 *args, **kwargs):

        super().__init__(test_object=test_object,
                         workdir=workdir,
                         num_test_cases=NUM_METHOD_CTI_GAL_TEST_CASES,
                         l_test_case_info=None, *args, **kwargs)

        self.regression_results_row_index = regression_results_row_index
        self.d_regression_results_tables = d_regression_results_tables
        self.fail_sigma_calculator = fail_sigma_calculator
        self.d_bin_limits = d_bin_limits
        self.method_data_exists = method_data_exists

    def _init_test_case_writer(self, **kwargs):
        """ Override _init_test_case_writer to create a CtiGalTestCaseWriter
        """
        return CtiGalTestCaseWriter(self, **kwargs)

    def _get_method_info(self,
                         method: str,
                         test_case: str,
                         l_test_case_bins: List[float],
                         l_test_case_regression_results_tables: List[table.Table]) -> Tuple[List[float],
                                                                                            List[float],
                                                                                            List[float],
                                                                                            List[float],
                                                                                            List[List[float]]]:
        """ Sort the data out from the tables for this method.
        """

        num_bins = len(l_test_case_bins) - 1

        l_slope = [None] * num_bins
        l_slope_err = [None] * num_bins
        l_intercept = [None] * num_bins
        l_intercept_err = [None] * num_bins
        l_bin_limits = [None] * num_bins

        for bin_index, bin_test_case_regression_results_table in enumerate(l_test_case_regression_results_tables):
            regression_results_row = bin_test_case_regression_results_table[self.regression_results_row_index]
            l_slope[bin_index] = regression_results_row[getattr(RR_TF, f"slope_{method}")]
            l_slope_err[bin_index] = regression_results_row[getattr(RR_TF, f"slope_err_{method}")]
            l_intercept[bin_index] = regression_results_row[getattr(RR_TF, f"intercept_{method}")]
            l_intercept_err[bin_index] = regression_results_row[getattr(RR_TF, f"intercept_err_{method}")]
            l_bin_limits[bin_index] = l_test_case_bins[bin_index:bin_index + 2]

        # For the global case, override the bin limits with None
        if test_case == CtiGalTestCases.GLOBAL:
            l_bin_limits = None

        return l_slope, l_slope_err, l_intercept, l_intercept_err, l_bin_limits

    def write_test_case_objects(self):
        """ Writes all data for each requirement subobject, modifying self._test_object.
        """
        # The results of this each test will be stored in an item of the ValidationTestList.
        # We'll iterate over the methods, test cases, and bins, and fill in each in turn

        test_case_index = 0

        for test_case in CtiGalTestCases:

            l_test_case_bins = self.d_bin_limits[test_case]

            slope_fail_sigma = self.fail_sigma_calculator.d_scaled_slope_sigma[test_case]
            intercept_fail_sigma = self.fail_sigma_calculator.d_scaled_intercept_sigma[test_case]

            l_test_case_regression_results_tables = self.d_regression_results_tables[test_case]

            for method in METHODS:

                test_case_writer = self.l_test_case_writers[test_case_index]

                # Use a modified test case info object to describe this test, clarifying it's
                # just for this method
                test_case_info = deepcopy(D_CTI_GAL_TEST_CASE_INFO[test_case])
                test_case_info._test_case_id = test_case_info.id + "-" + method

                test_case_writer._test_case_info = test_case_info

                # Fill in metadata about the test

                requirement_writer = test_case_writer.l_requirement_writers[0]

                if self.method_data_exists and test_case != CtiGalTestCases.EPOCH:

                    (l_slope,
                     l_slope_err,
                     l_intercept,
                     l_intercept_err,
                     l_bin_limits) = self._get_method_info(method,
                                                           test_case,
                                                           l_test_case_bins,
                                                           l_test_case_regression_results_tables)

                    report_method = None
                    report_kwargs = {}
                    write_kwargs = {"have_data": True,
                                    "l_slope": l_slope,
                                    "l_slope_err": l_slope_err,
                                    "l_intercept": l_intercept,
                                    "l_intercept_err": l_intercept_err,
                                    "l_bin_limits": l_bin_limits,
                                    "slope_fail_sigma": slope_fail_sigma,
                                    "intercept_fail_sigma": intercept_fail_sigma}

                elif test_case == CtiGalTestCases.EPOCH:
                    # Report that the test wasn't run due to it not yet being implemented
                    report_method = requirement_writer.report_test_not_run
                    report_kwargs = {"reason": MSG_NOT_IMPLEMENTED}
                    write_kwargs = {}
                else:
                    # Report that the test wasn't run due to a lack of data
                    report_method = requirement_writer.report_test_not_run
                    report_kwargs = {"reason": MSG_NO_DATA}
                    write_kwargs = {}

                write_kwargs["report_method"] = report_method
                write_kwargs["report_kwargs"] = report_kwargs

                test_case_writer.write(requirements_kwargs=write_kwargs,)

                test_case_index += 1


def fill_cti_gal_validation_results(test_result_product: dpdSheValidationTestResults,
                                    regression_results_row_index: int,
                                    d_regression_results_tables: Dict[str, List[table.Table]],
                                    pipeline_config: Dict[str, Any],
                                    d_bin_limits: Dict[str, np.ndarray],
                                    workdir: str,
                                    figures: Union[Dict[str, Union[Dict[str, str], List[str]]],
                                                   List[Union[Dict[str, str], List[str]]], ] = None,
                                    method_data_exists: bool = True):
    """ Interprets the results in the regression_results_row and other provided data to fill out the provided
        test_result_product with the results of this validation test.
    """

    # Set up a calculator object for scaled fail sigmas
    fail_sigma_calculator = FailSigmaCalculator(pipeline_config=pipeline_config,
                                                d_bin_limits=d_bin_limits)

    # Initialize a test results writer
    test_results_writer = CtiGalValidationResultsWriter(test_object=test_result_product,
                                                        workdir=workdir,
                                                        regression_results_row_index=regression_results_row_index,
                                                        d_regression_results_tables=d_regression_results_tables,
                                                        fail_sigma_calculator=fail_sigma_calculator,
                                                        d_bin_limits=d_bin_limits,
                                                        method_data_exists=method_data_exists,
                                                        figures=figures)

    test_results_writer.write()
