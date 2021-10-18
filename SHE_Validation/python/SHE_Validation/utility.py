""" @file utility.py

    Created 18 Oct 2021

    Utility functions related to requirement, test, and test case info.
"""

__updated__ = "2021-08-06"

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

from typing import Dict, Set

from astropy.table import Table

from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS, ShearEstimationMethods


def get_object_id_list_from_se_tables(d_shear_tables: Dict[ShearEstimationMethods, Table], ) -> Set[int]:
    """ Gets a set of object IDs from across all shear tables.
    """

    s_object_ids = set()
    for method in d_shear_tables:
        t = d_shear_tables[method]
        if t is None:
            continue
        tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        s_object_ids.update(t[tf.ID])

    return s_object_ids
