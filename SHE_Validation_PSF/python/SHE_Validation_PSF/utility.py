""" @file utility.py

    Created 18 May 2022

    Classes and functions for utility purposes for PSF Validation tests
"""

__updated__ = "2022-04-28"

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
from typing import Type, Union

from scipy.stats.stats import Ks_2sampResult, KstestResult

from SHE_PPT import logging
from SHE_PPT.table_formats.she_star_catalog import SheStarCatalogFormat, SheStarCatalogMeta
from SHE_PPT.table_utility import SheTableMeta
from SHE_Validation.binning.bin_data import BIN_TF

logger = logging.getLogger(__name__)

# Define a type for a union of the two possible types we'll get from the different modes of KS tests
KsResult = Union[KstestResult, Ks_2sampResult]


# We'll be modifying the star catalog table a bit, so define an extended table format for the new columns
class SheExtStarCatalogMeta(SheStarCatalogMeta):
    """ Modified star catalog metadata format which adds some meta values.
    """

    def __init__(self):
        super().__init__()

        self.bin_parameter = "BIN_PAR"
        self.bin_limits = "BIN_LIMS"


class SheExtStarCatalogFormat(SheStarCatalogFormat):
    """ Modified star catalog table format which adds a few extra columns and some metadata values.
    """
    meta_type: Type[SheTableMeta] = SheExtStarCatalogMeta
    meta: SheExtStarCatalogMeta
    m: SheExtStarCatalogMeta

    def __init__(self):
        super().__init__()

        self.snr = self.set_column_properties(BIN_TF.snr, dtype = BIN_TF.dtypes[BIN_TF.snr],
                                              fits_dtype = BIN_TF.fits_dtypes[BIN_TF.snr],
                                              is_optional = True)

        self.group_p = self.set_column_properties("SHE_STARCAT_GROUP_P", dtype = ">f4", fits_dtype = "E",
                                                  comment = "p-value for a Chi-squared test on this group",
                                                  is_optional = True)

        self.star_p = self.set_column_properties("SHE_STARCAT_STAR_P", dtype = ">f4", fits_dtype = "E",
                                                 comment = "p-value for a Chi-squared test on this star",
                                                 is_optional = True)

        self._finalize_init()


ESC_TF = SheExtStarCatalogFormat()
