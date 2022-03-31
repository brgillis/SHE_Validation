""" @file results_reporting.py

    Created 31 Mar 2022

    Functions to report results for PSF Residual validation
"""

__updated__ = "2021-08-27"

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

from typing import Dict, TypeVar

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_PPT.utility import is_inf_or_nan
from SHE_Validation.results_writer import (RequirementWriter,
                                           val_under_target, )

logger = getLogger(__name__)

# Define constants for various messages

PSF_RES_DIRECTORY_FILENAME = "ShePSFResResultsDirectory.txt"
PSF_RES_DIRECTORY_HEADER = "### OU-SHE Shear Bias Analysis Results File Directory ###"

REPORT_DIGITS = 8

# Type definitions for types used here
TK = TypeVar('TK')
TV = TypeVar('TV')
TIn = TypeVar('TIn')
TOut = TypeVar('TOut')
Number = TypeVar('Number', float, int)
ComponentDict = Dict[int, Number]


class PSFResRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    def _determine_results(self):
        """ Determine the test results if not already generated, filling in self.l_good_data and self.l_test_pass
        """

        if self.l_good_data is not None and self.l_test_pass is not None:
            return

        # Get an array of whether or not we have good data
        l_bad_val = is_inf_or_nan(self.l_val)
        self.l_good_data = np.logical_not(l_bad_val)

        # Make an array of test results
        self.l_test_pass = np.logical_not(val_under_target(val = self.l_val, val_target = self.l_val_target))
