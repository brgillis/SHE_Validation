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

from SHE_Validation_DataQuality.constants.gal_info_test_info import L_GAL_INFO_TEST_CASE_INFO
from SHE_Validation_DataQuality.gi_data_processing import get_gal_info_test_results
from SHE_Validation_DataQuality.testing.utility import SheDQTestCase


class TestGalInfoGalInfoessing(SheDQTestCase):
    """Test case for GalInfo validation test data processing
    """

    def post_setup(self):
        """Override parent setup, creating common data for each test
        """

        self.make_mock_gal_info_input()

    def test_good_input(self):
        """Unit test of the `get_gal_info_test_results` method with completely-good input
        """

        d_l_test_results = get_gal_info_test_results(self.good_gi_input)

        # Check that all results are as expected
        for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
            name = test_case_info.name
            id = test_case_info.id

            test_results = d_l_test_results[name][0]

            assert test_results.global_passed, f"{name=}"
