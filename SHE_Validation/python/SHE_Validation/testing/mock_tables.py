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

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import try_remove_file, write_listfile, write_product_and_table, write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.products.she_star_catalog import create_dpd_she_star_catalog
from SHE_PPT.products.she_validated_measurements import create_dpd_she_validated_measurements
from SHE_PPT.table_formats.mer_final_catalog import MerFinalCatalogFormat, mer_final_catalog_format
from SHE_PPT.table_formats.she_measurements import SheMeasurementsFormat, she_measurements_table_format
from SHE_PPT.table_formats.she_star_catalog import SHE_STAR_CAT_TF, SheStarCatalogFormat
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat, she_tu_matched_table_format
from SHE_PPT.testing.mock_data import NUM_TEST_POINTS
from SHE_PPT.testing.mock_tables import MockTableGenerator
from SHE_Validation.testing.constants import (KSB_MATCHED_TABLE_FILENAME, KSB_MEASUREMENTS_TABLE_FILENAME,
                                              LENSMC_MATCHED_TABLE_FILENAME,
                                              LENSMC_MEASUREMENTS_TABLE_FILENAME, MATCHED_TABLE_PRODUCT_FILENAME,
                                              MEASUREMENTS_TABLE_PRODUCT_FILENAME, MFC_TABLE_FILENAME,
                                              MFC_TABLE_LISTFILE_FILENAME, MFC_TABLE_PRODUCT_FILENAME,
                                              STAR_CAT_PRODUCT_FILENAME, STAR_CAT_TABLE_FILENAME, )
from SHE_Validation.testing.mock_data import (EST_SEED, MFC_SEED, MockMFCDataGenerator, MockShearEstimateDataGenerator,
                                              MockStarCatDataGenerator, MockTUGalaxyDataGenerator,
                                              MockTUMatchedDataGenerator, STAR_CAT_SEED, )
from ST_DataModelBindings.dpd.she.raw.starcatalog_stub import dpdSheStarCatalog
from ST_DataModelBindings.dpd.she.raw.validatedmeasurements_stub import DpdSheValidatedMeasurements

logger = getLogger(__name__)


class MockMFCGalaxyTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock galaxy tables.
    """

    # Attributes with overriding types
    mock_data_generator: MockMFCDataGenerator
    tf: Optional[MerFinalCatalogFormat] = mer_final_catalog_format


def make_mock_mfc_table(seed: int = MFC_SEED, ) -> Table:
    """ Function to generate a mock matched table table.
    """

    mock_data_generator = MockMFCDataGenerator(num_test_points = NUM_TEST_POINTS,
                                               seed = seed)

    mock_table_generator = MockMFCGalaxyTableGenerator(mock_data_generator =
                                                       mock_data_generator)

    return mock_table_generator.get_mock_table()


def write_mock_mfc_table(workdir: str) -> str:
    """ Returns filename of the matched table product.
    """

    write_product_and_table(product = create_dpd_mer_final_catalog(),
                            product_filename = MFC_TABLE_PRODUCT_FILENAME,
                            table = make_mock_mfc_table(seed = EST_SEED),
                            table_filename = MFC_TABLE_FILENAME)

    # Write the listfile
    write_listfile(os.path.join(workdir, MFC_TABLE_LISTFILE_FILENAME), [MFC_TABLE_PRODUCT_FILENAME])

    return MFC_TABLE_LISTFILE_FILENAME


def cleanup_mock_mfc_table(workdir: str):
    """ To be called in cleanup, deletes matched tables which have been written out.
    """

    try_remove_file(MFC_TABLE_FILENAME, workdir = workdir)
    try_remove_file(MFC_TABLE_PRODUCT_FILENAME, workdir = workdir)


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


def make_mock_measurements_table(method = ShearEstimationMethods.LENSMC,
                                 seed: int = EST_SEED, ) -> Table:
    """ Function to generate a mock shear measurements table.
    """

    mock_measurements_data_generator = MockShearEstimateDataGenerator(method = method,
                                                                      seed = seed)

    mock_measurements_table_generator = MockShearEstimateTableGenerator(method = method,
                                                                        mock_data_generator =
                                                                        mock_measurements_data_generator)

    return mock_measurements_table_generator.get_mock_table()


def write_mock_measurements_tables(workdir: str) -> str:
    """ Writes out and returns filename of the matched table product.
    """

    lensmc_measurements_table = make_mock_measurements_table(method = ShearEstimationMethods.LENSMC,
                                                             seed = EST_SEED)
    ksb_measurements_table = make_mock_measurements_table(method = ShearEstimationMethods.KSB,
                                                          seed = EST_SEED + 1)

    lensmc_measurements_table.write(os.path.join(workdir, LENSMC_MATCHED_TABLE_FILENAME))
    ksb_measurements_table.write(os.path.join(workdir, KSB_MATCHED_TABLE_FILENAME))

    # Set up and write the data product
    measurements_table_product = create_dpd_she_validated_measurements()
    measurements_table_product.set_LensMC_filename(LENSMC_MATCHED_TABLE_FILENAME)
    measurements_table_product.set_KSB_filename(KSB_MATCHED_TABLE_FILENAME)

    write_xml_product(measurements_table_product, MEASUREMENTS_TABLE_PRODUCT_FILENAME, workdir = workdir)

    return MEASUREMENTS_TABLE_PRODUCT_FILENAME


def cleanup_mock_measurements_tables(workdir: str):
    """ To be called in cleanup, deletes matched tables which have been written out.
    """

    try_remove_file(LENSMC_MEASUREMENTS_TABLE_FILENAME, workdir = workdir)
    try_remove_file(KSB_MEASUREMENTS_TABLE_FILENAME, workdir = workdir)
    try_remove_file(MEASUREMENTS_TABLE_PRODUCT_FILENAME, workdir = workdir)


class MockTUMatchedTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock TUM galaxy tables.
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

    def create_product(self) -> DpdSheValidatedMeasurements:
        """ Concretely implement method for creating a data product of the correct type for this table.
        """
        return create_dpd_she_validated_measurements()


def make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                            seed: int = EST_SEED, ) -> Table:
    """ Function to generate a mock matched table.
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
    """ Writes out and returns filename of the matched table product.
    """

    lensmc_matched_table = make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                                                   seed = EST_SEED)
    ksb_matched_table = make_mock_matched_table(method = ShearEstimationMethods.KSB,
                                                seed = EST_SEED + 1)

    lensmc_matched_table.write(os.path.join(workdir, LENSMC_MATCHED_TABLE_FILENAME))
    ksb_matched_table.write(os.path.join(workdir, KSB_MATCHED_TABLE_FILENAME))

    # Set up and write the data product
    matched_table_product = create_dpd_she_validated_measurements()
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


class MockStarCatTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock galaxy tables.
    """

    # Attributes with overriding types
    mock_data_generator: MockStarCatDataGenerator
    tf: Optional[SheStarCatalogFormat] = SHE_STAR_CAT_TF

    def create_product(self) -> dpdSheStarCatalog:
        """ Concretely implement method for creating a data product of the correct type for this table.
        """
        return create_dpd_she_star_catalog()


def make_mock_starcat_table(seed: int = STAR_CAT_SEED, ) -> Table:
    """ Function to generate a mock starcat table.
    """

    mock_data_generator = MockStarCatDataGenerator(num_test_points = NUM_TEST_POINTS,
                                                   seed = seed)

    mock_table_generator = MockStarCatTableGenerator(mock_data_generator =
                                                     mock_data_generator)

    return mock_table_generator.get_mock_table()


def write_mock_starcat_table(workdir: str) -> str:
    """ Returns filename of the starcat table product.
    """

    write_product_and_table(product = create_dpd_she_star_catalog(),
                            product_filename = STAR_CAT_PRODUCT_FILENAME,
                            table = make_mock_starcat_table(),
                            table_filename = STAR_CAT_TABLE_FILENAME,
                            workdir = workdir)

    return STAR_CAT_PRODUCT_FILENAME


def cleanup_mock_starcat_table(workdir: str):
    """ To be called in cleanup, deletes starcat tables which have been written out.
    """

    try_remove_file(STAR_CAT_TABLE_FILENAME, workdir = workdir)
    try_remove_file(STAR_CAT_PRODUCT_FILENAME, workdir = workdir)
