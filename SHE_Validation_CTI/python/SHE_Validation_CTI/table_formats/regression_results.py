"""
:file: python/SHE_Validation_CTI/table_formats/regression_results.py

:date: 14 December 2020
:author: Bryan Gillis

Table format definition for Regression Results for the purpose of CTI-Gal Validation
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

from collections import OrderedDict

from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import SheTableFormat, SheTableMeta

FITS_VERSION = "8.0"
FITS_DEF = "she.regressionResults"

logger = getLogger(__name__)


class SheRegressionResultsMeta(SheTableMeta):
    """
        @brief A class defining the metadata for Regression Results tables.
    """

    __version__: str = FITS_VERSION
    table_format: str = FITS_DEF

    # Table metadata labels
    product_type: str = "PRODTYPE"
    test_case: str = "TESTCASE"
    bin_limit_min: str = "BIN_MIN"
    bin_limit_max: str = "BIN_MAX"

    def __init__(self):
        # Store the less-used comments in a dict
        super().__init__(comments=OrderedDict(((self.fits_version, None),
                                               (self.fits_def, None),
                                               (self.product_type, "Whether this is a test of an observation (OBS) " +
                                                "or exposure (EXP)"),
                                               (self.test_case, None),
                                               (self.bin_limit_min, None),
                                               (self.bin_limit_max, None),
                                               )))


class SheRegressionResultsFormat(SheTableFormat):
    """
        @brief A class defining the format for Regression Results tables. Only the regression_results_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        # Get the metadata (contained within its own class)
        super().__init__(SheRegressionResultsMeta())

        # Table column labels

        self.index = self.set_column_properties(f"INDEX", dtype=int, fits_dtype=">i2")
        self.method = self.set_column_properties(f"METHOD", dtype=str, fits_dtype="A", length=9)

        self.weight = self.set_column_properties(f"WEIGHT")
        self.slope = self.set_column_properties(f"M")
        self.intercept = self.set_column_properties(f"B")
        self.slope_err = self.set_column_properties(f"M_ERR")
        self.intercept_err = self.set_column_properties(f"B_ERR")
        self.slope_intercept_covar = self.set_column_properties(f"MB_COV")

        self._finalize_init()


# Define an instance of this object that can be imported
REGRESSION_RESULTS_TABLE_FORMAT = SheRegressionResultsFormat()

# And a convenient alias for it
TF = REGRESSION_RESULTS_TABLE_FORMAT
