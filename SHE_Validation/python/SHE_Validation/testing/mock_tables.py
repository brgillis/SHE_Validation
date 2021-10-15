""" @file mock_tables.py

    Created 15 October 2021.

    Utilities to generate mock tables for validation tests.
"""

__updated__ = "2021-10-05"

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
from typing import Optional

from astropy.table import Table

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import try_remove_file, write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.she_measurements import SheMeasurementsFormat, she_measurements_table_format
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat, she_tu_matched_table_format
from SHE_PPT.testing.mock_data import NUM_TEST_POINTS
from SHE_PPT.testing.mock_tables import MockTableGenerator
from SHE_Validation.testing.constants import (KSB_MATCHED_TABLE_FILENAME, LENSMC_MATCHED_TABLE_FILENAME,
                                              MATCHED_TABLE_PRODUCT_FILENAME, )
from SHE_Validation.testing.mock_data import (EST_SEED, MockShearEstimateDataGenerator,
                                              MockTUGalaxyDataGenerator, MockTUMatchedDataGenerator, )

logger = getLogger(__name__)


class MockTUGalaxyTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock galaxy tables.
    """

    # Attributes with overriding types
    mock_data_generator: MockTUGalaxyDataGenerator
    tf: Optional[SheTUMatchedFormat] = she_tu_matched_table_format


class MockShearEstimateTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock shear measurement tables.
    """

    # Attributes with overriding types
    mock_data_generator: MockShearEstimateDataGenerator
    tf: Optional[SheMeasurementsFormat] = she_measurements_table_format

    # New attributes for this subclass
    method: ShearEstimationMethods

    def __init__(self,
                 method: ShearEstimationMethods,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method attribute and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]


class MockTUMatchedTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock galaxy tables.
    """

    # Attributes with overriding types
    mock_data_generator: MockTUMatchedDataGenerator
    tf: Optional[SheTUMatchedFormat] = she_tu_matched_table_format

    # New attributes for this subclass
    method: ShearEstimationMethods

    def __init__(self,
                 method: ShearEstimationMethods,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method attribute and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]


def make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                            seed: int = EST_SEED, ) -> Table:
    """ Function to generate a mock matched table table.
    """

    mock_tu_galaxy_data_generator = MockTUGalaxyDataGenerator(num_test_points = NUM_TEST_POINTS,
                                                              seed = seed)
    mock_tu_matched_data_generator = MockTUMatchedDataGenerator(method = method,
                                                                mock_tu_galaxy_data_generator =
                                                                mock_tu_galaxy_data_generator,
                                                                seed = seed + 1)

    mock_tu_matched_table_generator = MockTUMatchedTableGenerator(method = method,
                                                                  mock_data_generator =
                                                                  mock_tu_matched_data_generator)

    return mock_tu_matched_table_generator.get_mock_table()


def write_mock_matched_tables(workdir: str) -> str:
    """ Returns filename of the matched table product.
    """

    lensmc_matched_table = make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                                                   seed = EST_SEED)
    ksb_matched_table = make_mock_matched_table(method = ShearEstimationMethods.KSB,
                                                seed = EST_SEED + 1)

    lensmc_matched_table.write(os.path.join(workdir, LENSMC_MATCHED_TABLE_FILENAME))
    ksb_matched_table.write(os.path.join(workdir, KSB_MATCHED_TABLE_FILENAME))

    # Set up and write the data product
    matched_table_product = products.she_validated_measurements.create_dpd_she_validated_measurements()
    matched_table_product.set_LensMC_filename(LENSMC_MATCHED_TABLE_FILENAME)
    matched_table_product.set_KSB_filename(KSB_MATCHED_TABLE_FILENAME)

    write_xml_product(matched_table_product, MATCHED_TABLE_PRODUCT_FILENAME, workdir = workdir)

    return MATCHED_TABLE_PRODUCT_FILENAME


def cleanup_mock_matched_tables(workdir: str):
    """ To be called in cleanup, deletes matched tables which have been written out.
    """

    try_remove_file(LENSMC_MATCHED_TABLE_FILENAME, workdir = workdir)
    try_remove_file(KSB_MATCHED_TABLE_FILENAME, workdir = workdir)
    try_remove_file(MATCHED_TABLE_PRODUCT_FILENAME, workdir = workdir)
