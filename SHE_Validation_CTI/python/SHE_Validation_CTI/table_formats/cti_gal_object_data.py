""" @file cti_gal_object_data.py

    Created 14 December 2020

    Table format definition for object data read in for the purpose of CTI-Gal Validation
"""
from collections import OrderedDict
from typing import List

from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.magic_values import fits_version_label, fits_def_label
from SHE_PPT.table_utility import is_in_format, init_table, SheTableFormat
from astropy import table

from SHE_Validation.constants.test_info import BinParameters, D_BIN_PARAMETER_META


__updated__ = "2021-08-04"

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


FITS_VERSION = "8.0"
FITS_DEF = "she.ctiGalObjectData"

logger = getLogger(__name__)


class SheCtiGalObjectDataMeta():
    """
        @brief A class defining the metadata for CTI-Gal Object Data tables.
    """

    def __init__(self):

        self.__version__ = FITS_VERSION
        self.table_format = FITS_DEF

        # Table metadata labels
        self.fits_version = fits_version_label
        self.fits_def = fits_def_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheCtiGalObjectDataFormat(SheTableFormat):
    """
        @brief A class defining the format for CTI-Gal Object Data tables. Only the cti_gal_object_data_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheCtiGalObjectDataMeta())

        # Table column labels
        self.ID = self.set_column_properties("OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.x = self.set_column_properties("X_IMAGE", comment="pixels")
        self.y = self.set_column_properties("Y_IMAGE", comment="pixels")

        self.det_ix = self.set_column_properties("DET_X", dtype=">i2", fits_dtype="I")
        self.det_iy = self.set_column_properties("DET_Y", dtype=">i2", fits_dtype="I")

        self.quadrant = self.set_column_properties("QUAD", dtype="str", fits_dtype="A", length=1, is_optional=True)
        self.readout_dist = self.set_column_properties("READOUT_DIST", comment="pixels", is_optional=True)

        # Data we might bin by
        for bin_parameter in BinParameters:
            name = D_BIN_PARAMETER_META[bin_parameter].name
            comment = D_BIN_PARAMETER_META[bin_parameter].comment
            setattr(self, name, self.set_column_properties(name.upper(), comment=comment, is_optional=True))

        # Set up separate shear columns for each shear estimation method

        for method in METHODS:

            upper_method = method.upper()

            setattr(self, f"g1_world_{method}", self.set_column_properties(
                f"G1_WORLD_{upper_method}", is_optional=True))
            setattr(self, f"g2_world_{method}", self.set_column_properties(
                f"G2_WORLD_{upper_method}", is_optional=True))

            setattr(self, f"weight_{method}", self.set_column_properties(f"WEIGHT_{upper_method}"))

            setattr(self, f"g1_image_{method}",
                    self.set_column_properties(f"G1_IMAGE_{upper_method}"))
            setattr(self, f"g2_image_{method}",
                    self.set_column_properties(f"G2_IMAGE_{upper_method}"))

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
CTI_GAL_OBJECT_DATA_TABLE_FORMAT = SheCtiGalObjectDataFormat()

# And a convient alias for it
TF = CTI_GAL_OBJECT_DATA_TABLE_FORMAT


def make_cti_gal_object_data_table_header():
    """
        @brief Generate a header for a CTI-Gal Object Data table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[TF.m.fits_version] = TF.__version__
    header[TF.m.fits_def] = FITS_DEF

    return header


def initialise_cti_gal_object_data_table(optional_columns: List[str] = None,
                                         init_cols: List[table.Column] = None,
                                         size: int = None):
    """
        @brief Initialise a CTI-Gal Object Data table.

        @param optional_columns <list<str>> List of names for optional columns to include.

        @return cti_gal_object_data_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in TF.all:
                raise ValueError("Invalid optional column name: " + colname)

    cti_gal_object_data_table = init_table(TF, optional_columns=optional_columns, init_cols=init_cols, size=size)

    cti_gal_object_data_table.meta = make_cti_gal_object_data_table_header()

    assert is_in_format(cti_gal_object_data_table, TF, verbose=True)

    return cti_gal_object_data_table
