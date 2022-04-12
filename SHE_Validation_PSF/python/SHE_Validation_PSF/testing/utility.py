""" @file utility.py

    Created 12 April 2022 by Bryan Gillis

    Utility functions and classes for testing of SHE_Validation_PSF code
"""

__updated__ = "2021-10-05"

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
from SHE_PPT.file_io import read_product_and_table
from SHE_Validation.testing.utility import SheValTestCase
from SHE_Validation_PSF.testing.mock_data import MockRefValStarCatTableGenerator, MockValStarCatTableGenerator


class SheValPsfTestCase(SheValTestCase):
    """Test case base class which defines convenience methods to create test data.
    """

    def _make_mock_ref_starcat_product(self):
        mock_ref_starcat_table_gen = MockRefValStarCatTableGenerator(workdir = self.workdir)
        mock_ref_starcat_product_filename = mock_ref_starcat_table_gen.write_mock_product()
        (self.mock_ref_starcat_product,
         self.mock_ref_starcat_table) = read_product_and_table(mock_ref_starcat_product_filename,
                                                               workdir = self.workdir)

    def _make_mock_starcat_product(self):
        mock_starcat_table_gen = MockValStarCatTableGenerator(workdir = self.workdir)
        mock_starcat_product_filename = mock_starcat_table_gen.write_mock_product()
        (self.mock_starcat_product,
         self.mock_starcat_table) = read_product_and_table(mock_starcat_product_filename,
                                                           workdir = self.workdir)
