""" @file sb_results_reporting_test.py

    Created 17 December 2020

    Unit tests of the Shear Bias results_reporting.py module
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

import os
from typing import NamedTuple

import numpy as np
import pytest

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements
from SHE_PPT.pipeline_utility import ValidationConfigKeys, read_config
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS_STR, ExecutionMode, FailSigmaScaling
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.results_writer import (INFO_MULTIPLE, RESULT_FAIL, RESULT_PASS, )
from SHE_Validation.test_info_utility import find_test_case_info
from SHE_Validation_ShearBias.constants.shear_bias_default_config import (D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                                                          D_SHEAR_BIAS_CONFIG_TYPES, )
from SHE_Validation_ShearBias.constants.shear_bias_test_info import (L_SHEAR_BIAS_TEST_CASE_C_INFO,
                                                                     L_SHEAR_BIAS_TEST_CASE_INFO,
                                                                     L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                     NUM_SHEAR_BIAS_TEST_CASES,
                                                                     SHEAR_BIAS_C_REQUIREMENT_INFO,
                                                                     SHEAR_BIAS_M_REQUIREMENT_INFO, ShearBiasTestCases,
                                                                     get_prop_from_id, )
from SHE_Validation_ShearBias.results_reporting import (D_DESC_INFO, KEY_G1_INFO, KEY_G2_INFO,
                                                        REPORT_DIGITS, fill_shear_bias_test_results, )

logger = getLogger(__name__)


class TestCase:
    """
    """

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir):

        self.workdir = tmpdir.strpath
        os.makedirs(os.path.join(self.workdir, "data"))

        # Make a pipeline_config using the default values
        self.pipeline_config = read_config(None,
                                           workdir = self.workdir,
                                           defaults = D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                           config_keys = ValidationConfigKeys,
                                           d_types = D_SHEAR_BIAS_CONFIG_TYPES)

        self.pipeline_config[ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING] = FailSigmaScaling.NONE

        # Make a dictionary of bin limits
        self.d_bin_limits = {}
        for test_case_info in L_SHEAR_BIAS_TEST_CASE_M_INFO:
            bins_config_key = test_case_info.bins_config_key
            if bins_config_key is None:
                bin_limits_string = DEFAULT_BIN_LIMITS_STR
            else:
                bin_limits_string = D_SHEAR_BIAS_CONFIG_DEFAULTS[bins_config_key]

            bin_limits_list = list(map(float, bin_limits_string.strip().split()))
            bin_limits_array = np.array(bin_limits_list, dtype = float)

            self.d_bin_limits[test_case_info.bins] = bin_limits_array

    def test_fill_sb_val_results(self):
        """ Test of the fill_shear_bias_test_results function.
        """

        class RegResults(NamedTuple):
            slope: float
            slope_err: float
            intercept: float
            intercept_err: float
            slope_intercept_covar: float

        lmc_global_m_test_case_info: TestCaseInfo = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                        ShearEstimationMethods.LENSMC,
                                                                        BinParameters.GLOBAL, return_one = True)
        lmc_global_m_name: str = lmc_global_m_test_case_info.name

        lmc_global_c_test_case_info: TestCaseInfo = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_C_INFO,
                                                                        ShearEstimationMethods.LENSMC,
                                                                        BinParameters.GLOBAL, return_one = True)
        lmc_global_c_name: str = lmc_global_c_test_case_info.name

        # Fill the bias measurements with mock data
        d_bias_measurements = {}

        d_bias_measurements[lmc_global_m_name] = {1: BiasMeasurements(RegResults(1.1, 0.03, 0.002, 0.0003, 0)),
                                                  2: BiasMeasurements(RegResults(0.9, 0.01, -0.002, 0.0004, 0))}
        d_bias_measurements[lmc_global_c_name] = d_bias_measurements[lmc_global_m_name]

        # Set up the output data product
        sb_test_results_product = products.she_validation_test_results.create_validation_test_results_product(
            num_tests = NUM_SHEAR_BIAS_TEST_CASES)

        fill_shear_bias_test_results(test_result_product = sb_test_results_product,
                                     workdir = self.workdir,
                                     d_bin_limits = self.d_bin_limits,
                                     d_bias_measurements = d_bias_measurements,
                                     pipeline_config = self.pipeline_config,
                                     dl_l_figures = None,
                                     method_data_exists = True,
                                     mode = ExecutionMode.LOCAL)

        # Check the results are as expected. Only check for LensMC-Global here

        # Figure out the index for LensMC Global test results and save it for each check
        test_case_index = 0
        for test_case_info in L_SHEAR_BIAS_TEST_CASE_INFO:
            if (test_case_info.method == ShearEstimationMethods.LENSMC and
                    test_case_info.bins == BinParameters.GLOBAL):
                if get_prop_from_id(test_case_info.id) == ShearBiasTestCases.M:
                    lensmc_global_m_test_case_index = test_case_index
                elif get_prop_from_id(test_case_info.id) == ShearBiasTestCases.C:
                    lensmc_global_c_test_case_index = test_case_index
            test_case_index += 1

        sb_m_test_result = sb_test_results_product.Data.ValidationTestList[lensmc_global_m_test_case_index]
        sb_c_test_result = sb_test_results_product.Data.ValidationTestList[lensmc_global_c_test_case_index]

        # Do detailed checks on the m and c test results

        # M
        assert sb_m_test_result.GlobalResult == RESULT_FAIL

        requirement_object = sb_m_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Parameter == SHEAR_BIAS_M_REQUIREMENT_INFO.parameter
        assert np.isclose(requirement_object.MeasuredValue[0].Value.FloatValue, (0.1 - 0.0001) / 0.01)
        assert requirement_object.ValidationResult == RESULT_FAIL

        sb_info = requirement_object.SupplementaryInformation

        assert sb_info.Parameter[0].Key == KEY_G1_INFO
        assert sb_info.Parameter[0].Description == D_DESC_INFO["m1"]
        m1_info_string = sb_info.Parameter[0].StringValue
        assert f"m1 = {0.1:.{REPORT_DIGITS}f}\n" in m1_info_string
        assert f"m1_err = {0.03:.{REPORT_DIGITS}f}\n" in m1_info_string
        assert f"m1_z = {(0.1 - 0.0001) / 0.03:.{REPORT_DIGITS}f}\n" in m1_info_string
        assert (f"Maximum allowed m_z = " +
                f"{self.pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA]:.{REPORT_DIGITS}f}\n"
                in m1_info_string)
        assert f"Result: {RESULT_PASS}\n" in m1_info_string

        assert sb_info.Parameter[1].Key == KEY_G2_INFO
        assert sb_info.Parameter[1].Description == D_DESC_INFO["m2"]
        m2_info_string = sb_info.Parameter[1].StringValue
        assert f"m2 = {-0.1:.{REPORT_DIGITS}f}\n" in m2_info_string
        assert f"m2_err = {0.01:.{REPORT_DIGITS}f}\n" in m2_info_string
        assert f"m2_z = {(0.1 - 0.0001) / 0.01:.{REPORT_DIGITS}f}\n" in m2_info_string
        assert (f"Maximum allowed m_z = " +
                f"{self.pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA]:.{REPORT_DIGITS}f}\n"
                in m2_info_string)
        assert f"Result: {RESULT_FAIL}\n" in m2_info_string

        # C
        assert sb_c_test_result.GlobalResult == RESULT_FAIL

        requirement_object = sb_c_test_result.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Parameter == SHEAR_BIAS_C_REQUIREMENT_INFO.parameter
        assert np.isclose(requirement_object.MeasuredValue[0].Value.FloatValue, (0.002 - 0.000005) / 0.0003)
        assert requirement_object.ValidationResult == RESULT_FAIL

        sb_info = requirement_object.SupplementaryInformation

        assert sb_info.Parameter[0].Key == KEY_G1_INFO
        assert sb_info.Parameter[0].Description == D_DESC_INFO["c1"]
        c1_info_string = sb_info.Parameter[0].StringValue
        assert f"c1 = {0.002:.{REPORT_DIGITS}f}\n" in c1_info_string
        assert f"c1_err = {0.0003:.{REPORT_DIGITS}f}\n" in c1_info_string
        assert f"c1_z = {(0.002 - 0.000005) / 0.0003:.{REPORT_DIGITS}f}\n" in c1_info_string
        assert (f"Maximum allowed c_z = " +
                f"{self.pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA]:.{REPORT_DIGITS}f}\n"
                in c1_info_string)
        assert f"Result: {RESULT_FAIL}\n" in c1_info_string

        assert sb_info.Parameter[1].Key == KEY_G2_INFO
        assert sb_info.Parameter[1].Description == D_DESC_INFO["c2"]
        c2_info_string = sb_info.Parameter[1].StringValue
        assert f"c2 = {-0.002:.{REPORT_DIGITS}f}\n" in c2_info_string
        assert f"c2_err = {0.0004:.{REPORT_DIGITS}f}\n" in c2_info_string
        assert f"c2_z = {(0.002 - 0.000005) / 0.0004:.{REPORT_DIGITS}f}\n" in c2_info_string
        assert (f"Maximum allowed c_z = " +
                f"{self.pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA]:.{REPORT_DIGITS}f}\n"
                in c2_info_string)
        assert f"Result: {RESULT_PASS}\n" in c2_info_string
