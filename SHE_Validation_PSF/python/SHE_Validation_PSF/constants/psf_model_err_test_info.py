""" @file psf_model_err_test_info.py

    Created 06 October 2022 by Bryan Gillis

    Default values for information about tests and test cases.
"""

__updated__ = "2022-10-06"

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

# Metadata about the requirements
PSF_MODEL_ERR_E_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-PRD-F-110",
                                                   description=("For each ellipticity component, the transfer of the "
                                                                "VIS PSF model to the weak-lensing objects shall not "
                                                                "introduce errors larger than 5×10^-5 (1-sigma)."),
                                                   parameter=("Errors transferred to the weak-lensing objects from the "
                                                              "VIS PSF model for each ellipticity component."))
PSF_MODEL_ERR_R2_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-PRD-F-120",
                                                    description=("For the PSF R^2 component, the transfer of the VIS "
                                                                 "PSF model to the weak-lensing objects shall not "
                                                                 "introduce errors larger than sigma(R)/R< 5×10^-4."),
                                                    parameter=("Errors transferred to the weak-lensing objects from "
                                                               "the VIS PSF model for the PSF R^2 component."))

# Metadata about the test
PSF_MODEL_ERR_TEST_INFO = TestInfo(test_id="T-SHE-000004-PSF-model-err-propa",
                                   description=("Propagate the uncertainty in the PSF to the galaxy ellipticity and "
                                                "size, and ensure below requirements."))

PSF_MODEL_ERR_E_TEST_CASE_INFO = TestCaseInfo(base_test_case_id="TC-SHE-100011-PSF-model-err-propa-ell",
                                              base_name=f"PME-E",
                                              base_description=f"{PSF_MODEL_ERR_TEST_INFO.description} Effect on "
                                                               "ellipticity.",
                                              base_id_number=100011)
PSF_MODEL_ERR_R2_TEST_CASE_INFO = TestCaseInfo(base_test_case_id="TC-SHE-100012-PSF-model-err-propa-R2",
                                               base_name=f"PME-R2",
                                               base_description=f"{PSF_MODEL_ERR_TEST_INFO.description} Effect on "
                                                                f"size.",
                                               base_id_number=100012)

# Create a dict of the test case info

L_PSF_MODEL_ERR_TEST_CASE_INFO = [PSF_MODEL_ERR_E_TEST_CASE_INFO,
                                  PSF_MODEL_ERR_R2_TEST_CASE_INFO]

NUM_PSF_MODEL_ERR_TEST_CASES = len(L_PSF_MODEL_ERR_TEST_CASE_INFO)

# Create a dict of the requirement info
D_L_PSF_MODEL_ERR_REQUIREMENT_INFO = {PSF_MODEL_ERR_E_TEST_CASE_INFO.name: PSF_MODEL_ERR_E_REQUIREMENT_INFO,
                                      PSF_MODEL_ERR_R2_TEST_CASE_INFO.name: PSF_MODEL_ERR_R2_REQUIREMENT_INFO,
                                      }
