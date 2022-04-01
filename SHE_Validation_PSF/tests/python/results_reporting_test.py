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
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.config_utility import get_d_l_bin_limits
from SHE_Validation.results_writer import INFO_MULTIPLE, RESULT_FAIL, RESULT_PASS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.constants.psf_res_test_info import L_PSF_RES_TEST_CASE_INFO, NUM_PSF_RES_TEST_CASES
from SHE_Validation_PSF.results_reporting import PsfResValidationResultsWriter

logger = getLogger(__name__)

P_TOT = 0.06
P_SNR_0 = 0.94
P_SNR_1 = 0.03


class TestCtiResultsReporting(SheTestCase):
    """ Test case for CTI validation results reporting.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def post_setup(self):
        # Make a pipeline_config using the default values
        self.pipeline_config = self.mock_pipeline_config_factory.pipeline_config
        base_snr_bin_limits = self.pipeline_config[ValidationConfigKeys.VAL_SNR_BIN_LIMITS]
        self.pipeline_config[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] = np.append(base_snr_bin_limits, 2.5)

        # Make a dictionary of bin limits
        self.d_l_bin_limits = get_d_l_bin_limits(self.pipeline_config)

        # Make a mock star cataolog product
        mock_starcat_table_gen = MockStarCatTableGenerator(workdir = self.workdir)
        mock_starcat_table_gen.write_mock_product()
        self.mock_starcat_product = read_xml_product(mock_starcat_table_gen.product_filename, workdir = self.workdir, )

        # Make a dict of mock test results
        self.d_l_test_results = {L_PSF_RES_TEST_CASE_INFO[0].name: [KstestResult(np.nan, P_TOT)],
                                 L_PSF_RES_TEST_CASE_INFO[1].name: [KstestResult(np.nan, P_SNR_0),
                                                                    KstestResult(np.nan, P_SNR_1),
                                                                    KstestResult(np.nan, np.nan)]}

    @pytest.fixture(scope = 'class')
    def test_result_product(self, class_setup):
        test_result_product = create_dpd_she_validation_test_results(reference_product = self.mock_starcat_product,
                                                                     num_tests = NUM_PSF_RES_TEST_CASES)
        test_results_writer = PsfResValidationResultsWriter(test_object = test_result_product,
                                                            workdir = self.workdir,
                                                            d_l_bin_limits = self.d_l_bin_limits,
                                                            d_l_test_results = self.d_l_test_results, )

        test_results_writer.write()

        return test_result_product

    def test_meta(self, test_result_product):
        """ Test that results can be written to a product without any errors, and test case metadata in it is correct.
        """

        # Write the product

        # Check that the results are as expected
        test_result_product.validateBinding()

        # Check metadata for all test cases
        for test_case_index, test_case_info in enumerate(L_PSF_RES_TEST_CASE_INFO):

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
