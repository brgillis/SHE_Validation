""" @file data_processing.py

    Created 24 December 2020

    Utility functions for CTI-Gal validation, for processing the data.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from typing import Dict, Sequence, Tuple

from SHE_PPT import mdb
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import linregress_with_errors
from astropy import table

from SHE_Validation.binning.bin_constraints import (BinParameterBinConstraint, FitflagsBinConstraint,
                                                    HeteroBinConstraint)
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters
import numpy as np

from .table_formats.cti_gal_object_data import TF as CGOD_TF
from .table_formats.regression_results import TF as RR_TF

logger = getLogger(__name__)


def add_readout_register_distance(object_data_table: table.Table):
    """ Calculates the distance of each object from the readout register and adds a column of these distances to
        the table.
    """

    # If we already have the data calculated and in the table, return
    if CGOD_TF.readout_dist in object_data_table.colnames:
        return

    # Get the y-dimension size of the detector from the mdb, and split by half of it
    det_size_y = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
    det_split_y = det_size_y / 2

    y_pos = object_data_table[CGOD_TF.y]

    readout_distance_data = np.where(y_pos < det_split_y, y_pos, det_size_y - y_pos)

    readout_distance_column = table.Column(name=CGOD_TF.readout_dist, data=readout_distance_data)
    object_data_table.add_column(readout_distance_column)


def get_ids_in_bin(bin_parameter: BinParameters,
                   bin_limits: Sequence[float],
                   method: ShearEstimationMethods,
                   detections_table: table.Table,
                   measurements_table: table.Table) -> Sequence[int]:
    """ Get an array of good indices based on the bin_parameter and bin_limits
    """

    # Set up a bin constraint, and get the IDs in the bin with it
    bin_parameter_bin_constraint = BinParameterBinConstraint(bin_parameter=bin_parameter,
                                                             bin_limits=bin_limits)
    fitflags_bin_constraint = FitflagsBinConstraint(method=method)

    # If we don't have a measurements table, do what we can with just the detections table
    if measurements_table is None:
        ids_in_bin = bin_parameter_bin_constraint.get_ids_in_bin(detections_table)
    else:
        full_bin_constraint = HeteroBinConstraint(l_bin_constraints=[bin_parameter_bin_constraint,
                                                                     fitflags_bin_constraint])

        ids_in_bin = full_bin_constraint.get_ids_in_bin(l_tables=[detections_table, measurements_table])

    return ids_in_bin


def get_d_ids_in_bin(bin_parameter: BinParameters,
                     bin_limits: Sequence[float],
                     detections_table: table.Table,
                     d_measurements_tables: table.Table) -> Dict[ShearEstimationMethods, Sequence[int]]:
    """ Get arrays of good indices for each shear estimation method.
    """

    d_ids_in_bin = {}

    for method in ShearEstimationMethods:
        if not method in d_measurements_tables or d_measurements_tables[method] is None:
            measurements_table = None
        else:
            measurements_table = d_measurements_tables[method]
        d_ids_in_bin[method] = get_ids_in_bin(bin_parameter=bin_parameter,
                                              bin_limits=bin_limits,
                                              method=method,
                                              detections_table=detections_table,
                                              measurements_table=measurements_table)

    return d_ids_in_bin


def calculate_regression_results(object_data_table: table.Table,
                                 detections_table: table.Table,
                                 d_measurements_tables: Dict[ShearEstimationMethods, table.Table],
                                 product_type: str = "UNKNOWN",
                                 bin_parameter: BinParameters = BinParameters.GLOBAL,
                                 bin_limits: Tuple[float, float] = DEFAULT_BIN_LIMITS):
    """ Performs a linear regression of g1 versus readout register distance for each shear estimation method,
        using data in the input object_data_table, and returns it as a one-row table of format regression_results.
    """

    # Initialize a table for the output data
    regression_results_table = RR_TF.init_table(product_type=product_type, size=1)

    rr_row = regression_results_table[0]

    d_ids_in_bin = get_d_ids_in_bin(bin_parameter=bin_parameter,
                                    bin_limits=bin_limits,
                                    detections_table=detections_table,
                                    d_measurements_tables=d_measurements_tables)

    if not CGOD_TF.ID in object_data_table.indices:
        object_data_table.add_index(CGOD_TF.ID)

    # Perform a regression for each method
    for method in ShearEstimationMethods:

        method_name = method.value

        # Get required data
        object_data_table_in_bin = object_data_table.loc[d_ids_in_bin[method]]

        readout_dist_data = object_data_table_in_bin[CGOD_TF.readout_dist]

        g1_data = object_data_table_in_bin[getattr(CGOD_TF, f"g1_image_{method_name}")]
        weight_data = object_data_table_in_bin[getattr(CGOD_TF, f"weight_{method_name}")]

        tot_weight = np.nansum(weight_data)

        # If there's no weight, skip the regression and output NaN for all values
        if tot_weight <= 0.:
            rr_row[getattr(RR_TF, f"weight_{method_name}")] = 0.
            rr_row[getattr(RR_TF, f"slope_{method_name}")] = np.NaN
            rr_row[getattr(RR_TF, f"intercept_{method_name}")] = np.NaN
            rr_row[getattr(RR_TF, f"slope_err_{method_name}")] = np.NaN
            rr_row[getattr(RR_TF, f"intercept_err_{method_name}")] = np.NaN
            rr_row[getattr(RR_TF, f"slope_intercept_covar_{method_name}")] = np.NaN
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
        rr_row[getattr(RR_TF, f"weight_{method_name}")] = tot_weight
        rr_row[getattr(RR_TF, f"slope_{method_name}")] = linregress_results.slope
        rr_row[getattr(RR_TF, f"intercept_{method_name}")] = linregress_results.intercept
        rr_row[getattr(RR_TF, f"slope_err_{method_name}")] = linregress_results.slope_err
        rr_row[getattr(RR_TF, f"intercept_err_{method_name}")] = linregress_results.intercept_err
        rr_row[getattr(RR_TF, f"slope_intercept_covar_{method_name}")] = linregress_results.slope_intercept_covar

    return regression_results_table
