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
import os
from dataclasses import dataclass
from typing import Dict, List, MutableSequence, Optional, Sequence, TYPE_CHECKING, Union

import numpy as np
from astropy.table import Column, Table

import SHE_Validation
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.file_io import get_allowed_filename
from SHE_PPT.flags import failure_flags
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_formats.she_measurements import tf as sem_tf
from SHE_PPT.utility import is_inf_nan_or_masked, is_masked
from SHE_Validation.constants.misc import MSG_NA
from SHE_Validation.results_writer import RESULT_FAIL, RESULT_PASS
from SHE_Validation_DataQuality.constants.gal_info_test_info import (GAL_INFO_DATA_TEST_CASE_INFO,
                                                                     GAL_INFO_N_TEST_CASE_INFO,
                                                                     L_GAL_INFO_TEST_CASE_INFO, )
from SHE_Validation_DataQuality.constants.gid_criteria import L_GID_CRITERIA
from SHE_Validation_DataQuality.table_formats.gid_objects import (GIDC_TF, GIDM_TF, GID_CHECK_TAIL, GID_MAX, GID_MIN,
                                                                  GID_VAL, )

if TYPE_CHECKING:
    from SHE_Validation_DataQuality.gi_input import GalInfoInput  # noqa F401

MEAS_ATTR = "meas"
CHAINS_ATTR = "chains"

STR_TABLE_TYPE_NAME = "SHE-GID-%s"
TEXTFILE_TABLE_FORMAT = "ascii.ecsv"

MSG_N_IN = "%s n_in = %i\n"
MSG_N_OUT = "%s n_out = %i\n"
MSG_F_OUT = "%s n_out/n_in = %f\n"
MSG_MISSING_IDS = "Missing %s IDs: %s\n"

MSG_N_INV = "%s n_inv = %i\n"
MSG_INVALID_IDS = "Invalid %s IDs: %s\n"

MSG_ATTR_RESULT = "%s Result: %s\n"


@dataclass
class GalInfoTestResults(abc.ABC):
    """Abstract dataclass containing test results for a single shear estimation method for one of the GalInfo test cases

    Methods
    -------
    meas_passed: bool
        (Read-only property) Whether the Shear Measurements data passed
    chains_passed: bool
        (Read-only property) Whether the Chains data passed
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    get_supp_info_message: str
        Returns a string which reports detailed test results and can be written to the output data product's
        SupplementaryInfo for the associated test case.
    get_measured_value: float
        Returns the "measured value" for the test (defined per test case)
    """

    @property
    @abc.abstractmethod
    def meas_passed(self) -> bool:
        """Whether the Shear Measurements data passed
        """
        pass

    @property
    @abc.abstractmethod
    def chains_passed(self) -> bool:
        """Whether the Chains data passed
        """
        pass

    @property
    @abc.abstractmethod
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        pass

    def get_supp_info_message(self) -> str:
        """Return a formatted SupplementaryInfo message based on the results, which can be output to the results data
        product.
        """

        message = ""

        for attr in (MEAS_ATTR, CHAINS_ATTR):

            attr_capped = attr.capitalize()

            message += self._get_unique_supp_info(attr)

            attr_result = RESULT_PASS if getattr(self, f"{attr}_passed") else RESULT_FAIL
            message += MSG_ATTR_RESULT % (attr_capped, attr_result)

            message += "\n"

        return message

    @abc.abstractmethod
    def _get_unique_supp_info(self, attr):
        """Get the unique portion of the SupplementaryInfo for this test case
        """

    @abc.abstractmethod
    def get_measured_value(self) -> float:
        """Abstract method to return the measured value of the test case.
        """
        pass

    @staticmethod
    def write_textfiles(workdir):
        """Write out any textfiles associated with this test, and return a dict providing their filenames. This may
        be overridden by subclasses which generate any textfiles.

        Parameters
        ----------
        workdir: str
            The workdir for this program. Any generated textfiles will be written to this directory.

        Returns
        -------
        d_textfiles: Dict[str, str]
            A dictionary providing the workdir-relative filenames of all textfiles written out. The key for each
            filename will be used in the generated "directory" file, to aid automatic parsing of it and finding of
            filenames
        """

        return {}


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
    meas_passed: bool
        (Read-only property) Whether the Shear Measurements data passed
    chains_passed: bool
        (Read-only property) Whether the Chains data passed
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    get_supp_info_message: str
        Returns a string which reports detailed test results and can be written to the output data product's
        SupplementaryInfo for the associated test case.
    get_measured_value: float
        Returns the "measured value" for the test. For this test, this is the fraction of weak lensing objects in the
        input catalog which are also present in the output shear measurements catalog, where 1.0 constitutes a pass.
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
    def meas_passed(self) -> bool:
        """Whether the Shear Measurements data passed
        """
        return self.n_in == self.n_out_meas

    @property
    def chains_passed(self) -> bool:
        """Whether the Chains data passed
        """
        return self.n_in == self.n_out_chains

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return self.meas_passed

    def _get_unique_supp_info(self, attr):
        """Get the unique portion of the SupplementaryInfo for this test case
        """

        attr_capped = attr.capitalize()

        message = MSG_N_IN % (attr_capped, self.n_in)

        n_out = getattr(self, f"n_out_{attr}")

        message += MSG_N_OUT % (attr_capped, n_out)
        message += MSG_F_OUT % (attr_capped, n_out / self.n_in)

        if n_out < self.n_in:
            # Get the list of missing IDs as a list, to ensure it'll be formatted properly in output
            l_missing_ids = list(getattr(self, f"l_missing_ids_{attr}"))
            message += MSG_MISSING_IDS % (attr_capped, str(l_missing_ids))
        else:
            message += MSG_MISSING_IDS % (attr_capped, MSG_NA)

        return message

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
    invalid_data_table_meas: Optional[Table]
        If any measurements data is invalid, a table detailing the values and which checks were failed, otherwise None
    invalid_data_table_chains: Optional[Table]
        If any chains data is invalid, a table detailing the values and which checks were failed, otherwise None


    Methods
    -------
    n_inv_meas: int
        (Read-only property) The number of objects in the output measurements catalog with invalid data
    n_inv_chains: int
        (Read-only property) The number of objects in the output chains catalog with invalid data
    meas_passed: bool
        (Read-only property) Whether the Shear Measurements data passed
    chains_passed: bool
        (Read-only property) Whether the Chains data passed
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    get_supp_info_message: str
        Returns a string which reports detailed test results and can be written to the output data product's
        SupplementaryInfo for the associated test case.
    get_measured_value: float
        Returns the "measured value" for the test. For this test, this is the number of objects with invalid data in
        the measurements catalog, where 0 constitutes a pass.
    """

    l_invalid_ids_meas: Sequence[int]
    l_invalid_ids_chains: Sequence[int]

    invalid_data_table_meas: Optional[Table] = None
    invalid_data_table_chains: Optional[Table] = None

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
    def meas_passed(self) -> bool:
        """Whether the Shear Measurements data passed
        """
        return self.n_inv_meas == 0

    @property
    def chains_passed(self) -> bool:
        """Whether the Chains data passed
        """
        return self.n_inv_chains == 0

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return self.meas_passed

    def _get_unique_supp_info(self, attr):
        """Get the unique portion of the SupplementaryInfo for this test case
        """

        attr_capped = attr.capitalize()

        n_inv = getattr(self, f"n_inv_{attr}")

        message = MSG_N_INV % (attr_capped, n_inv)

        if n_inv > 0:
            # Get the list of missing IDs as a list, to ensure it'll be formatted properly in output
            l_invalid_ids = list(getattr(self, f"l_invalid_ids_{attr}"))
            message += MSG_INVALID_IDS % (attr_capped, str(l_invalid_ids))
        else:
            message += MSG_INVALID_IDS % (attr_capped, MSG_NA)

        return message

    def get_measured_value(self) -> float:
        """Abstract method to return the measured value of the test case.
        """
        return self.n_inv_meas

    def write_textfiles(self, workdir):
        """For this subclass, we implement this method to write out the tables of invalid measurements and chains
        objects as textfiles.
        """

        d_textfiles = {}

        for table, key in ((self.invalid_data_table_meas, MEAS_ATTR),
                           (self.invalid_data_table_chains, CHAINS_ATTR)):
            if table is None:
                continue

            table_filename = get_allowed_filename(type_name=STR_TABLE_TYPE_NAME % key.upper(),
                                                  instance_id=str(os.getpid()),
                                                  extension=".dat",
                                                  version=SHE_Validation.__version__)
            table.write(os.path.join(workdir, table_filename), format=TEXTFILE_TABLE_FORMAT)

            d_textfiles[key] = table_filename

        return d_textfiles


def get_gal_info_test_results(gal_info_input, workdir):
    """Get the results of the GalInfo test for each shear estimation method, based on the provided input data.

    Parameters
    ----------
    gal_info_input: GalInfoInput
        The input data, as read in by the `read_gal_info_input` method in the `gi_input.py` module
    workdir: str
        The workdir for execution of this program. Any output textfiles will be written in this directory

    Returns
    -------
    d_l_test_results: Dict[str, List[GalInfoNTestResults or GalInfoDataTestResults]]
        A dict of the test results for each shear estimation method (indexed by the test case name). The result is
        returned as a dict of lists of one element each for consistency of format with other validation tests
    d_d_textfiles: Dict[str, Dict[str, str]]
        A dict providing dicts of the filenames of textfiles output for each test case
    """

    # The MER Final Catalog is used identically by all test cases, so prepare it first by pruning to only rows
    # detected in the VIS filter
    good_mfc_rows = gal_info_input.mer_cat[mfc_tf.vis_det] == 1
    mer_cat = gal_info_input.mer_cat[good_mfc_rows]

    she_chains = gal_info_input.she_chains

    # Prepare output dicts, which we'll fill in for each method
    d_l_test_results: Dict[str, List[GalInfoTestResults]] = {}
    d_d_textfiles: Dict[str, Dict[str, str]] = {}

    for test_case_info in L_GAL_INFO_TEST_CASE_INFO:
        method = test_case_info.method
        name = test_case_info.name

        method_she_cat = gal_info_input.d_she_cat[method]

        # Split execution depending on which test case we're running

        if test_case_info.test_case_id.startswith(GAL_INFO_N_TEST_CASE_INFO.base_test_case_id):

            test_results = _get_gal_info_n_test_results(method_she_cat, she_chains, mer_cat)

        elif test_case_info.test_case_id.startswith(GAL_INFO_DATA_TEST_CASE_INFO.base_test_case_id):

            test_results = _get_gal_info_data_test_results(method_she_cat, she_chains, method)

        else:

            raise ValueError(f"Unrecognized test case id: {test_case_info.test_case_id}")

        # Store the results in a list, to match the common format expected by the ResultsWriter
        d_l_test_results[name] = [test_results]

        # Write out textfiles associated with the test results
        d_d_textfiles[name] = test_results.write_textfiles(workdir=workdir)

    return d_l_test_results, d_d_textfiles


def _get_gal_info_n_test_results(she_cat: Optional[Table],
                                 she_chains: Optional[Table],
                                 mer_cat: Table) -> GalInfoNTestResults:
    """Private implementation of determining test results for the GalInfo-N test case.
    """

    l_mer_ids = mer_cat[mfc_tf.ID]
    n_in = len(l_mer_ids)

    d_l_missing_ids: Dict[str, np.ndarray] = {}

    for cat, cat_type in ((she_cat, MEAS_ATTR),
                          (she_chains, CHAINS_ATTR)):
        # Check for case where we don't have a catalog provided
        if cat is None:
            d_l_missing_ids[cat_type] = np.array(l_mer_ids, dtype=int)
            continue

        l_she_ids = cat[sem_tf.ID]

        # Use set difference to find IDs that aren't present in the SHE catalog
        d_l_missing_ids[cat_type] = np.setdiff1d(l_mer_ids, l_she_ids)

    return GalInfoNTestResults(n_in=n_in,
                               l_missing_ids_meas=d_l_missing_ids[MEAS_ATTR],
                               l_missing_ids_chains=d_l_missing_ids[CHAINS_ATTR])


def _get_gal_info_data_test_results(she_cat: Optional[Table],
                                    she_chains: Optional[Table],
                                    method: ShearEstimationMethods) -> GalInfoDataTestResults:
    """Private implementation of determining test results for the GalInfo-Data test case.
    """

    d_l_invalid_ids: Dict[str, np.ndarray] = {}
    d_invalid_data_tables: Dict[str, Optional[Table]] = {}

    for cat, cat_type in ((she_cat, MEAS_ATTR),
                          (she_chains, CHAINS_ATTR)):

        # Check for case where we don't have a catalog provided
        if cat is None:
            d_l_invalid_ids[cat_type] = np.ndarray(shape=(0,), dtype=int)
            d_invalid_data_tables[cat_type] = None
            continue

        # Some different setup between measurements and chains catalogs
        if cat_type == MEAS_ATTR:
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
        l_l_val: List[Column] = []
        l_l_checks: List[Column] = []
        for gid_criteria in L_GID_CRITERIA:

            attr = gid_criteria.attr
            meas_colname: str = getattr(tf, attr)
            gid_colname: str = getattr(GIDM_TF, attr)
            gid_val_check_colname: str = getattr(GIDM_TF, f"{attr}_{GID_VAL}_{GID_CHECK_TAIL}")
            gid_min_check_colname: str = getattr(GIDM_TF, f"{attr}_{GID_MIN}_{GID_CHECK_TAIL}")
            gid_max_check_colname: str = getattr(GIDM_TF, f"{attr}_{GID_MAX}_{GID_CHECK_TAIL}")

            # For chains, we need to use slightly-different methods, which reduce the multidimensional array
            # properly, to do checks on values
            if cat_type == MEAS_ATTR or not gid_criteria.is_chain:
                bad_value_test = _meas_bad_value
                min_value_test = _meas_min_value
                max_value_test = _meas_max_value
            else:
                bad_value_test = _chains_bad_value
                min_value_test = _chains_min_value
                max_value_test = _chains_max_value

            # Get a column of the value we're testing
            l_val = Column(good_cat[meas_colname], name=gid_colname)

            # Confirm the value is not Inf, NaN, or masked
            l_val_check = Column(np.logical_not(bad_value_test(good_cat[meas_colname])), name=gid_val_check_colname)

            # Confirm the value is between the minimum and maximum, exclusive
            l_min_check = Column(min_value_test(good_cat[meas_colname], gid_criteria.min), name=gid_min_check_colname)
            l_max_check = Column(max_value_test(good_cat[meas_colname], gid_criteria.max), name=gid_max_check_colname)

            # Store the checks in the ongoing list we can use to see which objects fail any check
            l_l_checks.append(l_val_check)
            l_l_checks.append(l_min_check)
            l_l_checks.append(l_max_check)

            # Also store a column for the attribute value for later output if needed
            l_l_val.append(l_val)

        l_fail_some_checks = ~np.logical_and.reduce(l_l_checks)

        # Now, get a list of IDs which failed checks to output
        l_invalid_ids = Column(good_cat[l_fail_some_checks][sem_tf.ID], name=GIDM_TF.ID)
        d_l_invalid_ids[cat_type] = l_invalid_ids

        # If anything failed to pass a check, create a table to detail info about those objects
        if np.sum(l_fail_some_checks) == 0:
            d_invalid_data_tables[cat_type] = None
            continue

        d_l_invalid_data_cols: Dict[str, Column] = {GIDM_TF.ID: l_invalid_ids,
                                                    GIDM_TF.fit_flags: good_cat[l_fail_some_checks][tf.fit_flags]}
        for l_data_col in (*l_l_val, *l_l_checks):
            d_l_invalid_data_cols[l_data_col.name] = l_data_col[l_fail_some_checks]

        if cat_type == MEAS_ATTR:
            gid_table_format = GIDM_TF
        else:
            gid_table_format = GIDC_TF
        d_invalid_data_tables[cat_type] = gid_table_format.init_table(init_cols=d_l_invalid_data_cols)

    return GalInfoDataTestResults(l_invalid_ids_meas=d_l_invalid_ids[MEAS_ATTR],
                                  l_invalid_ids_chains=d_l_invalid_ids[CHAINS_ATTR],
                                  invalid_data_table_meas=d_invalid_data_tables[MEAS_ATTR],
                                  invalid_data_table_chains=d_invalid_data_tables[CHAINS_ATTR])


def _meas_bad_value(a: np.ndarray) -> Union[np.ndarray, MutableSequence[bool]]:
    return is_inf_nan_or_masked(a)


def _chains_bad_value(a: np.ndarray) -> Union[np.ndarray, MutableSequence[bool]]:
    return np.logical_or(is_masked(a), np.any(np.logical_or(np.isinf(a), np.isnan(a)), axis=1))


def _meas_min_value(a: np.ndarray, min_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return a > min_value


def _chains_min_value(a: np.ndarray, min_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return np.all(a > min_value, axis=1)


def _meas_max_value(a: np.ndarray, max_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return a < max_value


def _chains_max_value(a: np.ndarray, max_value: float) -> Union[np.ndarray, MutableSequence[bool]]:
    return np.all(a < max_value, axis=1)
