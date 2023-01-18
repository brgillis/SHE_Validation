"""
:file: tests/python/dp_input_test.py

:date: 01/18/23
:author: Bryan Gillis

Tests of function to read in input data for the DataProc test
"""
import os
import re

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.misc import DATA_SUBDIR
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.file_io import write_xml_product
from SHE_PPT.products.she_reconciled_lensmc_chains import create_dpd_she_reconciled_lensmc_chains
from SHE_PPT.products.she_reconciled_measurements import create_dpd_she_reconciled_measurements
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_formats.she_lensmc_measurements import lensmc_measurements_table_format
from SHE_PPT.table_utility import is_in_format
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
                                              SHE_RECONCILED_CHAINS_TABLE_FILENAME,
                                              SHE_RECONCILED_MEASUREMENTS_PRODUCT_FILENAME,
                                              SHE_RECONCILED_MEASUREMENTS_TABLE_FILENAME, )
from SHE_Validation.testing.utility import compile_regex
from SHE_Validation_DataQuality.dp_input import ERR_MEASUREMENTS_NONE, read_data_proc_input
from ST_DataModelBindings.dpd.she.reconciledlensmcchains_stub import dpdSheReconciledLensMcChains
from ST_DataModelBindings.dpd.she.reconciledmeasurements_stub import dpdSheReconciledMeasurements


class TestDataProcInput(SheTestCase):
    """Test case for DataProc validation test integration tests.
    """

    def post_setup(self):
        """ Override parent setup, downloading data to work with here.
        """

        # Create mock products to test

        rec_cat = lensmc_measurements_table_format.init_table(size=1)
        rec_cat.write(os.path.join(self.workdir, DATA_SUBDIR, SHE_RECONCILED_MEASUREMENTS_TABLE_FILENAME))

        p_rec_cat = create_dpd_she_reconciled_measurements(LensMC_filename=SHE_RECONCILED_MEASUREMENTS_TABLE_FILENAME)
        write_xml_product(p_rec_cat, SHE_RECONCILED_MEASUREMENTS_PRODUCT_FILENAME, workdir=self.workdir)

        rec_chains = lensmc_chains_table_format.init_table(size=1)
        rec_chains.write(os.path.join(self.workdir, DATA_SUBDIR, SHE_RECONCILED_CHAINS_TABLE_FILENAME))

        p_rec_chains = create_dpd_she_reconciled_lensmc_chains(SHE_RECONCILED_CHAINS_TABLE_FILENAME)
        write_xml_product(p_rec_chains, SHE_RECONCILED_CHAINS_PRODUCT_FILENAME, workdir=self.workdir)

    def test_read_input(self):
        """Test that the program runs without raising any uncaught exceptions.
        """

        data_proc_input = read_data_proc_input(p_rec_cat_filename=SHE_RECONCILED_MEASUREMENTS_PRODUCT_FILENAME,
                                               p_rec_chains_filename=SHE_RECONCILED_CHAINS_PRODUCT_FILENAME,
                                               workdir=self.workdir)

        # Check that the input is as expected

        assert isinstance(data_proc_input.p_rec_cat, dpdSheReconciledMeasurements), data_proc_input.err_p_rec_cat
        assert data_proc_input.err_p_rec_cat is None

        method_none_pattern = compile_regex(ERR_MEASUREMENTS_NONE)

        for method, tf in D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.items():
            if method == ShearEstimationMethods.LENSMC:
                assert is_in_format(table=data_proc_input.d_rec_cat[method],
                                    table_format=lensmc_measurements_table_format,
                                    verbose=True), data_proc_input.d_err_rec_cat[method]
                assert data_proc_input.d_err_rec_cat[method] is None
            else:
                assert data_proc_input.d_rec_cat[method] is None
                regex_match = re.match(method_none_pattern, data_proc_input.d_err_rec_cat[method])
                assert regex_match.groups()[0] == method.value

        assert isinstance(data_proc_input.p_rec_chains, dpdSheReconciledLensMcChains), data_proc_input.err_p_rec_chains
        assert data_proc_input.err_p_rec_chains is None

        assert is_in_format(data_proc_input.rec_chains, lensmc_chains_table_format, verbose=True)
        assert data_proc_input.err_rec_chains is None
