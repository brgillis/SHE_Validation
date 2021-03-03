""" @file cti_gal_default_config.py

    Created 15 Dec 2020

    Default configuration values, for if nothing is passed at command-line or in the pipeline config
"""
from collections import namedtuple

from SHE_PPT.constants.shear_estimation_methods import NUM_METHODS as NUM_SHEAR_ESTIMATION_METHODS
from SHE_PPT.pipeline_utility import AnalysisConfigKeys

from SHE_Validation_CTI.constants.cti_gal_default_config import BACKGROUND_LEVEL_UNITS,\
    COLOUR_DEFINITION, SIZE_DEFINITION


__updated__ = "2021-03-03"

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


# Metadata about the requirement
CTI_GAL_REQUIREMENT_ID = "R-SHE-CAL-F-140"
CTI_GAL_REQUIREMENT_DESCRIPTION = "Residual of CTI to galaxy multiplicative bias mu <5x10-4 (1-sigma)."
CTI_GAL_PARAMETER = ("Z-value for slope of g1_image versus distance from readout register compared to expectation " +
                     "of zero.")

# Metadata about the test
CTI_GAL_TEST_ID = "T-SHE-000010-CTI-gal"
CTI_GAL_TEST_DESCRIPTION = "Linear dependence of galaxy ellipticity with read-out register distance (slope)."

# Define a namedtuple class to store id and description info for each test case
TestCaseInfo = namedtuple("TestCaseInfo", ["id",
                                           "description",
                                           "bins_cline_arg",
                                           "bins_config_key",
                                           "name",
                                           "comment"])

CTI_GAL_TEST_CASE_GLOBAL = "Global"
CTI_GAL_TEST_CASE_SNR = "SNR"
CTI_GAL_TEST_CASE_BG = "Background level"
CTI_GAL_TEST_CASE_COLOUR = "Colour"
CTI_GAL_TEST_CASE_SIZE = "Size"
CTI_GAL_TEST_CASE_EPOCH = "Epoch"

D_CTI_GAL_TEST_CASE_INFO = {CTI_GAL_TEST_CASE_GLOBAL: TestCaseInfo("T-SHE-000010-CTI-gal",
                                                                   ("Linear dependence of " +
                                                                    "residual galaxy ellipticity with read-out " +
                                                                    "register distance (slope) unbinned."),
                                                                   None,
                                                                   None,
                                                                   "global",
                                                                   None,),
                            CTI_GAL_TEST_CASE_SNR: TestCaseInfo("TC-SHE-100028-CTI-gal-SNR",
                                                                ("Linear dependence of " +
                                                                 "residual galaxy ellipticity with read-out register " +
                                                                 "distance (slope) in bins of SNR of galaxies."),
                                                                "snr_bin_limits",
                                                                AnalysisConfigKeys.CGV_SNR_BIN_LIMITS.value,
                                                                "snr",
                                                                None,),
                            CTI_GAL_TEST_CASE_BG: TestCaseInfo("TC-SHE-100029-CTI-gal-bg",
                                                               ("Linear dependence of residual galaxy ellipticity " +
                                                                "with read-out register distance (slope) in bins of " +
                                                                "sky background levels."),
                                                               "bg_bin_limits",
                                                               AnalysisConfigKeys.CGV_BG_BIN_LIMITS.value,
                                                               "bg",
                                                               BACKGROUND_LEVEL_UNITS),
                            CTI_GAL_TEST_CASE_COLOUR: TestCaseInfo("TC-SHE-100030-CTI-gal-col",
                                                                   ("Linear dependence of residual galaxy " +
                                                                    "ellipticity with read-out register distance " +
                                                                    "(slope) in bins of colour of galaxies."),
                                                                   "colour_bin_limits",
                                                                   AnalysisConfigKeys.CGV_COLOUR_BIN_LIMITS.value,
                                                                   "colour",
                                                                   COLOUR_DEFINITION),
                            CTI_GAL_TEST_CASE_SIZE: TestCaseInfo("TC-SHE-100031-CTI-gal-size",
                                                                 ("Linear dependence of residual galaxy ellipticity " +
                                                                  "with read-out register distance (slope) in bins " +
                                                                  "of size of galaxies."),
                                                                 "size_bin_limits",
                                                                 AnalysisConfigKeys.CGV_SIZE_BIN_LIMITS.value,
                                                                 "size",
                                                                 SIZE_DEFINITION),
                            CTI_GAL_TEST_CASE_EPOCH: TestCaseInfo("TC-SHE-100032-CTI-gal-epoch",
                                                                  ("Linear dependence of residual galaxy " +
                                                                   "ellipticity with read-out register distance " +
                                                                   "(slope) in bins of observation epoch"),
                                                                  None,
                                                                  None,
                                                                  "epoch",
                                                                  None), }

CTI_GAL_TEST_CASES = D_CTI_GAL_TEST_CASE_INFO.keys()

NUM_CTI_GAL_TEST_CASES = len(CTI_GAL_TEST_CASES)

NUM_METHOD_CTI_GAL_TEST_CASES = NUM_SHEAR_ESTIMATION_METHODS * NUM_CTI_GAL_TEST_CASES
