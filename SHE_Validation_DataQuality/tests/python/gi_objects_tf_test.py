"""
:file: tests/python/gi_objects_tf_test.py

:date: 02/03/23
:author: Bryan Gillis

Tests of the GID Objects table format
"""
import itertools
import os

import pytest
from astropy.table import Table

from SHE_PPT.table_utility import is_in_format
from SHE_Validation_DataQuality.constants.gid_criteria import L_GID_CRITERIA
from SHE_Validation_DataQuality.gi_data_processing import TEXTFILE_TABLE_EXTENSION, TEXTFILE_TABLE_FORMAT
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

from SHE_Validation_DataQuality.table_formats.gid_objects import GIDC_TF, GIDM_TF, GID_IS_CHAIN, GID_MAX, GID_MIN
from SHE_Validation_DataQuality.testing.utility import SheDQTestCase


class TestGIDObjectsTableFormat(SheDQTestCase):
    """Test case for GID Objects table format
    """

    TABLE_SIZE = 10

    @pytest.fixture
    def mock_gid_meas_table(self) -> Table:
        """Pytest fixture providing a mock GID Objects table for testing
        """

        return GIDM_TF.init_table(size=self.TABLE_SIZE)

    @pytest.fixture
    def mock_gid_chains_table(self) -> Table:
        """Pytest fixture providing a mock GID Objects table for testing
        """

        return GIDC_TF.init_table(size=self.TABLE_SIZE)

    def test_table_defaults(self, mock_gid_meas_table, mock_gid_chains_table):
        """Test that the default table is set up as expected.
        """

        for table, tf in ((mock_gid_meas_table, GIDM_TF),
                          (mock_gid_chains_table, GIDC_TF)):

            self._check_table(table, tf)

    def test_table_rw(self, mock_gid_meas_table, mock_gid_chains_table):
        """Test that a table survives being written out and read back in.
        """

        qualified_table_filename = os.path.join(self.workdir, f"test_table{TEXTFILE_TABLE_EXTENSION}")

        for table, tf in ((mock_gid_meas_table, GIDM_TF),
                          (mock_gid_chains_table, GIDC_TF)):

            table.write(qualified_table_filename, overwrite=True, format=TEXTFILE_TABLE_FORMAT)
            table_read_in = Table.read(qualified_table_filename, format=TEXTFILE_TABLE_FORMAT)

            self._check_table(table_read_in, tf)

    def _check_table(self, table, tf):
        """Run common checks on a table, ensuring that it is as expected.
        """

        # Do some basic checks on the table
        assert is_in_format(table, tf, verbose=True)
        assert len(table) == self.TABLE_SIZE

        # Check that metadata is set up as expected

        assert table.meta[tf.m.fits_version] == tf.m.__version__
        assert table.meta[tf.m.fits_def] == tf.m.table_format

        for gid_criteria, prop in itertools.product(L_GID_CRITERIA, (GID_MIN,
                                                                     GID_MAX,
                                                                     GID_IS_CHAIN)):
            attr = gid_criteria.attr
            attr_prop = f"{attr}_{prop}"
            meta_key = getattr(tf.m, attr_prop)

            assert table.meta[meta_key] == getattr(gid_criteria, prop), f"{attr=}, {prop=}"
