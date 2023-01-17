"""
:file: python/SHE_Validation_PSF/utility.py

:date: 18 May 2022
:author: Bryan Gillis

Classes and functions for utility purposes for PSF Validation tests
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
from copy import deepcopy
from typing import List, Mapping, Optional, Sequence, Type, TypeVar, Union

import numpy as np
from astropy.table import Row, Table
from scipy.stats import chi2
from scipy.stats.stats import Ks_2sampResult, KstestResult

from SHE_PPT import logging
from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.table_formats.she_star_catalog import SheStarCatalogFormat, SheStarCatalogMeta
from SHE_PPT.table_utility import SheTableMeta
from SHE_PPT.utility import is_nan_or_masked
from SHE_Validation.binning.bin_constraints import get_table_of_ids
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

        self.snr = self.set_column_properties(BIN_TF.snr, dtype=BIN_TF.dtypes[BIN_TF.snr],
                                              fits_dtype=BIN_TF.fits_dtypes[BIN_TF.snr],
                                              is_optional=True)

        self.group_p = self.set_column_properties("SHE_STARCAT_GROUP_P", dtype=">f4", fits_dtype="E",
                                                  comment="p-value for a Chi-squared test on this group",
                                                  is_optional=True)

        self.star_p = self.set_column_properties("SHE_STARCAT_STAR_P", dtype=">f4", fits_dtype="E",
                                                 comment="p-value for a Chi-squared test on this star",
                                                 is_optional=True)

        self._finalize_init()


ESC_TF = SheExtStarCatalogFormat()


def calculate_p_values(cat: Optional[Table], group_mode: bool) -> Optional[List[float]]:
    """ Calculates and returns p values for all objects or groups in a star catalog.
    """

    if cat is None:
        return None

    # Select the columns to use based on the mode
    if group_mode:
        id_colname = ESC_TF.group_id
        chisq_colname = ESC_TF.group_chisq
        num_pix_colname = ESC_TF.group_unmasked_pix
        num_fitted_params_colname: Optional[str] = ESC_TF.group_num_fitted_params
        p_colname = ESC_TF.group_p
    else:
        id_colname = ESC_TF.id
        chisq_colname = ESC_TF.star_chisq
        num_pix_colname = ESC_TF.star_unmasked_pix
        num_fitted_params_colname: Optional[str] = None
        p_colname = ESC_TF.star_p

    # Add a column to store p values if necessary (the function handles a check if it's already there)
    add_p_columns_to_star_cat(cat)

    # We'll just use one row from each group, or each individual star, for the test
    l_unique_ids: Sequence[int] = np.unique(cat[id_colname])
    num_groups = len(l_unique_ids)

    l_ps = np.ones(num_groups, dtype=float)

    # Run the test for each group
    cat.add_index(id_colname)

    for i, group_id in enumerate(l_unique_ids):

        # Extract just the first row of each group
        table_or_row_in_group: Union[Table, Row] = cat.loc[group_id]

        if isinstance(table_or_row_in_group, Table):
            # Multiple rows are in this group, so just get the first
            data_row: Row = table_or_row_in_group[0]
        elif isinstance(table_or_row_in_group, Row):
            data_row: Row = table_or_row_in_group
        else:
            raise TypeError(f"Type of object returned by Table.loc is not recognized: {type(table_or_row_in_group)}")

        # Check if the p value has already been calculated, and use that if so
        if not is_nan_or_masked(data_row[p_colname]):
            l_ps[i] = data_row[p_colname]
            continue

        # Run the test on this row

        # Get the number of fitted params - if the colname is None, that means we have 0 fitted params
        if num_fitted_params_colname is not None:
            num_fitted_params = data_row[num_fitted_params_colname]
        else:
            num_fitted_params = 0

        l_ps[i] = chi2.sf(x=data_row[chisq_colname],
                          df=data_row[num_pix_colname] - num_fitted_params)

        # Save this value in the initial data table
        table_or_row_in_group[p_colname] = l_ps[i]

    return l_ps


def get_table_in_bin(cat: Optional[Table],
                     bin_parameter: BinParameters,
                     bin_index: int,
                     l_bin_limits: np.ndarray,
                     l_test_case_object_ids: Optional[Sequence[int]]) -> Optional[Table]:
    """Gets a table with only the rows within a given bin. Returns None if cat is None.
    """
    if cat is None:
        return None

    table_in_bin = deepcopy(get_table_of_ids(cat, l_test_case_object_ids, id_colname=ESC_TF.id))

    # Save the info about bin_parameter and bin_limits in the table's metadata
    table_in_bin.meta[ESC_TF.m.bin_parameter] = bin_parameter.value
    table_in_bin.meta[ESC_TF.m.bin_limits] = str(l_bin_limits[bin_index:bin_index + 2])

    return table_in_bin


KeyType = TypeVar('KeyType')
ItemType = TypeVar('ItemType')


def getitem_or_none(a: Optional[Mapping[KeyType, ItemType]], i: KeyType) -> Optional[ItemType]:
    """Utility function to either get an item of a list or dict if it's not None, or return None if it is None."""
    if a is None:
        return None
    else:
        return a[i]


def add_snr_column_to_star_cat(star_cat: Table) -> None:
    """Adds the SNR column to the star catalog if not already present.
    """
    if ESC_TF.snr not in star_cat.colnames:
        star_cat[ESC_TF.snr] = star_cat[ESC_TF.flux] / star_cat[ESC_TF.flux_err]


def add_p_columns_to_star_cat(star_cat: Table) -> None:
    """ Adds columns for star and group p-values to the table if not already present. The new columns will initially
        be filled with np.NaN to indicate it has not yet been calculated.
    """
    len_star_cat = len(star_cat)
    if ESC_TF.group_p not in star_cat.colnames:
        star_cat[ESC_TF.group_p] = np.NaN * np.ones(len_star_cat, dtype=ESC_TF.dtypes[ESC_TF.group_p])
    if ESC_TF.star_p not in star_cat.colnames:
        star_cat[ESC_TF.star_p] = np.NaN * np.ones(len_star_cat, dtype=ESC_TF.dtypes[ESC_TF.star_p])
