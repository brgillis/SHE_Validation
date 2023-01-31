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
from typing import Dict, Optional

from astropy.table import Table

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.file_io import write_xml_product
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.products.she_lensmc_chains import create_dpd_she_lensmc_chains
from SHE_PPT.products.she_validated_measurements import create_dpd_she_validated_measurements
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.testing.mock_measurements_cat import MockShearEstimateTableGenerator
from SHE_PPT.testing.mock_mer_final_cat import MockMFCGalaxyTableGenerator
from SHE_Validation.testing.mock_data import (ExtendedMockChainsTableGenerator, ExtendedMockMeasDataGenerator,
                                              SHE_CHAINS_PRODUCT_FILENAME,
                                              SHE_CHAINS_TABLE_FILENAME, )
from SHE_Validation.testing.utility import SheValTestCase, compile_regex
from SHE_Validation_DataQuality.dp_input import DataProcInput
from SHE_Validation_DataQuality.gi_input import GalInfoInput

BAD_FILENAME = "junk"
ERR_READING_FILE_PATTERN = compile_regex("Error reading file %s.")
ERR_NO_FILE_PATTERN = compile_regex("[Errno 2] No such file or directory: '%s'")


class SheDQTestCase(SheValTestCase):
    """A test case which provides useful utilities for DataQuality validation tests.
    """

    TABLE_SIZE = 10

    good_dp_input: Optional[DataProcInput] = None
    good_gi_input: Optional[GalInfoInput] = None

    def make_data_proc_input_files(self):
        """Makes data in the workdir needed to run DataProc validation tests.
        """

        MockShearEstimateTableGenerator(num_test_points=self.TABLE_SIZE, workdir=self.workdir).write_mock_product()

        she_chains = lensmc_chains_table_format.init_table(size=self.TABLE_SIZE,
                                                           optional_columns=[lensmc_chains_table_format.re])
        she_chains.write(os.path.join(self.workdir, SHE_CHAINS_TABLE_FILENAME))

        p_she_chains = create_dpd_she_lensmc_chains(SHE_CHAINS_TABLE_FILENAME)
        write_xml_product(p_she_chains, SHE_CHAINS_PRODUCT_FILENAME, workdir=self.workdir)

    def make_gal_info_input_files(self):
        """Makes data in the workdir needed to run GalInfo validation tests.
        """

        # Create the DataProc info, since this data is a superset of that
        self.make_data_proc_input_files()

        MockMFCGalaxyTableGenerator(num_test_points=self.TABLE_SIZE, workdir=self.workdir).write_mock_product()

    def make_mock_data_proc_input(self):
        """Makes mock input for the DataProc validation test, to be used for testing its data processing step.
        """

        p_she_cat = create_dpd_she_validated_measurements()
        p_she_chains = create_dpd_she_lensmc_chains()

        d_she_cat: Dict[ShearEstimationMethods, Optional[Table]] = {}
        mock_measurements_data_generator: Optional[ExtendedMockMeasDataGenerator] = None
        for method in ShearEstimationMethods:
            if method == ShearEstimationMethods.LENSMC:
                mock_measurements_data_generator = ExtendedMockMeasDataGenerator(num_test_points=self.TABLE_SIZE,
                                                                                 method=method)
                d_she_cat[method] = MockShearEstimateTableGenerator(
                    mock_data_generator=mock_measurements_data_generator).get_mock_table()
            else:
                d_she_cat[method] = None

        she_chains = ExtendedMockChainsTableGenerator(
            mock_measurements_data_generator=mock_measurements_data_generator).get_mock_table()

        # Make a mock input object with good data
        self.good_dp_input = DataProcInput(p_she_cat=p_she_cat,
                                           err_p_she_cat=None,
                                           d_she_cat=d_she_cat,
                                           d_err_she_cat=None,
                                           p_she_chains=p_she_chains,
                                           err_p_she_chains=None,
                                           she_chains=she_chains,
                                           err_she_chains=None)

    def make_mock_gal_info_input(self):
        """Makes mock input for the GalInfo validation test, to be used for testing its data processing step.
        """

        self.make_mock_data_proc_input()

        p_mer_cat = create_dpd_mer_final_catalog()
        mer_cat = MockMFCGalaxyTableGenerator(num_test_points=self.TABLE_SIZE).get_mock_table()

        self.good_gi_input = GalInfoInput(**self.good_dp_input.__dict__,
                                          p_mer_cat=p_mer_cat,
                                          err_p_mer_cat=None,
                                          mer_cat=mer_cat,
                                          err_mer_cat=None)
