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

from SHE_PPT.logging import getLogger
from SHE_Validation.results_writer import RESULT_FAIL, RESULT_PASS, RequirementWriter
from SHE_Validation_DataQuality.dp_data_processing import DataProcTestResults

logger = getLogger(__name__)

STR_DP_STAT = ""


class DataProcRequirementWriter(RequirementWriter):
    """ Class for managing reporting of results for a single Shear Bias requirement
    """

    value_name: str = STR_DP_STAT
    l_test_results: Optional[List[DataProcTestResults]]

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
