""" @file regression_results.py

    Created 14 December 2020

    Table format definition for object data read in for the purpose of CTI-Gal Validation
"""

__updated__ = "2021-08-17"

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

from SHE_PPT.constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format, init_table, SheTableFormat, SheTableMeta
from astropy import table

from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMIT_MIN, DEFAULT_BIN_LIMIT_MAX

from ..constants.cti_gal_test_info import L_CTI_GAL_TEST_CASE_INFO


FITS_VERSION = "8.0"
FITS_DEF = "she.regressionResults"

logger = getLogger(__name__)


class SheRegressionResultsMeta(SheTableMeta):
    """
        @brief A class defining the metadata for Regression Results tables.
    """

    def __init__(self):

        self.__version__ = FITS_VERSION
        self.table_format = FITS_DEF

        # Table metadata labels
        self.fits_version = FITS_VERSION_LABEL
        self.fits_def = FITS_DEF_LABEL
        self.product_type = "PRODTYPE"
        self.test_case = "TESTCASE"
        self.bin_limit_min = "BIN_MIN"
        self.bin_limit_max = "BIN_MAX"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.product_type, "Whether this is a test of an observation (OBS) " +
                                                         "or exposure (EXP)"),
                                     (self.test_case, None),
                                     (self.bin_limit_min, None),
                                     (self.bin_limit_max, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheRegressionResultsFormat(SheTableFormat):
    """
        @brief A class defining the format for Regression Results tables. Only the regression_results_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        super().__init__(SheRegressionResultsMeta())

        # Table column labels

        # Set up separate result columns for each shear estimation method

        for method in ShearEstimationMethods:

            method_name = method.value
            upper_method = method_name.upper()

            setattr(self, f"weight_{method_name}", self.set_column_properties(f"WEIGHT_{upper_method}"))
            setattr(self, f"slope_{method_name}", self.set_column_properties(f"M_{upper_method}"))
            setattr(self, f"intercept_{method_name}", self.set_column_properties(f"B_{upper_method}"))
            setattr(self, f"slope_err_{method_name}", self.set_column_properties(f"M_ERR_{upper_method}"))
            setattr(self, f"intercept_err_{method_name}", self.set_column_properties(f"B_ERR_{upper_method}"))
            setattr(self, f"slope_intercept_covar_{method_name}", self.set_column_properties(f"MB_COV_{upper_method}"))

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
REGRESSION_RESULTS_TABLE_FORMAT = SheRegressionResultsFormat()

# And a convenient alias for it
TF = REGRESSION_RESULTS_TABLE_FORMAT
