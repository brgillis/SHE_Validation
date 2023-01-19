"""
:file: python/SHE_Validation_DataQuality/dp_data_processing.py

:date: 01/19/23
:author: Bryan Gillis

Code for processing data in the DataProc validation test
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

from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING

import numpy as np
from astropy.table import Table

from SHE_PPT.constants.classes import ShearEstimationMethods

if TYPE_CHECKING:
    from SHE_Validation_DataQuality.dp_input import DataProcInput  # noqa F401


@dataclass
class DataProcTestResults:
    """Dataclass containing test results for a single shear estimation method

    Attributes
    ----------
    p_rec_cat_passed: bool
        Whether the check for a valid Reconciled Shear Measurements data product passed
    err_p_rec_cat: str or None
        The text of any exceptions raised when attempting to read in the Reconciled Shear Measurements data product,
        or else None
    rec_cat_passed: bool
        Whether the check for a valid Reconciled Shear Measurements catalog passed
    err_rec_cat: str or None
        The text of any exceptions raised when attempting to read each Reconciled Shear Measurements catalog, or else
        None
    p_rec_chains_passed: bool
        Whether the check for a valid Chains data product passed
    err_p_rec_chains: str or None
        The text of any exceptions raised when attempting to read in the Reconciled Chains data product, or else None
    rec_chains_passed: bool
        Whether the check for a valid Chains catalog passed
    err_rec_chains: Table or None
        The text of any exceptions raised when attempting to read in the Reconciled Chains catalog, or else None

    Methods
    -------
    global_passed: bool
        (Read-only property) Whether the test case as a whole passed
    """

    p_rec_cat_passed: bool
    err_p_rec_cat: Optional[str]

    rec_cat_passed: bool
    err_rec_cat: Optional[str]

    p_rec_chains_passed: bool
    err_p_rec_chains: Optional[str]

    rec_chains_passed: bool
    err_rec_chains: Optional[str]

    @property
    def global_passed(self) -> bool:
        """Whether the test case as a whole passed
        """
        return np.all((self.p_rec_cat_passed, self.rec_cat_passed, self.p_rec_chains_passed, self.rec_chains_passed))


def get_data_proc_test_results(data_proc_input):
    """Get the results of the DataProc test for each shear estimation method, based on the provided input data.

    Parameters
    ----------
    data_proc_input: DataProcInput
        The input data, as read in by the `read_data_proc_input` method in the `dp_input.py` module

    Returns
    -------
    Dict[ShearEstimationMethods, List[DataProcTestResults]]
        A dict of the test results for each shear estimation method. The result is returned as a dict of lists of one
        element each for consistency of format with other validation tests
    """

    # Prepare an output dict, which we'll fill in for each method
    d_l_test_results: Dict[ShearEstimationMethods, List[DataProcTestResults]] = {}

    # Determine results common to all methods

    err_p_rec_cat = data_proc_input.err_p_rec_cat
    p_rec_cat_passed = (err_p_rec_cat is None) and (data_proc_input.p_rec_cat is not None)

    err_p_rec_chains = data_proc_input.err_p_rec_chains
    p_rec_chains_passed = (err_p_rec_chains is None) and (data_proc_input.p_rec_chains is not None)

    err_rec_chains = data_proc_input.err_rec_chains
    rec_chains_passed = p_rec_chains_passed and (err_rec_chains is None) and (data_proc_input.rec_chains is not None)

    for method in ShearEstimationMethods:

        # Determine method-specific results
        err_rec_cat = data_proc_input.d_err_rec_cat[method]
        rec_cat_passed = p_rec_cat_passed and (err_rec_cat is None) and (data_proc_input.d_rec_cat[method] is not None)

        d_l_test_results[method] = [DataProcTestResults(p_rec_cat_passed=p_rec_cat_passed,
                                                        err_p_rec_cat=err_p_rec_cat,
                                                        rec_cat_passed=rec_cat_passed,
                                                        err_rec_cat=err_rec_cat,
                                                        p_rec_chains_passed=p_rec_chains_passed,
                                                        err_p_rec_chains=err_p_rec_chains,
                                                        rec_chains_passed=rec_chains_passed,
                                                        err_rec_chains=err_rec_chains)]

    return d_l_test_results
