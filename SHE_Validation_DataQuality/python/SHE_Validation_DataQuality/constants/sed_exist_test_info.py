"""@file sed_exist_test_info.py

Created 21 September 2022

Default values for information about the SED-Exist test and test cases.
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
SED_EXIST_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-060",
                                             description="Tests whether the template assignment exists for all stars "
                                                         "used to determine the PSF model. The template assignment is "
                                                         "provided from PHZ data products.",
                                             parameter="Fraction of stars for which template is provided.")

# Metadata about the test
SED_EXIST_TEST_INFO = TestInfo(test_id="T-SHE-000011-star-SED-exist",
                               description="Verify that an estimate of the SED of the stars used in the PSF modelling "
                                           "has been provided, using available data. This is provided by OU-PHZ.")

SED_EXIST_TEST_CASE_INFO = TestCaseInfo(test_info=SED_EXIST_TEST_INFO,
                                        base_test_case_id="TC-SHE-100033-star-SED-exist",
                                        base_name="SEDExist",
                                        base_description="Tests whether the template assignment exists for all stars "
                                                         "used to determine the PSF model. The template assignment is "
                                                         "provided from PHZ data products.")

L_SED_EXIST_TEST_CASE_INFO = [SED_EXIST_TEST_CASE_INFO]

# Dict associated the test cases to requirements
D_L_SED_EXIST_REQUIREMENT_INFO = {SED_EXIST_TEST_CASE_INFO.name: SED_EXIST_REQUIREMENT_INFO}
