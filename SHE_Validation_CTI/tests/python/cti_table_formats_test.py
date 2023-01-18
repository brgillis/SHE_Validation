"""
:file: tests/python/cti_table_formats_test.py

:date: 14 December 2020
:author: Bryan Gillis

Unit tests relating to table formats
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
from typing import List

from SHE_PPT.table_utility import SheTableFormat
# noinspection PyProtectedMember
from SHE_PPT.testing.tables import _test_is_in_format
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF
from SHE_Validation_CTI.table_formats.regression_results import TF as RR_TF


class TestTableFormats:
    """
    """

    formats: List[SheTableFormat]
    filename_base: str
    filenames: List[str]

    @classmethod
    def setup_class(cls):
        # Define a list of the table formats we'll be testing
        cls.formats = [CGOD_TF, RR_TF, ]

        cls.filename_base = "test_table"

        cls.filenames = [cls.filename_base + ".ecsv", cls.filename_base + ".fits"]

    @classmethod
    def teardown_class(cls):
        del cls.formats

        for filename in cls.filenames:
            if os.path.exists(filename):
                os.remove(filename)

    def test_is_in_format(self):

        # Call the test stored in the table_testing module
        _test_is_in_format(self.formats)
