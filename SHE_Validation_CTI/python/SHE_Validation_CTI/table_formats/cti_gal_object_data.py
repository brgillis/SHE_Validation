""" @file cti_gal_object_data.py

    Created 14 December 2020

    Table format definition for object data read in for the purpose of CTI-Gal Validation
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


from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import SheTableFormat, SheTableMeta

FITS_VERSION = "8.0"
FITS_DEF = "she.ctiGalObjectData"

logger = getLogger(__name__)


class SheCtiGalObjectDataMeta(SheTableMeta):
    """
        @brief A class defining the metadata for CTI-Gal Object Data tables.
    """

    __version__: str = FITS_VERSION
    table_format: str = FITS_DEF


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

        self.quadrant = self.set_column_properties("QUAD", dtype="str", fits_dtype="A", length=1,
                                                   is_optional=True)
        self.readout_dist = self.set_column_properties("READOUT_DIST", comment="pixels", is_optional=True)

        # Set up separate shear columns for each shear estimation method

        for method in ShearEstimationMethods:

            method_name = method.value
            upper_method = method_name.upper()

            setattr(self, f"g1_world_{method_name}", self.set_column_properties(
                f"G1_WORLD_{upper_method}", is_optional=True))
            setattr(self, f"g2_world_{method_name}", self.set_column_properties(
                f"G2_WORLD_{upper_method}", is_optional=True))

            setattr(self, f"weight_{method_name}", self.set_column_properties(f"WEIGHT_{upper_method}"))

            setattr(self, f"g1_image_{method_name}",
                    self.set_column_properties(f"G1_IMAGE_{upper_method}"))
            setattr(self, f"g2_image_{method_name}",
                    self.set_column_properties(f"G2_IMAGE_{upper_method}"))

        self._finalize_init()


# Define an instance of this object that can be imported
CTI_GAL_OBJECT_DATA_TABLE_FORMAT = SheCtiGalObjectDataFormat()

# And a convenient alias for it
TF = CTI_GAL_OBJECT_DATA_TABLE_FORMAT
