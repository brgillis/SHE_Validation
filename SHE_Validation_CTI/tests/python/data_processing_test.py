""" @file data_processing_test.py

    Created 15 December 2020

    Unit tests of the data_processing.py module
"""

__updated__ = "2020-12-16"

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
import time

from astropy import table
import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT import mdb
from SHE_PPT.file_io import read_xml_product, find_file, read_listfile
from SHE_PPT.logging import getLogger
from SHE_Validation_CTI import constants
from SHE_Validation_CTI.data_processing import add_readout_register_distance
from SHE_Validation_CTI.table_formats.cti_gal_object_data import tf as cgod_tf, initialise_cti_gal_object_data_table
import numpy as np


test_data_location = "SHE_PPT_8_5"

# Input data filenames
mdb_filename = "sample_mdb-SC8.xml"


class TestCase:
    """


    """

    @classmethod
    def setup_class(cls):

        # Download the MDB from WebDAV
        sync_mdb = DataSync("testdata/sync.conf", "testdata/test_mdb.txt")
        sync_mdb.download()
        qualified_mdb_filename = sync_datastack.absolutePath(
            os.path.join(test_data_location, mdb_filename))
        assert os.path.isfile(
            qualified_mdb_filename), f"Cannot find file: {qualified_mdb_filename}"

        mdb.init(mdb_files=qualified_mdb_filename)

        # Get the workdir based on where the mdb file is
        cls.workdir = os.path.split(qualified_mdb_filename)[0]
        cls.logdir = os.path.join(cls.workdir, "logs")

        return

    @classmethod
    def teardown_class(cls):

        return

    def test_add_readout_register_distance(self):

        # Get the detector y-size from the MDB
        det_size_y = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
        assert det_size_y == 4136  # Calculations here rely on this being the value

        # Make some mock data
        mock_y_data = np.array([-100., 0., 500., 1000., 2000., 3000., 4000., 5000.])

        mock_data_table = initialise_cti_gal_object_data_table(init_cols={cgod_tf.y: mock_y_data})

        # Run the function
        add_readout_register_distance(mock_data_table)

        # Check the results are as expected
        ro_dist = mock_data_table[cgod_tf.readout_dist]

        assert np.allclose(ro_dist, np.array([-100., 0., 500., 1000., 2000., 1136., 136., -864.]))

        return
