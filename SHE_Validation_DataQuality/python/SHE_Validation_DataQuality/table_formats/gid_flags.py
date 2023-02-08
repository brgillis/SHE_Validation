"""
:file: python/SHE_Validation_DataQuality/table_formats/gid_flags.py

:date: 02/08/23
:author: Bryan Gillis

Table format definition for a table providing details on occurrence rates of failure flags
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

import itertools

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_formats.she_lensmc_chains import len_chain
from SHE_PPT.table_utility import SheTableFormat, SheTableMeta
from SHE_Validation_DataQuality.constants.fit_flags import MAX_FLAG_NAME_LEN
from SHE_Validation_DataQuality.constants.gid_criteria import L_GID_CRITERIA
from SHE_Validation_DataQuality.table_formats.gid_objects import GIDO_META_METHOD, GIDO_META_OBS_IDS, GIDO_META_TILE_IDS

GIDF_FITS_VERSION = "9.1"
GIDF_FITS_DEF = "she.galInfoDataFlags"

GIDF_COLNAME_HEAD = "SHE_GIDF"

GIDF_META_METHOD = GIDO_META_METHOD
GIDF_META_OBS_IDS = GIDO_META_OBS_IDS
GIDF_META_TILE_IDS = GIDO_META_TILE_IDS

logger = getLogger(__name__)


class GalInfoDataFlagsMeta(SheTableMeta):
    """A class defining the metadata for GalInfo-Data flags tables
    """

    __version__: str = GIDF_FITS_VERSION
    table_format: str = GIDF_FITS_DEF

    method = GIDF_META_METHOD
    obs_ids = GIDF_META_OBS_IDS
    tile_ids = GIDF_META_TILE_IDS


class GalInfoDataFlagsFormat(SheTableFormat):
    """A class defining the columns in the GalInfo-Data flags tables
    """
    meta_type = GalInfoDataFlagsMeta

    # Column names
    name: str
    value: str
    count: str
    rate: str

    def __init__(self, final=True, **meta_kwargs):
        super().__init__(meta=self.meta_type(**meta_kwargs))

        # Table column labels
        self.name = self.set_column_properties(f"{GIDF_COLNAME_HEAD}_NAME", dtype=str, fits_dtype="A",
                                               length=MAX_FLAG_NAME_LEN)
        self.value = self.set_column_properties(f"{GIDF_COLNAME_HEAD}_VALUE", dtype=">i8", fits_dtype="K")
        self.count = self.set_column_properties(f"{GIDF_COLNAME_HEAD}_COUNT", dtype=">i4", fits_dtype="J")
        self.rate = self.set_column_properties(f"{GIDF_COLNAME_HEAD}_NAME", dtype=">f4", fits_dtype="E")

        self._finalize_init()


# Define an instance of this object that can be imported
GAL_INFO_DATA_FLAGS_FORMAT = GalInfoDataFlagsFormat()

# And a convenient alias for it
GIDF_TF = GAL_INFO_DATA_FLAGS_FORMAT
