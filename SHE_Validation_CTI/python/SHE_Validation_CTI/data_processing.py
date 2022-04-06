""" @file data_processing.py

    Created 24 December 2020

    Utility functions for CTI-Gal validation, for processing the data.
"""

__updated__ = "2021-08-26"

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

from typing import Optional, Sequence

import numpy as np
from astropy import table

from SHE_PPT import mdb
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import linregress_with_errors
from SHE_PPT.table_formats.she_star_catalog import TF as SC_TF
from SHE_Validation.binning.bin_constraints import get_table_of_ids
from .table_formats.cti_gal_object_data import TF as CGOD_TF
from .table_formats.regression_results import TF as RR_TF

CTI_GAL_N_BOOTSTRAP_SAMPLES = 1000

logger = getLogger(__name__)


def add_readout_register_distance(object_data_table: table.Table,
                                  y_colname: str = CGOD_TF.y,
                                  rr_dist_colname: str = CGOD_TF.readout_dist):
    """ Calculates the distance of each object from the readout register and adds a column of these distances to
        the table.
    """

    # If we already have the data calculated and in the table, return
    if rr_dist_colname in object_data_table.colnames:
        return

    # Get the y-dimension size of the detector from the mdb, and split by half of it
    det_size_y = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
    det_split_y = det_size_y / 2

    y_pos = object_data_table[y_colname]

    readout_distance_data = np.where(y_pos < det_split_y, y_pos, det_size_y - y_pos)

    readout_distance_column = table.Column(name = CGOD_TF.readout_dist, data = readout_distance_data)
    object_data_table.add_column(readout_distance_column)


def _set_row_empty(rr_row: table.Row, ):
    """TODO: Add docstring for this function."""
    rr_row[RR_TF.weight] = 0.
    rr_row[RR_TF.slope] = np.NaN
    rr_row[RR_TF.intercept] = np.NaN
    rr_row[RR_TF.slope_err] = np.NaN
    rr_row[RR_TF.intercept_err] = np.NaN
    rr_row[RR_TF.slope_intercept_covar] = np.NaN


def calculate_regression_results(object_data_table: table.Table,
                                 l_ids_in_bin: Sequence[int],
                                 method: Optional[ShearEstimationMethods] = None,
                                 index: int = 0,
                                 product_type: str = "UNKNOWN",
                                 bootstrap: bool = False) -> table.Row:
    """ Performs a linear regression of g1 versus readout register distance for each shear estimation method,
        using data in the input object_data_table, and returns it as a one-row table of format regression_results.
    """

    # Figure out the type of input table based on whether or not a method is provided
    if method is not None:
        method_name = method.value
        method_tail = f"_{method_name}"
        odt_tf = CGOD_TF
    else:
        method_name = None
        method_tail = ""
        odt_tf = SC_TF

    # Initialize a table for the output data
    regression_results_table = RR_TF.init_table(product_type = product_type, size = 1)

    rr_row = regression_results_table[0]

    rr_row[RR_TF.method] = method_name
    rr_row[RR_TF.index] = index

    # Add index to the table if needed
    if CGOD_TF.ID not in object_data_table.indices:
        object_data_table.add_index(CGOD_TF.ID)

    # Get required data
    object_data_table_in_bin = get_table_of_ids(object_data_table, l_ids_in_bin)

    id_data = object_data_table_in_bin[CGOD_TF.ID]
    readout_dist_data = object_data_table_in_bin[CGOD_TF.readout_dist]

    if method is not None:
        g1_data = object_data_table_in_bin[getattr(odt_tf, f"g1_image{method_tail}")]
        weight_data = object_data_table_in_bin[getattr(odt_tf, f"weight{method_tail}")]
    else:
        g1_data = object_data_table_in_bin[odt_tf.e1]
        g1_err_data = object_data_table_in_bin[odt_tf.e1_err]
        weight_data = np.power(g1_err_data, -2)

    tot_weight = np.nansum(weight_data)

    # If there's no weight, skip the regression and output NaN for all values
    if tot_weight <= 0.:
        _set_row_empty(rr_row)
        return rr_row

    # Get a mask for the data where the weight is > 0 and not NaN
    bad_data_mask = np.logical_or(np.isnan(weight_data), weight_data <= 0)

    masked_id_data = np.ma.masked_array(id_data, mask = bad_data_mask)
    masked_readout_dist_data = np.ma.masked_array(readout_dist_data, mask = bad_data_mask)
    masked_g1_data = np.ma.masked_array(g1_data, mask = bad_data_mask)
    masked_g1_err_data = np.sqrt(1 / np.ma.masked_array(weight_data, mask = bad_data_mask))

    # Perform the regression

    linregress_results = linregress_with_errors(x = masked_readout_dist_data[~bad_data_mask],
                                                y = masked_g1_data[~bad_data_mask],
                                                y_err = masked_g1_err_data[~bad_data_mask],
                                                id = masked_id_data[~bad_data_mask],
                                                bootstrap = bootstrap,
                                                n_bootstrap_samples = CTI_GAL_N_BOOTSTRAP_SAMPLES)

    # Save the results in the output table
    rr_row[RR_TF.weight] = tot_weight
    rr_row[RR_TF.slope] = linregress_results.slope
    rr_row[RR_TF.intercept] = linregress_results.intercept
    rr_row[RR_TF.slope_err] = linregress_results.slope_err
    rr_row[RR_TF.intercept_err] = linregress_results.intercept_err
    rr_row[RR_TF.slope_intercept_covar] = linregress_results.slope_intercept_covar

    return rr_row
