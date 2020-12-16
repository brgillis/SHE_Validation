""" @file input_data.py

    Created 24 December 2020

    Utility functions for CTI-Gal validation, for reading in and sorting input data
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


from typing import Dict

from astropy import table

from SHE_PPT import shear_utility
from SHE_PPT.logging import getLogger
from SHE_PPT.magic_values import ccdid_label
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.telescope_coords import get_vis_quadrant
from SHE_Validation_CTI import constants
import numpy as np

logger = getLogger(__name__)


class ShearInfo(object):
    def __init__(self,
                 g1: float = np.NaN,
                 g2: float = np.NaN,
                 weight: float = 0):
        self.g1 = g1
        self.g2 = g2
        self.weight = weight


class PositionInfo(object):
    def __init__(self, stamp=None,
                 world_shear_info=None,
                 ra=None,
                 dec=None):

        # Get input data from the provided stamp; otherwise use initializer input
        if stamp is not None:

            if ra is None or dec is None:
                self.x_pix = stamp.offset[0]
                self.y_pix = stamp.offset[1]
            else:
                x_pix_stamp, y_pix_stamp = stamp.world2pix(ra, dec)
                self.x_pix = stamp.offset[0] + x_pix_stamp
                self.y_pix = stamp.offset[1] + y_pix_stamp

            ccdid = stamp.header[ccdid_label]
            self.det_ix = int(ccdid[6])
            self.det_iy = int(ccdid[8])

            self.quadrant = get_vis_quadrant(x_pix=self.x_pix, y_pix=self.y_pix, det_iy=self.det_iy)

            # Calculate the shear in the image coords for this exposure for each method

            self.exposure_shear_info = {}

            if world_shear_info is not None:
                for method in constants.methods:

                    method_world_shear_info = world_shear_info[method]

                    if method_world_shear_info is None:
                        self.exposure_shear_info[method] = ShearInfo()
                        continue

                    shear_estimate = shear_utility.ShearEstimate(g1=method_world_shear_info.g1,
                                                                 g2=method_world_shear_info.g2)
                    shear_utility.uncorrect_for_wcs_shear_and_rotation(shear_estimate, stamp)

                    self.exposure_shear_info[method] = ShearInfo(g1=shear_estimate.g1,
                                                                 g2=shear_estimate.g2,
                                                                 weight=method_world_shear_info.weight)

            else:
                for method in constants.methods:
                    self.exposure_shear_info[method] = ShearInfo()

        else:  # Default initialize

            self.x_pix = np.NaN
            self.y_pix = np.NaN

            self.det_ix = 0
            self.det_iy = 0

            self.quadrant = "X"

            self.exposure_shear_info = {}
            for method in constants.methods:
                self.exposure_shear_info[method] = ShearInfo()


class SingleObjectData(object):
    def __init__(self,
                 ID: int = None,
                 num_exposures: int = 1,
                 ):
        self.ID = ID
        # To be filled with objects of type PositionInfo, one for each exposure
        self.position_info = [None] * num_exposures
        self.world_shear_info = {}  # To be filled with objects of type ShearInfo, with method names as keys

        return


def get_raw_cti_gal_object_data(data_stack: SHEFrameStack,
                                shear_estimate_tables: Dict[str, table.Table]
                                ):

    # Start by getting a set of all object ids, merging from all methods tables

    s_object_ids = set()

    for method in constants.methods:

        # Check if the table exists for this method
        shear_estimate_table = shear_estimate_tables[method]
        if shear_estimate_table is None:
            continue

        # Update the set with the Object ID column from the table
        sem_tf = constants.d_shear_estimation_method_table_formats[method]
        s_object_ids.update(shear_estimate_table[sem_tf.ID])

        # Set up the table to use the ID as an index
        shear_estimate_table.add_index(sem_tf.ID)

        # Since extra indices can occasionally lead to bugs, we remove this index in the
        # "finally" block below

    l_object_data = [None] * len(s_object_ids)

    try:

        # Create a SingleObjectData for each object_id and store them in a list to output
        l_object_data = [None] * len(s_object_ids)
        for oid_index, object_id in enumerate(s_object_ids):

            # Find the object's pixel coordinates by extracting a size 0 stamp
            ministamp_stack = data_stack.extract_galaxy_stack(object_id, width=1, none_if_out_of_bounds=True)

            if ministamp_stack is None:
                logger.warning(f"Object {object_id} is outside the observation.")
                continue

            object_data = SingleObjectData(ID=object_id,
                                           num_exposures=len(ministamp_stack.exposures))

            # Set the shear info for each method
            for method in constants.methods:
                shear_estimate_table = shear_estimate_tables[method]
                if shear_estimate_table is None:
                    object_data.world_shear_info[method] = ShearInfo()
                    continue

                sem_tf = constants.d_shear_estimation_method_table_formats[method]

                object_row = shear_estimate_table.loc[object_id]

                object_data.world_shear_info[method] = ShearInfo(g1=object_row[sem_tf.g1],
                                                                 g2=object_row[sem_tf.g2],
                                                                 weight=object_row[sem_tf.weight])

            # Get the object's world position from the detections catalog
            ra = data_stack.detections_catalogue.loc[object_id][mfc_tf.gal_x_world]
            dec = data_stack.detections_catalogue.loc[object_id][mfc_tf.gal_y_world]

            # Set the position info for each exposure
            for exp_index, exposure_ministamp in enumerate(ministamp_stack.exposures):

                # Add the position info by using the stamp as an initializer. The initializer
                # will properly use default values if the stamp is None
                object_data.position_info[exp_index] = PositionInfo(stamp=exposure_ministamp,
                                                                    world_shear_info=object_data.world_shear_info,
                                                                    ra=ra,
                                                                    dec=dec)

            l_object_data[oid_index] = object_data

    finally:
        # Make sure to remove the indices from the tables
        for method in constants.methods:
            shear_estimate_table = shear_estimate_tables[method]
            if shear_estimate_table is None:
                continue
            shear_estimate_table.remove_indices(sem_tf.ID)

    return l_object_data
