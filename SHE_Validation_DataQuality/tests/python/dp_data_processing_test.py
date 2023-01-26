"""
:file: tests/python/dp_data_processing_test.py

:date: 01/19/23
:author: Bryan Gillis

Tests of function to process data and determine test results for the DataProc test
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

from copy import deepcopy

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_Validation.constants.misc import MSG_ERROR
from SHE_Validation_DataQuality.constants.data_proc_test_info import L_DATA_PROC_TEST_CASE_INFO
from SHE_Validation_DataQuality.dp_data_processing import MSG_NO_CHAINS, get_data_proc_test_results
from SHE_Validation_DataQuality.testing.utility import SheDQTestCase

MSG_P_CAT = "1"
ERR_P_CAT = f"{MSG_ERROR}: {MSG_P_CAT}"
MSG_KSB_CAT = "KSB-2"
ERR_KSB_CAT = f"{MSG_ERROR}: {MSG_KSB_CAT}"
MSG_LENSMC_CAT = "LENSMC-2"
ERR_LENSMC_CAT = f"{MSG_ERROR}: {MSG_LENSMC_CAT}"
MSG_P_CHAINS = "3"
ERR_P_CHAINS = f"{MSG_ERROR}: {MSG_P_CHAINS}"
MSG_CHAINS = "4"
ERR_CHAINS = f"{MSG_ERROR}: {MSG_CHAINS}"


class TestDataProcDataProcessing(SheDQTestCase):
    """Test case for DataProc validation test data processing
    """

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        self.make_mock_data_proc_input()

    def test_good_input(self):
        """Unit test of the `get_data_proc_test_results` method with completely-good input
        """

        d_l_test_results = get_data_proc_test_results(self.good_dp_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method

            if not method == ShearEstimationMethods.LENSMC:
                continue

            test_results = d_l_test_results[name][0]

            assert test_results.p_she_cat_passed, f"{name=}"
            assert test_results.msg_p_she_cat is None, f"{name=}"

            assert test_results.she_cat_passed, f"{name=}"
            assert test_results.msg_she_cat is None, f"{name=}"

            assert test_results.p_she_chains_passed, f"{name=}"
            assert test_results.msg_p_she_chains is None, f"{name=}"

            assert test_results.she_chains_passed, f"{name=}"
            assert test_results.msg_she_chains is None, f"{name=}"

            assert test_results.global_passed, f"{name=}"

    def test_missing_cat_prod(self):
        """Unit test of the `get_data_proc_test_results` method in a case where the catalog data product is missing
        """
        missing_cat_prod_input = deepcopy(self.good_dp_input)
        missing_cat_prod_input.p_she_cat = None
        missing_cat_prod_input.err_p_she_cat = MSG_P_CAT

        d_l_test_results = get_data_proc_test_results(missing_cat_prod_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method

            if not method == ShearEstimationMethods.LENSMC:
                continue

            test_results = d_l_test_results[name][0]

            assert not test_results.p_she_cat_passed, f"{name=}"
            assert test_results.msg_p_she_cat == ERR_P_CAT, f"{name=}"

            assert not test_results.she_cat_passed, f"{name=}"
            assert test_results.msg_she_cat is None, f"{name=}"

            assert not test_results.global_passed, f"{name=}"

    def test_missing_she_cats(self):
        """Unit test of the `get_data_proc_test_results` method in a case where some catalogs are missing.
        """
        missing_cats_input = deepcopy(self.good_dp_input)

        missing_cats_input.d_she_cat[ShearEstimationMethods.KSB] = None
        missing_cats_input.d_she_cat[ShearEstimationMethods.LENSMC] = None

        missing_cats_input.d_err_she_cat = {ShearEstimationMethods.KSB: MSG_KSB_CAT,
                                            ShearEstimationMethods.LENSMC: MSG_LENSMC_CAT}

        d_l_test_results = get_data_proc_test_results(missing_cats_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method

            if not method == ShearEstimationMethods.LENSMC:
                continue

            test_results = d_l_test_results[name][0]

            assert test_results.p_she_cat_passed, f"{name=}"
            assert test_results.msg_p_she_cat is None, f"{name=}"

            if method == ShearEstimationMethods.KSB:

                assert not test_results.she_cat_passed, f"{name=}"
                assert test_results.msg_she_cat == ERR_KSB_CAT, f"{name=}"

                assert not test_results.global_passed, f"{name=}"

            elif method == ShearEstimationMethods.LENSMC:

                assert not test_results.she_cat_passed, f"{name=}"
                assert test_results.msg_she_cat == ERR_LENSMC_CAT, f"{name=}"

                assert not test_results.global_passed, f"{name=}"

            else:

                assert test_results.she_cat_passed, f"{name=}"
                assert test_results.msg_she_cat is None, f"{name=}"

                assert test_results.global_passed, f"{name=}"

    def test_no_chains(self):
        """Unit test of the `get_data_proc_test_results` method in a case where chains are deliberately not provided
        """
        missing_chains_input = deepcopy(self.good_dp_input)
        missing_chains_input.p_she_chains = None
        missing_chains_input.she_chains = None

        d_l_test_results = get_data_proc_test_results(missing_chains_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method

            if not method == ShearEstimationMethods.LENSMC:
                continue

            test_results = d_l_test_results[name][0]

            assert test_results.p_she_chains_passed, f"{name=}"
            assert test_results.msg_p_she_chains == MSG_NO_CHAINS, f"{name=}"

            assert test_results.she_chains_passed, f"{name=}"
            assert test_results.msg_she_chains == MSG_NO_CHAINS, f"{name=}"

            assert test_results.global_passed, f"{name=}"

    def test_missing_chains_prod(self):
        """Unit test of the `get_data_proc_test_results` method in a case where the chains data product is missing
        """
        missing_chains_prod_input = deepcopy(self.good_dp_input)
        missing_chains_prod_input.p_she_chains = None
        missing_chains_prod_input.err_p_she_chains = MSG_P_CHAINS

        d_l_test_results = get_data_proc_test_results(missing_chains_prod_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name

            test_results = d_l_test_results[name][0]

            assert not test_results.p_she_chains_passed, f"{name=}"
            assert test_results.msg_p_she_chains == ERR_P_CHAINS, f"{name=}"

            assert not test_results.she_chains_passed, f"{name=}"
            assert test_results.msg_she_chains is None, f"{name=}"

            assert not test_results.global_passed, f"{name=}"

    def test_missing_chains_cat(self):
        """Unit test of the `get_data_proc_test_results` method in a case where the chains catalog is missing
        """
        missing_chains_cat_input = deepcopy(self.good_dp_input)
        missing_chains_cat_input.she_chains = None
        missing_chains_cat_input.err_she_chains = MSG_CHAINS

        d_l_test_results = get_data_proc_test_results(missing_chains_cat_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name

            test_results = d_l_test_results[name][0]

            assert test_results.p_she_chains_passed, f"{name=}"
            assert test_results.msg_p_she_chains is None, f"{name=}"

            assert not test_results.she_chains_passed, f"{name=}"
            assert test_results.msg_she_chains == ERR_CHAINS, f"{name=}"

            assert not test_results.global_passed, f"{name=}"
