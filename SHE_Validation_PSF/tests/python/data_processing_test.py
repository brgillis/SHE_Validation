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
import numpy as np

from SHE_PPT.argument_parser import CA_PIPELINE_CONFIG
from SHE_PPT.testing.mock_she_star_cat import MockSheStarCatTableGenerator
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.data_processing import test_psf_res_for_bin

MIN_ALLOWED_P = 0.05


class TestPsfDataProcessing(SheTestCase):
    """ Test case for PSF-Res validation test data processing code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def post_setup(self):
        """ Override parent setup, setting up data to work with here.
        """

        mock_starcat_table_gen = MockSheStarCatTableGenerator(workdir = self.workdir)
        self.mock_starcat_table = mock_starcat_table_gen.get_mock_table()

        setattr(self._args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.pipeline_config)

        return

    def test_test_psf_res_for_bin(self, local_setup):
        """ Test running the "test_psf_res_for_bin" function, using all data in the table.
        """

        # Run a test for individual stars
        star_kstest_result = test_psf_res_for_bin(star_cat = self.mock_starcat_table,
                                                  group_mode = False)

        # And for the group
        group_kstest_result = test_psf_res_for_bin(star_cat = self.mock_starcat_table,
                                                   group_mode = True)

        # Check that the results are reasonable, and that the two modes are doing something different
        assert star_kstest_result.pvalue > MIN_ALLOWED_P
        assert group_kstest_result.pvalue > MIN_ALLOWED_P

        assert not np.isclose(star_kstest_result.pvalue, group_kstest_result.pvalue)

    pass
