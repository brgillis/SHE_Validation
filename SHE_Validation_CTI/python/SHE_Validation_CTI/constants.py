""" @file constants.py

    Created 15 Dec 2020

    Constants relating to CTI-Gal validation
"""

__updated__ = "2021-01-06"

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

from collections import namedtuple

# Metadata about the requirement
CTI_GAL_REQUIREMENT_ID = "R-SHE-CAL-F-140"
CTI_GAL_REQUIREMENT_DESCRIPTION = "Residual of CTI to galaxy multiplicative bias mu <5x10-4 (1-sigma)."
CTI_GAL_PARAMETER = ("Z-value for slope of g1_image versus distance from readout register compared to expectation " +
                     "of zero.")

# Metadata about the test
CTI_GAL_TEST_ID = "T-SHE-000010-CTI-gal"
CTI_GAL_TEST_DESCRIPTION = "Linear dependence of galaxy ellipticity with read-out register distance (slope)."

# Define a namedtuple class to store id and description info for each test case
TestCaseInfo = namedtuple("TestCaseInfo", ["id", "description"])

CTI_GAL_TEST_CASE_INFO = {"Global": TestCaseInfo("T-SHE-000010-CTI-gal", "Linear dependence of residual galaxy " +
                                                 "ellipticity with read-out register distance (slope) unbinned."),
                          "SNR": TestCaseInfo("TC-SHE-100028-CTI-gal-SNR", "Linear dependence of residual galaxy " +
                                              "ellipticity with read-out register distance (slope) in bins of SNR " +
                                              "of galaxies."),
                          "BG": TestCaseInfo("TC-SHE-100029-CTI-gal-bg", "Linear dependence of residual galaxy " +
                                             "ellipticity with read-out register distance (slope) in bins of sky " +
                                             "background levels."),
                          "Colour": TestCaseInfo("TC-SHE-100030-CTI-gal-col", "Linear dependence of residual galaxy " +
                                                 "ellipticity with read-out register distance (slope) in bins of "
                                                 "colour of galaxies."),
                          "Size": TestCaseInfo("TC-SHE-100031-CTI-gal-size", "Linear dependence of residual galaxy " +
                                               "ellipticity with read-out register distance (slope) in bins of size " +
                                               "of galaxies."),
                          "Epoch": TestCaseInfo("TC-SHE-100032-CTI-gal-epoch", "Linear dependence of residual galaxy " +
                                                "ellipticity with read-out register distance (slope) in bins of " +
                                                "observation epoch"), }

CTI_GAL_TEST_CASES = CTI_GAL_TEST_CASE_INFO.keys()

NUM_CTI_GAL_TEST_CASES = len(CTI_GAL_TEST_CASES)

# Failure thresholds - these will likely be set in the configuration file in the future
SLOPE_FAIL_SIGMA = 5
INTERCEPT_FAIL_SIGMA = 5

from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf

D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS = {"KSB": ksbm_tf,
                                           "REGAUSS": regm_tf,
                                           "MomentsML": mmlm_tf,
                                           "LensMC": lmcm_tf}

METHODS = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.keys()

NUM_METHODS = len(METHODS)

NUM_METHOD_CTI_GAL_TEST_CASES = NUM_METHODS * NUM_CTI_GAL_TEST_CASES
