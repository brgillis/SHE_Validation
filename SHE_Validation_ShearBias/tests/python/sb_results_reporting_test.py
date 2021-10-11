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
from typing import Dict, List, NamedTuple, Optional

import numpy as np
import pytest

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, DEFAULT_C_TARGET, DEFAULT_M_TARGET
from SHE_PPT.pipeline_utility import ValidationConfigKeys
from SHE_Validation.constants.default_config import ExecutionMode, FailSigmaScaling
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.results_writer import (INFO_MULTIPLE, RESULT_FAIL, RESULT_PASS, )
from SHE_Validation.test_info_utility import find_test_case_info
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_ShearBias.constants.shear_bias_test_info import (L_SHEAR_BIAS_TEST_CASE_C_INFO,
                                                                     L_SHEAR_BIAS_TEST_CASE_INFO,
                                                                     L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                     NUM_SHEAR_BIAS_TEST_CASES,
                                                                     SHEAR_BIAS_M_REQUIREMENT_INFO, ShearBiasTestCases,
                                                                     get_prop_from_id, )
from SHE_Validation_ShearBias.results_reporting import (D_DESC_INFO, KEY_G1_INFO, KEY_G2_INFO,
                                                        REPORT_DIGITS, fill_shear_bias_test_results, )
from SHE_Validation_ShearBias.testing.mock_shear_bias_data import INPUT_BIAS, TEST_BIN_PARAMETERS, TEST_METHODS

logger = getLogger(__name__)


class TestCase:
    """
    """

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir):

        self.workdir = tmpdir.strpath
        os.makedirs(os.path.join(self.workdir, "data"))

        # Make a pipeline_config using the default values
        mock_pipeline_config_factory = MockValPipelineConfigFactory(workdir = self.workdir)
        self.pipeline_config = mock_pipeline_config_factory.pipeline_config

        self.pipeline_config[ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING] = FailSigmaScaling.NONE
        self.pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA] = 5.

        # Get a dictionary of bin limits
        self.d_bin_limits = mock_pipeline_config_factory.d_l_bin_limits

    def test_fill_sb_val_results(self):
        """ Test of the fill_shear_bias_test_results function.
        """

        # Convenience shortened constants
        LMC = ShearEstimationMethods.LENSMC
        KSB = ShearEstimationMethods.KSB
        GBL = BinParameters.GLOBAL
        SNR = BinParameters.SNR

        class RegResults(NamedTuple):
            slope: float
            slope_err: float
            intercept: float
            intercept_err: float
            slope_intercept_covar: float

        # Fill the bias measurements with mock data
        d_l_d_bias_measurements: Dict[str, List[Dict[int, BiasMeasurements]]] = {}

        for method in TEST_METHODS:
            for bin_parameter in TEST_BIN_PARAMETERS:
                m_test_case_info: TestCaseInfo = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                     method,
                                                                     bin_parameter,
                                                                     return_one = True)
                m_name = m_test_case_info.name
                c_test_case_info: TestCaseInfo = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_C_INFO,
                                                                     method,
                                                                     bin_parameter,
                                                                     return_one = True)
                c_name = c_test_case_info.name

                if not bin_parameter in INPUT_BIAS[method]:
                    continue
                l_d_input_bias = INPUT_BIAS[method][bin_parameter]
                num_bins = len(l_d_input_bias)

                l_d_bias_measurements: List[Optional[Dict[int, BiasMeasurements]]] = [None] * num_bins

                for bin_index in range(num_bins):
                    d_input_bias = l_d_input_bias[bin_index]
                    d_bias_measurements = {}
                    for component_index in (1, 2):
                        d_bias_measurements[component_index] = BiasMeasurements(m = d_input_bias[f"m{component_index}"],
                                                                                m_err = d_input_bias[
                                                                                    f"m{component_index}_err"],
                                                                                c = d_input_bias[f"c{component_index}"],
                                                                                c_err = d_input_bias[
                                                                                    f"c{component_index}_err"],
                                                                                )
                        l_d_bias_measurements[bin_index] = d_bias_measurements

                    d_l_d_bias_measurements[m_name] = l_d_bias_measurements
                    d_l_d_bias_measurements[c_name] = l_d_bias_measurements

        # Set up the output data product
        sb_test_results_product = products.she_validation_test_results.create_validation_test_results_product(
            num_tests = NUM_SHEAR_BIAS_TEST_CASES)

        fill_shear_bias_test_results(test_result_product = sb_test_results_product,
                                     d_l_d_bias_measurements = d_l_d_bias_measurements,
                                     pipeline_config = self.pipeline_config,
                                     d_l_bin_limits = self.d_bin_limits,
                                     workdir = self.workdir,
                                     dl_dl_plot_filenames = None,
                                     method_data_exists = True,
                                     mode = ExecutionMode.LOCAL)

        # Check the results are as expected. Only check for LensMC-Global here

        # Figure out the index for LensMC Global test results and save it for each check
        test_case_index = 0
        lensmc_global_m_test_case_index = -1
        lensmc_global_c_test_case_index = -1
        ksb_snr_m_test_case_index = -1
        ksb_snr_c_test_case_index = -1
        for test_case_info in L_SHEAR_BIAS_TEST_CASE_INFO:
            if (test_case_info.method == LMC and test_case_info.bins == GBL):
                if get_prop_from_id(test_case_info.id) == ShearBiasTestCases.M:
                    lensmc_global_m_test_case_index = test_case_index
                elif get_prop_from_id(test_case_info.id) == ShearBiasTestCases.C:
                    lensmc_global_c_test_case_index = test_case_index
            elif (test_case_info.method == KSB and test_case_info.bins == SNR):
                if get_prop_from_id(test_case_info.id) == ShearBiasTestCases.M:
                    ksb_snr_m_test_case_index = test_case_index
                elif get_prop_from_id(test_case_info.id) == ShearBiasTestCases.C:
                    ksb_snr_c_test_case_index = test_case_index
            test_case_index += 1

        # Make sure we've found the test cases
        assert lensmc_global_m_test_case_index >= 0
        assert lensmc_global_c_test_case_index >= 0
        assert ksb_snr_m_test_case_index >= 0
        assert ksb_snr_c_test_case_index >= 0
        lmc_sb_c_test_result = sb_test_results_product.Data.ValidationTestList[lensmc_global_c_test_case_index]
        ksb_sb_m_test_result = sb_test_results_product.Data.ValidationTestList[ksb_snr_m_test_case_index]
        ksb_sb_c_test_result = sb_test_results_product.Data.ValidationTestList[ksb_snr_c_test_case_index]

        # Do detailed checks on the m and c test results

        # M

        lmc_sb_m_test_result = sb_test_results_product.Data.ValidationTestList[lensmc_global_m_test_case_index]

        d_ex_result = {"m1": RESULT_PASS,
                       "m2": RESULT_FAIL,
                       "c1": RESULT_FAIL,
                       "c2": RESULT_PASS, }
        d_info_keys = {"m1": KEY_G1_INFO,
                       "m2": KEY_G2_INFO,
                       "c1": KEY_G1_INFO,
                       "c2": KEY_G2_INFO, }
        method = LMC
        bins = GBL

        for comp, test_result, ex_global_result, target in (("m", lmc_sb_m_test_result, RESULT_FAIL, DEFAULT_M_TARGET),
                                                            ("c", lmc_sb_c_test_result, RESULT_FAIL, DEFAULT_C_TARGET),
                                                            ):
            self._check_results_string(method = method,
                                       bins = bins,
                                       comp = comp,
                                       target_val = target,
                                       test_result_object = test_result,
                                       ex_global_result = ex_global_result,
                                       d_ex_results = d_ex_result,
                                       d_ex_info_keys = d_info_keys, )

    def _check_results_string(self, method, bins, comp, target_val, test_result_object, ex_global_result, d_ex_results,
                              d_ex_info_keys):

        assert test_result_object.GlobalResult == ex_global_result

        d_bias = {}

        for index in (1, 2):
            d_bias[f'{comp}{index}'] = INPUT_BIAS[method][bins][0][f"{comp}{index}"]
            d_bias[f'{comp}{index}_err'] = INPUT_BIAS[method][bins][0][f"{comp}{index}_err"]
            d_bias[f'{comp}{index}_z'] = ((abs(d_bias[f'{comp}{index}']) - target_val) /
                                          d_bias[f'{comp}{index}_err'])

            requirement_object = test_result_object.ValidatedRequirements.Requirement[0]
            assert requirement_object.Comment == INFO_MULTIPLE
            # TODO - fix parameter
            assert requirement_object.MeasuredValue[0].Parameter == SHEAR_BIAS_M_REQUIREMENT_INFO.parameter
            assert requirement_object.ValidationResult == RESULT_FAIL

            sb_info = requirement_object.SupplementaryInformation

            assert sb_info.Parameter[index - 1].Key == d_ex_info_keys[f"{comp}{index}"]
            assert sb_info.Parameter[index - 1].Description == D_DESC_INFO[f"{comp}{index}"]
            info_string = sb_info.Parameter[index - 1].StringValue

            assert f"{comp}{index} = {d_bias[f'{comp}{index}']:.{REPORT_DIGITS}f}\n" in info_string
            assert f"{comp}{index}_err = {d_bias[f'{comp}{index}_err']:.{REPORT_DIGITS}f}\n" in info_string
            assert f"{comp}{index}_z = {d_bias[f'{comp}{index}_z']:.{REPORT_DIGITS}f}\n" in info_string
            assert (f"Maximum allowed m_z = " +
                    f"{self.pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA]:.{REPORT_DIGITS}f}\n"
                    in info_string)
            assert f"Result: {d_ex_results[f'{comp}{index}']}\n" in info_string

        assert np.isclose(requirement_object.MeasuredValue[0].Value.FloatValue,
                          max(d_bias[f'{comp}1_z'], d_bias[f'{comp}2_z']))
