"""
:file: python/SHE_Validation_DataQuality/constants/gid_criteria.py

:date: 01/30/23
:author: Bryan Gillis

Constants detailing the specific criteria for passing the GalInfo-Data test case
"""

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

from dataclasses import dataclass

import numpy as np


@dataclass
class GalInfoDataCriteria:
    """Dataclass describing the criteria needed for a given object datum to be classified as "good" for the
    GalInfo-Data validation test.

    Attributes
    ----------
    attr: str
        The name of the attribute, which can be used to get the appropriate column name via `getattr(tf, attr)`
    min: float
        The minimum (exclusive) value allowed
    max: float
        The maximum (exclusive) value allowed
    is_chain: bool
        Whether the data is expressed as a chain in the chains catalog
    """
    attr: str
    min: float
    max: float
    is_chain: bool


# Explanation of min/max values:
# - In general, -1e99 and 1e99 are used to indicate failure. But in the case of failure, this should be
#   flagged instead, so we limit to values between those
# - g1/g2: These are physically limited to between -1 and 1 exclusive
# - weight: 0 would indicate no weight, or not to be used, but this should be flagged as a failure instead
# - fit_class: Any integer value is valid
# - re: Size is physically limited to be greater than 0
L_GID_CRITERIA = (GalInfoDataCriteria("g1", -1, 1, True),
                  GalInfoDataCriteria("g2", -1, 1, True),
                  GalInfoDataCriteria("weight", 0., 1e99, False),
                  GalInfoDataCriteria("fit_class", -np.inf, np.inf, False),
                  GalInfoDataCriteria("re", 0., 1e99, True),)
