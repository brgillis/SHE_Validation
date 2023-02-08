"""
:file: python/SHE_Validation_DataQuality/constants/fit_flags.py

:date: 02/08/23
:author: Bryan Gillis

Constants detailing information about fit quality flags, which are defined in SHE_PPT/flags.py
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
from typing import List

from SHE_PPT import flags

STR_FLAG_HEAD = "flag_"
STR_FLAG_SUCCESS = "flag_success"
LEN_FLAG_HEAD = len(STR_FLAG_HEAD)


@dataclass
class FlagInfo:
    """Dataclass to store info about each FIT_CLASS flag.
    """
    name: str
    value: int
    is_failure: bool


def get_flag_info():
    """Function to run on import, parsing the variable names used for flags in the SHE_PPT.flags module into a
    structured format.
    """

    l_flag_info: List[FlagInfo] = []
    max_flag_name_len = 0

    for name, value in flags.__dict__.items():
        if not name.startswith(STR_FLAG_HEAD) or name == STR_FLAG_SUCCESS:
            continue
        l_flag_info.append(FlagInfo(name=name[LEN_FLAG_HEAD:],
                                    value=value,
                                    is_failure=bool(value & flags.failure_flags)))
        if len(name) > max_flag_name_len:
            max_flag_name_len = len(name)

    return l_flag_info, max_flag_name_len


L_FLAG_INFO, MAX_FLAG_NAME_LEN = get_flag_info()
NUM_FLAGS = len(L_FLAG_INFO)
D_FLAG_INFO_FROM_NAME = {flag_info.name: flag_info for flag_info in L_FLAG_INFO}
D_FLAG_INFO_FROM_VALUE = {flag_info.value: flag_info for flag_info in L_FLAG_INFO}
