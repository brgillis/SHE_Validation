""" @file bin_data.py

    Created 24 August 2021

    Table format and useful functions for determining bin data
"""

__updated__ = "2021-08-24"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import SheTableFormat, SheTableMeta

from SHE_Validation.constants.test_info import BinParameters

FITS_VERSION = "8.0"
FITS_DEF = "she.sheBinData"

logger = getLogger(__name__)

# Table and metadata format for data needed for binning


class SheBinDataMeta(SheTableMeta):
    """
        @brief A class defining the metadata for bin data tables.
    """

    __version__: str = FITS_VERSION
    table_format: str = FITS_DEF


class SheBinDataFormat(SheTableFormat):
    """
        @brief A class defining the format for bin Data tables.
    """

    # global: str - have to specify with setattr due to "global" keyword
    snr: str
    bg: str
    colour: str
    size: str
    epoch: str

    def __init__(self):
        super().__init__(SheBinDataMeta())

        # Set a column for each bin parameter
        for bin_parameter in BinParameters:
            setattr(self, bin_parameter.value, self.set_column_properties(name=bin_parameter.name, is_optional=True,
                                                                          dtype=">f4", fits_dtype="E"))

        self._finalize_init()


# Define an instance of this object that can be imported
BIN_DATA_TABLE_FORMAT = SheBinDataFormat()

# And a convient alias for it
TF = BIN_DATA_TABLE_FORMAT
