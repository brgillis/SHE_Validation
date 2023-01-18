"""
:file: tests/python/dp_input_test.py

:date: 01/18/23
:author: Bryan Gillis

Tests of function to read in input data for the DataProc test
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

from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.testing.mock_data import (SHE_RECONCILED_CHAINS_PRODUCT_FILENAME,
                                              SHE_RECONCILED_MEASUREMENTS_PRODUCT_FILENAME, )
from SHE_Validation_DataQuality.dp_input import read_data_proc_input


class TestDataProcInput(SheTestCase):
    """Test case for DataProc validation test integration tests.
    """

    def setup_workdir(self):
        """ Override parent setup, downloading data to work with here.
        """

        self._download_datastack(read_in=False)

    def test_read_input(self):
        """Test that the program runs without raising any uncaught exceptions.
        """

        data_proc_input = read_data_proc_input(p_rec_cat_filename=SHE_RECONCILED_MEASUREMENTS_PRODUCT_FILENAME,
                                               p_rec_chains_filename=SHE_RECONCILED_CHAINS_PRODUCT_FILENAME,
                                               workdir=self.workdir)
