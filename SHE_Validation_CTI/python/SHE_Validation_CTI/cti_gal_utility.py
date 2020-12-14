""" @file cti_residual_validation.py

    Created 24 December 2020

    Utility functions for CTI-Gal validation, handling different pieces of the code
"""

__updated__ = "2020-12-14"

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

from SHE_PPT.logging import getLogger
from SHE_PPT.magic_values import ccdid_label
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_Validation_CTI import magic_values as mv
import numpy as np


logger = getLogger(__name__)


class ShearInfo(object):
    def __init__(self,
                 g1_world: float = np.NaN,
                 g2_world: float = np.NaN,
                 weight: float = 0):
        self.g1_world = g1_world
        self.g2_world = g2_world
        self.weight = weight


class PositionInfo(object):
    def __init__(self,
                 x_pix: float = np.NaN,
                 y_pix: float = np.NaN,
                 det_ix: int = 0,
                 det_iy: int = 0,
                 quadrant: str = "X",):

        self.x_pix = x_pix
        self.y_pix = y_pix
        self.det_ix = det_ix
        self.det_iy = det_iy
        self.quadrant = quadrant


class SingleObjectData(object):
    def __init__(self,
                 ID: int = None,
                 num_exposures: int = 1,
                 ):
        self.ID = ID
        self.position_info = [None] * num_exposures
        self.y_pix = [None] * num_exposures
        self.det_ix = [None] * num_exposures
        self.det_iy = [None] * num_exposures
        self.quadrant = [None] * num_exposures

        self.shear_info = {}  # To be filled with objects of type ShearInfo, with method names as keys

        return


def get_raw_cti_gal_object_data(data_stack: SHEFrameStack,
                                shear_estimate_tables: Dict[str, table.Table]
                                ):

    # Start by getting a set of all object ids, merging from all methods tables
    s_object_ids = set()
    for method in mv.methods:
        # Update the set with the Object ID column from the
        s_object_ids.update(shear_estimate_tables[method][d_shear_estimation_method_table_formats[method].ID])

    # Create a SingleObjectData for each object_id and store them in a list to output
    l_object_data = [None] * len(s_object_ids)
    for oid_index, object_id in enumerate(s_object_ids):

        # Find the object's pixel coordinates by extracting a size 0 stamp
        ministamp_stack = data_stack.extract_galaxy_stack(object_id, width=0, none_if_out_of_bounds=True)

        if ministamp_stack is None:
            logger.warning(f"Object {object_id} is outside the observation.")
            continue

        object_data = SingleObjectData(ID=object_id)
        for exp_index, exposure_ministamp in ministamp_stack.exposures:

            if exposure_ministamp is None:
                object_data.position_info[exp_index] = PositionInfo()
            else:

                ccdid = exposure_ministamp.header[ccdid_label]

                object_data.position_info[exp_index] = PositionInfo(x_pix=exposure_ministamp.offset[0],
                                                                    y_pix=exposure_ministamp.offset[1],
                                                                    det_ix=ccdid[0],
                                                                    det_iy=ccdid[1],
                                                                    quadrant="X")

        l_object_data[oid_index] = object_data

    return
