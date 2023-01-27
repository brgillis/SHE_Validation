"""
:file: tests/python/pr_sp_read_input_test.py

:date: 10 March 2022
:author: Bryan Gillis

Unit tests of reading in input data for the PSF Residual validation test
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

from argparse import Namespace
from copy import deepcopy

import numpy as np

from SHE_PPT.argument_parser import CA_PIPELINE_CONFIG, CA_SHE_STAR_CAT
from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_PPT.testing.constants import STAR_CAT_PRODUCT_FILENAME
from SHE_Validation.binning.bin_data import add_bin_columns
from SHE_Validation.binning.utility import get_d_l_bin_limits
from SHE_Validation.constants.default_config import DEFAULT_N_BIN_LIMITS_QUANTILES, STR_AUTO_BIN_LIMITS_HEAD
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.testing.constants import DEFAULT_MOCK_BIN_LIMITS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.ValidatePSFResStarPos import defineSpecificProgramOptions
from SHE_Validation_PSF.argument_parser import CA_REF_SHE_STAR_CAT
from SHE_Validation_PSF.constants.psf_res_sp_test_info import L_PSF_RES_SP_BIN_PARAMETERS
from SHE_Validation_PSF.testing.constants import REF_STAR_CAT_PRODUCT_FILENAME
from SHE_Validation_PSF.testing.utility import SheValPsfTestCase
from SHE_Validation_PSF.validate_psf_res_star_pos import D_PSF_RES_SP_BIN_KEYS, load_psf_res_input


class TestPsfResReadInput(SheValPsfTestCase):
    """ Test case for PSF-Res validation test code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> Namespace:
        """ Get a mock argument parser we can use.
        """
        args = defineSpecificProgramOptions().parse_args([])
        setattr(args, CA_SHE_STAR_CAT, STAR_CAT_PRODUCT_FILENAME)

        return args

    def post_setup(self):
        """ Override parent setup, setting up data to work with here.
        """

        # Create a star catalog table and product, and a reference version
        self._write_mock_starcat_product()
        self._write_mock_ref_starcat_product()

        setattr(self._args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.pipeline_config)

        return

    def test_read_input_no_ref(self, local_setup):
        """ Test of reading in just a star catalog
        """

        # Make sure we're set to not load a reference star catalog
        d_args = deepcopy(self.d_args)
        d_args[CA_REF_SHE_STAR_CAT] = None

        psf_res_sp_input = load_psf_res_input(d_args, self.workdir)

        # Check that the input is as expected
        np.testing.assert_allclose(psf_res_sp_input.d_l_bin_limits[BinParameters.SNR], DEFAULT_MOCK_BIN_LIMITS)

        # Check that star catalog matches expectation
        assert (self.mock_starcat_product.Header.ProductId.value() ==
                psf_res_sp_input.p_star_cat.Header.ProductId.value())
        assert (self.mock_starcat_table == psf_res_sp_input.star_cat).all()

        # Check that we didn't load a reference star catalog
        assert psf_res_sp_input.p_ref_star_cat is None
        assert psf_res_sp_input.ref_star_cat is None

    def test_read_input_with_ref(self, local_setup):
        """ Test of reading in both a star catalog and a reference star catalog
        """

        # Make sure we're set to not load a reference star catalog
        d_args = deepcopy(self.d_args)
        d_args[CA_REF_SHE_STAR_CAT] = REF_STAR_CAT_PRODUCT_FILENAME

        psf_res_sp_input = load_psf_res_input(d_args, self.workdir)

        # Check that the input is as expected
        np.testing.assert_allclose(psf_res_sp_input.d_l_bin_limits[BinParameters.SNR], DEFAULT_MOCK_BIN_LIMITS)

        # Check that star catalog matches expectation
        assert (self.mock_starcat_product.Header.ProductId.value() ==
                psf_res_sp_input.p_star_cat.Header.ProductId.value())
        assert (self.mock_starcat_table == psf_res_sp_input.star_cat).all()

        # Check that reference star catalog matches expectation (with binning columns added)
        assert (self.mock_ref_starcat_product.Header.ProductId.value() ==
                psf_res_sp_input.p_ref_star_cat.Header.ProductId.value())

        ex_mock_ref_star_cat = deepcopy(self.mock_ref_starcat_table)
        add_bin_columns(ex_mock_ref_star_cat, data_stack=None, l_bin_parameters=L_PSF_RES_SP_BIN_PARAMETERS)

        assert np.all(ex_mock_ref_star_cat == psf_res_sp_input.ref_star_cat)

        # Check that the star catalog and reference star catalog don't match
        assert np.all(psf_res_sp_input.star_cat != psf_res_sp_input.ref_star_cat)

    def test_config_bin_limits(self):
        """ Test the bin limits from the pipeline config are interpreted properly.
        """

        # Create a copy of the pipeline_config which we'll modify here
        pipeline_config_cpy = deepcopy(self.pipeline_config)

        num_global_bins = 2
        num_local_bins = 3
        num_default_bins = DEFAULT_N_BIN_LIMITS_QUANTILES

        # Check if the defaults are the same as one of the test values - if so, test values will need update
        assert ((num_global_bins != num_default_bins) and (num_local_bins != num_default_bins) and
                (num_global_bins != num_default_bins)), ("Number of bins for test global, local, and default cases "
                                                         "must all differ for test to be run properly.")

        test_global_val = f"{STR_AUTO_BIN_LIMITS_HEAD}-{num_global_bins}"
        test_local_val = f"{STR_AUTO_BIN_LIMITS_HEAD}-{num_local_bins}"

        # We'll test four cases here - setting/not setting each of the global key and local key
        for (set_global, set_local, ex_num_bins) in ((False, False, num_default_bins),
                                                     (False, True, num_local_bins),
                                                     (True, False, num_global_bins),
                                                     (True, True, num_local_bins),
                                                     ):

            # Set pipeline config values as desired

            if set_global:
                pipeline_config_cpy[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] = test_global_val
            elif ValidationConfigKeys.VAL_SNR_BIN_LIMITS in pipeline_config_cpy:
                del pipeline_config_cpy[ValidationConfigKeys.VAL_SNR_BIN_LIMITS]

            if set_local:
                pipeline_config_cpy[ValidationConfigKeys.PRSP_SNR_BIN_LIMITS] = test_local_val
            elif ValidationConfigKeys.PRSP_SNR_BIN_LIMITS in pipeline_config_cpy:
                del pipeline_config_cpy[ValidationConfigKeys.PRSP_SNR_BIN_LIMITS]

            # Generate a dict of bin limits
            d_l_bin_limits = get_d_l_bin_limits(pipeline_config_cpy,
                                                bin_data_table=self.mock_starcat_table,
                                                l_bin_parameters=L_PSF_RES_SP_BIN_PARAMETERS,
                                                d_local_bin_keys=D_PSF_RES_SP_BIN_KEYS)

            l_snr_bin_limits = d_l_bin_limits[BinParameters.SNR]

            # Check that we got the right limits by testing the length
            assert len(l_snr_bin_limits) == ex_num_bins + 1
