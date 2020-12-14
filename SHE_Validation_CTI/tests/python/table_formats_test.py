""" @file table_formats_test.py

    Created 14 December 2020

    Unit tests relating to table formats.
"""

__updated__ = "2020-12-14"

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

from astropy.table import Column, Table
import pytest

from SHE_PPT.table_utility import is_in_format
from SHE_Validation.table_formats.cti_gal_object_data import tf as cgod_tf, initialise_cti_gal_object_data_table
import numpy as np


class TestTableFormats:
    """


    """

    @classmethod
    def setup_class(cls):
        # Define a list of the table formats we'll be testing
        cls.formats_and_initializers = [(cgod_tf, initialise_cti_gal_object_data_table),
                                        ]
        # (, ),

        cls.formats, cls.initializers = zip(*cls.formats_and_initializers)

        cls.filename_base = "test_table"

        cls.filenames = [cls.filename_base + ".ecsv", cls.filename_base + ".fits"]

        return

    @classmethod
    def teardown_class(cls):
        del cls.formats, cls.initializers

        for filename in cls.filenames:
            if os.path.exists(filename):
                os.remove(filename)

        return

    def test_is_in_format(self):
        # Test each format is detected correctly
        # TODO: This is copied from SHE_PPT. Should move to its own function and reuse that code instead of copying.

        empty_tables = []

        for init in self.initializers:
            empty_tables.append(init())

        assert len(self.initializers) == len(self.formats)

        for i in range(len(self.initializers)):

            # Try strict test
            for j in range((len(self.formats))):
                if i == j and not is_in_format(empty_tables[i], self.formats[j], strict=True):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " doesn't initialize a valid table" +
                                    " in strict test.")
                elif i != j and is_in_format(empty_tables[i], self.formats[j], strict=True):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " resolves true for tables of format " + self.formats[i].m.table_format +
                                    " in strict test.")

            # Try non-strict version now
            empty_tables[i].add_column(Column(name='new_column', data=np.zeros((0,))))
            for j in range((len(self.formats))):
                if i == j and not is_in_format(empty_tables[i], self.formats[j], strict=False):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " doesn't initialize a valid table" +
                                    " in non-strict test.")
                elif i != j and is_in_format(empty_tables[i], self.formats[j], strict=False):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " resolves true for tables of format " + self.formats[i].m.table_format +
                                    " in non-strict test.")

        return
