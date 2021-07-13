""" @file results_reporting_test.py

    Created 17 December 2020

    Unit tests of the results_reporting.py module
"""

__updated__ = "2021-07-13"

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

from collections import namedtuple
from copy import deepcopy
import os

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import _make_config_from_defaults
import pytest

from SHE_Validation.results_writer import (RESULT_PASS, RESULT_FAIL, COMMENT_LEVEL_INFO,
                                           COMMENT_LEVEL_WARNING, COMMENT_MULTIPLE,
                                           INFO_MULTIPLE, WARNING_TEST_NOT_RUN, WARNING_MULTIPLE,
                                           KEY_REASON, DESC_NOT_RUN_REASON, MSG_NO_DATA, MSG_NOT_IMPLEMENTED,
                                           WARNING_BAD_DATA,)
from SHE_Validation_CTI import constants
from SHE_Validation_CTI.constants.cti_gal_default_config import (AnalysisConfigKeys, CTI_GAL_DEFAULT_CONFIG,
                                                                 FAILSAFE_BIN_LIMITS, FailSigmaScaling)
from SHE_Validation_CTI.constants.cti_gal_test_info import (CtiGalTestCases,
                                                            CTI_GAL_REQUIREMENT_INFO, D_CTI_GAL_TEST_CASE_INFO,
                                                            NUM_CTI_GAL_TEST_CASES, NUM_METHOD_CTI_GAL_TEST_CASES)
from SHE_Validation_CTI.results_reporting import (fill_cti_gal_validation_results,
                                                  KEY_SLOPE_INFO, KEY_INTERCEPT_INFO,
                                                  DESC_SLOPE_INFO, DESC_INTERCEPT_INFO,
                                                  MSG_NAN_SLOPE, MSG_ZERO_SLOPE_ERR,
                                                  FailSigmaCalculator)
from SHE_Validation_CTI.table_formats.regression_results import TF as RR_TF, initialise_regression_results_table
import numpy as np


class TestCase:
    """


    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):

        self.workdir = tmpdir.strpath
        os.makedirs(os.path.join(self.workdir, "data"))

        # Make a pipeline_config using the default values
        self.pipeline_config = _make_config_from_defaults(config_keys=AnalysisConfigKeys,
                                                          defaults=CTI_GAL_DEFAULT_CONFIG)
        self.pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value] = FailSigmaScaling.NO_SCALE.value

        # Make a dictionary of bin limits
        self.d_bin_limits = {}
        for test_case in CtiGalTestCases:
            bins_config_key = D_CTI_GAL_TEST_CASE_INFO[test_case].bins_config_key
            if bins_config_key is None:
                bin_limits_string = FAILSAFE_BIN_LIMITS
            else:
                bin_limits_string = CTI_GAL_DEFAULT_CONFIG[bins_config_key]

            bin_limits_list = list(map(float, bin_limits_string.strip().split()))
            bin_limits_array = np.array(bin_limits_list, dtype=float)

            self.d_bin_limits[test_case] = bin_limits_array

    def test_fail_sigma_scaling(self):

        base_slope_fail_sigma = self.pipeline_config[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value]
        base_intercept_fail_sigma = self.pipeline_config[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value]

        # Make a copy of the pipeline config so we can test with different input
        test_pipeline_config = deepcopy(self.pipeline_config)

        # Test with no scaling - all sigma should be unchanged
        test_pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value] = FailSigmaScaling.NO_SCALE.value
        ns_fail_sigma_calculator = FailSigmaCalculator(pipeline_config=test_pipeline_config,
                                                       d_bin_limits=self.d_bin_limits)

        for test_case in CtiGalTestCases:
            assert np.isclose(ns_fail_sigma_calculator.d_scaled_slope_sigma[test_case], base_slope_fail_sigma)
            assert np.isclose(ns_fail_sigma_calculator.d_scaled_intercept_sigma[test_case], base_intercept_fail_sigma)

        # Test with other scaling types, and check that the fail sigmas increase with number of tries

        test_pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value] = FailSigmaScaling.BIN_SCALE.value
        bin_fail_sigma_calculator = FailSigmaCalculator(pipeline_config=test_pipeline_config,
                                                        d_bin_limits=self.d_bin_limits)
        test_pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value] = FailSigmaScaling.TEST_CASE_SCALE.value
        tc_fail_sigma_calculator = FailSigmaCalculator(pipeline_config=test_pipeline_config,
                                                       d_bin_limits=self.d_bin_limits)
        test_pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value] = FailSigmaScaling.TEST_CASE_BINS_SCALE.value
        tcb_fail_sigma_calculator = FailSigmaCalculator(pipeline_config=test_pipeline_config,
                                                        d_bin_limits=self.d_bin_limits)

        first_tc_slope_fail_sigma = None
        first_tc_intercept_fail_sigma = None
        first_tcb_slope_fail_sigma = None
        first_tcb_intercept_fail_sigma = None

        for test_case in CtiGalTestCases:

            # Check that they increase with increasing number of bins

            assert bin_fail_sigma_calculator.d_scaled_slope_sigma[test_case] >= base_slope_fail_sigma
            assert bin_fail_sigma_calculator.d_scaled_intercept_sigma[test_case] >= base_intercept_fail_sigma

            assert tc_fail_sigma_calculator.d_scaled_slope_sigma[test_case] > base_slope_fail_sigma
            assert tc_fail_sigma_calculator.d_scaled_intercept_sigma[test_case] > base_intercept_fail_sigma

            assert (tcb_fail_sigma_calculator.d_scaled_slope_sigma[test_case] >
                    bin_fail_sigma_calculator.d_scaled_slope_sigma[test_case])
            assert (tcb_fail_sigma_calculator.d_scaled_intercept_sigma[test_case] >
                    bin_fail_sigma_calculator.d_scaled_intercept_sigma[test_case])

            assert (tcb_fail_sigma_calculator.d_scaled_slope_sigma[test_case] >
                    tc_fail_sigma_calculator.d_scaled_slope_sigma[test_case])
            assert (tcb_fail_sigma_calculator.d_scaled_intercept_sigma[test_case] >
                    tc_fail_sigma_calculator.d_scaled_intercept_sigma[test_case])

            # Check that all test_cases and test_case_bins fail sigma are equal between test cases
            if first_tc_slope_fail_sigma is None:
                first_tc_slope_fail_sigma = tc_fail_sigma_calculator.d_scaled_slope_sigma[test_case]
                first_tc_intercept_fail_sigma = tc_fail_sigma_calculator.d_scaled_intercept_sigma[test_case]
                first_tcb_slope_fail_sigma = tcb_fail_sigma_calculator.d_scaled_slope_sigma[test_case]
                first_tcb_intercept_fail_sigma = tcb_fail_sigma_calculator.d_scaled_intercept_sigma[test_case]
            else:
                assert np.isclose(tc_fail_sigma_calculator.d_scaled_slope_sigma[test_case],
                                  first_tc_slope_fail_sigma)
                assert np.isclose(tc_fail_sigma_calculator.d_scaled_intercept_sigma[test_case],
                                  first_tc_intercept_fail_sigma)
                assert np.isclose(tcb_fail_sigma_calculator.d_scaled_slope_sigma[test_case],
                                  first_tcb_slope_fail_sigma)
                assert np.isclose(tcb_fail_sigma_calculator.d_scaled_intercept_sigma[test_case],
                                  first_tcb_intercept_fail_sigma)

        return

    def test_fill_cti_gal_validation_results(self):
        """ Test of the fill_cti_gal_validation_results function.
        """

        RegResults = namedtuple("RegResults", ["slope", "slope_err",
                                               "intercept", "intercept_err", ])

        exp_results_list = [RegResults(3., 2., 0., 2.),
                            RegResults(-15, 2., 0., 2.),
                            RegResults(3., 2., 44., 5.),
                            RegResults(-15., 2., 44., 5.),
                            RegResults(-15., 0., 44., 0.),
                            RegResults(np.NaN, np.NaN, np.NaN, np.NaN), ]

        num_exposures = len(exp_results_list)
        exp_product_list = [None] * num_exposures

        # Set up mock input data and fill the products for each set of possible results
        base_exp_results_table = initialise_regression_results_table(product_type="EXP", size=len(exp_results_list))

        d_exp_results_tables = {}
        for test_case in CtiGalTestCases:
            num_bins = len(self.d_bin_limits[test_case]) - 1
            d_exp_results_tables[test_case] = [None] * num_bins
            for bin_index in range(num_bins):
                exp_results_table = deepcopy(base_exp_results_table)
                d_exp_results_tables[test_case][bin_index] = exp_results_table

                # Set up data for each test case
                for exp_index, exp_results in enumerate(exp_results_list):
                    exp_row = exp_results_table[exp_index]
                    # To test handling of empty bins, set bin_index 2 to NaN, otherwise normal data
                    if bin_index == 2:
                        exp_row[RR_TF.slope_LensMC] = np.NaN
                        exp_row[RR_TF.slope_err_LensMC] = np.NaN
                        exp_row[RR_TF.intercept_LensMC] = np.NaN
                        exp_row[RR_TF.intercept_err_LensMC] = np.NaN
                    else:
                        exp_row[RR_TF.slope_LensMC] = exp_results.slope
                        exp_row[RR_TF.slope_err_LensMC] = exp_results.slope_err
                        exp_row[RR_TF.intercept_LensMC] = exp_results.intercept
                        exp_row[RR_TF.intercept_err_LensMC] = exp_results.intercept_err

        # Set up the exposure output data products
        for exp_index, exp_results in enumerate(exp_results_list):
            exp_product = products.she_validation_test_results.create_validation_test_results_product(
                num_tests=NUM_METHOD_CTI_GAL_TEST_CASES)

            fill_cti_gal_validation_results(test_result_product=exp_product,
                                            regression_results_row_index=exp_index,
                                            d_regression_results_tables=d_exp_results_tables,
                                            pipeline_config=self.pipeline_config,
                                            d_bin_limits=self.d_bin_limits,
                                            workdir=self.workdir,
                                            method_data_exists=True)

            exp_product_list[exp_index] = exp_product

        # Check the results for each exposure are as expected. Only check for LensMC-Global here

        # Figure out the index for LensMC Global and Colour test results and save it for each check
        test_case_index = 0
        for test_case in CtiGalTestCases:
            for method in METHODS:
                if method == "LensMC":
                    if test_case == CtiGalTestCases.GLOBAL:
                        lensmc_global_test_case_index = test_case_index
                    elif test_case == CtiGalTestCases.COLOUR:
                        lensmc_colour_test_case_index = test_case_index

                test_case_index += 1

        # Exposure 0 Global - slope pass and intercept pass. Do most detailed checks here
        exp_test_result = exp_product_list[0].Data.ValidationTestList[lensmc_global_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_PASS

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Parameter == CTI_GAL_REQUIREMENT_INFO.parameter
        assert requirement_object.MeasuredValue[0].Value.FloatValue == 3. / 2.
        assert requirement_object.ValidationResult == RESULT_PASS

        exp_info = requirement_object.SupplementaryInformation

        assert exp_info.Parameter[0].Key == KEY_SLOPE_INFO
        assert exp_info.Parameter[0].Description == DESC_SLOPE_INFO
        exp_slope_info_string = exp_info.Parameter[0].StringValue
        assert f"slope = {3.}\n" in exp_slope_info_string
        assert f"slope_err = {2.}\n" in exp_slope_info_string
        assert f"slope_z = {3. / 2.}\n" in exp_slope_info_string
        assert (f"Maximum allowed slope_z = " +
                f"{CTI_GAL_DEFAULT_CONFIG[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value]}\n"
                in exp_slope_info_string)
        assert f"Result: {RESULT_PASS}\n" in exp_slope_info_string

        assert exp_info.Parameter[1].Key == KEY_INTERCEPT_INFO
        assert exp_info.Parameter[1].Description == DESC_INTERCEPT_INFO
        exp_intercept_info_string = exp_info.Parameter[1].StringValue
        assert f"intercept = {0.}\n" in exp_intercept_info_string
        assert f"intercept_err = {2.}\n" in exp_intercept_info_string
        assert f"intercept_z = {0. / 2.}\n" in exp_intercept_info_string
        assert ("Maximum allowed intercept_z = " +
                f"{CTI_GAL_DEFAULT_CONFIG[AnalysisConfigKeys.CGV_INTERCEPT_FAIL_SIGMA.value]}\n"
                in exp_intercept_info_string)
        assert f"Result: {RESULT_PASS}\n" in exp_intercept_info_string

        # Exposure 0 Colour - slope pass and intercept pass for all bins except index 2
        exp_test_result = exp_product_list[0].Data.ValidationTestList[lensmc_colour_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_PASS

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.ValidationResult == RESULT_PASS

        exp_info = requirement_object.SupplementaryInformation
        exp_slope_info_string = exp_info.Parameter[0].StringValue

        # Check for good bin data
        assert f"slope = {3.}\n" in exp_slope_info_string
        assert f"slope_err = {2.}\n" in exp_slope_info_string
        assert f"slope_z = {3. / 2.}\n" in exp_slope_info_string
        assert (f"Maximum allowed slope_z = " +
                f"{CTI_GAL_DEFAULT_CONFIG[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value]}\n"
                in exp_slope_info_string)
        assert f"Result: {RESULT_PASS}\n" in exp_slope_info_string

        # Check for bad bin data
        assert f"slope = nan\n" in exp_slope_info_string
        assert f"slope_err = nan\n" in exp_slope_info_string
        assert f"slope_z = nan\n" in exp_slope_info_string
        assert (f"Maximum allowed slope_z = " +
                f"{CTI_GAL_DEFAULT_CONFIG[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value]}\n"
                in exp_slope_info_string)
        assert f"Result: {RESULT_FAIL}\n" in exp_slope_info_string

        # Exposure 1 - slope fail and intercept pass
        exp_test_result = exp_product_list[1].Data.ValidationTestList[lensmc_global_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_FAIL

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Value.FloatValue == 15. / 2.
        assert requirement_object.ValidationResult == RESULT_FAIL

        # Exposure 2 - slope pass and intercept fail
        exp_test_result = exp_product_list[2].Data.ValidationTestList[lensmc_global_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_PASS

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == WARNING_MULTIPLE
        assert requirement_object.MeasuredValue[0].Value.FloatValue == 3. / 2.
        assert requirement_object.ValidationResult == RESULT_PASS

        # Exposure 3 - slope fail and intercept fail
        exp_test_result = exp_product_list[3].Data.ValidationTestList[lensmc_global_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_FAIL

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Value.FloatValue == 15. / 2.
        assert requirement_object.ValidationResult == RESULT_FAIL

        # Exposure 4 - zero slope_err and zero intercept_err
        exp_test_result = exp_product_list[4].Data.ValidationTestList[lensmc_global_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_FAIL

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == WARNING_MULTIPLE
        assert requirement_object.MeasuredValue[0].Value.FloatValue == -2.0
        assert requirement_object.ValidationResult == RESULT_FAIL

        exp_slope_info_string = requirement_object.SupplementaryInformation.Parameter[0].StringValue
        assert MSG_ZERO_SLOPE_ERR in exp_slope_info_string

        # Exposure 5 - NaN data
        exp_test_result = exp_product_list[5].Data.ValidationTestList[lensmc_global_test_case_index]
        assert exp_test_result.GlobalResult == RESULT_FAIL

        requirement_object = exp_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == WARNING_BAD_DATA
        assert requirement_object.MeasuredValue[0].Value.FloatValue == -1.0
        assert requirement_object.ValidationResult == RESULT_FAIL

        exp_slope_info_string = requirement_object.SupplementaryInformation.Parameter[0].StringValue
        assert MSG_NAN_SLOPE in exp_slope_info_string

        # With the observation, test saying we have no data
        obs_results_table = initialise_regression_results_table(product_type="OBS", size=1)

        obs_product = products.she_validation_test_results.create_validation_test_results_product(
            num_tests=NUM_METHOD_CTI_GAL_TEST_CASES)

        d_obs_results_tables = {}
        for test_case in CtiGalTestCases:
            num_bins = len(self.d_bin_limits[test_case]) - 1
            d_obs_results_tables[test_case] = [obs_results_table] * num_bins

        fill_cti_gal_validation_results(test_result_product=obs_product,
                                        regression_results_row_index=exp_index,
                                        d_regression_results_tables=d_obs_results_tables,
                                        pipeline_config=self.pipeline_config,
                                        d_bin_limits=self.d_bin_limits,
                                        workdir=self.workdir,
                                        method_data_exists=False)

        # Check that the product validates its binding
        obs_product.validateBinding()

        # Check metadata for all test cases
        test_case_index = 0
        for test_case in CtiGalTestCases:
            for method in METHODS:
                obs_test_result = obs_product.Data.ValidationTestList[test_case_index]
                assert D_CTI_GAL_TEST_CASE_INFO[test_case].id in obs_test_result.TestId
                assert method in obs_test_result.TestId
                assert obs_test_result.TestDescription == D_CTI_GAL_TEST_CASE_INFO[test_case].description

                # Check that the product indeed reports no data
                assert obs_test_result.GlobalResult == RESULT_PASS
                assert obs_test_result.ValidatedRequirements.Requirement[0].Comment == WARNING_TEST_NOT_RUN
                obs_info = obs_test_result.ValidatedRequirements.Requirement[0].SupplementaryInformation
                assert obs_info.Parameter[0].Key == KEY_REASON
                assert obs_info.Parameter[0].Description == DESC_NOT_RUN_REASON
                if test_case == CtiGalTestCases.EPOCH:
                    assert obs_info.Parameter[0].StringValue == MSG_NOT_IMPLEMENTED
                else:
                    assert obs_info.Parameter[0].StringValue == MSG_NO_DATA

                test_case_index += 1
