"""
:file: tests/python/dp_data_processing_test.py

:date: 01/19/23
:author: Bryan Gillis

Tests of function to read in input data for the DataProc test
"""
from copy import deepcopy
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

from typing import Dict

from astropy.table import Table

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.products.she_reconciled_lensmc_chains import create_dpd_she_reconciled_lensmc_chains
from SHE_PPT.products.she_reconciled_measurements import create_dpd_she_reconciled_measurements
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation_DataQuality.dp_data_processing import get_data_proc_test_results
from SHE_Validation_DataQuality.dp_input import DataProcInput

MSG_P_CAT_ERR = "1"
MSG_KSB_CAT_ERR = "KSB-2"
MSG_LENSMC_CAT_ERR = "LENSMC-2"
MSG_P_CHAINS_ERR = "3"
MSG_CHAINS_ERR = "4"


class TestDataProcDataProcessing(SheTestCase):
    """Test case for DataProc validation test data processing
    """

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        p_rec_cat = create_dpd_she_reconciled_measurements()
        p_rec_chains = create_dpd_she_reconciled_lensmc_chains()
        rec_chains = lensmc_chains_table_format.init_table(size=1)

        d_rec_cat: Dict[ShearEstimationMethods, Table] = {}
        for method, tf in D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.items():
            d_rec_cat[method] = tf.init_table(size=1)

        # Make a mock input object with good data
        self.good_input = DataProcInput(p_rec_cat=p_rec_cat,
                                        err_p_rec_cat=None,
                                        d_rec_cat=d_rec_cat,
                                        d_err_rec_cat=None,
                                        p_rec_chains=p_rec_chains,
                                        err_p_rec_chains=None,
                                        rec_chains=rec_chains,
                                        err_rec_chains=None)

    def test_good_input(self):
        """Unit test of the `get_data_proc_test_results` method with completely-good input
        """

        d_l_test_results = get_data_proc_test_results(self.good_input)

        # Check that all results are as expected
        for method in ShearEstimationMethods:

            method_test_results = d_l_test_results[method][0]

            assert method_test_results.p_rec_cat_passed, f"{method=}"
            assert method_test_results.err_p_rec_cat is None, f"{method=}"

            assert method_test_results.rec_cat_passed, f"{method=}"
            assert method_test_results.err_rec_cat is None, f"{method=}"

            assert method_test_results.p_rec_chains_passed, f"{method=}"
            assert method_test_results.err_p_rec_chains is None, f"{method=}"

            assert method_test_results.rec_chains_passed, f"{method=}"
            assert method_test_results.err_rec_chains is None, f"{method=}"

    def test_no_chains(self):
        """Unit test of the `get_data_proc_test_results` method in a case where chains are deliberately not provided
        """
        missing_chains_input = deepcopy(self.good_input)
        missing_chains_input.p_rec_chains = None
        missing_chains_input.rec_chains = None

        d_l_test_results = get_data_proc_test_results(missing_chains_input)

        # Check that all results are as expected
        for method in ShearEstimationMethods:

            method_test_results = d_l_test_results[method][0]

            assert method_test_results.p_rec_chains_passed, f"{method=}"
            assert method_test_results.err_p_rec_chains is None, f"{method=}"

            assert method_test_results.rec_chains_passed, f"{method=}"
            assert method_test_results.err_rec_chains is None, f"{method=}"
