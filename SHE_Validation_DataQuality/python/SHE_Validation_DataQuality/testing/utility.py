"""
:file: python/SHE_Validation_DataQuality/testing/utility.py

:date: 24 January 2023
:author: Bryan Gillis

Utility functions and classes for testing of SHE_Validation_DataQuality code
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

from SHE_PPT.testing.mock_measurements_cat import MockShearEstimateTableGenerator
from SHE_PPT.testing.mock_mer_final_cat import MockMFCGalaxyTableGenerator
from SHE_PPT.testing.utility import SheTestCase

from SHE_PPT.file_io import write_xml_product
from SHE_PPT.products.she_lensmc_chains import create_dpd_she_lensmc_chains
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_Validation.testing.mock_data import (SHE_CHAINS_PRODUCT_FILENAME,
                                              SHE_CHAINS_TABLE_FILENAME, )


class SheDQTestCase(SheTestCase):
    """A test case which provides useful utilities for DataQuality validation tests.
    """

    TABLE_SIZE = 10

    def make_data_proc_input(self):
        """Makes data in the workdir needed to run DataProc validation tests.
        """

        MockShearEstimateTableGenerator(num_test_points=self.TABLE_SIZE, workdir=self.workdir).write_mock_product()

        she_chains = lensmc_chains_table_format.init_table(size=self.TABLE_SIZE)
        she_chains.write(os.path.join(self.workdir, SHE_CHAINS_TABLE_FILENAME))

        p_she_chains = create_dpd_she_lensmc_chains(SHE_CHAINS_TABLE_FILENAME)
        write_xml_product(p_she_chains, SHE_CHAINS_PRODUCT_FILENAME, workdir=self.workdir)

    def make_gal_info_input(self):
        """Makes data in the workdir needed to run GalInfo validation tests.
        """

        # Create the DataProc info, since this data is a superset of that
        self.make_data_proc_input()

        MockMFCGalaxyTableGenerator(num_test_points=self.TABLE_SIZE, workdir=self.workdir).write_mock_product()
