""" @file testing/mock_data.py

    Created 15 October 2021.

    Utilities to generate mock data for validation tests
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

from typing import Dict, Optional, Type

import numpy as np

from SHE_PPT.constants.classes import BinParameters, ShearEstimationMethods
from SHE_PPT.flags import flag_success, flag_unclassified_failure
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_lensmc_chains import create_dpd_she_lensmc_chains
from SHE_PPT.table_formats.she_lensmc_chains import SheLensMcChainsFormat, len_chain, lensmc_chains_table_format
from SHE_PPT.table_formats.she_lensmc_measurements import lensmc_measurements_table_format
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_TEST_POINTS
from SHE_PPT.testing.mock_measurements_cat import MockShearEstimateDataGenerator
from SHE_PPT.testing.mock_tables import MockDataGeneratorType, MockTableGenerator
from SHE_Validation.binning.bin_data import BIN_TF, SheBinDataFormat
from SHE_Validation.constants.default_config import TOT_BIN_LIMITS
from ST_DataModelBindings.dpd.she.raw.lensmcchains_stub import dpdSheLensMcChains

logger = getLogger(__name__)

SHE_CHAINS_PRODUCT_FILENAME = "she_chains.xml"
SHE_CHAINS_TABLE_FILENAME = "data/she_chains.fits"

SHE_TEST_RESULTS_PRODUCT_FILENAME = "she_validation_test_results.xml"

CHAINS_SEED = 5351

FIT_CLASS_GAL = 0
FIT_CLASS_STAR = 1
FIT_CLASS_UNKNOWN = 2


def make_mock_bin_limits() -> Dict[BinParameters, np.ndarray]:
    """ Generate a mock dictionary of bin limits for testing.
    """

    d_l_bin_limits: Dict[BinParameters, np.ndarray] = {}
    for bin_parameter in BinParameters:
        if bin_parameter == BinParameters.SNR:
            d_l_bin_limits[bin_parameter] = np.array([-0.5, 0.5, 1.5])
        else:
            d_l_bin_limits[bin_parameter] = np.array(TOT_BIN_LIMITS)

    return d_l_bin_limits


TEST_L_GOOD = 256  # Length of good data
TEST_L_NAN = 32  # Length of bad data
TEST_L_ZERO = 32  # Length of zero-weight data
TEST_L_TOT = TEST_L_GOOD + TEST_L_NAN + TEST_L_ZERO


class MockBinDataGenerator(MockDataGenerator):
    """ Data generator which generates data suitable for binning with various bin parameters.
    """
    tf: SheBinDataFormat = BIN_TF
    seed: int = 1245
    num_test_points = TEST_L_TOT

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        # Set mock snr, bg, colour, and size values to test different bins

        self.data[self.tf.snr] = np.where(self._indices % 2 < 1, self._ones, self._zeros)
        self.data[self.tf.bg] = np.where(self._indices % 4 < 2, self._ones, self._zeros)
        self.data[self.tf.colour] = np.where(self._indices % 8 < 4, self._ones, self._zeros)
        self.data[self.tf.size] = np.where(self._indices % 16 < 8, self._ones, self._zeros)
        self.data[self.tf.epoch] = np.where(self._indices % 32 < 16, self._ones, self._zeros)


class MockBinTableGenerator(MockTableGenerator):
    """ Table generator for a binning data table.
    """
    mock_data_generator_type = MockBinDataGenerator
    tf = MockBinDataGenerator.tf
    seed = MockBinDataGenerator.seed
    num_test_points = MockBinDataGenerator.num_test_points

    def create_product(self):
        """ Dummy instantiation - this doesn't correspond to any particular product type, and so none should be
            written out.
        """
        return None


class ExtendedMockMeasDataGenerator(MockShearEstimateDataGenerator):
    """A MockShearEstimateDataGenerator, extended to also produce all data checked for in the validation steps.
    """

    # New class attributes for this child class
    flag_bad: bool = True

    # New class constants
    RE_MIN: float = 0.1
    RE_MAX: float = 0.2

    FIT_CLASS_CHANCE_GAL = 0.8
    FIT_CLASS_CHANCE_STAR = 0.1

    def __init__(self,
                 flag_bad: Optional[bool] = None,
                 *args, **kwargs):
        """Inherit init so we can set extra values.
        """

        super().__init__(*args, **kwargs)
        if flag_bad is not None:
            self.flag_bad = flag_bad

    def _generate_unique_data(self):
        """Inherit and add generation of new data.
        """

        # Inherit parent data generation
        super()._generate_unique_data()

        # Generate mock sizes through uniform distribution (don't want to risk them going negative on rare occasions)
        self.data[self.tf.re] = self._rng.uniform(self.RE_MIN, self.RE_MAX, self.num_test_points)
        self.data[self.tf.re_err] = (self.RE_MAX - self.RE_MIN) / 2 * np.ones(self.num_test_points, dtype=float)

        # Generate random gal/star/unknown classifications
        l_p = self._rng.uniform(size=self.num_test_points)
        self.data[self.tf.fit_class] = np.where(l_p < self.FIT_CLASS_CHANCE_GAL,
                                                FIT_CLASS_GAL,
                                                np.where(l_p < self.FIT_CLASS_CHANCE_GAL + self.FIT_CLASS_CHANCE_STAR,
                                                         FIT_CLASS_STAR,
                                                         FIT_CLASS_UNKNOWN))

        # If desired, flag all bad data as such
        if self.flag_bad:
            self.data[self.tf.fit_flags] = np.where(self._indices < self.num_good_test_points,
                                                    flag_success,
                                                    flag_unclassified_failure)
        else:
            self.data[self.tf.fit_flags] = flag_success * np.ones_like(self._indices)


class ExtendedMockChainsDataGenerator(MockDataGenerator):
    """A MockDataGenerator for generating LensMC chains data.
    """

    # Overriding base class default values
    tf: SheLensMcChainsFormat
    seed: int = CHAINS_SEED

    # New attributes for this subclass
    mock_measurements_data_generator: ExtendedMockMeasDataGenerator

    # Attributes used while generating data
    _meas_data: Optional[Dict[str, np.ndarray]] = None

    def __init__(self,
                 mock_measurements_data_generator: Optional[ExtendedMockMeasDataGenerator] = None,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock_measurements_data_generator.
        """
        super().__init__(*args, **kwargs)

        if mock_measurements_data_generator is None:
            self.mock_measurements_data_generator = ExtendedMockMeasDataGenerator(method=ShearEstimationMethods.LENSMC,
                                                                                  num_test_points=self.num_test_points,
                                                                                  seed=self.seed)
        else:
            self.mock_measurements_data_generator = mock_measurements_data_generator
            self.num_test_points = self.mock_measurements_data_generator.num_test_points
            self.seed = self.mock_measurements_data_generator.seed

        self.tf = lensmc_chains_table_format

    def _generate_unique_data(self):
        """ Generate chains data based off of the measurements data.
        """

        # Get the data generated from the measurements catalog and its table format
        self._meas_data = self.mock_measurements_data_generator.get_data()
        m_tf = lensmc_measurements_table_format

        # Copy over data where appropriate
        self.data[self.tf.ID] = self._meas_data[m_tf.ID]
        self.data[self.tf.fit_flags] = self._meas_data[m_tf.fit_flags]
        self.data[self.tf.weight] = self._meas_data[m_tf.weight]
        self.data[self.tf.fit_class] = self._meas_data[m_tf.fit_class]

        # Generate random chains for g1, g2, and re

        for (attr, min_value, max_value) in (("g1", -0.99, 0.99),
                                             ("g2", -0.99, 0.99),
                                             ("re", 0.01, 1e99)):

            # Get the data reshaped to 2D arrays so that numpy can broadcast them properly for operations
            val_colname = getattr(m_tf, attr)
            l_l_val_reshaped = np.reshape(self._meas_data[val_colname], (self.num_test_points, 1))

            err_colname = getattr(m_tf, f"{attr}_err")
            l_l_err_reshaped = np.reshape(self._meas_data[err_colname], (self.num_test_points, 1))

            # Calculate a set of normal deviates, and use them to calculate mock chains for the output
            deviates = self._rng.normal(size=(self.num_test_points, len_chain))

            # Calculate values, and clip them to be within min and max
            l_l_chain_values = l_l_val_reshaped + deviates * l_l_err_reshaped
            l_l_chain_values_clipped = np.clip(l_l_chain_values, min_value, max_value)

            self.data[getattr(self.tf, attr)] = l_l_chain_values_clipped


class ExtendedMockChainsTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock mer final catalog tables.
    """

    mock_data_generator_type: Type[MockDataGeneratorType] = ExtendedMockChainsDataGenerator

    def create_product(self) -> dpdSheLensMcChains:
        return create_dpd_she_lensmc_chains()

    # Attributes with overriding types
    tf: Optional[SheLensMcChainsFormat] = lensmc_chains_table_format
    seed: int = CHAINS_SEED
    table_filename: str = SHE_CHAINS_TABLE_FILENAME
    product_filename: str = SHE_CHAINS_PRODUCT_FILENAME

    # New attributes
    method: ShearEstimationMethods = ShearEstimationMethods.LENSMC

    def __init__(self,
                 *args,
                 mock_data_generator: Optional[MockDataGeneratorType] = None,
                 mock_measurements_data_generator: Optional[ExtendedMockMeasDataGenerator] = None,
                 seed: Optional[int] = None,
                 num_test_points: Optional[int] = None,
                 **kwargs, ):
        # Initialize new attributes for this subtype

        # Set up the mock data generator with the proper type

        self.seed = seed if seed is not None else self.seed
        self.num_test_points = num_test_points if num_test_points is not None else self.num_test_points

        if mock_data_generator is None:
            mock_data_generator = self.mock_data_generator_type(
                mock_measurements_data_generator=mock_measurements_data_generator,
                num_test_points=self.num_test_points,
                seed=self.seed)
        else:
            self.seed = mock_data_generator.seed
            self.num_test_points = mock_data_generator.num_test_points

        super().__init__(*args,
                         mock_data_generator=mock_data_generator,
                         **kwargs)
