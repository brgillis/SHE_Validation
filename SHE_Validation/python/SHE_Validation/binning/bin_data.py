""" @file bin_data.py

    Created 24 August 2021

    Table format and useful functions for determining bin data
"""

__updated__ = "2021-08-25"

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

from typing import Sequence, Union

import numpy as np
from astropy.table import Column, Row, Table

from SHE_PPT.logging import getLogger
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_utility import SheTableFormat, SheTableMeta
from ..constants.test_info import BinParameters, NON_GLOBAL_BIN_PARAMETERS

logger = getLogger(__name__)

FITS_VERSION = "8.0"
FITS_DEF = "she.sheBinData"

BG_STAMP_SIZE = 1


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

    snr: str
    bg: str
    colour: str
    size: str
    epoch: str

    def __init__(self):
        super().__init__(SheBinDataMeta())

        # Set a column for each bin parameter
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:
            setattr(self, bin_parameter.value, self.set_column_properties(name = bin_parameter.name, is_optional = True,
                                                                          dtype = ">f4", fits_dtype = "E"))

        self._finalize_init()


# Define an instance of this object that can be imported
BIN_DATA_TABLE_FORMAT = SheBinDataFormat()

# And a convenient alias for it
TF = BIN_DATA_TABLE_FORMAT


# Functions to add columns of bin data to a table


def add_global_column(_t: Table,
                      _data_stack: SHEFrameStack) -> None:
    """ Dummy method to add a global column, for a consistent interface.
    """
    pass


def add_snr_column(t: Table,
                   data_stack: SHEFrameStack) -> None:
    """ Calculates SNR data and adds a column for it to the table.
    """

    # Check first if necessary data is in the target table
    data_table = _determine_data_table(t, data_stack, data_colname = MFC_TF.FLUXERR_VIS_APER)

    snr_data: Sequence[float] = np.where(data_table[MFC_TF.FLUXERR_VIS_APER] != 0.,
                                         data_table[MFC_TF.FLUX_VIS_APER] / data_table[MFC_TF.FLUXERR_VIS_APER],
                                         np.NaN)

    snr_column: Column = Column(data = snr_data, name = TF.snr, dtype = TF.dtypes[TF.snr])

    t.add_column(snr_column)


def add_colour_column(t: Table,
                      data_stack: SHEFrameStack) -> None:
    """ Calculates colour data and adds a column for it to the table.
    """

    # Check first if necessary data is in the target table
    data_table = _determine_data_table(t, data_stack, data_colname = MFC_TF.FLUX_NIR_STACK_APER)

    colour_data: Sequence[float] = np.where(data_table[MFC_TF.FLUX_NIR_STACK_APER] != 0.,
                                            2.5 * np.log10(data_table[MFC_TF.FLUX_VIS_APER] /
                                                           data_table[MFC_TF.FLUX_NIR_STACK_APER]),
                                            np.NaN)

    colour_column: Column = Column(data = colour_data, name = TF.colour, dtype = TF.dtypes[TF.colour])

    t.add_column(colour_column)


def add_size_column(t: Table,
                    data_stack: SHEFrameStack) -> None:
    """ Calculates size data and adds a column for it to the table.
    """

    # Check first if necessary data is in the target table
    data_table = _determine_data_table(t, data_stack, data_colname = MFC_TF.SEGMENTATION_AREA)

    size_data: Sequence[float] = data_table[MFC_TF.SEGMENTATION_AREA].data

    size_column: Column = Column(data = size_data, name = TF.size, dtype = TF.dtypes[TF.size])

    t.add_column(size_column)


def add_bg_column(t: Table,
                  data_stack: SHEFrameStack):
    """ Calculates background level data and adds a column for it to the table.
    """

    l_object_ids: Sequence[int] = t[MFC_TF.ID]

    bg_data: np.ndarray = np.zeros_like(l_object_ids, dtype = TF.dtypes[TF.bg])

    # Loop over objects to calculate background level
    for object_index, object_id in enumerate(l_object_ids):

        # Get the background level from background image at the object position
        stamp_stack = data_stack.extract_galaxy_stack(object_id, width = BG_STAMP_SIZE, extract_stacked_stamp = False)
        l_background_level = [None] * len(stamp_stack.exposures)
        for exp_index, exp_image in enumerate(stamp_stack.exposures):
            if exp_image is not None:
                l_background_level[exp_index] = exp_image.background_map.mean()

        # Calculate the mean background level of all valid exposures
        bg_array: np.ndarray = np.array(l_background_level)
        # noinspection PyPep8,PyComparisonWithNone
        valid_bg: np.ndarray = bg_array != None
        # noinspection PyUnresolvedReferences
        if valid_bg.sum() > 0:
            bg_data[object_index] = bg_array[valid_bg].mean()
        else:
            # No data, so set -99 for mean background level
            bg_data[object_index] = -99

    bg_column: Column = Column(data = bg_data, name = TF.bg, dtype = TF.dtypes[TF.bg])

    t.add_column(bg_column)


def add_epoch_column(t: Table,
                     data_stack: SHEFrameStack) -> None:
    """ Calculates epoch data and adds a column for it to the table.
    """

    # Check first if necessary data is in the target table
    data_table = _determine_data_table(t, data_stack, data_colname = MFC_TF.FLUXERR_VIS_APER)

    # TODO: Fill in with proper calculation
    epoch_data: Sequence[float] = np.zeros_like(data_table[MFC_TF.FLUXERR_VIS_APER].data)

    epoch_column: Column = Column(data = epoch_data, name = TF.epoch, dtype = TF.dtypes[TF.epoch])

    t.add_column(epoch_column)


def _determine_data_table(t: Table,
                          data_stack: SHEFrameStack,
                          data_colname: str) -> Union[Table, Row]:
    data_table: Table
    if data_colname in t.colnames:
        data_table = t
    elif data_colname in data_stack.detections_catalogue.colnames:
        full_data_table: Table = data_stack.detections_catalogue

        # We need to make sure IDs align, so here we select on IDs in t
        if not MFC_TF.ID in full_data_table.indices:
            full_data_table.add_index(MFC_TF.ID)

        data_table = full_data_table.loc[t[MFC_TF.ID]]

    else:
        raise ValueError("Cannot find necessary data to calculate bin data in either target table or data stack.")
    return data_table


D_COLUMN_ADDING_METHODS = {
    BinParameters.GLOBAL: add_global_column,
    BinParameters.SNR   : add_snr_column,
    BinParameters.BG    : add_bg_column,
    BinParameters.COLOUR: add_colour_column,
    BinParameters.SIZE  : add_size_column,
    BinParameters.EPOCH : add_epoch_column}
