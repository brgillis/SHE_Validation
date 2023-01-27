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
from typing import Dict, List, MutableSequence, Optional, Sequence, TYPE_CHECKING, Union

import numpy as np
from astropy.table import Table

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.flags import failure_flags
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_formats.she_measurements import tf as sem_tf
from SHE_PPT.utility import is_inf_nan_or_masked, is_inf_or_nan
from SHE_Validation.constants.misc import MSG_NA
from SHE_Validation.results_writer import RESULT_FAIL, RESULT_PASS
from SHE_Validation_DataQuality.constants.gal_info_test_info import (GAL_INFO_DATA_TEST_CASE_INFO,
                                                                     GAL_INFO_N_TEST_CASE_INFO,
                                                                     L_GAL_INFO_TEST_CASE_INFO, )

if TYPE_CHECKING:
    from SHE_Validation_DataQuality.gi_input import GalInfoInput  # noqa F401

MEAS_KEY = "meas"
CHAINS_KEY = "chains"


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

    @abc.abstractmethod
    def get_supp_info_message(self) -> str:
        """Abstract method to return a formatted SupplementaryInfo message based on the results, which can be output to
        the results data product.
        """
        pass

    @abc.abstractmethod
    def get_measured_value(self) -> float:
        """Abstract method to return the measured value of the test case.
        """
        pass


@dataclass
class GalInfoNTestResults(GalInfoTestResults):
    """Dataclass containing test results for the GalInfo-N test case.

    Attributes
    ---------
    n_in: int
        The number of weak lensing objects in the input catalog
    l_missing_ids_meas: Sequence[int]
        A sequence of the IDs of all weak lensing objects in the input catalog which are not present in the output
        measurements catalog
    l_missing_ids_chains: Sequence[int]
        A sequence of the IDs of all weak lensing objects in the input catalog which are not present in the output
        chains catalog

    Methods
    -------
    n_out_meas: int
        (Read-only property) The number of objects in the output measurements catalog
    n_out_chains: int
        (Read-only property) The number of objects in the output chains catalog
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    """

    n_in: int

    l_missing_ids_meas: Sequence[int]
    l_missing_ids_chains: Sequence[int]

    @property
    def n_out_meas(self) -> int:
        """The number of objects in the output measurements catalog
        """
        return self.n_in - len(self.l_missing_ids_meas)

    @property
    def n_out_chains(self) -> int:
        """The number of objects in the output chains catalog
        """
        return self.n_in - len(self.l_missing_ids_chains)

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return self.n_in == self.n_out_meas

    @abc.abstractmethod
    def get_supp_info_message(self) -> str:
        """Return a formatted SupplementaryInfo message based on the results, which can be output to the results data
        product.
        """

        message = f"n_in = {self.n_in}\n"

        for attr in (MEAS_KEY, CHAINS_KEY):

            n_out = getattr(self, f"n_out_{attr}")

            message += f"n_out_{attr} = {n_out}\n"
            message += f"n_out_{attr}/n_in = {n_out / self.n_in}\n"

            if n_out < self.n_in:
                # Get the list of missing IDs as a list, to ensure it'll be formatted properly in output
                l_missing_ids = list(getattr(self, f"l_missing_ids_{attr}"))
                message += f"Missing IDs: {l_missing_ids}"
            else:
                message += f"Missing IDs: {MSG_NA}"

        if self.global_passed:
            result = RESULT_PASS
        else:
            result = RESULT_FAIL
        message += f"Result: {result}"

        return message

    @abc.abstractmethod
    def get_measured_value(self) -> float:
        """Abstract method to return the measured value of the test case.
        """
        return self.n_out_meas / self.n_in


@dataclass
class GalInfoDataTestResults(GalInfoTestResults):
    """Dataclass containing test results for the GalInfo-N test case.

    Attributes
    ---------
    l_invalid_ids_meas: Sequence[int]
        A sequence of the IDs of all objects in the output measurements catalog which have invalid data
    l_invalid_ids_chains: Sequence[int]
        A sequence of the IDs of all objects in the output chains catalog which have invalid data

    Methods
    -------
    n_inv_meas: int
        (Read-only property) The number of objects in the output measurements catalog with invalid data
    n_inv_chains: int
        (Read-only property) The number of objects in the output chains catalog with invalid data
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    """

    l_invalid_ids_meas: Sequence[int]
    l_invalid_ids_chains: Sequence[int]

    @property
    def n_inv_meas(self) -> int:
        """The number of objects in the output measurements catalog with invalid data
        """
        return len(self.l_invalid_ids_meas)

    @property
    def n_inv_chains(self) -> int:
        """The number of objects in the output chains catalog with invalid data
        """
        return len(self.l_invalid_ids_chains)

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return self.n_inv_meas == 0

    @abc.abstractmethod
    def get_supp_info_message(self) -> str:
        """Return a formatted SupplementaryInfo message based on the results, which can be output to the results data
        product.
        """

        message = ""

        for attr in (MEAS_KEY, CHAINS_KEY):

            n_inv = getattr(self, f"n_inv_{attr}")

            message += f"n_inv_{attr} = {n_inv}\n"

            if n_inv > 0:
                # Get the list of missing IDs as a list, to ensure it'll be formatted properly in output
                l_invalid_ids = list(getattr(self, f"l_invalid_ids_{attr}"))
                message += f"Invalid IDs: {l_invalid_ids}"
            else:
                message += f"Invalid IDs: {MSG_NA}"

        if self.global_passed:
            message += f"Result: {RESULT_PASS}"
        else:
            message += f"Result: {RESULT_FAIL}"

        return message

    @abc.abstractmethod
    def get_measured_value(self) -> float:
        """Abstract method to return the measured value of the test case.
        """
        return self.n_inv_meas


def get_gal_info_test_results(gal_info_input):
    """Get the results of the GalInfo test for each shear estimation method, based on the provided input data.

    Parameters
    ----------
    gal_info_input: GalInfoInput
        The input data, as read in by the `read_gal_info_input` method in the `gi_input.py` module

    Returns
    -------
    Dict[str, List[GalInfoNTestResults or GalInfoDataTestResults]]
        A dict of the test results for each shear estimation method (indexed by the test case name). The result is
        returned as a dict of lists of one element each for consistency of format with other validation tests
    """

    # The MER Final Catalog is used identically by all test cases, so prepare it first by pruning to only rows
    # detected in the VIS filter
    good_mfc_rows = gal_info_input.mer_cat[mfc_tf.vis_det] == 1
    mer_cat = gal_info_input.mer_cat[good_mfc_rows]

    she_chains = gal_info_input.she_chains

    # Prepare an output dict, which we'll fill in for each method
    d_l_test_results: Dict[str, List[GalInfoTestResults]] = {}

    for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
        method = test_case_info.method
        name = test_case_info.name

        method_she_cat = gal_info_input.d_she_cat[method]

        # Split execution depending on which test case we're running

        if test_case_info.test_case_id.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id):

            d_l_test_results[name] = [_get_gal_info_n_test_results(method_she_cat, she_chains, mer_cat)]

        elif test_case_info.test_case_id.startswith(GAL_INFO_DATA_TEST_CASE_INFO.base_test_case_id):

            d_l_test_results[name] = [_get_gal_info_data_test_results(method_she_cat, she_chains, method)]

        else:

            raise ValueError(f"Unrecognized test case id: {test_case_info.test_case_id}")

    return d_l_test_results


def _get_gal_info_n_test_results(she_cat: Optional[Table],
                                 she_chains: Optional[Table],
                                 mer_cat: Table) -> GalInfoNTestResults:
    """Private implementation of determining test results for the GalInfo-N test case.
    """

    l_mer_ids = mer_cat[mfc_tf.ID]
    n_in = len(l_mer_ids)

    d_l_missing_ids: Dict[str, np.ndarray] = {}

    for cat, cat_type in ((she_cat, MEAS_KEY),
                          (she_chains, CHAINS_KEY)):
        # Check for case where we don't have a catalog provided
        if cat is None:
            d_l_missing_ids[cat_type] = np.array(l_mer_ids, dtype=int)
            continue

        l_she_ids = cat[sem_tf.ID]

        # Use set difference to find IDs that aren't present in the SHE catalog
        d_l_missing_ids[cat_type] = np.setdiff1d(l_mer_ids, l_she_ids)

    return GalInfoNTestResults(n_in=n_in,
                               l_missing_ids_meas=d_l_missing_ids[MEAS_KEY],
                               l_missing_ids_chains=d_l_missing_ids[CHAINS_KEY])


def _get_gal_info_data_test_results(she_cat: Optional[Table],
                                    she_chains: Optional[Table],
                                    method: ShearEstimationMethods) -> GalInfoDataTestResults:
    """Private implementation of determining test results for the GalInfo-Data test case.
    """

    d_l_invalid_ids: Dict[str, np.ndarray] = {}

    for cat, cat_type in ((she_cat, MEAS_KEY),
                          (she_chains, CHAINS_KEY)):

        # Check for case where we don't have a catalog provided
        if cat is None:
            d_l_invalid_ids[cat_type] = np.ndarray(shape=(0,), dtype=int)
            continue

        # Some different setup between measurements and chains catalogs
        if cat_type == MEAS_KEY:
            tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        else:
            tf = lensmc_chains_table_format

        # First, we check for any objects which are flagged as failures - these are all considered to be flagged
        # properly
        l_flagged_fail = np.asarray(cat[tf.fit_flags] & failure_flags, bool)

        # Exclude the objects marked as failures from the remaining analysis
        good_cat = cat[~l_flagged_fail]

        # We'll now do a check on each required column to ensure that it has valid data, then get the final results by
        # combining the checks
        l_l_checks: List[np.ndarray] = []
        colname: str
        min_value: float
        max_value: float
        is_chain: bool
        for colname, min_value, max_value, is_chain in ((tf.g1, -1, 1, True),
                                                        (tf.g2, -1, 1, True),
                                                        (tf.weight, 0., 1e99, False),
                                                        (tf.fit_class, -np.inf, np.inf, False),
                                                        (tf.re, 0., 1e99, True),):
            # Explanation of min/max values:
            # - In general, -1e99 and 1e99 are used to indicate failure. But in the case of failure, this should be
            #   flagged instead, so we limit to values between those
            # - g1/g2: These are physically limited to between -1 and 1 exclusive
            # - weight: 0 would indicate no weight, or not to be used, but this should be flagged as a failure instead
            # - fit_class: Any integer value is valid
            # - re: Size is physically limited to be greater than 0

            # For chains, we need to use slightly-different methods, which reduce the multi-dimensional array
            # properly, to do checks on values
            if cat_type == MEAS_KEY or not is_chain:
                bad_value_test = _meas_bad_value
                min_value_test = _meas_min_value
                max_value_test = _meas_max_value
            else:
                bad_value_test = _chains_bad_value
                min_value_test = _chains_min_value
                max_value_test = _chains_max_value

            # Confirm the value is not Inf, NaN, or masked
            l_good_value_check = np.logical_not(bad_value_test(good_cat[colname]))

            # Confirm the value is between the minimum and maximum, exclusive
            l_min_check = min_value_test(good_cat[colname], min_value)
            l_max_check = max_value_test(good_cat[colname], max_value)

            # Store the checks in the ongoing list
            l_l_checks.append(l_good_value_check)
            l_l_checks.append(l_min_check)
            l_l_checks.append(l_max_check)

        l_pass_all_checks = np.logical_and.reduce(l_l_checks)

        # Now, get a list of IDs which failed checks to output
        d_l_invalid_ids[cat_type] = good_cat[~l_pass_all_checks][sem_tf.ID]

    return GalInfoDataTestResults(l_invalid_ids_meas=d_l_invalid_ids[MEAS_KEY],
                                  l_invalid_ids_chains=d_l_invalid_ids[CHAINS_KEY])


def _meas_bad_value(a: np.ndarray) -> Union[np.ndarray, MutableSequence[bool]]:
    return is_inf_nan_or_masked(a)


def _chains_bad_value(a: np.ndarray) -> Union[np.ndarray, MutableSequence[bool]]:
    return np.any(is_inf_or_nan(a), axis=1)


def _meas_min_value(a: np.ndarray, min_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return a > min_value


def _chains_min_value(a: np.ndarray, min_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return np.all(a > min_value, axis=1)


def _meas_max_value(a: np.ndarray, max_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return a < max_value


def _chains_max_value(a: np.ndarray, max_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return np.all(a < max_value, axis=1)
