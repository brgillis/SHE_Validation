"""
:file: tests/python/pr_sp_integration_test.py

:date: 8 March 2022
:author: Bryan Gillis

Unit tests the input/output interface of the PSF-Res validation task.
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

import os
from argparse import Namespace

from SHE_PPT.argument_parser import CA_SHE_STAR_CAT
from SHE_PPT.testing.constants import STAR_CAT_PRODUCT_FILENAME
from SHE_Validation.argument_parser import CA_SHE_TEST_RESULTS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.ValidatePSFResStarPos import defineSpecificProgramOptions, mainMethod
# Output data filenames
from SHE_Validation_PSF.argument_parser import CA_REF_SHE_STAR_CAT
from SHE_Validation_PSF.results_reporting import PSF_RES_SP_DIRECTORY_FILENAME
from SHE_Validation_PSF.testing.constants import REF_STAR_CAT_PRODUCT_FILENAME
from SHE_Validation_PSF.testing.utility import SheValPsfTestCase

SHE_TEST_RESULTS_PRODUCT_FILENAME = "she_validation_test_results.xml"


class TestPsfResRun(SheValPsfTestCase):
    """ Test case for PSF-Res validation test code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> Namespace:
        """ Get a mock argument parser we can use.

            This overrides the _make_mock_args() method of the SheTestCase class, which is called by the
            self.args property, setting the cached value self._args = self._make_mock_args() if self._args
            is None (which it will be when the object is initialized). This means that in each test case,
            self.args will return the result of this method (cached so that it only runs once).
        """
        args = defineSpecificProgramOptions().parse_args([])

        setattr(args, CA_SHE_STAR_CAT, STAR_CAT_PRODUCT_FILENAME)
        setattr(args, CA_REF_SHE_STAR_CAT, REF_STAR_CAT_PRODUCT_FILENAME)
        setattr(args, CA_SHE_TEST_RESULTS, SHE_TEST_RESULTS_PRODUCT_FILENAME)

        # The pipeline_config attribute of args isn't set here. This is because when parser.parse_args() is
        # called, it sets it to the default value of None. For the case of the pipeline_config, this is a
        # valid value, which will result in all defaults for configurable parameters being used.

        return args

    def post_setup(self) -> None:
        """ Override parent setup, setting up data to work with here.
        """

        self._write_mock_starcat_product()
        self._write_mock_ref_starcat_product()

        return

    def test_psf_res_integration(self):
        """ "Integration" test of the full executable, using the unit-testing framework so it can be run automatically.
        """

        # Call to validation function, which was imported directly from the entry-point file
        mainMethod(self.args)

        # Check the resulting data product and plots exist in the expected locations

        workdir = self.workdir
        output_filename = getattr(self.args, CA_SHE_TEST_RESULTS)
        qualified_output_filename = os.path.join(workdir, output_filename)

        assert os.path.isfile(qualified_output_filename)

        # Check the data product exists, as do the expected analysis files
        assert os.path.isfile(qualified_output_filename)

        self._check_ana_files(qualified_test_results_filename=qualified_output_filename,
                              test_id_substring="tot",
                              directory_filename=PSF_RES_SP_DIRECTORY_FILENAME,
                              l_ex_keys=["tot-0-hist", "tot-scatter"])
