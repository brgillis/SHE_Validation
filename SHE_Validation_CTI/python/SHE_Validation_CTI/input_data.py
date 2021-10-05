""" @file input_data.py

    Created 14 December 2020

    Utility functions for CTI-Gal validation, for reading in and sorting input data
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

# The size for the stamp used for calculating the background level

from copy import deepcopy
from typing import Dict, List, Optional, Set

import numpy as np
from astropy import table
from astropy.table import Row, Table

from SHE_PPT import shear_utility
from SHE_PPT.constants.fits import CCDID_LABEL
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS, ShearEstimationMethods
from SHE_PPT.detector import get_vis_quadrant
from SHE_PPT.flags import is_flagged_failure
from SHE_PPT.logging import getLogger
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_image_stack import SHEImageStack
from SHE_PPT.shear_utility import ShearEstimate
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_utility import SheTableFormat
from .data_processing import add_readout_register_distance
from .table_formats.cti_gal_object_data import TF as CGOD_TF

BG_STAMP_SIZE = 1

logger = getLogger(__name__)


class PositionInfo():
    """ Class to store all data related to the position of an object across multiple exposures.
    """

    x_pix: float = np.NaN
    y_pix: float = np.NaN
    det_ix: int = 0
    det_iy: int = 0
    quadrant: str = "X"
    exposure_shear_info: Dict[ShearEstimationMethods, ShearEstimate]

    def _init_default_exp_shear_info(self):
        self.exposure_shear_info = {}
        for method in ShearEstimationMethods:
            self.exposure_shear_info[method] = ShearEstimate(weight = 0)

    def __init__(self,
                 stamp: Optional[SHEImage] = None,
                 world_shear_info: Optional[ShearEstimate] = None,
                 ra: Optional[float] = None,
                 dec: Optional[float] = None):

        # Default initialise if stamp isn't provided
        if stamp is None:
            self._init_default_exp_shear_info()
            return

        # Get input data from the provided stamp
        if ra is None or dec is None:
            self.x_pix = stamp.offset[0]
            self.y_pix = stamp.offset[1]
        else:
            x_pix_stamp, y_pix_stamp = stamp.world2pix(ra, dec)
            self.x_pix = stamp.offset[0] + x_pix_stamp
            self.y_pix = stamp.offset[1] + y_pix_stamp

        ccdid: str = stamp.header[CCDID_LABEL]
        if len(ccdid) == 3:
            # Short form
            self.det_ix = int(ccdid[0])
            self.det_iy = int(ccdid[2])
        elif len(ccdid) == 9:
            # Long form
            self.det_ix = int(ccdid[6])
            self.det_iy = int(ccdid[8])

        self.quadrant = get_vis_quadrant(x_pix = self.x_pix, y_pix = self.y_pix, det_iy = self.det_iy)

        # Init default exposure shear if we don't have any world shear info
        if world_shear_info is None:
            self._init_default_exp_shear_info()
            return

        # Calculate the shear in the image coords for this exposure for each method
        self.exposure_shear_info = {}
        for method in ShearEstimationMethods:

            method_world_shear_info: ShearEstimate = world_shear_info[method]

            if method_world_shear_info is None:
                self.exposure_shear_info[method] = ShearEstimate()
                continue

            shear_estimate = deepcopy(method_world_shear_info)
            shear_utility.uncorrect_for_wcs_shear_and_rotation(shear_estimate, stamp)

            self.exposure_shear_info[method] = shear_estimate


class SingleObjectData():
    """ Class to store the required information for a single object in the catalogue.
    """

    # Attributes set at init
    id: Optional[int] = None
    num_exposures: int = 1
    data_stack: Optional[SHEFrameStack] = None

    # Attributes set up to be able to store data, but not calculated at init
    position_info: List[PositionInfo]

    def __init__(self,
                 object_id: Optional[int] = None,
                 num_exposures: int = 1,
                 ):
        self.id = object_id

        # To be filled with objects of type PositionInfo, one for each exposure
        self.position_info = [None] * num_exposures

        # To be filled with objects of type ShearEstimate, with method names as keys
        self.world_shear_info = {}


def _get_raw_cg_data_for_object(data_stack: SHEFrameStack,
                                d_shear_estimate_tables: Dict[str, Table],
                                object_id: int,
                                wcs_stack: SHEImageStack) -> SingleObjectData:
    """ Get raw data for a single object.
    """

    detections_row: Row = data_stack.detections_catalogue.loc[object_id]
    object_data: SingleObjectData = SingleObjectData(object_id = object_id,
                                                     num_exposures = len(wcs_stack.exposures), )

    # Set the shear info for this method
    for method in ShearEstimationMethods:

        shear_estimate_table: Table = d_shear_estimate_tables[method]
        if shear_estimate_table is None:
            object_data.world_shear_info[method] = ShearEstimate(weight = 0)
            continue

        sem_tf: SheTableFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        object_row: Row = shear_estimate_table.loc[object_id]

        # Check the object isn't flagged as a failure
        object_weight: float
        if ((not is_flagged_failure(object_row[sem_tf.fit_flags])) and not (np.isinf(object_row[sem_tf.g1_err]) or
                                                                            np.isinf(object_row[sem_tf.g2_err]) or
                                                                            np.isnan(object_row[sem_tf.g1_err]) or
                                                                            np.isnan(object_row[sem_tf.g2_err]))):
            object_weight = object_row[sem_tf.weight]
        else:
            object_weight = 0

        object_data.world_shear_info[method] = ShearEstimate(g1 = object_row[sem_tf.g1],
                                                             g2 = object_row[sem_tf.g2],
                                                             g1_err = object_row[sem_tf.g1_err],
                                                             g2_err = object_row[sem_tf.g2_err],
                                                             g1g2_covar = object_row[sem_tf.g1g2_covar],
                                                             weight = object_weight)

    # Get the object's world position from the detections catalog
    ra: float = detections_row[mfc_tf.gal_x_world]
    dec: float = detections_row[mfc_tf.gal_y_world]

    # Set the position info for each exposure
    for exp_index, exposure_wcs_stamp in enumerate(wcs_stack.exposures):
        # Add the position info by using the stamp as an initializer. The initializer
        # will properly use default values if the stamp is None
        object_data.position_info[exp_index] = PositionInfo(stamp = exposure_wcs_stamp,
                                                            world_shear_info = object_data.world_shear_info,
                                                            ra = ra,
                                                            dec = dec)

    return object_data


def get_raw_cti_gal_object_data(data_stack: SHEFrameStack,
                                d_shear_estimate_tables: Dict[ShearEstimationMethods, table.Table]
                                ):
    """ Get a list of raw object data out of the data stack and shear estimates tables.
    """

    # Start by getting a set of all object ids, merging from all methods tables

    s_object_ids: Set[int] = set()

    for method in ShearEstimationMethods:

        # Check if the table exists for this method
        shear_estimate_table = d_shear_estimate_tables[method]
        if shear_estimate_table is None:
            continue

        # Get the table format for this method
        sem_tf: SheTableFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]

        # Update the set with the Object ID column from the table
        s_object_ids.update(shear_estimate_table[sem_tf.ID])

        # Set up the table to use the ID as an index
        shear_estimate_table.add_index(sem_tf.ID)

        # Since extra indices can occasionally lead to bugs, we remove this index in the
        # "finally" block below

    try:

        # Create a SingleObjectData for each object_id and store them in a list to output
        l_object_data: List[SingleObjectData] = [None] * len(s_object_ids)

        for oid_index, object_id in enumerate(s_object_ids):

            # Find the object's pixel coordinates by extracting a wcs
            wcs_stack: SHEImageStack = data_stack.extract_galaxy_wcs_stack(object_id, none_if_out_of_bounds = True)

            if wcs_stack is None:
                logger.warning(f"Object {object_id} is outside the observation.")
                continue

            l_object_data[oid_index] = _get_raw_cg_data_for_object(data_stack,
                                                                   d_shear_estimate_tables,
                                                                   object_id,
                                                                   wcs_stack)

    finally:
        # Make sure to remove the indices from the tables
        for method in ShearEstimationMethods:
            shear_estimate_table = d_shear_estimate_tables[method]
            if shear_estimate_table is None:
                continue
            shear_estimate_table.remove_indices(sem_tf.ID)

    return l_object_data


def sort_raw_object_data_into_table(l_raw_object_data: List[SingleObjectData]) -> List[Table]:
    """ Takes a list of raw object data and sorts it into an astropy Table of format cti_gal_object_data.
    """

    num_objects: int = len(l_raw_object_data)
    num_exposures: int
    if num_objects == 0:
        num_exposures = 1
    else:
        num_exposures = len(l_raw_object_data[0].position_info)

    # Create a table for each exposure
    l_object_data_tables: List[Table] = [None] * num_exposures

    for exp_index in range(num_exposures):

        # Initialise the table with one row for each object
        object_data_table: Table = CGOD_TF.init_table(size = num_objects,
                                                      optional_columns = [CGOD_TF.quadrant, ])

        # Fill in the data for each object
        for object_data, row in zip(l_raw_object_data, object_data_table):

            position_info: PositionInfo = object_data.position_info[exp_index]

            row[CGOD_TF.ID] = object_data.id

            row[CGOD_TF.x] = position_info.x_pix
            row[CGOD_TF.y] = position_info.y_pix

            row[CGOD_TF.det_ix] = position_info.det_ix
            row[CGOD_TF.det_iy] = position_info.det_iy

            # Fill in data for each shear estimate method
            for method in ShearEstimationMethods:

                exposure_shear_info: ShearEstimate = position_info.exposure_shear_info[method]

                method_name = method.value
                row[getattr(CGOD_TF, f"g1_image_{method_name}")] = exposure_shear_info.g1
                row[getattr(CGOD_TF, f"g2_image_{method_name}")] = exposure_shear_info.g2
                row[getattr(CGOD_TF, f"weight_{method_name}")] = exposure_shear_info.weight

        # We'll need to calculate the distance from the readout register, so add columns for that as well
        add_readout_register_distance(object_data_table = object_data_table)

        l_object_data_tables[exp_index] = object_data_table

    return l_object_data_tables
