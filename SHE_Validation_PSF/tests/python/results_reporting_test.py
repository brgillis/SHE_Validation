""" @file results_reporting_test.py

    Created 1 April 2022

    Unit tests of the results_reporting.py module
"""

__updated__ = "2022-04-01"

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

import numpy as np
import pytest
from scipy.stats.stats import KstestResult

from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_validation_test_results import create_dpd_she_validation_test_results
from SHE_PPT.testing.mock_she_star_cat import MockStarCatTableGenerator
from SHE_Validation.results_writer import INFO_MULTIPLE, RESULT_FAIL, RESULT_PASS, TargetType
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.constants.psf_res_sp_test_info import (L_PSF_RES_SP_TEST_CASE_INFO, NUM_PSF_RES_SP_TEST_CASES,
                                                               PSF_RES_SP_VAL_NAME, )
from SHE_Validation_PSF.results_reporting import PsfResValidationResultsWriter, STR_KS_STAT
from SHE_Validation_PSF.testing.utility import SheValPsfTestCase

logger = getLogger(__name__)

KSS_TOT = 0.1
KSS_SNR_0 = 0.5
KSS_SNR_1 = 0.8

P_TOT = 0.06
P_SNR_0 = 0.94
P_SNR_1 = 0.03

TEST_P_TARGET = 0.045


class TestCtiResultsReporting(SheValPsfTestCase):
    """ Test case for CTI validation results reporting.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def post_setup(self):
        # Set up the pipeline config for this test
        base_snr_bin_limits = self.pipeline_config[ValidationConfigKeys.VAL_SNR_BIN_LIMITS]
        self.pipeline_config[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] = np.append(base_snr_bin_limits, 2.5)

        # Get the dict of bin limits based on the updated pipeline config
        self.d_l_bin_limits = self.make_d_l_bin_limits()

        # Make a mock star cataolog product
        mock_starcat_table_gen = MockStarCatTableGenerator(workdir=self.workdir)
        mock_starcat_table_gen.write_mock_product()
        self.mock_starcat_product = read_xml_product(mock_starcat_table_gen.product_filename, workdir=self.workdir, )

        # Make a dict of mock test results
        self.d_l_test_results = {L_PSF_RES_SP_TEST_CASE_INFO[0].name: [KstestResult(KSS_TOT, P_TOT)],
                                 L_PSF_RES_SP_TEST_CASE_INFO[1].name: [KstestResult(KSS_SNR_0, P_SNR_0),
                                                                       KstestResult(KSS_SNR_1, P_SNR_1),
                                                                       KstestResult(np.nan, np.nan)]}

    @pytest.fixture(scope='class')
    def test_result_product(self, class_setup):
        test_result_product = create_dpd_she_validation_test_results(reference_product=self.mock_starcat_product,
                                                                     num_tests=NUM_PSF_RES_SP_TEST_CASES)
        test_results_writer = PsfResValidationResultsWriter(test_object=test_result_product,
                                                            workdir=self.workdir,
                                                            d_l_bin_limits=self.d_l_bin_limits,
                                                            d_l_test_results=self.d_l_test_results,
                                                            d_requirement_writer_kwargs={"p_fail": TEST_P_TARGET})

        test_results_writer.write()

        return test_result_product

    def test_meta(self, test_result_product):
        """ Test that results can be written to a product without any errors, and test case metadata in it is correct.
        """

        # Write the product

        # Check that the results are as expected
        test_result_product.validateBinding()

        # Check metadata for all test cases
        for test_case_index, test_case_info in enumerate(L_PSF_RES_SP_TEST_CASE_INFO):

            test_result = test_result_product.Data.ValidationTestList[test_case_index]

            assert test_case_info.id in test_result.TestId
            assert test_result.TestDescription == test_case_info.description

    def test_tot_results(self, test_result_product):
        """ Test that the filled results are as expected
        """

        # Exposure 1 - slope fail and intercept pass
        test_results = test_result_product.Data.ValidationTestList[0]
        assert test_results.GlobalResult == RESULT_PASS

        requirement_object = test_results.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Value.FloatValue == P_TOT
        assert requirement_object.ValidationResult == RESULT_PASS

        supp_info = requirement_object.SupplementaryInformation
        supp_info_string = supp_info.Parameter[0].StringValue

        # Check for specific data in supplementary info
        assert f"{STR_KS_STAT} = {KSS_TOT}\n" in supp_info_string
        assert f"{PSF_RES_SP_VAL_NAME} = {P_TOT}\n" in supp_info_string
        assert f"{PSF_RES_SP_VAL_NAME}_target ({TargetType.MIN.value}) = {TEST_P_TARGET}\n" in supp_info_string

    def test_snr_results(self, test_result_product):
        """ Test that the filled results are as expected
        """

        # Exposure 1 - slope fail and intercept pass
        test_results = test_result_product.Data.ValidationTestList[1]
        assert test_results.GlobalResult == RESULT_FAIL

        requirement_object = test_results.ValidatedRequirements.Requirement[0]
        assert requirement_object.Comment == INFO_MULTIPLE
        assert requirement_object.MeasuredValue[0].Value.FloatValue == P_SNR_1
        assert requirement_object.ValidationResult == RESULT_FAIL

        supp_info = requirement_object.SupplementaryInformation
        supp_info_string = supp_info.Parameter[0].StringValue

        # Check for specific data in supplementary info
        assert f"{STR_KS_STAT} = {KSS_SNR_0}\n" in supp_info_string
        assert f"{PSF_RES_SP_VAL_NAME} = {P_SNR_0}\n" in supp_info_string
        assert f"{STR_KS_STAT} = {KSS_SNR_1}\n" in supp_info_string
        assert f"{PSF_RES_SP_VAL_NAME} = {P_SNR_1}\n" in supp_info_string
        assert f"{PSF_RES_SP_VAL_NAME}_target ({TargetType.MIN.value}) = {TEST_P_TARGET}\n" in supp_info_string
