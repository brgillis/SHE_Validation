""" @file data_processing.py

    Created 24 December 2020

    Utility functions for CTI-Gal validation, for processing the data.
"""

__updated__ = "2020-12-16"

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


from astropy import table

from SHE_PPT import mdb
from SHE_PPT.logging import getLogger
from SHE_Validation_CTI import constants
from SHE_Validation_CTI.table_formats.cti_gal_object_data import tf as cgod_tf
from SHE_Validation_CTI.table_formats.regression_results import tf as rr_tf, initialise_regression_results_table
import numpy as np


logger = getLogger(__name__)


def add_readout_register_distance(object_data_table: table.Table):
    """ Calculates the distance of each object from the readout register and adds a column of these distances to
        the table.
    """

    # Get the y-dimension size of the detector from the mdb, and split by half of it
    det_size_y = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
    det_split_y = det_size_y / 2

    y_pos = object_data_table[cgod_tf.y]

    readout_distance_data = np.where(y_pos < det_split_y, y_pos, det_size_y - y_pos)

    readout_distance_column = table.Column(name=cgod_tf.readout_dist, data=readout_distance_data)

    object_data_table.add_column(readout_distance_column)

    return


def calculate_regression_results(object_data_table: table.Table,
                                 product_type: str = "UNKNOWN"):
    """ Performs a linear regression of g1 versus readout register distance for each shear estimation method,
        using data in the input object_data_table, and returns it as a one-row table of format regression_results.
    """

    # Initialize a table for the output data
    regression_results_table = initialise_regression_results_table(product_type=product_type, size=1)

    rr_row = regression_results_table[0]

    # Perform a regression for each method
    for method in constants.methods:

        # Get required data
        g1 = object_data_table[getattr(cgod_tf, f"g1_image_{method}")]

    return regression_results_table
