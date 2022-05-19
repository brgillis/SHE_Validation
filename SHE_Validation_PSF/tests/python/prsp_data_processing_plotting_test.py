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
from scipy.stats.stats import KstestResult

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint, get_ids_for_test_cases
from SHE_Validation.config_utility import get_d_l_bin_limits
from SHE_Validation.constants.default_config import DEFAULT_P_FAIL
from SHE_Validation.test_info_utility import find_test_case_info
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.constants.psf_res_sp_test_info import L_PSF_RES_SP_TEST_CASE_INFO
from SHE_Validation_PSF.data_processing import (run_psf_res_val_test,
                                                run_psf_res_val_test_for_bin, )
from SHE_Validation_PSF.file_io import PsfResSPCumHistFileNamer, PsfResSPHistFileNamer
from SHE_Validation_PSF.plotting import PsfResSPHistPlotter
from SHE_Validation_PSF.testing.utility import SheValPsfTestCase
from SHE_Validation_PSF.utility import ESC_TF


class TestPsfDataProcessing(SheValPsfTestCase):
    """ Test case for PSF-Res validation test data processing code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    _NUM_TEST_POINTS: int = 1000

    def post_setup(self):
        """ Override parent setup, setting up data to work with here.
        """

        pipeline_config = self.mock_pipeline_config_factory.pipeline_config

        # For the bin limits, add an extra bin we expect to be empty
        base_snr_bin_limits = pipeline_config[ValidationConfigKeys.VAL_SNR_BIN_LIMITS]
        self.l_bin_limits = np.append(base_snr_bin_limits, 2.5)
        pipeline_config[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] = self.l_bin_limits

        self.bin_parameter = BinParameters.SNR

        # self.mock_starcat_table is generated when the attributed is accessed

        # Make a reference table which is a bit worse than the test table
        self.mock_ref_starcat_table = deepcopy(self.mock_starcat_table)
        self.mock_ref_starcat_table[ESC_TF.star_chisq] += 2

        # And tables with bad chi2 data
        self.mock_bad_starcat_table = deepcopy(self.mock_starcat_table)
        self.mock_too_good_starcat_table = deepcopy(self.mock_starcat_table)

        # Let's pretend chi2 for individual stars is too bad for the first table, and too good for the second
        self.mock_bad_starcat_table[ESC_TF.star_chisq] += 4
        self.mock_too_good_starcat_table[ESC_TF.star_chisq] -= 2

    def test_run_psf_res_val_test_for_bin(self):
        """ Test running the "test_psf_res_for_bin" function, using all data in the table.
        """

        for ref_star_cat in (None, self.mock_ref_starcat_table):

            # Run a test for individual stars
            star_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_starcat_table,
                                                              ref_star_cat = ref_star_cat,
                                                              group_mode = False)

            # And for the group
            group_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_starcat_table,
                                                               ref_star_cat = ref_star_cat,
                                                               group_mode = True)

            # Check that the results are reasonable, and that the two modes are doing something different
            assert 1.0 >= star_kstest_result.pvalue > DEFAULT_P_FAIL
            assert 1.0 >= group_kstest_result.pvalue > DEFAULT_P_FAIL

            # Check both are different (unless both are close to 1.0)
            assert ((np.isclose(star_kstest_result.pvalue, 1.0) and np.isclose(group_kstest_result.pvalue, 1.0)) or
                    (not np.isclose(star_kstest_result.pvalue, group_kstest_result.pvalue)))

            # Now try with the bad and too-good data, and check that the p-values for each are lower
            star_bad_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_bad_starcat_table,
                                                                  ref_star_cat = ref_star_cat,
                                                                  group_mode = False)
            star_too_good_kstest_result = run_psf_res_val_test_for_bin(star_cat = self.mock_too_good_starcat_table,
                                                                       ref_star_cat = ref_star_cat,
                                                                       group_mode = False)

            assert star_bad_kstest_result.pvalue < star_kstest_result.pvalue
            if ref_star_cat is None:
                assert star_too_good_kstest_result.pvalue < star_kstest_result.pvalue
            else:
                assert star_too_good_kstest_result.pvalue > DEFAULT_P_FAIL

    def test_plot_psf_res_sp_for_bin(self):
        """ Test that a figure is properly generated for data in individual bins.
        """

        snr_test_case_info = find_test_case_info(l_test_case_info = L_PSF_RES_SP_TEST_CASE_INFO,
                                                 bin_parameters = BinParameters.SNR,
                                                 return_one = True)

        d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = [snr_test_case_info],
                                                            d_bin_limits = {BinParameters.SNR: self.l_bin_limits},
                                                            detections_table = self.mock_starcat_table,
                                                            bin_constraint_type = BinParameterBinConstraint)

        l_l_test_case_object_ids = d_l_l_test_case_object_ids[snr_test_case_info.name]

        for cumulative in (False, True):

            for ref_star_cat in (None, self.mock_ref_starcat_table):

                for bin_index in range(len(self.l_bin_limits) - 1):

                    l_test_case_object_ids = l_l_test_case_object_ids[bin_index]

                    if cumulative:
                        file_namer_type = PsfResSPCumHistFileNamer
                    else:
                        file_namer_type = PsfResSPHistFileNamer

                    hist_plotter = PsfResSPHistPlotter(star_cat = self.mock_starcat_table,
                                                       ref_star_cat = ref_star_cat,
                                                       file_namer = file_namer_type(
                                                           bin_parameter = self.bin_parameter,
                                                           bin_index = bin_index,
                                                           workdir = self.workdir),
                                                       bin_limits = self.l_bin_limits[bin_index:bin_index + 2],
                                                       l_ids_in_bin = l_test_case_object_ids,
                                                       l_ref_ids_in_bin = l_test_case_object_ids,
                                                       ks_test_result = KstestResult(0.1412, 0.2),
                                                       group_mode = False,
                                                       cumulative = cumulative)
                    hist_plotter.plot()

    def test_run_psf_res_val_test(self):
        """ Test that the function for testing across all bins works as expected.
        """

        for ref_star_cat in (None, self.mock_ref_starcat_table):

            d_l_kstest_results = run_psf_res_val_test(star_cat = self.mock_starcat_table,
                                                      ref_star_cat = ref_star_cat,
                                                      d_l_bin_limits = get_d_l_bin_limits(self.pipeline_config),
                                                      workdir = self.workdir)

            tc_tot = L_PSF_RES_SP_TEST_CASE_INFO[0]
            tc_snr = L_PSF_RES_SP_TEST_CASE_INFO[1]

            # Compare the results for the test cases and bins
            tot_kstest_result = d_l_kstest_results[tc_tot.name][0]
            l_snr_kstest_results = d_l_kstest_results[tc_snr.name]

            # Make sure they all pass
            assert 1.0 >= tot_kstest_result.pvalue > DEFAULT_P_FAIL
            assert 1.0 >= l_snr_kstest_results[0].pvalue > DEFAULT_P_FAIL
            assert 1.0 >= l_snr_kstest_results[1].pvalue > DEFAULT_P_FAIL

            # Make sure they aren't all the same
            assert (tot_kstest_result.pvalue == 1.0 or
                    not np.isclose(tot_kstest_result.pvalue, l_snr_kstest_results[0].pvalue))
            assert (l_snr_kstest_results[0].pvalue == 1.0 or
                    not np.isclose(l_snr_kstest_results[0].pvalue, l_snr_kstest_results[1].pvalue))

            # Check that the empty bin at the end has a NaN p value, as expected
            assert np.isnan(l_snr_kstest_results[2].pvalue)
