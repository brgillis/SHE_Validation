"""
:file: tests/python/gi_input_test.py

:date: 01/24/23
:author: Bryan Gillis

Tests of function to read in input data for the GalInfo test
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
import re

from SHE_PPT.constants.misc import DATA_SUBDIR
from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.table_formats.mer_final_catalog import mer_final_catalog_format
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.testing.mock_measurements_cat import EST_TABLE_PRODUCT_FILENAME
from SHE_PPT.testing.mock_mer_final_cat import MFC_TABLE_PRODUCT_FILENAME
from SHE_Validation.testing.mock_data import SHE_CHAINS_PRODUCT_FILENAME
from SHE_Validation_DataQuality.gi_input import read_gal_info_input
from SHE_Validation_DataQuality.testing.utility import (BAD_FILENAME, ERR_NO_FILE_PATTERN, ERR_READING_FILE_PATTERN,
                                                        SheDQTestCase, )
from ST_DataModelBindings.dpd.mer.raw.finalcatalog_stub import dpdMerFinalCatalog


class TestGalInfoInput(SheDQTestCase):
    """Test case for DataProc validation test reading of input data
    """

    def post_setup(self):
        """ Override parent setup, creating data to work with in the workdir
        """

        # Create mock products and data to test
        self.make_gal_info_input()

    def test_read_input_default(self):
        """Test that data is read in as expected in the default case (only LensMC data)
        """

        gal_info_input = read_gal_info_input(p_she_cat_filename=EST_TABLE_PRODUCT_FILENAME,
                                             p_she_chains_filename=SHE_CHAINS_PRODUCT_FILENAME,
                                             p_mer_cat_filename=MFC_TABLE_PRODUCT_FILENAME,
                                             workdir=self.workdir)

        # Check that the read-in input is as expected. The data shared with the DataProc test is checked in that test
        # case, so we only need to look at the unique data here

        assert isinstance(gal_info_input.p_mer_cat, dpdMerFinalCatalog), gal_info_input.err_p_mer_cat
        assert gal_info_input.err_p_mer_cat is None

        assert is_in_format(gal_info_input.mer_cat, mer_final_catalog_format, verbose=True)
        assert gal_info_input.err_mer_cat is None

    def test_read_input_missing_products(self):
        """Test data is read in as expected when products are missing.
        """

        gal_info_input = read_gal_info_input(p_she_cat_filename=EST_TABLE_PRODUCT_FILENAME,
                                             p_she_chains_filename=SHE_CHAINS_PRODUCT_FILENAME,
                                             p_mer_cat_filename=BAD_FILENAME,
                                             workdir=self.workdir)

        # Check that the read-in input is as expected, again only checking data unique to this test

        assert gal_info_input.p_mer_cat is None
        chains_regex_match = re.match(ERR_READING_FILE_PATTERN, gal_info_input.err_p_mer_cat)
        assert chains_regex_match
        assert chains_regex_match.groups()[0] == os.path.join(self.workdir, BAD_FILENAME)

        assert gal_info_input.mer_cat is None
        assert gal_info_input.err_mer_cat is None

    def test_read_input_missing_cats(self):
        """Test data is read in as expected when catalogs are missing.
        """

        # Make copies of the products which point to nonexistent catalogs

        mer_cat_missing_filename = "mer_cat_missing.xml"

        p_mer_cat = read_xml_product(MFC_TABLE_PRODUCT_FILENAME, workdir=self.workdir,
                                     product_type=dpdMerFinalCatalog)
        p_mer_cat.set_data_filename(BAD_FILENAME)
        write_xml_product(p_mer_cat, mer_cat_missing_filename, workdir=self.workdir)

        gal_info_input = read_gal_info_input(p_she_cat_filename=EST_TABLE_PRODUCT_FILENAME,
                                             p_she_chains_filename=SHE_CHAINS_PRODUCT_FILENAME,
                                             p_mer_cat_filename=mer_cat_missing_filename,
                                             workdir=self.workdir)

        # Check that the read-in input is as expected, again only checking data unique to this test

        assert isinstance(gal_info_input.p_mer_cat, dpdMerFinalCatalog), gal_info_input.err_p_mer_cat
        assert gal_info_input.err_p_mer_cat is None

        assert gal_info_input.mer_cat is None
        regex_match = re.match(ERR_NO_FILE_PATTERN, gal_info_input.err_mer_cat)
        assert regex_match, f"Value '{gal_info_input.err_mer_cat}' does not match regex pattern " \
                            f"{ERR_NO_FILE_PATTERN}"
        assert regex_match.groups()[0] == os.path.join(self.workdir, DATA_SUBDIR, BAD_FILENAME)
