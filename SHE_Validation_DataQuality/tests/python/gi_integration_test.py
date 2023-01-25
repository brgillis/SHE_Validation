"""
:file: tests/python/gi_integration_test.py

:date: 09/26/22
:author: Bryan Gillis

Integration test of the GalInfo validation test
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

from SHE_PPT.testing.mock_measurements_cat import EST_TABLE_PRODUCT_FILENAME
from SHE_PPT.testing.mock_mer_final_cat import MFC_TABLE_PRODUCT_FILENAME
from SHE_Validation.argument_parser import CA_MER_CAT_PROD, CA_SHE_CAT, CA_SHE_CHAINS, CA_SHE_TEST_RESULTS
from SHE_Validation.testing.mock_data import (SHE_CHAINS_PRODUCT_FILENAME,
                                              SHE_TEST_RESULTS_PRODUCT_FILENAME, )
from SHE_Validation_DataQuality.ValidateGalInfo import defineSpecificProgramOptions, mainMethod
from SHE_Validation_DataQuality.testing.utility import SheDQTestCase


class TestGalInfoRun(SheDQTestCase):
    """Test case for GalInfo validation test integration tests.
    """

    def _make_mock_args(self) -> Namespace:
        """ Get a mock argument parser we can use.

            This overrides the _make_mock_args() method of the SheTestCase class, which is called by the
            self.args property, setting the cached value self._args = self._make_mock_args() if self._args
            is None (which it will be when the object is initialized). This means that in each test case,
            self.args will return the result of this method (cached so that it only runs once).
        """
        parser = defineSpecificProgramOptions()
        args = parser.parse_args([])

        setattr(args, CA_SHE_CAT, EST_TABLE_PRODUCT_FILENAME)
        setattr(args, CA_SHE_CHAINS, SHE_CHAINS_PRODUCT_FILENAME)
        setattr(args, CA_MER_CAT_PROD, MFC_TABLE_PRODUCT_FILENAME)
        setattr(args, CA_SHE_TEST_RESULTS, SHE_TEST_RESULTS_PRODUCT_FILENAME)

        # The pipeline_config attribute of args isn't set here. This is because when parser.parse_args() is
        # called, it sets it to the default value of None. For the case of the pipeline_config, this is a
        # valid value, which will result in all defaults for configurable parameters being used.

        return args

    def post_setup(self):
        """ Override parent setup, creating data to work with in the workdir
        """

        # Create mock products and data to test
        self.make_gal_info_input()

    def test_gal_info_run(self, local_setup):
        """Test that the program runs without raising any uncaught exceptions.
        """

        # Call the mainMethod, to ensure we're testing the full executable
        mainMethod(self.args)