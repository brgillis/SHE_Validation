""" @file cti_gal_object_data.py

    Created 14 December 2020

    Table format definition for object data read in for the purpose of CTI-Gal Validation
"""

__updated__ = "2020-12-14"

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

from collections import OrderedDict
from typing import List

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format, setup_table_format, set_column_properties, init_table


fits_version = "8.0"
fits_def = "she.ctiGalObjectData"

logger = getLogger(mv.logger_name)


class SheCtiGalObjectDataMeta(object):
    """
        @brief A class defining the metadata for CTI-Gal Object Data tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheCtiGalObjectDataFormat(object):
    """
        @brief A class defining the format for CTI-Gal Object Data tables. Only the cti_gal_object_data_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = SheCtiGalObjectDataMeta()

        setup_table_format(self)

        # Table column labels
        self.ID = set_column_properties(self, "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.x = set_column_properties(self, "X_IMAGE", comment="pixels")
        self.y = set_column_properties(self, "Y_IMAGE", comment="pixels")

        self.det_x = set_column_properties(self, "DET_X", dtype=">i2", fits_dtype="I")
        self.det_y = set_column_properties(self, "DET_Y", dtype=">i2", fits_dtype="I")

        self.quadrant = set_column_properties(self, "QUAD", dtype="str", fits_dtype="A", length=1)

        self.g1_world = set_column_properties(self, "G1_WORLD")
        self.g2_world = set_column_properties(self, "G2_WORLD")

        self.g1_image = set_column_properties(self, "G1_IMAGE")
        self.g2_image = set_column_properties(self, "G2_IMAGE")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
cti_gal_object_data_table_format = SheCtiGalObjectDataFormat()

# And a convient alias for it
tf = cti_gal_object_data_table_format


def make_cti_gal_object_data_table_header():
    """
        @brief Generate a header for a CTI-Gal Object Data table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

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
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    cti_gal_object_data_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    cti_gal_object_data_table.meta = make_cti_gal_object_data_table_header()

    assert(is_in_format(cti_gal_object_data_table, tf, verbose=True))

    return cti_gal_object_data_table
