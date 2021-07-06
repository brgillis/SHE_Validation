""" @file input_data.py

    Created 14 December 2020

    Utility functions for CTI-Gal validation, for reading in and sorting input data
"""

__updated__ = "2021-07-06"

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
from typing import Dict, List

from SHE_PPT import shear_utility
from SHE_PPT.constants.shear_estimation_methods import METHODS, D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.detector import get_vis_quadrant
from SHE_PPT.flags import is_flagged_failure
from SHE_PPT.logging import getLogger
from SHE_PPT.magic_values import ccdid_label
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.shear_utility import ShearEstimate
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from astropy import table

import numpy as np

from .table_formats.cti_gal_object_data import TF as CGOD_TF, initialise_cti_gal_object_data_table

BG_STAMP_SIZE = 128

logger = getLogger(__name__)


class PositionInfo():
    """ Class to store all data related to the position of an object across multiple exposures.
    """

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
            if len(ccdid) == 3:
                # Short form
                self.det_ix = int(ccdid[0])
                self.det_iy = int(ccdid[2])
            elif len(ccdid) == 9:
                # Long form
                self.det_ix = int(ccdid[6])
                self.det_iy = int(ccdid[8])

            self.quadrant = get_vis_quadrant(x_pix=self.x_pix, y_pix=self.y_pix, det_iy=self.det_iy)

            # Calculate the shear in the image coords for this exposure for each method

            self.exposure_shear_info = {}

            if world_shear_info is not None:
                for method in METHODS:

                    method_world_shear_info = world_shear_info[method]

                    if method_world_shear_info is None:
                        self.exposure_shear_info[method] = ShearEstimate()
                        continue

                    shear_estimate = deepcopy(method_world_shear_info)
                    shear_utility.uncorrect_for_wcs_shear_and_rotation(shear_estimate, stamp)

                    self.exposure_shear_info[method] = shear_estimate

            else:
                for method in METHODS:
                    self.exposure_shear_info[method] = ShearEstimate()

        # Default initialize
        else:

            self.x_pix = np.NaN
            self.y_pix = np.NaN

            self.det_ix = 0
            self.det_iy = 0

            self.quadrant = "X"

            self.exposure_shear_info = {}
            for method in METHODS:
                self.exposure_shear_info[method] = ShearEstimate()


class SingleObjectData():
    """ Class to store the required information for a single object in the catalogue.
    """

    def __init__(self,
                 object_id: int=None,
                 num_exposures: int=1,
                 data_stack: SHEFrameStack=None,
                 ):
        self.id = object_id

        # To be filled with objects of type PositionInfo, one for each exposure
        self.position_info = [None] * num_exposures

        # To be filled with objects of type ShearEstimate, with method names as keys
        self.world_shear_info = {}

        # Get info from the data_stack if possible

        self.background_level = [None] * num_exposures

        if data_stack is not None:

            detections_row = data_stack.detections_catalogue.loc[object_id]

            if detections_row[mfc_tf.FLUXERR_VIS_APER] == 0.:
                self.snr = np.NaN
            else:
                self.snr = detections_row[mfc_tf.FLUX_VIS_APER] / detections_row[mfc_tf.FLUXERR_VIS_APER]

            if detections_row[mfc_tf.FLUX_NIR_STACK_APER] == 0.:
                self.colour = np.NaN
            else:
                self.colour = 2.5 * np.log10(detections_row[mfc_tf.FLUX_VIS_APER] /
                                             detections_row[mfc_tf.FLUX_NIR_STACK_APER])

            self.size = detections_row[mfc_tf.SEGMENTATION_AREA]

            # Get the background level from the mean of a stamp around the object
            stamp_stack = data_stack.extract_galaxy_stack(object_id, width=BG_STAMP_SIZE, extract_stacked_stamp=False)
            for exp_index, exp_image in enumerate(stamp_stack.exposures):
                if exp_image is not None:
                    unmasked_background_data = exp_image.background_map[~exp_image.boolmask]
                    if len(unmasked_background_data) > 0:
                        self.background_level[exp_index] = unmasked_background_data.mean()

            # Calculate the mean background level of all valid exposures
            bg_array = np.array(self.background_level)
            valid_bg = bg_array != None
            if valid_bg.sum() > 0:
                self.mean_background_level = bg_array[valid_bg].mean()
            else:
                # No data, so set -99 for mean background level
                self.mean_background_level = -99

        else:
            self.snr = None
            self.colour = None
            self.size = None
            self.mean_background_level = None


def get_raw_cti_gal_object_data(data_stack: SHEFrameStack,
                                shear_estimate_tables: Dict[str, table.Table]
                                ):
    """ Get a list of raw object data out of the data stack and shear estimates tables.
    """

    # Start by getting a set of all object ids, merging from all methods tables

    s_object_ids = set()

    for method in METHODS:

        # Check if the table exists for this method
        shear_estimate_table = shear_estimate_tables[method]
        if shear_estimate_table is None:
            continue

        # Update the set with the Object ID column from the table
        sem_tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
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

            # Find the object's pixel coordinates by extracting a wcs
            wcs_stack = data_stack.extract_galaxy_wcs_stack(object_id, none_if_out_of_bounds=True)

            if wcs_stack is None:
                logger.warning(f"Object {object_id} is outside the observation.")
                continue

            detections_row = data_stack.detections_catalogue.loc[object_id]

            object_data = SingleObjectData(object_id=object_id,
                                           num_exposures=len(wcs_stack.exposures),
                                           data_stack=data_stack)

            # Set the shear info for each method
            for method in METHODS:
                shear_estimate_table = shear_estimate_tables[method]
                if shear_estimate_table is None:
                    object_data.world_shear_info[method] = ShearEstimate()
                    continue

                sem_tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]

                object_row = shear_estimate_table.loc[object_id]

                # Check the object isn't flagged as a failure
                if not is_flagged_failure(object_row[sem_tf.fit_flags]):
                    object_weight = object_row[sem_tf.weight]
                else:
                    object_weight = 0

                object_data.world_shear_info[method] = ShearEstimate(g1=object_row[sem_tf.g1],
                                                                     g2=object_row[sem_tf.g2],
                                                                     g1_err=object_row[sem_tf.g1_err],
                                                                     g2_err=object_row[sem_tf.g2_err],
                                                                     g1g2_covar=object_row[sem_tf.g1g2_covar],
                                                                     weight=object_weight)

            # Get the object's world position from the detections catalog
            ra = detections_row[mfc_tf.gal_x_world]
            dec = detections_row[mfc_tf.gal_y_world]

            # Set the position info for each exposure
            for exp_index, exposure_wcs_stamp in enumerate(wcs_stack.exposures):

                # Add the position info by using the stamp as an initializer. The initializer
                # will properly use default values if the stamp is None
                object_data.position_info[exp_index] = PositionInfo(stamp=exposure_wcs_stamp,
                                                                    world_shear_info=object_data.world_shear_info,
                                                                    ra=ra,
                                                                    dec=dec)

            l_object_data[oid_index] = object_data

    finally:
        # Make sure to remove the indices from the tables
        for method in METHODS:
            shear_estimate_table = shear_estimate_tables[method]
            if shear_estimate_table is None:
                continue
            shear_estimate_table.remove_indices(sem_tf.ID)

    return l_object_data


def sort_raw_object_data_into_table(raw_object_data_list: List[SingleObjectData]):
    """ Takes a list of raw object data and sorts it into an astropy Table of format cti_gal_object_data.
    """

    num_objects = len(raw_object_data_list)
    if num_objects == 0:
        num_exposures = 1
    else:
        num_exposures = len(raw_object_data_list[0].position_info)

    # Create a table for each exposure
    l_object_data_tables = [None] * num_exposures

    for exp_index in range(num_exposures):

        # Initialise the table with one row for each object
        object_data_table = initialise_cti_gal_object_data_table(size=num_objects,
                                                                 optional_columns=[CGOD_TF.quadrant,
                                                                                   CGOD_TF.snr,
                                                                                   CGOD_TF.bg,
                                                                                   CGOD_TF.colour,
                                                                                   CGOD_TF.size,
                                                                                   ])

        # Fill in the data for each object
        for object_data, row in zip(raw_object_data_list, object_data_table):

            position_info = object_data.position_info[exp_index]

            row[CGOD_TF.ID] = object_data.id

            row[CGOD_TF.x] = position_info.x_pix
            row[CGOD_TF.y] = position_info.y_pix

            row[CGOD_TF.det_ix] = position_info.det_ix
            row[CGOD_TF.det_iy] = position_info.det_iy

            row[CGOD_TF.snr] = object_data.snr
            row[CGOD_TF.colour] = object_data.colour
            row[CGOD_TF.size] = object_data.size

            bg_level = object_data.background_level[exp_index]
            if bg_level is not None:
                row[CGOD_TF.bg] = bg_level
            else:
                row[CGOD_TF.bg] = -99

            # Fill in data for each shear estimate method
            for method in METHODS:

                exposure_shear_info = position_info.exposure_shear_info[method]

                row[getattr(CGOD_TF, f"g1_image_{method}")] = exposure_shear_info.g1
                row[getattr(CGOD_TF, f"g2_image_{method}")] = exposure_shear_info.g2
                row[getattr(CGOD_TF, f"weight_{method}")] = exposure_shear_info.weight

        l_object_data_tables[exp_index] = object_data_table

    return l_object_data_tables
