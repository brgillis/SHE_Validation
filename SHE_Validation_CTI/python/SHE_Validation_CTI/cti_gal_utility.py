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

from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_Validation_CTI import magic_values as mv
import numpy as np


def get_raw_cti_gal_object_data(data_stack: SHEFrameStack,
                                shear_estimate_tables: Dict[str, table.Table]
                                ):

    return
