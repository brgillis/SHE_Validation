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

import os
import re

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.misc import DATA_SUBDIR
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.products.she_lensmc_chains import create_dpd_she_lensmc_chains
from SHE_PPT.products.she_validated_measurements import create_dpd_she_validated_measurements
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_formats.she_lensmc_measurements import lensmc_measurements_table_format
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.testing.constants import LENSMC_MEASUREMENTS_TABLE_FILENAME, MEASUREMENTS_TABLE_PRODUCT_FILENAME
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.testing.mock_data import (SHE_CHAINS_PRODUCT_FILENAME,
                                              SHE_CHAINS_TABLE_FILENAME, )
from SHE_Validation.testing.utility import compile_regex
from SHE_Validation_DataQuality.dp_input import ERR_MEASUREMENTS_NONE, read_data_proc_input
from ST_DataModelBindings.dpd.she.raw.lensmcchains_stub import dpdSheLensMcChains
from ST_DataModelBindings.dpd.she.raw.validatedmeasurements_stub import dpdSheValidatedMeasurements

BAD_FILENAME = "junk"
ERR_READING_FILE_PATTERN = compile_regex("Error reading file %s.")
ERR_NO_FILE_PATTERN = compile_regex("[Errno 2] No such file or directory: '%s'")


class TestDataProcInput(SheTestCase):
    """Test case for DataProc validation test reading of input data
    """

    def post_setup(self):
        """ Override parent setup, creating data to work with in the workdir
        """

        # Create mock products to test

        she_cat = lensmc_measurements_table_format.init_table(size=1)
        she_cat.write(os.path.join(self.workdir, LENSMC_MEASUREMENTS_TABLE_FILENAME))

        p_she_cat = create_dpd_she_validated_measurements(LensMC_filename=LENSMC_MEASUREMENTS_TABLE_FILENAME)
        write_xml_product(p_she_cat, MEASUREMENTS_TABLE_PRODUCT_FILENAME, workdir=self.workdir)

        she_chains = lensmc_chains_table_format.init_table(size=1)
        she_chains.write(os.path.join(self.workdir, SHE_CHAINS_TABLE_FILENAME))

        p_she_chains = create_dpd_she_lensmc_chains(SHE_CHAINS_TABLE_FILENAME)
        write_xml_product(p_she_chains, SHE_CHAINS_PRODUCT_FILENAME, workdir=self.workdir)

    def test_read_input_default(self):
        """Test that data is read in as expected in the default case (only LensMC data)
        """

        data_proc_input = read_data_proc_input(p_she_cat_filename=MEASUREMENTS_TABLE_PRODUCT_FILENAME,
                                               p_she_chains_filename=SHE_CHAINS_PRODUCT_FILENAME,
                                               workdir=self.workdir)

        # Check that the read-in input is as expected

        assert isinstance(data_proc_input.p_she_cat, dpdSheValidatedMeasurements), data_proc_input.err_p_she_cat
        assert data_proc_input.err_p_she_cat is None

        method_none_pattern = compile_regex(ERR_MEASUREMENTS_NONE)

        for method, tf in D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.items():
            if method == ShearEstimationMethods.LENSMC:
                assert is_in_format(table=data_proc_input.d_she_cat[method],
                                    table_format=lensmc_measurements_table_format,
                                    verbose=True), data_proc_input.d_err_she_cat[method]
                assert data_proc_input.d_err_she_cat[method] is None
            else:
                assert data_proc_input.d_she_cat[method] is None
                regex_match = re.match(method_none_pattern, data_proc_input.d_err_she_cat[method])
                assert regex_match.groups()[0] == method.value

        assert isinstance(data_proc_input.p_she_chains, dpdSheLensMcChains), data_proc_input.err_p_she_chains
        assert data_proc_input.err_p_she_chains is None

        assert is_in_format(data_proc_input.she_chains, lensmc_chains_table_format, verbose=True)
        assert data_proc_input.err_she_chains is None

    def test_read_input_missing_products(self):
        """Test data is read in as expected when products are missing.
        """

        data_proc_input = read_data_proc_input(p_she_cat_filename=BAD_FILENAME,
                                               p_she_chains_filename=BAD_FILENAME,
                                               workdir=self.workdir)

        # Check that the read-in input is as expected

        assert data_proc_input.p_she_cat is None
        cat_regex_match = re.match(ERR_READING_FILE_PATTERN, data_proc_input.err_p_she_cat)
        assert cat_regex_match
        assert cat_regex_match.groups()[0] == os.path.join(self.workdir, BAD_FILENAME)

        assert data_proc_input.d_she_cat is None
        assert data_proc_input.d_err_she_cat is None

        assert data_proc_input.p_she_chains is None
        chains_regex_match = re.match(ERR_READING_FILE_PATTERN, data_proc_input.err_p_she_chains)
        assert chains_regex_match
        assert cat_regex_match.groups()[0] == os.path.join(self.workdir, BAD_FILENAME)

        assert data_proc_input.she_chains is None
        assert data_proc_input.err_she_chains is None

        # Check that if the chains filename is None, it isn't flagged as an error

        data_proc_input_none_chains = read_data_proc_input(p_she_cat_filename=BAD_FILENAME,
                                                           p_she_chains_filename=None,
                                                           workdir=self.workdir)
        assert data_proc_input_none_chains.p_she_chains is None
        assert data_proc_input_none_chains.err_p_she_chains is None

    def test_read_input_missing_cats(self):
        """Test data is read in as expected when catalogs are missing.
        """

        # Make copies of the products which point to nonexistent catalogs

        she_cat_missing_filename = "she_cat_missing.xml"

        p_she_cat = read_xml_product(MEASUREMENTS_TABLE_PRODUCT_FILENAME, workdir=self.workdir,
                                     product_type=dpdSheValidatedMeasurements)
        p_she_cat.set_method_filename(ShearEstimationMethods.LENSMC, BAD_FILENAME)
        write_xml_product(p_she_cat, she_cat_missing_filename, workdir=self.workdir)

        she_chains_missing_filename = "she_chains_missing.xml"

        p_she_chains = read_xml_product(SHE_CHAINS_PRODUCT_FILENAME, workdir=self.workdir,
                                        product_type=dpdSheLensMcChains)
        p_she_chains.set_data_filename(BAD_FILENAME)
        write_xml_product(p_she_chains, she_chains_missing_filename, workdir=self.workdir)

        data_proc_input = read_data_proc_input(p_she_cat_filename=she_cat_missing_filename,
                                               p_she_chains_filename=she_chains_missing_filename,
                                               workdir=self.workdir)

        # Check that the read-in input is as expected

        assert isinstance(data_proc_input.p_she_cat, dpdSheValidatedMeasurements), data_proc_input.err_p_she_cat
        assert data_proc_input.err_p_she_cat is None

        for method, tf in D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.items():
            if method == ShearEstimationMethods.LENSMC:
                assert data_proc_input.d_she_cat[method] is None
                regex_match = re.match(ERR_NO_FILE_PATTERN, data_proc_input.d_err_she_cat[method])
                assert regex_match, f"Value '{data_proc_input.d_err_she_cat[method]}' does not match regex pattern " \
                                    f"{ERR_NO_FILE_PATTERN}"
                assert regex_match.groups()[0] == os.path.join(self.workdir, DATA_SUBDIR, BAD_FILENAME)

        assert isinstance(data_proc_input.p_she_chains, dpdSheLensMcChains), data_proc_input.err_p_she_chains
        assert data_proc_input.err_p_she_chains is None

        assert data_proc_input.she_chains is None
        regex_match = re.match(ERR_NO_FILE_PATTERN, data_proc_input.err_she_chains)
        assert regex_match, f"Value '{data_proc_input.err_she_chains}' does not match regex pattern " \
                            f"{ERR_NO_FILE_PATTERN}"
        assert regex_match.groups()[0] == os.path.join(self.workdir, DATA_SUBDIR, BAD_FILENAME)
