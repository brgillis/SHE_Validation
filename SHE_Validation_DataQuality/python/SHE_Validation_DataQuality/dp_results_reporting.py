"""
:file: python/SHE_Validation_DataQuality/dp_results_reporting.py

:date: 01/19/23
:author: Bryan Gillis

Code for reporting the results of the DataProc validation test in a data product
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

from typing import List, Optional

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_Validation.results_writer import (RESULT_FAIL, RESULT_PASS, RequirementWriter, TestCaseWriter,
                                           ValidationResultsWriter, get_result_string, )
from SHE_Validation_DataQuality.constants.data_proc_test_info import (D_L_DATA_PROC_REQUIREMENT_INFO,
                                                                      L_DATA_PROC_TEST_CASE_INFO, )
from SHE_Validation_DataQuality.dp_data_processing import DataProcTestResults

logger = getLogger(__name__)

STR_DP_STAT = ""

STR_P_SHE_CAT = "Shear Estimates Data Product"
STR_SHE_CAT = "Shear Estimates Catalog"
STR_P_SHE_CHAINS = "Chains Data Product"
STR_SHE_CHAINS = "Chains Catalog"

MSG_PRESENT_AND_VALID = "Presence and validity of %s: "
MSG_DETAILS = "Details: "
MSG_NA = "N/A"


class DataProcRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    value_name: str = STR_DP_STAT
    l_test_results: Optional[List[DataProcTestResults]]

    # Protected methods
    def _interpret_test_results(self) -> None:
        """Override to set values to None, to ensure we don't print out data on it
        """
        self.l_val = None

    def _get_val_message_for_bin(self, bin_index: int = 0) -> str:
        """Override to implement desired reporting format of messages. Since this doesn't do any binning,
        we don't include any reporting of the bin index or bin limits.
        """
        test_results = self.l_test_results[bin_index]

        message = ""

        # Construct the message similarly for each thing we test for the presence and validity of

        for (attr_base, name) in (("p_she_cat", STR_P_SHE_CAT),
                                  ("she_cat", STR_SHE_CAT),
                                  ("p_she_chains", STR_P_SHE_CHAINS),
                                  ("she_chains", STR_SHE_CHAINS),):

            message += MSG_PRESENT_AND_VALID % name

            if getattr(test_results, f"{attr_base}_passed"):
                message += RESULT_PASS
            else:
                message += RESULT_FAIL

            message += f"\n{MSG_DETAILS}"

            attr_message = getattr(test_results, f"msg_{attr_base}")
            if attr_message:
                message += f"\"{attr_message}\"\n\n"
            else:
                message += f"{MSG_NA}\n\n"

        return message

    def _determine_results(self):
        """Determine the test results if not already generated, filling in self.l_good_data and self.l_test_pass
        and self.measured_value
        """

        if self.l_good_data is not None and self.l_test_pass is not None and self.measured_value is not None:
            return

        # Make an array of test results
        self.l_test_pass = [test_results.global_passed for test_results in self.l_test_results]

        self.measured_value = np.all(self.l_test_pass)

        # For this test, we consider all data to be "good" for the purposes of outputting results
        self.l_good_data = np.ones_like(np.all(self.l_test_pass), dtype=bool)

    def _determine_overall_results(self):
        """Override determination of overall results. This implementation simplifies things a bit since we don't have
        bins, and also avoids setting self.l_val, which ensures no extra unwanted lines will be output to
        SupplementaryInfo.
        """

        # Get the list of results for bins
        self.l_result = list(map(get_result_string, self.l_test_pass))

        # Get the overall results
        self.good_data = True

        self.test_pass = np.all(self.l_test_pass)

        self.result = get_result_string(self.test_pass)


class DataProcTestCaseWriter(TestCaseWriter):
    """ TestCaseWriter specialized for the PSF-Res validation test.
    """

    # Class members

    # Types of child objects, overriding those in base class
    requirement_writer_type = DataProcRequirementWriter


class DataProcValidationResultsWriter(ValidationResultsWriter):
    """ ValidationResultsWriter specialized for the PSF-Res validation test.
    """

    # Types of child classes
    test_case_writer_type = DataProcTestCaseWriter
    l_test_case_info = L_DATA_PROC_TEST_CASE_INFO
    dl_l_requirement_info = D_L_DATA_PROC_REQUIREMENT_INFO
