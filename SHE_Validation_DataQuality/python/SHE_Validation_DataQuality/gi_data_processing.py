"""
:file: python/SHE_Validation_DataQuality/gi_data_processing.py

:date: 01/24/23
:author: Bryan Gillis

Code for processing data in the GalInfo validation test
"""
import abc
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, TYPE_CHECKING

import numpy as np
from astropy.table import Table

from SHE_Validation.constants.misc import MSG_ERROR, MSG_INFO
from SHE_Validation_DataQuality.constants.gal_info_test_info import L_GAL_INFO_TEST_CASE_INFO

if TYPE_CHECKING:
    from SHE_Validation_DataQuality.gi_input import GalInfoInput  # noqa F401


@dataclass
class GalInfoTestResults(abc.ABC):
    """Abstract dataclass containing test results for a single shear estimation method for one of the GalInfo test cases

    Methods
    -------
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    """

    @property
    @abc.abstractmethod
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        pass


@dataclass
class GalInfoNTestResults(GalInfoTestResults):
    """Dataclass containing test results for the GalInfo-N test case.

    Attributes
    ---------
    n_in: int
        The number of weak lensing objects in the input catalog
    l_missing_ids: Sequence[int]
        A sequence of the IDs of all weak lensing objects in the input catalog which are not present in the output
        catalog

    Methods
    -------
    n_out: int
        (Read-only property) The number of objects in the output catalog
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    """

    n_in: int

    l_missing_ids: Sequence[int]

    @property
    def n_out(self) -> int:
        """The number of objects in the output catalog
        """
        return self.n_in - len(self.l_missing_ids)

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return self.n_in == self.n_out


@dataclass
class GalInfoDataTestResults(GalInfoTestResults):
    """Dataclass containing test results for the GalInfo-N test case.

    Attributes
    ---------
    l_invalid_ids: Sequence[int]
        A sequence of the IDs of all objects in the output catalog which have invalid data

    Methods
    -------
    n_inv: int
        (Read-only property) The number of objects in the output catalog with invalid data
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    """

    l_invalid_ids: Sequence[int]

    @property
    def n_inv(self) -> int:
        """The number of objects in the output catalog with invalid data
        """
        return len(self.l_invalid_ids)

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return self.n_inv == 0
