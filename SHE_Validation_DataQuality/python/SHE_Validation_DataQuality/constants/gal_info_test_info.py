"""@file gal_info_test_info.py

Created 21 September 2022

Default values for information about the gal-info test and test cases.
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
GAL_INFO_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-PRD-F-180",
                                            description="R-SHE-PRD-F-180: For each galaxy used in the weak lensing "
                                                        "analysis up to the limiting magnitude the following"
                                                        "information should be available:\n"
                                                        "* At least one ellipticity measurement such that a shear "
                                                        "estimate can be inferred\n"
                                                        "* The posterior distribution of the ellipticity\n"
                                                        "* The posterior distribution of the photometric redshift\n"
                                                        "* ~~An estimate of the covariance between photometric "
                                                        "redshift and ellipticity, from joint inference of redshift and"
                                                        "ellipticity~~ NOTE: Excluded from test due to design changes\n"
                                                        "* The star-galaxy classification\n"
                                                        "* At least one measurement of galaxy size\n"
                                                        "* Quality flags\n"
                                                        "* A morphology/type quantifier is optional but should be "
                                                        "clearly flagged if present or not present",
                                            parameter="Fraction of required data provided")

# Metadata about the test
GAL_INFO_TEST_INFO = TestInfo(test_id="T-SHE-000008-gal-info",
                              description="The data products of the weak lensing pipeline must include essential "
                                          "information on any weak lensing object or indicate why information is "
                                          "missing (flags). All essential data fields require a confidence level and "
                                          "a quality flag. Furthermore, all objects identified as weak lensing "
                                          "objects prior to OU-SHE have to be included. As additional goal, the "
                                          "catalogue should also contain quantifiers of the galaxy morphology and "
                                          "type.")

GAL_INFO_N_TEST_CASE_INFO = TestCaseInfo(test_info=GAL_INFO_TEST_INFO,
                                         base_test_case_id="TC-SHE-100022-gal-N-out",
                                         base_name="GalInfo-N",
                                         base_description="Compare the number of objects in the input and output "
                                                          "catalogues for SHE.")

GAL_INFO_DATA_TEST_CASE_INFO = TestCaseInfo(test_info=GAL_INFO_TEST_INFO,
                                            base_test_case_id="TC-SHE-100023-gal-info-out",
                                            base_name="GalInfo-Data",
                                            base_description="Test that all SHE measurements in shear catalogue have "
                                                             "a measurement or are flagged appropriately.")

# Dict associated the test cases to requirements
D_L_GAL_INFO_REQUIREMENT_INFO = {GAL_INFO_N_TEST_CASE_INFO.name: GAL_INFO_REQUIREMENT_INFO,
                                 GAL_INFO_DATA_TEST_CASE_INFO.name: GAL_INFO_REQUIREMENT_INFO}
