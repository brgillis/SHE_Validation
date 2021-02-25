""" @file regression_results.py

    Created 14 December 2020

    Table format definition for object data read in for the purpose of CTI-Gal Validation
"""

__updated__ = "2021-02-25"

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

from astropy import table

from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.magic_values import fits_version_label, fits_def_label
from SHE_PPT.table_utility import is_in_format, setup_table_format, set_column_properties, init_table

from ..constants.cti_gal_default_config import DEFAULT_BIN_LIMIT_MIN, DEFAULT_BIN_LIMIT_MAX
from ..constants.cti_gal_test_info import CTI_GAL_TEST_CASE_GLOBAL


FITS_VERSION = "8.0"
FITS_DEF = "she.regressionResults"

logger = getLogger(__name__)


class SheRegressionResultsMeta(object):
    """
        @brief A class defining the metadata for Regression Results tables.
    """

    def __init__(self):

        self.__version__ = FITS_VERSION
        self.table_format = FITS_DEF

        # Table metadata labels
        self.fits_version = fits_version_label
        self.fits_def = fits_def_label
        self.product_type = "PRODTYPE"
        self.test_case = "TESTCASE"
        self.bin_limit_min = "BIN_MIN"
        self.bin_limit_max = "BIN_MAX"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.product_type, "Whether this is a test of an observation (OBS) or exposure (EXP)")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheRegressionResultsFormat(object):
    """
        @brief A class defining the format for Regression Results tables. Only the regression_results_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = SheRegressionResultsMeta()

        setup_table_format(self)

        # Table column labels

        # Set up separate result columns for each shear estimation method

        for method in METHODS:

            upper_method = method.upper()

            setattr(self, f"weight_{method}", set_column_properties(self, f"WEIGHT_{upper_method}"))
            setattr(self, f"slope_{method}", set_column_properties(self, f"M_{upper_method}"))
            setattr(self, f"intercept_{method}", set_column_properties(self, f"B_{upper_method}"))
            setattr(self, f"slope_err_{method}", set_column_properties(self, f"M_ERR_{upper_method}"))
            setattr(self, f"intercept_err_{method}", set_column_properties(self, f"B_ERR_{upper_method}"))
            setattr(self, f"slope_intercept_covar_{method}", set_column_properties(self, f"MB_COV_{upper_method}"))

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


def make_regression_results_table_header(product_type: str = None,
                                         test_case: str = CTI_GAL_TEST_CASE_GLOBAL,
                                         bin_limit_min: float = DEFAULT_BIN_LIMIT_MIN,
                                         bin_limit_max: float = DEFAULT_BIN_LIMIT_MAX):
    """
        @brief Generate a header for a Regression Results table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[TF.m.fits_version] = TF.__version__
    header[TF.m.fits_def] = FITS_DEF

    header[TF.m.product_type] = product_type
    header[TF.m.test_case] = test_case
    header[TF.m.bin_limit_min] = bin_limit_min
    header[TF.m.bin_limit_max] = bin_limit_max

    return header


def initialise_regression_results_table(optional_columns: List[str] = None,
                                        init_cols: List[table.Column] = None,
                                        size: int = None,
                                        product_type: str = None):
    """
        @brief Initialise a Regression Results table.

        @param optional_columns <list<str>> List of names for optional columns to include.

        @return regression_results_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in TF.all:
                raise ValueError("Invalid optional column name: " + colname)

    regression_results_table = init_table(TF, optional_columns=optional_columns, init_cols=init_cols, size=size)

    regression_results_table.meta = make_regression_results_table_header(product_type=product_type)

    assert is_in_format(regression_results_table, TF, verbose=True)

    return regression_results_table
