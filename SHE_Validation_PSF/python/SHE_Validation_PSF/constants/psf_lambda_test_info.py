"""
:file: python/SHE_Validation_PSF/psf_lambda_test_info.py

:date: 10/05/22
:author: Bryan Gillis

Default values for information about the PSF-Lambda test and test cases
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

# Metadata about the requirements
PSF_LAMBDA_E_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-040",
                                                description=("The uncertainty on the bias in the ellipticity of an "
                                                             "object arising from the transfer of the VIS PSF "
                                                             "ellipticity model to the weak-lensing objects shall be "
                                                             "smaller than 3.5x10^-5 (1-sigma)."),
                                                parameter=("The uncertainty on the additive bias in the ellipticity of "
                                                           "an object arising from the transfer of the VIS PSF "
                                                           "ellipticity model to the weak-lensing objects."))
PSF_LAMBDA_R2_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-050",
                                                 description=("The bias caused in the inferred R^2 of an object "
                                                              "arising from the transfer of the wavelength dependence "
                                                              "of the VIS PSF shall be < 3.5x10^-4."),
                                                 parameter=("The bias caused in the inferred R^2 of an object arising "
                                                            "from the transfer of the wavelength dependence of the "
                                                            "VIS PSF."))

# Metadata about the test
PSF_LAMBDA_TEST_INFO = TestInfo(test_id="T-SHE-000002-PSF-lambda",
                                description=("Approximate PSF from broad-band magnitudes compared to precise PSF from "
                                             "spectroscopic data."))

PSF_LAMBDA_E_TEST_CASE_INFO = TestCaseInfo(base_test_case_id="TC-SHE-100003-PSF-lambda-ell",
                                           base_name=f"PL-E",
                                           base_description=f"{PSF_LAMBDA_TEST_INFO.description} Effect on "
                                                            "ellipticity.",
                                           base_id_number=100003)
PSF_LAMBDA_R2_TEST_CASE_INFO = TestCaseInfo(base_test_case_id="TC-SHE-100004-PSF-lambda-R2",
                                            base_name=f"PL-R2",
                                            base_description=f"{PSF_LAMBDA_TEST_INFO.description} Effect on size.",
                                            base_id_number=100004)

# Create a dict of the test case info

L_PSF_LAMBDA_TEST_CASE_INFO = [PSF_LAMBDA_E_TEST_CASE_INFO,
                               PSF_LAMBDA_R2_TEST_CASE_INFO]

NUM_PSF_LAMBDA_TEST_CASES = len(L_PSF_LAMBDA_TEST_CASE_INFO)

# Create a dict of the requirement info
D_L_PSF_LAMBDA_REQUIREMENT_INFO = {PSF_LAMBDA_E_TEST_CASE_INFO.name: PSF_LAMBDA_E_REQUIREMENT_INFO,
                                   PSF_LAMBDA_R2_TEST_CASE_INFO.name: PSF_LAMBDA_R2_REQUIREMENT_INFO,
                                   }
