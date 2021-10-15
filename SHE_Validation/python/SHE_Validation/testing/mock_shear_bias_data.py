""" @file mock_pipeline_config.py

    Created 5 October 2021.

    Utilities to generate mock data for shear bias validation unit tests.
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
from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Dict, List, Optional

import numpy as np
from astropy.table import Table
from dataclasses import dataclass

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import try_remove_file, write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.she_measurements import SheMeasurementsFormat
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat, she_tu_matched_table_format
from SHE_PPT.table_utility import SheTableFormat
from SHE_PPT.utility import default_init_if_none, default_value_if_none
from SHE_Validation.constants.default_config import (DEFAULT_BIN_LIMITS)
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation_ShearBias.constants.shear_bias_test_info import FULL_L_SHEAR_BIAS_TEST_CASE_M_INFO

logger = getLogger(__name__)

# Input data filenames
PIPELINE_CONFIG_FILENAME = "shear_bias_pipeline_config.xml"
MATCHED_CATALOG_PRODUCT_FILENAME = "shear_bias_matched_catalog.xml"
LENSMC_MATCHED_CATALOG_FILENAME = "data/lensmc_shear_bias_matched_catalog.fits"
KSB_MATCHED_CATALOG_FILENAME = "data/ksb_bias_matched_catalog.fits"

# Output data filename
SHE_BIAS_TEST_RESULT_FILENAME = "she_observation_validation_test_results.xml"

# Test data description

# Info about the shear estimation methods and associated tables
TEST_METHOD_GLOBAL = ShearEstimationMethods.LENSMC
TEST_METHOD_SNR = ShearEstimationMethods.KSB
MATCHED_TF_GLOBAL = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD_GLOBAL]
MATCHED_TF_SNR = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD_SNR]

TEST_METHODS = (ShearEstimationMethods.LENSMC, ShearEstimationMethods.KSB)
TEST_BIN_PARAMETERS = (BinParameters.GLOBAL, BinParameters.SNR)

# General info about the data
NUM_GOOD_TEST_POINTS = 32
NUM_NAN_TEST_POINTS = 2
NUM_ZERO_WEIGHT_TEST_POINTS = 1
NUM_TEST_POINTS = NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS + NUM_ZERO_WEIGHT_TEST_POINTS

# Input shear info
INPUT_G_MIN = -0.7
INPUT_G_MAX = 0.7

# Estimated shear info
EST_SEED = 6413
EST_G_ERR = 0.025
EXTRA_EST_G_ERR = 0.005
EXTRA_EST_G_ERR_ERR = 0.005

# Fail sigma values
LOCAL_FAIL_SIGMA = 4
GLOBAL_FAIL_SIGMA = 10

D_D_L_D_INPUT_BIAS: Dict[ShearEstimationMethods, Dict[BinParameters, List[Dict[str, float]]]] = {
    ShearEstimationMethods.LENSMC: {BinParameters.GLOBAL: [{"m1"    : 0.05,
                                                            "m1_err": 0.015,
                                                            "c1"    : -0.2,
                                                            "c1_err": 0.05,
                                                            "m2"    : -0.1,
                                                            "m2_err": 0.04,
                                                            "c2"    : 0.01,
                                                            "c2_err": 0.003, }]},
    ShearEstimationMethods.KSB   : {BinParameters.SNR: [{"m1"    : 0.2,
                                                         "m1_err": 0.003,
                                                         "c1"    : -0.3,
                                                         "c1_err": 0.03,
                                                         "m2"    : 0.1,
                                                         "m2_err": 0.21,
                                                         "c2"    : -0.4,
                                                         "c2_err": 0.43, },
                                                        {"m1"    : -0.3,
                                                         "m1_err": 0.031,
                                                         "c1"    : -0.5,
                                                         "c1_err": 0.05,
                                                         "m2"    : 0.35,
                                                         "m2_err": 0.15,
                                                         "c2"    : 0.,
                                                         "c2_err": 0.1,
                                                         }]}}


class MockDataGenerator(ABC):
    """ A class to handle the generation of mock data for testing.
    """

    # Attributes optionally set at init or with defaults
    tf: Optional[SheTableFormat] = None
    num_test_points: int = NUM_TEST_POINTS
    seed: int = 0

    # Attributes set when data is generated
    data: Optional[Dict[str, np.ndarray]] = None

    def __init__(self,
                 tf: Optional[SheTableFormat] = None,
                 num_test_points: Optional[int] = None,
                 seed: Optional[int] = None) -> None:
        """ Initializes the class.
        """
        self.tf = default_value_if_none(x = tf,
                                        default_x = self.tf)
        self.num_test_points = default_value_if_none(x = num_test_points,
                                                     default_x = self.num_test_points)
        self.seed = default_value_if_none(x = seed,
                                          default_x = self.seed)

    def _generate_base_data(self):
        """ Set up base data which is commonly used.
        """
        self._indices = np.indices((NUM_TEST_POINTS,), dtype = int, )[0]
        self._zeros = np.zeros(NUM_TEST_POINTS, dtype = '>f4')
        self._ones = np.ones(NUM_TEST_POINTS, dtype = '>f4')

    def _seed_rng(self):
        """Seed the random number generator
        """
        self._rng = np.random.default_rng(self.seed)

    def get_data(self):
        """ Get the data, generating if needed.
        """
        if self.data is None:
            self.generate_data()
        return self.data

    def generate_data(self):
        """ Generates data based on input parameters.
        """

        # Generate generic data first
        self._seed_rng()
        self._generate_base_data()

        # Call the abstract method to generate unique data for each type
        self._generate_unique_data()

    @abstractmethod
    def _generate_unique_data(self):
        """ Generates data unique to this type.
        """


class MockTUGalaxyDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock galaxy catalog data.
    """

    # Overring base class default values
    tf: SheTUMatchedFormat = she_tu_matched_table_format
    seed: int = 3513

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        self.data[self.tf.ID] = self._indices

        # Fill in input data
        self.data[self.tf.tu_gamma1] = -np.linspace(INPUT_G_MIN, INPUT_G_MAX, self.num_test_points)
        self.data[self.tf.tu_gamma2] = np.linspace(INPUT_G_MAX, INPUT_G_MIN, self.num_test_points)
        self.data[self.tf.tu_kappa] = np.zeros_like(self.data[self.tf.tu_gamma1])

        # Fill in data for bin parameter info, with different bins for each parameter

        i: int
        bin_parameter: BinParameters
        for i, bin_parameter in enumerate(BinParameters):
            if bin_parameter == BinParameters.GLOBAL:
                continue
            factor = 2 ** i
            self.data[bin_parameter.name] = np.where(self._indices % factor < factor / 2, self._ones, self._zeros)


class MockShearEstimateDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock shear estimates data.
    """

    # Overring base class default values
    tf: SheMeasurementsFormat
    seed: int = 75275

    # New attributes for this subclass
    mock_tu_galaxy_data_generator: MockTUGalaxyDataGenerator
    method: ShearEstimationMethods

    # Attributes used while generating data
    _tu_data: Optional[Dict[str, np.ndarray]] = None
    _tu_tf: Optional[SheTUMatchedFormat] = None

    def __init__(self,
                 method: ShearEstimationMethods,
                 mock_tu_galaxy_data_generator: Optional[MockTUGalaxyDataGenerator] = None,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]

        # Init the data generator
        self.mock_tu_galaxy_data_generator = default_init_if_none(mock_tu_galaxy_data_generator,
                                                                  type = MockTUGalaxyDataGenerator)

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        # Get the TU data generator and table format
        self._tu_data = self.mock_tu_galaxy_data_generator.get_data()
        self._tu_tf = self.mock_tu_galaxy_data_generator.tf

        self.data[self.tf.ID] = self._indices

        # Generate random noise for output data
        l_extra_g_err = EXTRA_EST_G_ERR + EXTRA_EST_G_ERR_ERR * self._rng.standard_normal(NUM_TEST_POINTS)
        l_g_err = np.sqrt(EST_G_ERR ** 2 + l_extra_g_err ** 2)
        l_g1_deviates = l_g_err * self._rng.standard_normal(NUM_TEST_POINTS)
        l_g2_deviates = l_g_err * self._rng.standard_normal(NUM_TEST_POINTS)

        # Save the error in the table
        self.data[self.tf.g1_err] = l_g_err
        self.data[self.tf.g2_err] = l_g_err
        self.data[self.tf.weight] = 0.5 * l_g_err ** -2

        # Fill in rows with mock output data - this bit depends on which method we're using
        d_l_d_method_input_bias = D_D_L_D_INPUT_BIAS[self.method]
        if self.method == ShearEstimationMethods.LENSMC:
            d_bias_0m2 = d_l_d_method_input_bias[BinParameters.GLOBAL][0]
            d_bias_1m2 = d_l_d_method_input_bias[BinParameters.GLOBAL][0]
        else:
            d_bias_0m2 = d_l_d_method_input_bias[BinParameters.SNR][0]
            d_bias_1m2 = d_l_d_method_input_bias[BinParameters.SNR][1]

        g1_0m2 = d_bias_0m2["c1"] + (1 + d_bias_0m2["m1"]) * -self._tu_data[self._tu_tf.tu_gamma1] + l_g1_deviates
        g1_1m2 = d_bias_1m2["c1"] + (1 + d_bias_1m2["m1"]) * -self._tu_data[self._tu_tf.tu_gamma1] + l_g1_deviates

        g2_0m2 = d_bias_0m2["c2"] + (1 + d_bias_0m2["m2"]) * self._tu_data[self._tu_tf.tu_gamma2] + l_g2_deviates
        g2_1m2 = d_bias_1m2["c2"] + (1 + d_bias_1m2["m2"]) * self._tu_data[self._tu_tf.tu_gamma2] + l_g2_deviates

        # Add to table, flipping g1 due to SIM's format
        self.data[self.tf.g1] = np.where(self._indices % 2 < 1, g1_0m2, g1_1m2)
        self.data[self.tf.g2] = np.where(self._indices % 2 < 1, g2_0m2, g2_1m2)

        # TODO: Set numbers of good, nan, and inf test points as fields

        # Flag the last bit of data as bad or zero weight
        self.data[self.tf.g1][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:-NUM_ZERO_WEIGHT_TEST_POINTS] = np.NaN
        self.data[self.tf.g1_err][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:] = np.NaN
        self.data[self.tf.g2][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:-NUM_ZERO_WEIGHT_TEST_POINTS] = np.NaN
        self.data[self.tf.g2_err][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:] = np.NaN

        self.data[self.tf.g1_err][-NUM_ZERO_WEIGHT_TEST_POINTS:] = np.inf
        self.data[self.tf.g2_err][-NUM_ZERO_WEIGHT_TEST_POINTS:] = np.inf
        self.data[self.tf.weight][-NUM_ZERO_WEIGHT_TEST_POINTS:] = 0

        # Set the fit flags
        self.data[self.tf.fit_flags] = np.where(self._indices < NUM_GOOD_TEST_POINTS, 0,
                                                np.where(self._indices < NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS, 1,
                                                         0))


class MockCatalogGenerator(ABC):
    """ A class to handle the generation of a mock catalog from mock data.
    """

    # Attributes set at init
    mock_data_generator: MockDataGenerator

    # Attributes optionally set at init or with defaults
    tf: Optional[SheTableFormat] = None

    # Attributes set when catalog is generated.
    _mock_catalog: Optional[Table] = None

    def __init__(self,
                 mock_data_generator: MockDataGenerator,
                 tf: Optional[SheTableFormat] = None) -> None:
        """ Initializes the class.
        """
        self.mock_data_generator = mock_data_generator
        self.tf = default_value_if_none(x = tf, default_x = self.tf)

    @abstractmethod
    def _make_mock_catalog(self) -> None:
        """ Abstract method to generate the mock catalog, filling in self._mock_catalog with a Table.
        """
        pass

    def get_mock_catalog(self) -> Table:
        """ Gets the generated mock catalog.
        """
        if self._mock_catalog is None:
            self.mock_data_generator.generate_data()
            self._make_mock_catalog()
        return self._mock_catalog


class MockGalaxyCatalogGenerator(MockCatalogGenerator):
    """ A class to handle the generation of mock galaxy catalogs.
    """

    # Attributes with overriding types
    mock_data_generator: MockTUGalaxyDataGenerator
    tf: Optional[SheTableFormat] = she_tu_matched_table_format


def make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                            seed: int = EST_SEED, ) -> Table:
    """ Function to generate a mock matched catalog table.
    """

    tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]
    d_l_d_method_input_bias = D_D_L_D_INPUT_BIAS[method]

    # Seed the random number generator
    rng = np.random.default_rng(seed)

    # Create the table
    matched_table = tf.init_table(size = NUM_TEST_POINTS)

    indices = np.indices((NUM_TEST_POINTS,), dtype = int, )[0]
    zeros = np.zeros(NUM_TEST_POINTS, dtype = '>f4')
    ones = np.ones(NUM_TEST_POINTS, dtype = '>f4')

    matched_table[tf.ID] = indices

    # Fill in input data
    matched_table[tf.tu_gamma1] = -np.linspace(INPUT_G_MIN, INPUT_G_MAX, NUM_TEST_POINTS)
    matched_table[tf.tu_gamma2] = np.linspace(INPUT_G_MAX, INPUT_G_MIN, NUM_TEST_POINTS)
    matched_table[tf.tu_kappa] = np.zeros_like(matched_table[tf.tu_gamma1])

    # Fill in data for bin parameter info, with different bins for each parameter

    i: int
    bin_parameter: BinParameters
    for i, bin_parameter in enumerate(BinParameters):
        if bin_parameter == BinParameters.GLOBAL:
            continue
        factor = 2 ** i
        matched_table[bin_parameter.name] = np.where(indices % factor < factor / 2, ones, zeros)

    # Generate random noise for output data
    l_extra_g_err = EXTRA_EST_G_ERR + EXTRA_EST_G_ERR_ERR * rng.standard_normal(NUM_TEST_POINTS)
    l_g_err = np.sqrt(EST_G_ERR ** 2 + l_extra_g_err ** 2)
    l_g1_deviates = l_g_err * rng.standard_normal(NUM_TEST_POINTS)
    l_g2_deviates = l_g_err * rng.standard_normal(NUM_TEST_POINTS)

    # Save the error in the table
    matched_table[tf.g1_err] = l_g_err
    matched_table[tf.g2_err] = l_g_err
    matched_table[tf.weight] = 0.5 * l_g_err ** -2

    # Fill in rows with mock output data - this bit depends on which method we're using
    if method == ShearEstimationMethods.LENSMC:
        d_bias_0m2 = d_l_d_method_input_bias[BinParameters.GLOBAL][0]
        d_bias_1m2 = d_l_d_method_input_bias[BinParameters.GLOBAL][0]
    else:
        d_bias_0m2 = d_l_d_method_input_bias[BinParameters.SNR][0]
        d_bias_1m2 = d_l_d_method_input_bias[BinParameters.SNR][1]

    g1_0m2 = d_bias_0m2["c1"] + (1 + d_bias_0m2["m1"]) * -matched_table[tf.tu_gamma1] + l_g1_deviates
    g1_1m2 = d_bias_1m2["c1"] + (1 + d_bias_1m2["m1"]) * -matched_table[tf.tu_gamma1] + l_g1_deviates

    g2_0m2 = d_bias_0m2["c2"] + (1 + d_bias_0m2["m2"]) * matched_table[tf.tu_gamma1] + l_g2_deviates
    g2_1m2 = d_bias_1m2["c2"] + (1 + d_bias_1m2["m2"]) * matched_table[tf.tu_gamma1] + l_g2_deviates

    # Add to table, flipping g1 due to SIM's format
    matched_table[tf.g1] = np.where(indices % 2 < 1, g1_0m2, g1_1m2)
    matched_table[tf.g2] = np.where(indices % 2 < 1, g2_0m2, g2_1m2)

    # Flag the last bit of data as bad or zero weight
    matched_table[tf.g1][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:-NUM_ZERO_WEIGHT_TEST_POINTS] = np.NaN
    matched_table[tf.g1_err][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:] = np.NaN
    matched_table[tf.g2][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:-NUM_ZERO_WEIGHT_TEST_POINTS] = np.NaN
    matched_table[tf.g2_err][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:] = np.NaN

    matched_table[tf.g1_err][-NUM_ZERO_WEIGHT_TEST_POINTS:] = np.inf
    matched_table[tf.g2_err][-NUM_ZERO_WEIGHT_TEST_POINTS:] = np.inf
    matched_table[tf.weight][-NUM_ZERO_WEIGHT_TEST_POINTS:] = 0

    # Set the fit flags
    matched_table[tf.fit_flags] = np.where(indices < NUM_GOOD_TEST_POINTS, 0,
                                           np.where(indices < NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS, 1, 0))

    return matched_table


def write_mock_matched_tables(workdir: str) -> str:
    """ Returns filename of the matched table product.
    """

    lensmc_matched_table = make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                                                   seed = EST_SEED)
    ksb_matched_table = make_mock_matched_table(method = ShearEstimationMethods.KSB,
                                                seed = EST_SEED + 1)

    lensmc_matched_table.write(os.path.join(workdir, LENSMC_MATCHED_CATALOG_FILENAME))
    ksb_matched_table.write(os.path.join(workdir, KSB_MATCHED_CATALOG_FILENAME))

    # Set up and write the data product
    matched_table_product = products.she_validated_measurements.create_dpd_she_validated_measurements()
    matched_table_product.set_LensMC_filename(LENSMC_MATCHED_CATALOG_FILENAME)
    matched_table_product.set_KSB_filename(KSB_MATCHED_CATALOG_FILENAME)

    write_xml_product(matched_table_product, MATCHED_CATALOG_PRODUCT_FILENAME, workdir = workdir)

    return MATCHED_CATALOG_PRODUCT_FILENAME


def cleanup_mock_matched_tables(workdir: str):
    """ To be called in cleanup, deletes matched tables which have been written out.
    """

    try_remove_file(LENSMC_MATCHED_CATALOG_FILENAME, workdir = workdir)
    try_remove_file(KSB_MATCHED_CATALOG_FILENAME, workdir = workdir)
    try_remove_file(MATCHED_CATALOG_PRODUCT_FILENAME, workdir = workdir)


def make_mock_bin_limits() -> Dict[BinParameters, np.ndarray]:
    """ Generate a mock dictionary of bin limits for testing.
    """

    d_l_bin_limits: Dict[BinParameters, np.ndarray] = {}
    for bin_parameter in BinParameters:
        if bin_parameter == BinParameters.SNR:
            d_l_bin_limits[bin_parameter] = np.array([-0.5, 0.5, 1.5])
        else:
            d_l_bin_limits[bin_parameter] = np.array(DEFAULT_BIN_LIMITS)

    return d_l_bin_limits


@dataclass
class MockShearBiasArgs(Namespace):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    # Workdir and logdir need to be set in setup_class
    workdir: Optional[str] = None
    logdir: Optional[str] = None

    bootstrap_errors: Optional[bool] = None
    max_g_in: Optional[float] = None
    require_fitclass_zero: Optional[bool] = None

    matched_catalog: str = MATCHED_CATALOG_PRODUCT_FILENAME
    pipeline_config: str = PIPELINE_CONFIG_FILENAME
    shear_bias_validation_test_results_product: str = SHE_BIAS_TEST_RESULT_FILENAME

    profile: bool = False
    dry_run: bool = True

    def __post_init__(self):

        for test_case_info in FULL_L_SHEAR_BIAS_TEST_CASE_M_INFO:
            bin_limits_cline_arg = test_case_info.bins_cline_arg
            if bin_limits_cline_arg is not None:
                setattr(self, bin_limits_cline_arg, None)
