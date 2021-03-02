""" @file data_processing.py

    Created 24 December 2020

    Utility functions for CTI-Gal validation, for processing the data.
"""
from typing import Tuple

from SHE_PPT import mdb
from SHE_PPT.constants.shear_estimation_methods import METHODS
from SHE_PPT.logging import getLogger
from SHE_PPT.math import linregress_with_errors
from astropy import table

from SHE_Validation_CTI.constants.cti_gal_default_config import DEFAULT_BIN_LIMITS
from SHE_Validation_CTI.constants.cti_gal_test_info import (CTI_GAL_TEST_CASE_GLOBAL,
                                                            D_CTI_GAL_TEST_CASE_INFO,
                                                            CTI_GAL_TEST_CASE_EPOCH)
import numpy as np

from .table_formats.cti_gal_object_data import TF as CGOD_TF
from .table_formats.regression_results import TF as RR_TF, initialise_regression_results_table


__updated__ = "2021-02-26"

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


logger = getLogger(__name__)


def add_readout_register_distance(object_data_table: table.Table):
    """ Calculates the distance of each object from the readout register and adds a column of these distances to
        the table.
    """

    # Get the y-dimension size of the detector from the mdb, and split by half of it
    det_size_y = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
    det_split_y = det_size_y / 2

    y_pos = object_data_table[CGOD_TF.y]

    readout_distance_data = np.where(y_pos < det_split_y, y_pos, det_size_y - y_pos)

    if CGOD_TF.readout_dist in object_data_table.colnames:
        object_data_table[CGOD_TF.readout_dist] = readout_distance_data
    else:
        readout_distance_column = table.Column(name=CGOD_TF.readout_dist, data=readout_distance_data)
        object_data_table.add_column(readout_distance_column)


def calculate_regression_results(object_data_table: table.Table,
                                 product_type: str = "UNKNOWN",
                                 test_case: str = CTI_GAL_TEST_CASE_GLOBAL,
                                 bin_limits: Tuple[float, float] = DEFAULT_BIN_LIMITS):
    """ Performs a linear regression of g1 versus readout register distance for each shear estimation method,
        using data in the input object_data_table, and returns it as a one-row table of format regression_results.
    """

    # Initialize a table for the output data
    regression_results_table = initialise_regression_results_table(product_type=product_type, size=1)

    rr_row = regression_results_table[0]

    # Get an array of good indices based on the test_case and bin_limits
    if test_case == CTI_GAL_TEST_CASE_GLOBAL:
        # Set all to True
        rows_in_bin = np.ones(len(object_data_table), dtype=bool)
    elif test_case == CTI_GAL_TEST_CASE_EPOCH:
        # Not yet implemented, so set all to False
        rows_in_bin = np.zeros(len(object_data_table), dtype=bool)
    else:
        # Get the column name of this property from the table format and check it exists
        colname = getattr(CGOD_TF, D_CTI_GAL_TEST_CASE_INFO[test_case].name)
        if not colname in object_data_table.colnames:
            raise ValueError(f"Column {colname} is not preset in object_data_table - make sure it's added earlier " +
                             "in the code.")
        column = object_data_table[colname]
        rows_in_bin = np.logical_and(column >= bin_limits[0], column < bin_limits[1])

    object_data_table_in_bin = object_data_table[rows_in_bin]

    readout_dist_data = object_data_table_in_bin[CGOD_TF.readout_dist]

    # Perform a regression for each method
    for method in METHODS:

        # Get required data
        g1_data = object_data_table_in_bin[getattr(CGOD_TF, f"g1_image_{method}")]
        weight_data = object_data_table_in_bin[getattr(CGOD_TF, f"weight_{method}")]

        tot_weight = np.nansum(weight_data)

        # If there's no weight, skip the regression and output NaN for all values
        if tot_weight <= 0.:
            rr_row[getattr(RR_TF, f"weight_{method}")] = 0.
            rr_row[getattr(RR_TF, f"slope_{method}")] = np.NaN
            rr_row[getattr(RR_TF, f"intercept_{method}")] = np.NaN
            rr_row[getattr(RR_TF, f"slope_err_{method}")] = np.NaN
            rr_row[getattr(RR_TF, f"intercept_err_{method}")] = np.NaN
            rr_row[getattr(RR_TF, f"slope_intercept_covar_{method}")] = np.NaN
            continue

        # Get a mask for the data where the weight is > 0 and not NaN
        bad_data_mask = np.logical_or(np.isnan(weight_data), weight_data <= 0)

        masked_readout_dist_data = np.ma.masked_array(readout_dist_data, mask=bad_data_mask)
        masked_g1_data = np.ma.masked_array(g1_data, mask=bad_data_mask)
        masked_g1_err_data = np.sqrt(1 / np.ma.masked_array(weight_data, mask=bad_data_mask))

        # Perform the regression

        linregress_results = linregress_with_errors(masked_readout_dist_data[~bad_data_mask],
                                                    masked_g1_data[~bad_data_mask],
                                                    masked_g1_err_data[~bad_data_mask])

        # Save the results in the output table
        rr_row[getattr(RR_TF, f"weight_{method}")] = tot_weight
        rr_row[getattr(RR_TF, f"slope_{method}")] = linregress_results.slope
        rr_row[getattr(RR_TF, f"intercept_{method}")] = linregress_results.intercept
        rr_row[getattr(RR_TF, f"slope_err_{method}")] = linregress_results.slope_err
        rr_row[getattr(RR_TF, f"intercept_err_{method}")] = linregress_results.intercept_err
        rr_row[getattr(RR_TF, f"slope_intercept_covar_{method}")] = linregress_results.slope_intercept_covar

    return regression_results_table
