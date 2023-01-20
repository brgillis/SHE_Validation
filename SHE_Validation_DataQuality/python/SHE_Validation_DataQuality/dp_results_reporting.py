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

from copy import deepcopy
from typing import List, Optional

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_Validation.results_writer import (AnalysisWriter, RESULT_FAIL, RESULT_PASS, RequirementWriter, TestCaseWriter,
                                           ValidationResultsWriter, )
from SHE_Validation_DataQuality.constants.data_proc_test_info import (D_L_DATA_PROC_REQUIREMENT_INFO,
                                                                      L_DATA_PROC_TEST_CASE_INFO, )
from SHE_Validation_DataQuality.dp_data_processing import DataProcTestResults

logger = getLogger(__name__)

STR_DP_STAT = ""


class DataProcRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    value_name: str = STR_DP_STAT
    l_test_results: Optional[List[DataProcTestResults]]

    # Protected methods
    def _interpret_test_results(self) -> None:
        """Override to use the pvalue as the value and a constant target
        """
        self.l_val = [test_results.global_passed for test_results in self.l_test_results]
        self.l_val_target = np.ones_like(self.l_val, dtype=bool)

    def _get_val_message_for_bin(self, bin_index: int = 0) -> str:
        """Override to implement desired reporting format of messages. Since this doesn't do any binning,
        we don't include any reporting of the bin index or bin limits.
        """
        test_results = self.l_test_results[bin_index]

        message = ""

        # Construct the message similarly for each thing we test for the presence and validity of

        for (attr_base, name) in (("p_rec_cat", "Reconciled Shear Estimates Data Product"),):

            message += f"Presence and validity of {name}: "

            if getattr(test_results, f"{attr_base}_passed"):
                message += RESULT_PASS
            else:
                message += RESULT_FAIL

            message += "\nDetails: "

            attr_message = getattr(test_results, f"msg_{attr_base}")
            if attr_message:
                message += f"\"{attr_message}\"\n\n"
            else:
                message += "N/A\n\n"

        # Trim the final newline character that was added to the message
        message = message[:-1]

        return message

    def _determine_results(self):
        """ Determine the test results if not already generated, filling in self.l_good_data and self.l_test_pass
            and self.measured_value
        """

        if self.l_good_data is not None and self.l_test_pass is not None and self.measured_value is not None:
            return

        self.measured_value = np.all(self.l_val)

        # For this test, we consider all data to be "good" for the purposes of outputting results
        self.l_good_data = np.ones_like(np.all(self.l_val), dtype=bool)

        # Make an array of test results
        self.l_test_pass = deepcopy(self.l_val)


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
