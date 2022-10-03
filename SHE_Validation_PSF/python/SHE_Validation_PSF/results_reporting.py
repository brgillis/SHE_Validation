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

from typing import List, Optional

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_PPT.utility import default_value_if_none, is_inf_or_nan
from SHE_Validation.constants.default_config import DEFAULT_P_FAIL
from SHE_Validation.results_writer import (AnalysisWriter, RequirementWriter,
                                           TargetType, TestCaseWriter, ValidationResultsWriter, val_over_target, )
from SHE_Validation_PSF.constants.psf_res_sp_test_info import (D_L_PSF_RES_SP_REQUIREMENT_INFO,
                                                               L_PSF_RES_SP_TEST_CASE_INFO,
                                                               PSF_RES_SP_VAL_NAME, )
from SHE_Validation_PSF.utility import KsResult

logger = getLogger(__name__)

# Define constants for various messages etc.

PSF_RES_SP_DIRECTORY_FILENAME = "ShePSFResStarPosResultsDirectory.txt"
PSF_RES_SP_DIRECTORY_HEADER = "### OU-SHE PSF-Res-star-pos Analysis Results File Directory ###"
STR_KS_STAT = "KS Statistic"


class PsfResRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    target_type = TargetType.MIN

    value_name: str = PSF_RES_SP_VAL_NAME
    l_test_results: Optional[List[KsResult]]
    l_ks_statistic: Optional[List[float]] = None

    p_fail: float = DEFAULT_P_FAIL

    def __init__(self,
                 *args,
                 p_fail: Optional[float] = None,
                 **kwargs):

        self.p_fail = default_value_if_none(p_fail, self.p_fail)

        super().__init__(*args, **kwargs)

    # Protected methods
    def _interpret_test_results(self) -> None:
        """Override to use the pvalue as the value and a constant target
        """
        self.l_val = [test_results.pvalue for test_results in self.l_test_results]
        self.l_ks_statistic = [test_results.statistic for test_results in self.l_test_results]
        self.l_val_target = [self.p_fail for _ in self.l_test_results]

    def _get_val_message_for_bin(self, bin_index: int = 0) -> str:
        """ Override this method to also report the KS statistic before the p-value.
        """
        if self.l_ks_statistic is None:
            message: str = ""
        else:
            message: str = f"{STR_KS_STAT} = {self.l_ks_statistic[bin_index]}\n"
        message += super()._get_val_message_for_bin(bin_index)
        return message

    def _determine_results(self):
        """ Determine the test results if not already generated, filling in self.l_good_data and self.l_test_pass
            and self.measured_value
        """

        if self.l_good_data is not None and self.l_test_pass is not None and self.measured_value is not None:
            return

        self.measured_value = np.nanmin(self.l_val)

        # Get an array of whether or not we have good data
        l_bad_val = is_inf_or_nan(self.l_val)
        self.l_good_data = np.logical_not(l_bad_val)

        # Make an array of test results
        self.l_test_pass = val_over_target(val = self.l_val, val_target = self.l_val_target)


class PsfResAnalysisWriter(AnalysisWriter):
    """ Subclass of AnalysisWriter, to handle some changes specific for this test.
    """

    product_type = "PSF-RES-ANALYSIS-FILES"
    _directory_filename: str = PSF_RES_SP_DIRECTORY_FILENAME
    directory_header: str = PSF_RES_SP_DIRECTORY_HEADER


class PsfResTestCaseWriter(TestCaseWriter):
    """ TestCaseWriter specialized for the PSF-Res validation test.
    """

    # Class members

    # Types of child objects, overriding those in base class
    requirement_writer_type = PsfResRequirementWriter
    analysis_writer_type = PsfResAnalysisWriter


class PsfResValidationResultsWriter(ValidationResultsWriter):
    """ ValidationResultsWriter specialized for the PSF-Res validation test.
    """

    # Types of child classes
    test_case_writer_type = PsfResTestCaseWriter
    l_test_case_info = L_PSF_RES_SP_TEST_CASE_INFO
    dl_l_requirement_info = D_L_PSF_RES_SP_REQUIREMENT_INFO
