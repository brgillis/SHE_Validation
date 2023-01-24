"""
:file: python/SHE_Validation_DataQuality/gi_data_processing.py

:date: 01/24/23
:author: Bryan Gillis

Code for processing data in the GalInfo validation test
"""

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

import abc

from dataclasses import dataclass
from typing import Dict, List, Sequence, TYPE_CHECKING

import numpy as np
from astropy.table import Table

from SHE_PPT.flags import failure_flags
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_formats.she_measurements import tf as sem_tf
from SHE_PPT.utility import is_inf_nan_or_masked
from SHE_Validation_DataQuality.constants.gal_info_test_info import (GAL_INFO_DATA_TEST_CASE_INFO,
                                                                     GAL_INFO_N_TEST_CASE_INFO,
                                                                     L_GAL_INFO_TEST_CASE_INFO, )

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


def get_gal_info_test_results(gal_info_input):
    """Get the results of the GalInfo test for each shear estimation method, based on the provided input data.

    Parameters
    ----------
    gal_info_input: GalInfoInput
        The input data, as read in by the `read_gal_info_input` method in the `gi_input.py` module

    Returns
    -------
    Dict[str, List[GalInfoTestResults]]
        A dict of the test results for each shear estimation method (indexed by the test case name). The result is
        returned as a dict of lists of one element each for consistency of format with other validation tests
    """

    # The MER Final Catalog is used identically by all test cases, so prepare it first by pruning to only rows
    # detected in the VIS filter
    good_mfc_rows = gal_info_input.mer_cat[mfc_tf.vis_det] == 1
    mer_cat = gal_info_input.mer_cat[good_mfc_rows]

    # Prepare an output dict, which we'll fill in for each method
    d_l_test_results: Dict[str, List[GalInfoTestResults]] = {}

    for test_case_info in L_GAL_INFO_TEST_CASE_INFO:

        method_she_cat = gal_info_input.d_she_cat[test_case_info.method]

        # Split execution depending on which test case we're running

        if test_case_info.test_case_id.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id):

            return _get_gal_info_n_test_results(method_she_cat, mer_cat)

        elif test_case_info.test_case_id.startswith(GAL_INFO_DATA_TEST_CASE_INFO.base_test_case_id):

            return _get_gal_info_data_test_results(method_she_cat)

        else:

            raise ValueError(f"Unrecognized test case id: {test_case_info.test_case_id}")

    return d_l_test_results


def _get_gal_info_n_test_results(she_cat: Table, mer_cat: Table) -> GalInfoNTestResults:
    """Private implementation of determining test results for the GalInfo-N test case.
    """

    l_mer_ids = mer_cat[mfc_tf.ID]
    l_she_ids = she_cat[sem_tf.ID]

    n_in = len(l_mer_ids)

    # Use set difference to find IDs that aren't present in the SHE catalog
    l_missing_ids = np.setdiff1d(l_mer_ids, l_she_ids)

    return GalInfoNTestResults(n_in=n_in, l_missing_ids=l_missing_ids)


def _get_gal_info_data_test_results(she_cat: Table) -> GalInfoDataTestResults:
    """Private implementation of determining test results for the GalInfo-Data test case.
    """

    # First, we check for any objects which are flagged as failures - these are all considered to be flagged properly
    l_flagged_fail = she_cat[sem_tf.fit_flags] & failure_flags

    # Exclude the objects marked as failures from the remaining analysis
    good_she_cat = she_cat[~l_flagged_fail]

    # We'll now do a check on each required column to ensure that it has valid data, then get the final results by
    # combining the checks
    l_l_checks: List[np.ndarray] = []
    colname: str
    min_value: float
    max_value: float
    for colname, min_value, max_value in ((sem_tf.g1, -1, 1),
                                          (sem_tf.g2, -1, 1),
                                          (sem_tf.weight, 0., 1e99),
                                          (sem_tf.fit_class, -np.inf, np.inf),
                                          (sem_tf.re, 0., 1e99),):
        # Explanation of min/max values:
        # - In general, -1e99 and 1e99 are used to indicate failure. But in the case of failure, this should be
        #   flagged instead, so we limit to values between those
        # - g1/g2: These are physically limited to between -1 and 1 exclusive
        # - weight: 0 would indicate no weight, or not to be used, but this should be flagged as a failure instead
        # - fit_class: Any integer value is valid
        # - re: Size is physically limited to be greater than 0

        # Confirm the value is not Inf, NaN, or masked
        l_good_value_check = np.logical_not(is_inf_nan_or_masked(good_she_cat[colname]))

        # Confirm the value is between the minimum and maximum, exclusive
        l_min_check = good_she_cat[colname] > min_value
        l_max_check = good_she_cat[colname] < max_value

        # Store the checks in the ongoing list
        l_l_checks.append(l_good_value_check)
        l_l_checks.append(l_min_check)
        l_l_checks.append(l_max_check)

    l_pass_all_checks = np.logical_and.reduce(l_l_checks)

    # Now, get a list of IDs which failed checks to output
    l_invalid_ids = she_cat[~l_pass_all_checks][sem_tf.ID]

    return GalInfoDataTestResults(l_invalid_ids=l_invalid_ids)
