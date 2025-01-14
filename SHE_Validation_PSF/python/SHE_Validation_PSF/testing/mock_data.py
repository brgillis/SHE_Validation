"""
:file: python/SHE_Validation_PSF/testing/mock_data.py

:date: 12 April 2022
:author: Bryan Gillis

Utilities for creating mock data specifically for PSF validation tests
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

import numpy as np

from SHE_PPT.testing.mock_she_star_cat import MockStarCatDataGenerator, MockStarCatTableGenerator, STAR_CAT_SEED
from SHE_Validation_PSF.testing.constants import (REF_STAR_CAT_LISTFILE_FILENAME, REF_STAR_CAT_PRODUCT_FILENAME,
                                                  REF_STAR_CAT_TABLE_FILENAME, )
from SHE_Validation_PSF.utility import ESC_TF, SheExtStarCatalogFormat


class MockValStarCatDataGenerator(MockStarCatDataGenerator):
    """ Modified version of the data generator which adds bin columns in directly.
    """

    tf: SheExtStarCatalogFormat = ESC_TF

    def _generate_unique_data(self):
        super()._generate_unique_data()

        # Add the SNR column with controlled values - in pattern of 1, 1, 0, 0, repeating (plus random between -0.5
        # and 0.5)
        factor = 4
        l_rand = -0.5 + self._rng.uniform(size=self.num_test_points)
        self.data[self.tf.snr] = np.where(self._indices % factor < factor / 2,
                                          self._ones,
                                          self._zeros) + l_rand


class MockValStarCatTableGenerator(MockStarCatTableGenerator):
    """ Modified version of the table generator which used the modified version of the data generator.
    """

    tf: SheExtStarCatalogFormat = ESC_TF
    mock_data_generator_type = MockValStarCatDataGenerator


class MockRefValStarCatTableGenerator(MockValStarCatTableGenerator):
    seed: int = STAR_CAT_SEED + 1
    table_filename: str = REF_STAR_CAT_TABLE_FILENAME
    product_filename: str = REF_STAR_CAT_PRODUCT_FILENAME
    listfile_filename: str = REF_STAR_CAT_LISTFILE_FILENAME
