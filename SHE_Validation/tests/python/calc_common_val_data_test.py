""" @file calc_common_val_data_test.py

    Created 28 Oct 2021

    Unit tests of the calc_common_val_data.py module
"""

__updated__ = "2021-08-26"

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

import numpy as np
import pytest
from SHE_Validation.testing.mock_tables import (cleanup_mock_measurements_tables, cleanup_mock_mfc_table,
                                                write_mock_measurements_tables, write_mock_mfc_table, )
from astropy.table import Table
# noinspection PyProtectedMember
from py._path.local import LocalPath

from SHE_PPT.argument_parser import CA_MER_CAT, CA_SHE_MEAS
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.testing.mock_data import NUM_TEST_POINTS
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.CalcCommonValData import (defineSpecificProgramOptions, mainMethod, )
from SHE_Validation.argument_parser import CA_SHE_EXT_CAT
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory

EXTENDED_CATALOG_PRODUCT_FILENAME = "ext_mfc.xml"


class CCVDTestCase(SheTestCase):
    """ Tests for calculating common validation data.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> None:
        """ Get a mock argument parser we can use.
        """
        parser = defineSpecificProgramOptions()
        self.args = parser.parse_args([])

        setattr(self.args, CA_SHE_EXT_CAT, EXTENDED_CATALOG_PRODUCT_FILENAME)

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):

        super().teardown_class()
        if cls.workdir:
            cleanup_mock_measurements_tables(cls.workdir)
            cleanup_mock_mfc_table(cls.workdir)

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir: LocalPath):

        self._setup(tmpdir)

        # Write the mock input data and store filenames in the args
        meas_filename = write_mock_measurements_tables(self.workdir)
        setattr(self.args, CA_SHE_MEAS, meas_filename)

        mer_cat_filename = write_mock_mfc_table(self.workdir)
        setattr(self.args, CA_MER_CAT, mer_cat_filename)

    def test_run(self):
        """ Tests a complete run of calculating common validation data.
        """

        # Call to validation function
        mainMethod(self.args)

        # Load in the output data
        ext_cat_filename = getattr(self.args, CA_SHE_EXT_CAT)
        p = read_xml_product(ext_cat_filename, self.workdir)
        ext_cat_filename = p.get_data_filename()
        ext_cat = Table.read(os.path.join(self.workdir, ext_cat_filename))

        # Check that the data appears as expected

        # Check the length of the table
        assert len(ext_cat) == NUM_TEST_POINTS

        # First, check that all the bin data column names actually exist
        assert mfc_tf.snr in ext_cat.colnames
        assert mfc_tf.bg in ext_cat.colnames
        assert mfc_tf.colour in ext_cat.colnames
        assert mfc_tf.size in ext_cat.colnames
        assert mfc_tf.epoch in ext_cat.colnames

        # Check that data in these columns is as expected (where possible to do so)

        # Check Signal-to-noise
        assert np.allclose(ext_cat[mfc_tf.snr], ext_cat[mfc_tf.FLUX_VIS_APER] / ext_cat[mfc_tf.FLUXERR_VIS_APER])

        # Check Colour
        assert np.allclose(ext_cat[mfc_tf.colour], 2.5 * np.log10(ext_cat[mfc_tf.FLUX_VIS_APER] /
                                                                  ext_cat[mfc_tf.FLUX_NIR_STACK_APER]))

        # Check Size
        assert np.allclose(ext_cat[mfc_tf.size], ext_cat[mfc_tf.SEGMENTATION_AREA])
