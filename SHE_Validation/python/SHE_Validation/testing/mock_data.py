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

from typing import Dict

import numpy as np

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.logging import getLogger
from SHE_PPT.testing.mock_data import MockDataGenerator
from SHE_PPT.testing.mock_tables import MockTableGenerator
from SHE_Validation.binning.bin_data import BIN_TF, SheBinDataFormat
from SHE_Validation.constants.default_config import TOT_BIN_LIMITS

logger = getLogger(__name__)

SHE_RECONCILED_MEASUREMENTS_PRODUCT_FILENAME = "she_reconciled_measurements.xml"
SHE_RECONCILED_MEASUREMENTS_TABLE_FILENAME = "she_reconciled_measurements.fits"

SHE_RECONCILED_CHAINS_PRODUCT_FILENAME = "she_reconciled_chains.xml"
SHE_RECONCILED_CHAINS_TABLE_FILENAME = "she_reconciled_chains.fits"

SHE_TEST_RESULTS_PRODUCT_FILENAME = "she_validation_test_results.xml"


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
