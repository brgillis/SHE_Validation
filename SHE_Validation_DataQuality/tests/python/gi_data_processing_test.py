"""
:file: tests/python/gi_data_processing_test.py

:date: 01/25/23
:author: Bryan Gillis

Tests of function to process data and determine test results for the GalInfo test
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

import numpy as np
from astropy.table import Row

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.flags import failure_flags
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_formats.she_lensmc_measurements import lensmc_measurements_table_format
from SHE_PPT.testing.mock_data import NUM_NAN_TEST_POINTS, NUM_ZERO_WEIGHT_TEST_POINTS
from SHE_Validation_DataQuality.constants.gal_info_test_info import (GAL_INFO_DATA_TEST_CASE_INFO,
                                                                     GAL_INFO_N_TEST_CASE_INFO,
                                                                     L_GAL_INFO_TEST_CASE_INFO, )
from SHE_Validation_DataQuality.gi_data_processing import (GalInfoDataTestResults, GalInfoNTestResults,
                                                           get_gal_info_test_results, )
from SHE_Validation_DataQuality.table_formats.gid_objects import GIDM_TF
from SHE_Validation_DataQuality.testing.utility import SheDQTestCase


class TestGalInfoDataProcessing(SheDQTestCase):
    """Test case for GalInfo validation test data processing
    """

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        self.make_mock_gal_info_input()

    def test_good_input(self):
        """Unit test of the `get_gal_info_test_results` method with good input
        """

        d_l_test_results = get_gal_info_test_results(self.good_gi_input, workdir=self.workdir)

        # Check that all results are as expected
        for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method
            id_ = test_case_info.id

            test_results = d_l_test_results[name][0]

            if id_.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id):
                if method == ShearEstimationMethods.LENSMC:
                    assert test_results.global_passed, f"{name=}"
                else:
                    assert not test_results.global_passed, f"{name=}"
            else:
                assert test_results.global_passed, f"{name=}"

    def test_missing_objects(self):
        """Unit test of the `get_gal_info_test_results` method with input which is missing some objects.
        """

        l_ids_to_exclude_meas = np.array([2, 4])
        l_ids_to_exclude_chains = np.array([2, 3, 4])

        bad_gi_input = deepcopy(self.good_gi_input)

        # Create mock measurements data with some IDs missing

        she_cat = self.good_gi_input.d_she_cat[ShearEstimationMethods.LENSMC]
        m_tf = lensmc_measurements_table_format

        l_keep_condition_meas = np.logical_not(np.in1d(she_cat[m_tf.ID], l_ids_to_exclude_meas))

        # Sanity check that all IDs are properly excluded
        assert sum(~l_keep_condition_meas) == len(l_ids_to_exclude_meas)

        missing_she_cat = she_cat[l_keep_condition_meas]

        bad_gi_input.d_she_cat[ShearEstimationMethods.LENSMC] = missing_she_cat

        # Do the same for the chains

        she_chains = self.good_gi_input.she_chains
        c_tf = lensmc_chains_table_format

        l_keep_condition_chains = np.logical_not(np.in1d(she_chains[c_tf.ID], l_ids_to_exclude_chains))

        # Sanity check that all IDs are properly excluded
        assert sum(~l_keep_condition_chains) == len(l_ids_to_exclude_chains)

        missing_she_chains = she_chains[l_keep_condition_chains]

        bad_gi_input.she_chains = missing_she_chains

        # Run the test, and check that the IDs are missing as expected

        d_l_test_results = get_gal_info_test_results(bad_gi_input, workdir=self.workdir)
        for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method
            id_ = test_case_info.id

            if not (method == ShearEstimationMethods.LENSMC and
                    id_.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id)):
                continue

            test_results: GalInfoNTestResults = d_l_test_results[name][0]

            # Check that the lists of missing IDs are correct
            assert len(np.setxor1d(test_results.l_missing_ids_meas, l_ids_to_exclude_meas)) == 0
            assert len(np.setxor1d(test_results.l_missing_ids_chains, l_ids_to_exclude_chains)) == 0

            # Check that n_out is calculated correctly
            assert test_results.n_out_meas == test_results.n_in - len(l_ids_to_exclude_meas)
            assert test_results.n_out_chains == test_results.n_in - len(l_ids_to_exclude_chains)

            assert not test_results.global_passed

    def test_invalid_objects(self):
        """Unit test of the `get_gal_info_test_results` method with input which is missing some objects.
        """

        bad_gi_input = deepcopy(self.good_gi_input)

        # Create mock measurements data with some IDs made invalid

        she_cat = self.good_gi_input.d_she_cat[ShearEstimationMethods.LENSMC]
        m_tf = lensmc_measurements_table_format

        l_is_flagged_meas = np.asarray(she_cat[m_tf.fit_flags] & failure_flags, bool)

        # The mock input data should already have invalid data at the end flagged out. Double-check this is the case
        assert l_is_flagged_meas.sum() == NUM_NAN_TEST_POINTS + NUM_ZERO_WEIGHT_TEST_POINTS

        l_ids_to_inv_meas = she_cat[m_tf.ID][l_is_flagged_meas]
        inv_she_cat = deepcopy(she_cat)
        inv_she_cat[m_tf.fit_flags][l_is_flagged_meas] = 0

        l_g_is_nan = l_ids_to_inv_meas[:NUM_NAN_TEST_POINTS]
        l_weight_is_zero = l_ids_to_inv_meas[NUM_NAN_TEST_POINTS:]

        bad_gi_input.d_she_cat[ShearEstimationMethods.LENSMC] = inv_she_cat

        # Do the same for the chains

        she_chains = self.good_gi_input.she_chains
        c_tf = lensmc_chains_table_format

        l_is_flagged_chains = np.asarray(she_chains[c_tf.fit_flags] & failure_flags, bool)

        # The mock input data should already have invalid data at the end flagged out. Double-check this is the case
        # Use a slightly different list of IDs for the chains
        l_is_flagged_chains[-1] = False
        assert l_is_flagged_chains.sum() > 0

        l_ids_to_inv_chains = she_chains[c_tf.ID][l_is_flagged_chains]
        inv_she_chains = deepcopy(she_chains)
        inv_she_chains[c_tf.fit_flags][l_is_flagged_chains] = 0

        bad_gi_input.she_chains = inv_she_chains

        # Run the test, and check that the IDs are invalid as expected

        d_l_test_results = get_gal_info_test_results(bad_gi_input, workdir=self.workdir)
        for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
            name = test_case_info.name
            method = test_case_info.method
            id_ = test_case_info.id

            if not (method == ShearEstimationMethods.LENSMC and
                    id_.startswith(GAL_INFO_DATA_TEST_CASE_INFO.base_test_case_id)):
                continue

            test_results: GalInfoDataTestResults = d_l_test_results[name][0]

            # Check that the lists of missing IDs are correct
            assert len(np.setxor1d(test_results.l_invalid_ids_meas, l_ids_to_inv_meas)) == 0
            assert len(np.setxor1d(test_results.l_invalid_ids_chains, l_ids_to_inv_chains)) == 0

            # Check that n_out is calculated correctly
            assert test_results.n_inv_meas == len(l_ids_to_inv_meas)
            assert test_results.n_inv_chains == len(l_ids_to_inv_chains)

            assert not test_results.global_passed

            # Check that we have proper tables of the invalid objects
            meas_table = test_results.invalid_data_table_meas
            assert len(meas_table) == test_results.n_inv_meas
            assert len(np.setxor1d(meas_table[GIDM_TF.ID], l_ids_to_inv_meas)) == 0

            chains_table = test_results.invalid_data_table_chains
            assert len(chains_table) == test_results.n_inv_chains
            assert len(np.setxor1d(chains_table[GIDM_TF.ID], l_ids_to_inv_chains)) == 0

            # Check that rows for g1/g2 NaN and weight zero are marked appropriately for the measurements table
            meas_table.add_index(GIDM_TF.ID)

            meas_table_g_nan = meas_table.loc[l_g_is_nan]
            for row in meas_table_g_nan:
                assert np.isnan(row[GIDM_TF.g1])
                assert not row[GIDM_TF.g1_val_check]
                assert np.isnan(row[GIDM_TF.g2])
                assert not row[GIDM_TF.g2_val_check]

            meas_table_weight_zero = meas_table.loc[l_weight_is_zero]
            assert isinstance(meas_table_weight_zero, Row), "Expected only a single row"
            assert meas_table_weight_zero[GIDM_TF.weight] == 0
            assert not meas_table_weight_zero[GIDM_TF.weight_min_check]

            # Check that rows for g1/g2 NaN and weight zero are marked appropriately for the chains table
            chains_table.add_index(GIDM_TF.ID)

            chains_table_g_nan = chains_table.loc[l_g_is_nan]
            for row in chains_table_g_nan:
                assert np.isnan(row[GIDM_TF.g1]).any()
                assert not row[GIDM_TF.g1_val_check]
                assert np.isnan(row[GIDM_TF.g2]).any()
                assert not row[GIDM_TF.g2_val_check]
