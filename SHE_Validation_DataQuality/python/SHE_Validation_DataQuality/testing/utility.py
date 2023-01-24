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

from SHE_PPT.testing.utility import SheTestCase

from SHE_PPT.file_io import write_xml_product
from SHE_PPT.products.she_lensmc_chains import create_dpd_she_lensmc_chains
from SHE_PPT.products.she_measurements import create_dpd_she_measurements
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_formats.she_lensmc_measurements import lensmc_measurements_table_format
from SHE_PPT.testing.constants import LENSMC_MEASUREMENTS_TABLE_FILENAME, MEASUREMENTS_TABLE_PRODUCT_FILENAME
from SHE_Validation.testing.mock_data import (SHE_CHAINS_PRODUCT_FILENAME,
                                              SHE_CHAINS_TABLE_FILENAME, )


class SheDQTestCase(SheTestCase):
    """A test case which provides useful utilities for DataQuality validation tests.
    """

    def make_data_proc_input(self):
        """Makes data in the workdir needed to run DataProc validation tests.
        """
        she_cat = lensmc_measurements_table_format.init_table(size=1)
        she_cat.write(os.path.join(self.workdir, LENSMC_MEASUREMENTS_TABLE_FILENAME))

        p_she_cat = create_dpd_she_measurements(LensMC_filename=LENSMC_MEASUREMENTS_TABLE_FILENAME)
        write_xml_product(p_she_cat, MEASUREMENTS_TABLE_PRODUCT_FILENAME, workdir=self.workdir)

        she_chains = lensmc_chains_table_format.init_table(size=1)
        she_chains.write(os.path.join(self.workdir, SHE_CHAINS_TABLE_FILENAME))

        p_she_chains = create_dpd_she_lensmc_chains(SHE_CHAINS_TABLE_FILENAME)
        write_xml_product(p_she_chains, SHE_CHAINS_PRODUCT_FILENAME, workdir=self.workdir)
