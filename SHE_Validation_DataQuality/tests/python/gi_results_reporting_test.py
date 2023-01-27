"""
:file: tests/python/gi_results_reporting_test.py

:date: 01/27/23
:author: Bryan Gillis

Tests of code to output test results to in-memory data product for GalInfo validation test
"""

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

from typing import Dict, List, Optional

import pytest

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.products.she_validation_test_results import create_dpd_she_validation_test_results
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.results_writer import INFO_MULTIPLE, RESULT_FAIL, RESULT_PASS
from SHE_Validation_DataQuality.constants.gal_info_test_info import (GAL_INFO_DATA_TEST_CASE_INFO,
                                                                     GAL_INFO_N_TEST_CASE_INFO,
                                                                     L_GAL_INFO_TEST_CASE_INFO,
                                                                     NUM_GAL_INFO_TEST_CASES, )
from SHE_Validation_DataQuality.gi_data_processing import (CHAINS_ATTR, GalInfoDataTestResults, GalInfoNTestResults,
                                                           GalInfoTestResults, MEAS_ATTR, MSG_F_OUT, MSG_MISSING_IDS,
                                                           MSG_N_IN,
                                                           MSG_N_OUT, MSG_ATTR_RESULT, STR_GLOBAL, )
from SHE_Validation_DataQuality.gi_results_reporting import GalInfoValidationResultsWriter
from SHE_Validation.constants.misc import MSG_NA

MSG_SHE_CAT = "ERROR: she_cat message"
MSG_P_SHE_CHAINS = "ERROR: p_she_chains message"

N_IN = 100

L_MISSING_MEAS = []
N_OUT_MEAS = N_IN - len(L_MISSING_MEAS)

L_MISSING_CHAINS = [4, 6]
N_OUT_CHAINS = N_IN - len(L_MISSING_CHAINS)

L_INVALID_MEAS = [2, 3]
N_INVALID_MEAS = len(L_INVALID_MEAS)

L_INVALID_CHAINS = [2, 3, 4]
N_INVALID_CHAINS = len(L_INVALID_CHAINS)

MEAS_CAPPED = MEAS_ATTR.capitalize()
CHAINS_CAPPED = CHAINS_ATTR.capitalize()


class TestGalInfoResultsReporting(SheTestCase):
    """Test case for GalInfo validation test results reporting
    """

    lensmc_n_id: Optional[str] = None
    lensmc_data_id: Optional[str] = None

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        self.d_l_test_results: Dict[str, List[GalInfoTestResults]] = {}

        for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method
            id_ = test_case_info.id

            if id_.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id):
                self.d_l_test_results[name] = [GalInfoNTestResults(n_in=N_IN,
                                                                   l_missing_ids_meas=L_MISSING_MEAS,
                                                                   l_missing_ids_chains=L_MISSING_CHAINS)]
                # Note the LensMC ID for later specific tests
                if method == ShearEstimationMethods.LENSMC:
                    self.lensmc_n_id = test_case_info.id
            elif id_.startswith(GAL_INFO_DATA_TEST_CASE_INFO.base_test_case_id):
                self.d_l_test_results[name] = [GalInfoDataTestResults(l_invalid_ids_meas=L_INVALID_MEAS,
                                                                      l_invalid_ids_chains=L_INVALID_CHAINS)]
                # Note the LensMC ID for later specific tests
                if method == ShearEstimationMethods.LENSMC:
                    self.lensmc_data_id = test_case_info.id

    @pytest.fixture(scope='class')
    def p_test_results(self, class_setup):
        test_result_product = create_dpd_she_validation_test_results(num_tests=NUM_GAL_INFO_TEST_CASES)
        test_results_writer = GalInfoValidationResultsWriter(test_object=test_result_product,
                                                             workdir=self.workdir,
                                                             d_l_test_results=self.d_l_test_results)
        test_results_writer.write()

        return test_result_product

    def test_meta(self, p_test_results):
        """ Test that results can be written to a product without any errors, and test case metadata in it is correct.
        """

        # Write the product

        # Check that the results are as expected
        p_test_results.validateBinding()

        # Check metadata for all test cases
        for test_case_index, test_case_info in enumerate(L_GAL_INFO_TEST_CASE_INFO):

            test_result = p_test_results.Data.ValidationTestList[test_case_index]

            assert test_case_info.id in test_result.TestId
            assert test_result.TestDescription == test_case_info.description

    def test_results(self, p_test_results):
        """ Test that the filled results are as expected
        """

        for test_results in p_test_results.Data.ValidationTestList:

            requirement_object = test_results.ValidatedRequirements.Requirement[0]

            supp_info = requirement_object.SupplementaryInformation
            supp_info_string: str = supp_info.Parameter[0].StringValue

            # Split check depending on which test case this is
            if test_results.TestId.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id):

                assert test_results.GlobalResult == RESULT_PASS
                assert requirement_object.Comment == INFO_MULTIPLE
                assert requirement_object.MeasuredValue[0].Value.FloatValue == 1.
                assert requirement_object.ValidationResult == RESULT_PASS

                assert supp_info_string.startswith(MSG_N_IN % (MEAS_CAPPED, N_IN))
                assert MSG_N_OUT % (MEAS_CAPPED, N_OUT_MEAS) in supp_info_string
                assert MSG_F_OUT % (MEAS_CAPPED, N_OUT_MEAS / N_IN) in supp_info_string
                assert MSG_MISSING_IDS % (MEAS_CAPPED, MSG_NA) in supp_info_string
                assert MSG_ATTR_RESULT % (MEAS_CAPPED, RESULT_PASS) in supp_info_string

                assert MSG_N_IN % (CHAINS_CAPPED, N_IN) in supp_info_string
                assert MSG_N_OUT % (CHAINS_CAPPED, N_OUT_CHAINS) in supp_info_string
                assert MSG_F_OUT % (CHAINS_CAPPED, N_OUT_CHAINS / N_IN) in supp_info_string
                assert MSG_MISSING_IDS % (CHAINS_CAPPED, str(list(L_MISSING_CHAINS))) in supp_info_string
                assert MSG_ATTR_RESULT % (CHAINS_CAPPED, RESULT_FAIL) in supp_info_string

                assert supp_info_string.endswith(f"Result: {RESULT_PASS}")

            elif test_results.TestId.startswith(GAL_INFO_DATA_TEST_CASE_INFO.base_test_case_id):

                assert test_results.GlobalResult == RESULT_FAIL
                assert requirement_object.Comment == INFO_MULTIPLE
                assert requirement_object.MeasuredValue[0].Value.FloatValue == N_INVALID_MEAS
                assert requirement_object.ValidationResult == RESULT_FAIL

            else:

                raise ValueError(f"Invalid test ID: {test_results.TestId}")
