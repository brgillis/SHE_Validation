"""
:file: python/SHE_Validation_DataQuality/table_formats/gid_objects.py

:date: 01/30/23
:author: Bryan Gillis

Table format definition for a table providing details on objects which failed GalInfo-Data validity check.
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
from SHE_Validation_DataQuality.constants.gid_criteria import L_GID_CRITERIA

GID_FITS_VERSION = "9.1"
GID_FITS_DEF = "she.galInfoDataObjects"

GID_CHAINS_FITS_VERSION = GID_FITS_VERSION
GID_CHAINS_FITS_DEF = "she.galInfoDataObjectsChains"

GID_COLNAME_HEAD = "SHE_GID"

GID_META_METHOD = "SEMETHOD"
GID_META_OBS_IDS = "OBS_IDS"
GID_META_TILE_IDS = "TILE_IDS"

GID_META_G1 = "G1"
GID_META_G2 = "G2"
GID_META_WEIGHT = "W"
GID_META_FIT_CLASS = "FC"
GID_META_RE = "RE"

GID_META_MIN = "MIN"
GID_META_MAX = "MAX"
GID_META_IS_CHAIN = "ISC"

GID_VAL = "val"
GID_MIN = "min"
GID_MAX = "max"
GID_IS_CHAIN = "is_chain"

GID_CHECK_TAIL = "check"

logger = getLogger(__name__)


class GalInfoDataMeasMeta(SheTableMeta):
    """A class defining the metadata for GalInfo-Data objects measurements tables
    """

    __version__: str = GID_FITS_VERSION
    table_format: str = GID_FITS_DEF

    method = GID_META_METHOD
    obs_ids = GID_META_OBS_IDS
    tile_ids = GID_META_TILE_IDS

    g1_min = f"{GID_META_G1}_{GID_META_MIN}"
    g1_max = f"{GID_META_G1}_{GID_META_MAX}"
    g1_is_chain = f"{GID_META_G1}_{GID_META_IS_CHAIN}"

    g2_min = f"{GID_META_G2}_{GID_META_MIN}"
    g2_max = f"{GID_META_G2}_{GID_META_MAX}"
    g2_is_chain = f"{GID_META_G2}_{GID_META_IS_CHAIN}"

    weight_min = f"{GID_META_WEIGHT}_{GID_META_MIN}"
    weight_max = f"{GID_META_WEIGHT}_{GID_META_MAX}"
    weight_is_chain = f"{GID_META_WEIGHT}_{GID_META_IS_CHAIN}"

    fit_class_min = f"{GID_META_FIT_CLASS}_{GID_META_MIN}"
    fit_class_max = f"{GID_META_FIT_CLASS}_{GID_META_MAX}"
    fit_class_is_chain = f"{GID_META_FIT_CLASS}_{GID_META_IS_CHAIN}"

    re_min = f"{GID_META_RE}_{GID_META_MIN}"
    re_max = f"{GID_META_RE}_{GID_META_MAX}"
    re_is_chain = f"{GID_META_RE}_{GID_META_IS_CHAIN}"

    def init_meta(self, **kwargs):
        """Inherit init to also set up min/max/is_chain values for each parameter
        """
        m = super().init_meta(**kwargs)

        for gid_criteria, prop in itertools.product(L_GID_CRITERIA, (GID_MIN,
                                                                     GID_MAX,
                                                                     GID_IS_CHAIN)):

            attr = gid_criteria.attr
            attr_prop = f"{attr}_{prop}"
            meta_key = getattr(self, attr_prop)

            # Don't override any that have already been set through kwargs
            if m.get(meta_key) is not None:
                continue

            # Set the value from the `gid_criteria`
            m[meta_key] = getattr(gid_criteria, prop)

        return m


class GalInfoDataMeasFormat(SheTableFormat):
    """A class defining the columns in the GalInfo-Data object measurements tables
    """
    meta_type = GalInfoDataMeasMeta

    # Column names
    ID: str
    fit_flags: str

    g1: str
    g1_val_check: str
    g1_min_check: str
    g1_max_check: str

    g2: str
    g2_val_check: str
    g2_min_check: str
    g2_max_check: str

    weight: str
    weight_val_check: str
    weight_min_check: str
    weight_max_check: str

    fit_class: str
    fit_class_val_check: str
    fit_class_min_check: str
    fit_class_max_check: str

    re: str
    re_val_check: str
    re_min_check: str
    re_max_check: str

    def __init__(self, final=True, **meta_kwargs):
        super().__init__(meta=self.meta_type(**meta_kwargs))

        # Table column labels
        self.ID = self.set_column_properties(mfc_tf.ID, dtype=">i8", fits_dtype="K")
        self.fit_flags = self.set_column_properties(f"{GID_COLNAME_HEAD}_FIT_FLAGS",
                                                    dtype=">i8", fits_dtype="K")

        # Columns for each value we test
        for gid_criteria, prop in itertools.product(L_GID_CRITERIA, (None, GID_VAL, GID_MIN, GID_MAX)):

            attr = gid_criteria.attr

            # Split some setup depending on if we're setting the basic value or its checks
            if prop is None:
                attr_prop = attr
                comment = None
                if attr_prop == "fit_class":
                    dtype = ">i2"
                    fits_dtype = "I"
                else:
                    dtype = ">f4"
                    fits_dtype = "E"
            else:
                attr_prop = f"{attr}_{prop}_{GID_CHECK_TAIL}"
                dtype = "bool"
                fits_dtype = "L"
                comment = "True = pass check; False = fail check"

            colname = f"{GID_COLNAME_HEAD}_{attr_prop.upper()}"
            self.set_column_properties(colname, dtype=dtype, fits_dtype=fits_dtype, comment=comment)

            setattr(self, attr_prop, colname)

        if final:
            self._finalize_init()


# Define an instance of this object that can be imported
GAL_INFO_DATA_MEAS_FORMAT = GalInfoDataMeasFormat()

# And a convenient alias for it
GIDM_TF = GAL_INFO_DATA_MEAS_FORMAT


class GalInfoDataChainsMeta(GalInfoDataMeasMeta):
    """A class defining the metadata for GalInfo-Data object chains tables. This is subclassed from the measurements
    table, as the only difference is the value data types and some header info
    """

    __version__: str = GID_FITS_VERSION
    table_format: str = GID_FITS_DEF

    def init_meta(self, method=ShearEstimationMethods.LENSMC.value, **kwargs):
        """Inherit init to set method to LensMC if not otherwise set
        """
        return super().init_meta(method=method, **kwargs)


class GalInfoDataChainsFormat(GalInfoDataMeasFormat):
    """A class defining the columns in the GalInfo-Data object chains tables. This is subclassed from the measurements
    table, as the only difference is the value data types and some header info
    """
    meta_type = GalInfoDataChainsMeta

    def __init__(self, **meta_kwargs):
        super().__init__(final=False, **meta_kwargs)

        # Adjust the datatype for each chains column
        for gid_criteria in L_GID_CRITERIA:

            if not gid_criteria.is_chain:
                continue

            colname = f"{GID_COLNAME_HEAD}_{gid_criteria.attr.upper()}"
            self.lengths[colname] = len_chain

        self._finalize_init()


# Define an instance of this object that can be imported
GAL_INFO_DATA_CHAINS_FORMAT = GalInfoDataChainsFormat()

# And a convenient alias for it
GIDC_TF = GAL_INFO_DATA_CHAINS_FORMAT
