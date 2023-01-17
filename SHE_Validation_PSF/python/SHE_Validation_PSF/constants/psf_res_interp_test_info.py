"""
:file: python/SHE_Validation_PSF/psf_lambda_test_info.py

:date: 10/05/22
:author: Bryan Gillis

Default values for information about the PSF-Res-Interp test and test cases
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

from SHE_Validation.constants.test_info import (BinParameters, ID_NUMBER_REPLACE_TAG, NAME_REPLACE_TAG, RequirementInfo,
                                                TestCaseInfo, TestInfo, )
from SHE_Validation.test_info_utility import make_test_case_info_for_bins

# Metadata about the requirement
PSF_RES_INTERP_CAL_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-CAL-F-030",
                                                      description=("The r.m.s. of the ensemble averaged ΔQij/R^2 "
                                                                   "(where ΔQij is the quadrupole moment of the "
                                                                   "residual after the linearity correction) for a "
                                                                   "subset of observed and emulated stars in the "
                                                                   "range 18 < VIS < 24.5 as a function of magnitude "
                                                                   "in bins of width one magnitude shall be: "
                                                                   "<3.0x10^-5 (1-sigma) per moment if i=j and "
                                                                   "<1.75x10^-5 (1-sigma) if i≠j, averaging over "
                                                                   "magnitude bins and 100 fields."),
                                                      parameter=("The r.m.s. of the ensemble averaged ΔQij/R^2 for a "
                                                                 "subset of observed and emulated stars in the range "
                                                                 "18 < VIS < 24.5 as a function of magnitude in bins "
                                                                 "of width one magnitude"))
PSF_RES_INTERP_PRD_REQUIREMENT_INFO = RequirementInfo(requirement_id="R-SHE-PRD-F-090",
                                                      description=("The SGS shall create a model of the PSF such that "
                                                                   "the normalized moments Qii/R^2 of the ensemble "
                                                                   "averaged residual image (observed – PSF model) "
                                                                   "for a subset of observed stars in the range 18 < "
                                                                   "VIS < 23 as a function of magnitude in bins of "
                                                                   "width one magnitude shall be: < 8.6x10^-5 ("
                                                                   "1-sigma) per moment if i=j, and < 5x10^-5 if i≠j, "
                                                                   "averaging over magnitude bins and 100 fields."),
                                                      parameter=("The normalized moments Qii/R^2 of the ensemble "
                                                                 "averaged residual image for a subset of observed "
                                                                 "stars in the range 18 < VIS < 23 as a function of "
                                                                 "magnitude in bins of width one magnitude"))

# Metadata about the test
PSF_RES_INTERP_TEST_INFO = TestInfo(test_id="T-SHE-000003-PSF-res-interp-star-pos",
                                    description=(
                                        "Compare the PSF at a stellar position for a star **not** used in the PSF "
                                        "Fitting."))

BASE_PSF_RES_INTERP_TEST_CASE_INFO = TestCaseInfo(base_test_case_id=f"TC-SHE-{ID_NUMBER_REPLACE_TAG}-PSF-res-interp-"
                                                                    f"star-{NAME_REPLACE_TAG}",
                                                  base_name=f"PRI-{NAME_REPLACE_TAG}",
                                                  base_description=PSF_RES_INTERP_TEST_INFO.description,
                                                  base_id_number=100005)

PSF_RES_INTERP_VAL_NAME = "p"

# Create a dict of the test case info

# TODO: Expand bin limits when others are available
L_PSF_RES_INTERP_BIN_PARAMETERS = (BinParameters.TOT, BinParameters.SNR)

L_PSF_RES_INTERP_TEST_CASE_INFO = make_test_case_info_for_bins(BASE_PSF_RES_INTERP_TEST_CASE_INFO,
                                                               l_bin_parameters=L_PSF_RES_INTERP_BIN_PARAMETERS)

NUM_PSF_RES_INTERP_TEST_CASES = len(L_PSF_RES_INTERP_TEST_CASE_INFO)

# Create a dict of the requirement info
D_L_PSF_RES_INTERP_REQUIREMENT_INFO = {}
for test_case_info in L_PSF_RES_INTERP_TEST_CASE_INFO:
    D_L_PSF_RES_INTERP_REQUIREMENT_INFO[test_case_info.name] = [PSF_RES_INTERP_CAL_REQUIREMENT_INFO,
                                                                PSF_RES_INTERP_PRD_REQUIREMENT_INFO]
