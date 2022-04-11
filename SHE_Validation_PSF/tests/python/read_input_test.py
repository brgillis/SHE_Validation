""" @file read_input_test.py

    Created 10 March 2022 by Bryan Gillis

    Unit tests of reading in input data for the PSF Residual validation test.
"""

__updated__ = "2022-04-10"

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
from SHE_PPT.file_io import read_product_and_table
from SHE_PPT.testing.constants import STAR_CAT_PRODUCT_FILENAME, STAR_CAT_TABLE_FILENAME
from SHE_PPT.testing.mock_she_star_cat import MockStarCatTableGenerator
from SHE_PPT.testing.utility import SheTestCase
# Output data filenames
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.testing.constants import DEFAULT_MOCK_BIN_LIMITS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.ValidatePSFResStarPos import defineSpecificProgramOptions
from SHE_Validation_PSF.argument_parser import CA_REF_SHE_STAR_CAT
from SHE_Validation_PSF.validate_psf_res_star_pos import load_psf_res_input

REF_STAR_CAT_PRODUCT_FILENAME = "reference_star_cat_product.xml"
REF_STAR_CAT_TABLE_FILENAME = "data/reference_star_cat_table.fits"


class TestPsfResReadInput(SheTestCase):
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

        mock_starcat_table_gen = MockStarCatTableGenerator(table_filename = STAR_CAT_TABLE_FILENAME,
                                                           product_filename = STAR_CAT_PRODUCT_FILENAME,
                                                           workdir = self.workdir)
        mock_starcat_product_filename = mock_starcat_table_gen.write_mock_product()
        (self.mock_starcat_product,
         self.mock_starcat_table) = read_product_and_table(mock_starcat_product_filename,
                                                           workdir = self.workdir)

        mock_ref_starcat_table_gen = MockStarCatTableGenerator(seed = mock_starcat_table_gen.seed + 1,
                                                               table_filename = REF_STAR_CAT_TABLE_FILENAME,
                                                               product_filename = REF_STAR_CAT_PRODUCT_FILENAME,
                                                               workdir = self.workdir)
        mock_ref_starcat_product_filename = mock_ref_starcat_table_gen.write_mock_product()
        (self.mock_ref_starcat_product,
         self.mock_ref_starcat_table) = read_product_and_table(mock_ref_starcat_product_filename,
                                                               workdir = self.workdir)

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
        assert self.mock_starcat_product.Header.ProductId == psf_res_sp_input.p_star_cat.Header.ProductId
        assert (self.mock_starcat_table == psf_res_sp_input.star_cat).all()
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
        assert self.mock_starcat_product.Header.ProductId == psf_res_sp_input.p_star_cat.Header.ProductId
        assert (self.mock_starcat_table == psf_res_sp_input.star_cat).all()
        assert self.mock_ref_starcat_product.Header.ProductId == psf_res_sp_input.p_ref_star_cat.Header.ProductId
        assert (self.mock_ref_starcat_table == psf_res_sp_input.ref_star_cat).all()
