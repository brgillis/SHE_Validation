"""
:file: python/SHE_Validation_DataQuality/constants/data_proc_test_info.py

:date: 09/21/22
:author: Bryan Gillis

Default values for information about the data-proc test and test cases.
"""

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

from SHE_Validation.constants.test_info import RequirementInfo, TestCaseInfo, TestInfo

# Metadata about the requirement
DATA_PROC_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-PRD-F-010",
                                             description="Ground data processing shall generate Level-2 and higher "
                                                         "data, including the final mission products and catalogues.",
                                             parameter="True/False for whether or not all data is provided.")

# Metadata about the test
DATA_PROC_TEST_INFO = TestInfo(test_id="T-SHE-000013-data-proc",
                               description="Make sure that SHE provides the level-2 data including the final mission "
                                           "products and catalogs.")

DATA_PROC_TEST_CASE_INFO = TestCaseInfo(test_info=DATA_PROC_TEST_INFO,
                                        base_test_case_id="TC-SHE-100035-data-proc",
                                        base_name="DataProc",
                                        base_description="Output calibrated shear estimates.")

L_DATA_PROC_TEST_CASE_INFO = [DATA_PROC_TEST_CASE_INFO]

# Dict associated the test cases to requirements
D_L_DATA_PROC_REQUIREMENT_INFO = {DATA_PROC_TEST_CASE_INFO.name: DATA_PROC_REQUIREMENT_INFO}
