""" @file data_processing_test.py

    Created 30 March 2022 by Bryan Gillis

    Unit tests of data processing within the PSF Residual validation test.
"""

__updated__ = "2022-04-30"

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

from SHE_PPT.argument_parser import CA_PIPELINE_CONFIG
from SHE_PPT.testing.mock_she_star_cat import MockStarCatDataGenerator, MockStarCatTableGenerator
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.config_utility import get_d_l_bin_limits
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.constants.psf_res_test_info import L_PSF_RES_TEST_CASE_INFO
from SHE_Validation_PSF.data_processing import (ESC_TF, SheExtStarCatalogFormat, run_psf_res_val_test,
                                                run_psf_res_val_test_for_bin, )

MIN_ALLOWED_P = 0.05


class MockValStarCatDataGenerator(MockStarCatDataGenerator):
    """ Modified version of the data generator which adds bin columns in directly.
    """

    tf: SheExtStarCatalogFormat = ESC_TF

    def _generate_unique_data(self):
        super()._generate_unique_data()

        # Add the SNR column with controlled values - in pattern of 1, 1, 0, 0, repeating
        factor = 4
        self.num_test_points = self.num_test_points
        self.data[self.tf.snr] = np.where(self._indices % factor < factor / 2,
                                          self._ones,
                                          self._zeros)


class MockValStarCatTableGenerator(MockStarCatTableGenerator):
    """ Modified version of the table generator which used the modified version of the data generator.
    """

    tf: SheExtStarCatalogFormat = ESC_TF
    mock_data_generator_type = MockValStarCatDataGenerator


class TestPsfDataProcessing(SheTestCase):
    """ Test case for PSF-Res validation test data processing code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def post_setup(self):
        """ Override parent setup, setting up data to work with here.
        """

        setattr(self._args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.pipeline_config)

        # Generate a table with good chi2 data
        mock_starcat_table_gen = MockValStarCatTableGenerator(workdir = self.workdir)
        self.mock_good_starcat_table = mock_starcat_table_gen.get_mock_table()
        tf = mock_starcat_table_gen.tf

        # And tables with bad chi2 data
        self.mock_bad_starcat_table = deepcopy(self.mock_good_starcat_table)
        self.mock_too_good_starcat_table = deepcopy(self.mock_good_starcat_table)

        # Let's pretend chi2 for individual stars is too bad for the first table, and too good for the second
        self.mock_bad_starcat_table[tf.star_chisq] += 2
        self.mock_too_good_starcat_table[tf.star_chisq] -= 2

    def test_run_psf_res_val_test_for_bin(self):
        """ Test running the "test_psf_res_for_bin" function, using all data in the table.
        """

        # Run a test for individual stars
        star_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_good_starcat_table,
                                                          group_mode = False)

        # And for the group
        group_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_good_starcat_table,
                                                           group_mode = True)

        # Check that the results are reasonable, and that the two modes are doing something different
        assert 1 > star_kstest_result.pvalue > MIN_ALLOWED_P
        assert 1 > group_kstest_result.pvalue > MIN_ALLOWED_P

        assert not np.isclose(star_kstest_result.pvalue, group_kstest_result.pvalue)

        # Now try with the bad and too-good data, and check that the p-values for each are lower
        star_bad_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_bad_starcat_table,
                                                              group_mode = False)
        star_too_good_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_too_good_starcat_table,
                                                                   group_mode = False)

        assert star_bad_kstest_result.pvalue < star_kstest_result.pvalue
        assert star_too_good_kstest_result.pvalue < star_kstest_result.pvalue

    def test_run_psf_res_val_test(self):
        """ Test that the function for testing across all bins works as expected.
        """

        d_l_kstest_results = run_psf_res_val_test(star_cat = self.mock_good_starcat_table,
                                                  d_l_bin_limits = get_d_l_bin_limits(self.pipeline_config))

        tc_tot = L_PSF_RES_TEST_CASE_INFO[0]
        tc_snr = L_PSF_RES_TEST_CASE_INFO[1]

        # Compare the results for the test cases and bins
        tot_kstest_result = d_l_kstest_results[tc_tot.name][0]
        l_snr_kstest_results = d_l_kstest_results[tc_snr.name]

        # Make sure they all pass
        assert 1 > tot_kstest_result.pvalue > MIN_ALLOWED_P
        assert 1 > l_snr_kstest_results[0].pvalue > MIN_ALLOWED_P
        assert 1 > l_snr_kstest_results[1].pvalue > MIN_ALLOWED_P

        # Make sure they aren't all the same
        assert not np.isclose(tot_kstest_result.pvalue, l_snr_kstest_results[0].pvalue)
        assert not np.isclose(l_snr_kstest_results[0].pvalue, l_snr_kstest_results[1].pvalue)

        pass
