"""
:file: python/SHE_Validation_DataQuality/gi_results_reporting.py

:date: 01/27/23
:author: Bryan Gillis

Code for reporting the results of the GalInfo validation test in a data product
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
from SHE_Validation_DataQuality.constants.gal_info_test_info import (D_L_GAL_INFO_REQUIREMENT_INFO,
                                                                     L_GAL_INFO_TEST_CASE_INFO, )
from SHE_Validation_DataQuality.gi_data_processing import GalInfoTestResults

logger = getLogger(__name__)

STR_GI_STAT = ""


class GalInfoRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    value_name: str = STR_GI_STAT
    l_test_results: Optional[List[GalInfoTestResults]]

    # Protected methods
    def _interpret_test_results(self) -> None:
        """Override to set values to None, to ensure we don't print out data on it
        """
        self.l_val = None

    def _get_val_message_for_bin(self, bin_index: int = 0) -> str:
        """Override to implement desired reporting format of messages. Since this doesn't do any binning,
        we don't include any reporting of the bin index or bin limits.

        The implementation of this is forwarded to an abstract method of the GalInfoTestResults object, to account
        for the fact that it differs significantly between the two cases. The two test cases provide different
        implementations of writing the Supplementary Information.
        """

        return self.l_test_results[bin_index].get_supp_info_message()

    def _determine_results(self):
        """Determine the test results if not already generated, filling in self.l_good_data and self.l_test_pass
        and self.measured_value
        """

        if self.l_good_data is not None and self.l_test_pass is not None and self.measured_value is not None:
            return

        # Make an array of test results
        self.l_test_pass = [test_results.global_passed for test_results in self.l_test_results]

        self.measured_value = self.l_test_results[0].get_measured_value()

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


class GalInfoTestCaseWriter(TestCaseWriter):
    """ TestCaseWriter specialized for the PSF-Res validation test.
    """

    # Class members

    # Types of child objects, overriding those in base class
    requirement_writer_type = GalInfoRequirementWriter


class GalInfoValidationResultsWriter(ValidationResultsWriter):
    """ ValidationResultsWriter specialized for the PSF-Res validation test.
    """

    # Types of child classes
    test_case_writer_type = GalInfoTestCaseWriter
    l_test_case_info = L_GAL_INFO_TEST_CASE_INFO
    dl_l_requirement_info = D_L_GAL_INFO_REQUIREMENT_INFO
