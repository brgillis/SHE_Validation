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
from typing import Dict

from astropy.table import Table

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.products.she_lensmc_chains import create_dpd_she_lensmc_chains
from SHE_PPT.products.she_validated_measurements import create_dpd_she_validated_measurements
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.constants.misc import MSG_ERROR
from SHE_Validation_DataQuality.constants.data_proc_test_info import L_DATA_PROC_TEST_CASE_INFO
from SHE_Validation_DataQuality.dp_data_processing import MSG_NO_CHAINS, get_data_proc_test_results
from SHE_Validation_DataQuality.dp_input import DataProcInput

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


class TestDataProcDataProcessing(SheTestCase):
    """Test case for DataProc validation test data processing
    """

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        p_she_cat = create_dpd_she_validated_measurements()
        p_she_chains = create_dpd_she_lensmc_chains()
        she_chains = lensmc_chains_table_format.init_table(size=1)

        d_she_cat: Dict[ShearEstimationMethods, Table] = {}
        for method, tf in D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.items():
            d_she_cat[method] = tf.init_table(size=1)

        # Make a mock input object with good data
        self.good_input = DataProcInput(p_she_cat=p_she_cat,
                                        err_p_she_cat=None,
                                        d_she_cat=d_she_cat,
                                        d_err_she_cat=None,
                                        p_she_chains=p_she_chains,
                                        err_p_she_chains=None,
                                        she_chains=she_chains,
                                        err_she_chains=None)

    def test_good_input(self):
        """Unit test of the `get_data_proc_test_results` method with completely-good input
        """

        d_l_test_results = get_data_proc_test_results(self.good_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method.value

            method_test_results = d_l_test_results[name][0]

            assert method_test_results.p_she_cat_passed, f"{method=}"
            assert method_test_results.msg_p_she_cat is None, f"{method=}"

            assert method_test_results.she_cat_passed, f"{method=}"
            assert method_test_results.msg_she_cat is None, f"{method=}"

            assert method_test_results.p_she_chains_passed, f"{method=}"
            assert method_test_results.msg_p_she_chains is None, f"{method=}"

            assert method_test_results.she_chains_passed, f"{method=}"
            assert method_test_results.msg_she_chains is None, f"{method=}"

            assert method_test_results.global_passed, f"{method=}"

    def test_missing_cat_prod(self):
        """Unit test of the `get_data_proc_test_results` method in a case where the catalog data product is missing
        """
        missing_cat_prod_input = deepcopy(self.good_input)
        missing_cat_prod_input.p_she_cat = None
        missing_cat_prod_input.err_p_she_cat = MSG_P_CAT

        d_l_test_results = get_data_proc_test_results(missing_cat_prod_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method.value

            method_test_results = d_l_test_results[name][0]

            assert not method_test_results.p_she_cat_passed, f"{method=}"
            assert method_test_results.msg_p_she_cat == ERR_P_CAT, f"{method=}"

            assert not method_test_results.she_cat_passed, f"{method=}"
            assert method_test_results.msg_she_cat is None, f"{method=}"

            assert not method_test_results.global_passed, f"{method=}"

    def test_missing_she_cats(self):
        """Unit test of the `get_data_proc_test_results` method in a case where some catalogs are missing.
        """
        missing_cats_input = deepcopy(self.good_input)

        missing_cats_input.d_she_cat[ShearEstimationMethods.KSB] = None
        missing_cats_input.d_she_cat[ShearEstimationMethods.LENSMC] = None

        missing_cats_input.d_err_she_cat = {ShearEstimationMethods.KSB: MSG_KSB_CAT,
                                            ShearEstimationMethods.LENSMC: MSG_LENSMC_CAT}

        d_l_test_results = get_data_proc_test_results(missing_cats_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method.value

            method_test_results = d_l_test_results[name][0]

            assert method_test_results.p_she_cat_passed, f"{method=}"
            assert method_test_results.msg_p_she_cat is None, f"{method=}"

            if method == ShearEstimationMethods.KSB.value:

                assert not method_test_results.she_cat_passed, f"{method=}"
                assert method_test_results.msg_she_cat == ERR_KSB_CAT, f"{method=}"

                assert not method_test_results.global_passed, f"{method=}"

            elif method == ShearEstimationMethods.LENSMC.value:

                assert not method_test_results.she_cat_passed, f"{method=}"
                assert method_test_results.msg_she_cat == ERR_LENSMC_CAT, f"{method=}"

                assert not method_test_results.global_passed, f"{method=}"

            else:

                assert method_test_results.she_cat_passed, f"{method=}"
                assert method_test_results.msg_she_cat is None, f"{method=}"

                assert method_test_results.global_passed, f"{method=}"

    def test_no_chains(self):
        """Unit test of the `get_data_proc_test_results` method in a case where chains are deliberately not provided
        """
        missing_chains_input = deepcopy(self.good_input)
        missing_chains_input.p_she_chains = None
        missing_chains_input.she_chains = None

        d_l_test_results = get_data_proc_test_results(missing_chains_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method.value

            method_test_results = d_l_test_results[name][0]

            assert method_test_results.p_she_chains_passed, f"{method=}"
            assert method_test_results.msg_p_she_chains == MSG_NO_CHAINS, f"{method=}"

            assert method_test_results.she_chains_passed, f"{method=}"
            assert method_test_results.msg_she_chains == MSG_NO_CHAINS, f"{method=}"

            assert method_test_results.global_passed, f"{method=}"

    def test_missing_chains_prod(self):
        """Unit test of the `get_data_proc_test_results` method in a case where the chains data product is missing
        """
        missing_chains_prod_input = deepcopy(self.good_input)
        missing_chains_prod_input.p_she_chains = None
        missing_chains_prod_input.err_p_she_chains = MSG_P_CHAINS

        d_l_test_results = get_data_proc_test_results(missing_chains_prod_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method.value

            method_test_results = d_l_test_results[name][0]

            assert not method_test_results.p_she_chains_passed, f"{method=}"
            assert method_test_results.msg_p_she_chains == ERR_P_CHAINS, f"{method=}"

            assert not method_test_results.she_chains_passed, f"{method=}"
            assert method_test_results.msg_she_chains is None, f"{method=}"

            assert not method_test_results.global_passed, f"{method=}"

    def test_missing_chains_cat(self):
        """Unit test of the `get_data_proc_test_results` method in a case where the chains catalog is missing
        """
        missing_chains_cat_input = deepcopy(self.good_input)
        missing_chains_cat_input.she_chains = None
        missing_chains_cat_input.err_she_chains = MSG_CHAINS

        d_l_test_results = get_data_proc_test_results(missing_chains_cat_input)

        # Check that all results are as expected
        for test_case_info in L_DATA_PROC_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method.value

            method_test_results = d_l_test_results[name][0]

            assert method_test_results.p_she_chains_passed, f"{method=}"
            assert method_test_results.msg_p_she_chains is None, f"{method=}"

            assert not method_test_results.she_chains_passed, f"{method=}"
            assert method_test_results.msg_she_chains == ERR_CHAINS, f"{method=}"

            assert not method_test_results.global_passed, f"{method=}"
