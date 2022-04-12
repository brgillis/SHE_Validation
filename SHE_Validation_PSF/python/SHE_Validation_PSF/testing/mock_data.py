""" @file mock_data.py

    Created 12 April 2022 by Bryan Gillis

    Utilities for creating mock data specifically for PSF validation tests.
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

from SHE_PPT.testing.mock_she_star_cat import MockStarCatTableGenerator, STAR_CAT_SEED
from SHE_Validation_PSF.testing.constants import (REF_STAR_CAT_TABLE_FILENAME, REF_STAR_CAT_TABLE_LISTFILE_FILENAME,
                                                  REF_STAR_CAT_TABLE_PRODUCT_FILENAME, )


class MockRefStarCatTableGenerator(MockStarCatTableGenerator):
    seed: int = STAR_CAT_SEED + 1
    table_filename: str = REF_STAR_CAT_TABLE_FILENAME
    product_filename: str = REF_STAR_CAT_TABLE_PRODUCT_FILENAME
    listfile_filename: str = REF_STAR_CAT_TABLE_LISTFILE_FILENAME
