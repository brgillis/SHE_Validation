"""
:file: tests/python/dp_results_reporting_test.py

:date: 01/20/23
:author: Bryan Gillis

Tests of code to output test results to in-memory data product for DataProc validation test
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
from SHE_Validation_DataQuality.constants.data_proc_test_info import (L_DATA_PROC_TEST_CASE_INFO,
                                                                      NUM_DATA_PROC_TEST_CASES, )
from SHE_Validation_DataQuality.dp_data_processing import DataProcTestResults
from SHE_Validation_DataQuality.dp_results_reporting import (DataProcValidationResultsWriter, MSG_DETAILS,
                                                             MSG_NA, MSG_PRESENT_AND_VALID,
                                                             STR_P_REC_CAT, STR_P_REC_CHAINS, STR_REC_CAT,
                                                             STR_REC_CHAINS, )

MSG_REC_CAT = "ERROR: rec_cat message"
MSG_P_REC_CHAINS = "ERROR: p_rec_chains message"


class TestDataProcResultsReporting(SheTestCase):
    """Test case for DataProc validation test results reporting
    """

    lensmc_id: Optional[str] = None

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        self.d_l_test_results: Dict[str, List[DataProcTestResults]] = {}

        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method

            # Do things a bit different for LensMC
            if method == ShearEstimationMethods.LENSMC:
                self.lensmc_id = test_case_info.id
                rec_cat_passed = False
                msg_rec_cat = MSG_REC_CAT
            else:
                rec_cat_passed = True
                msg_rec_cat = None

            self.d_l_test_results[name] = [DataProcTestResults(p_rec_cat_passed=True,
                                                               msg_p_rec_cat=None,
                                                               rec_cat_passed=rec_cat_passed,
                                                               msg_rec_cat=msg_rec_cat,
                                                               p_rec_chains_passed=False,
                                                               msg_p_rec_chains=MSG_P_REC_CHAINS,
                                                               rec_chains_passed=False,
                                                               msg_rec_chains=None, )]

    @pytest.fixture(scope='class')
    def test_result_product(self, class_setup):
        test_result_product = create_dpd_she_validation_test_results(num_tests=NUM_DATA_PROC_TEST_CASES)
        test_results_writer = DataProcValidationResultsWriter(test_object=test_result_product,
                                                              workdir=self.workdir,
                                                              d_l_test_results=self.d_l_test_results)
        test_results_writer.write()

        return test_result_product

    def test_meta(self, test_result_product):
        """ Test that results can be written to a product without any errors, and test case metadata in it is correct.
        """

        # Write the product

        # Check that the results are as expected
        test_result_product.validateBinding()

        # Check metadata for all test cases
        for test_case_index, test_case_info in enumerate(L_DATA_PROC_TEST_CASE_INFO):

            test_result = test_result_product.Data.ValidationTestList[test_case_index]

            assert test_case_info.id in test_result.TestId
            assert test_result.TestDescription == test_case_info.description

    def test_results(self, test_result_product):
        """ Test that the filled results are as expected
        """

        for test_results in test_result_product.Data.ValidationTestList:

            assert test_results.GlobalResult == RESULT_FAIL

            requirement_object = test_results.ValidatedRequirements.Requirement[0]
            assert requirement_object.Comment == INFO_MULTIPLE
            assert requirement_object.MeasuredValue[0].Value.FloatValue == 0.
            assert requirement_object.ValidationResult == RESULT_FAIL

            supp_info = requirement_object.SupplementaryInformation
            supp_info_string = supp_info.Parameter[0].StringValue

            # Check that expected strings for all results are present
            assert (f"{MSG_PRESENT_AND_VALID % STR_P_REC_CAT}{RESULT_PASS}\n"
                    f"{MSG_DETAILS}{MSG_NA}" in supp_info_string)

            if test_results.TestId == self.lensmc_id:
                assert (f"{MSG_PRESENT_AND_VALID % STR_REC_CAT}{RESULT_FAIL}\n"
                        f"{MSG_DETAILS}\"{MSG_REC_CAT}\"" in supp_info_string)
            else:
                assert (f"{MSG_PRESENT_AND_VALID % STR_REC_CAT}{RESULT_PASS}\n"
                        f"{MSG_DETAILS}{MSG_NA}" in supp_info_string)

            assert (f"{MSG_PRESENT_AND_VALID % STR_P_REC_CHAINS}{RESULT_FAIL}\n"
                    f"{MSG_DETAILS}\"{MSG_P_REC_CHAINS}\"" in supp_info_string)

            assert (f"{MSG_PRESENT_AND_VALID % STR_REC_CHAINS}{RESULT_FAIL}\n"
                    f"{MSG_DETAILS}{MSG_NA}" in supp_info_string)
