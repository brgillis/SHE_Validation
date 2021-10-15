""" @file mock_pipeline_config.py

    Created 5 October 2021.

    Utilities to generate mock data for shear bias validation unit tests.
"""

__updated__ = "2021-10-05"

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

import os
from argparse import Namespace
from typing import Dict, List, Optional

import numpy as np
from astropy.table import Table
from dataclasses import dataclass

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import write_xml_product
from SHE_PPT.logging import getLogger
from SHE_Validation.constants.default_config import (DEFAULT_BIN_LIMITS)
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation_ShearBias.constants.shear_bias_test_info import FULL_L_SHEAR_BIAS_TEST_CASE_M_INFO

logger = getLogger(__name__)

# Input data filenames
PIPELINE_CONFIG_FILENAME = "shear_bias_pipeline_config.xml"
MATCHED_CATALOG_PRODUCT_FILENAME = "shear_bias_matched_catalog.xml"
LENSMC_MATCHED_CATALOG_FILENAME = "data/lensmc_shear_bias_matched_catalog.fits"
KSB_MATCHED_CATALOG_FILENAME = "data/ksb_bias_matched_catalog.fits"

# Output data filename
SHE_BIAS_TEST_RESULT_FILENAME = "she_observation_validation_test_results.xml"

# Test data description

# Info about the shear estimation methods and associated tables
TEST_METHOD_GLOBAL = ShearEstimationMethods.LENSMC
TEST_METHOD_SNR = ShearEstimationMethods.KSB
MATCHED_TF_GLOBAL = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD_GLOBAL]
MATCHED_TF_SNR = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD_SNR]

TEST_METHODS = (ShearEstimationMethods.LENSMC, ShearEstimationMethods.KSB)
TEST_BIN_PARAMETERS = (BinParameters.GLOBAL, BinParameters.SNR)

# General info about the data
NUM_GOOD_TEST_POINTS = 32
NUM_NAN_TEST_POINTS = 2
NUM_ZERO_WEIGHT_TEST_POINTS = 1
NUM_TEST_POINTS = NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS + NUM_ZERO_WEIGHT_TEST_POINTS

# Input shear info
INPUT_G_MIN = -0.7
INPUT_G_MAX = 0.7

# Estimated shear info
EST_SEED = 6413
EST_G_ERR = 0.025
EXTRA_EST_G_ERR = 0.005
EXTRA_EST_G_ERR_ERR = 0.005

# Fail sigma values
LOCAL_FAIL_SIGMA = 4
GLOBAL_FAIL_SIGMA = 10

INPUT_BIAS: Dict[ShearEstimationMethods, Dict[BinParameters, List[Dict[str, float]]]] = {
    ShearEstimationMethods.LENSMC: {BinParameters.GLOBAL: [{"m1"    : 0.05,
                                                            "m1_err": 0.015,
                                                            "c1"    : -0.2,
                                                            "c1_err": 0.05,
                                                            "m2"    : -0.1,
                                                            "m2_err": 0.04,
                                                            "c2"    : 0.01,
                                                            "c2_err": 0.003, }]},
    ShearEstimationMethods.KSB   : {BinParameters.SNR: [{"m1"    : 0.2,
                                                         "m1_err": 0.003,
                                                         "c1"    : -0.3,
                                                         "c1_err": 0.03,
                                                         "m2"    : 0.1,
                                                         "m2_err": 0.21,
                                                         "c2"    : -0.4,
                                                         "c2_err": 0.43, },
                                                        {"m1"    : -0.3,
                                                         "m1_err": 0.031,
                                                         "c1"    : -0.5,
                                                         "c1_err": 0.05,
                                                         "m2"    : 0.35,
                                                         "m2_err": 0.15,
                                                         "c2"    : 0.,
                                                         "c2_err": 0.1,
                                                         }]}}


def make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                            seed: int = EST_SEED, ) -> Table:
    """ Function to generate a mock matched catalog table.
    """

    tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]
    d_l_input_bias = INPUT_BIAS[method]

    # Seed the random number generator
    rng = np.random.default_rng(seed)

    # Create the table
    matched_table = tf.init_table(size = NUM_TEST_POINTS)

    indices = np.indices((NUM_TEST_POINTS,), dtype = int, )[0]
    zeros = np.zeros(NUM_TEST_POINTS, dtype = '>f4')
    ones = np.ones(NUM_TEST_POINTS, dtype = '>f4')

    matched_table[tf.ID] = indices

    # Fill in input data
    matched_table[tf.tu_gamma1] = -np.linspace(INPUT_G_MIN, INPUT_G_MAX, NUM_TEST_POINTS)
    matched_table[tf.tu_gamma2] = np.linspace(INPUT_G_MAX, INPUT_G_MIN, NUM_TEST_POINTS)
    matched_table[tf.tu_kappa] = np.zeros_like(matched_table[tf.tu_gamma1])

    # Fill in data for bin parameter info, with different bins for each parameter

    i: int
    bin_parameter: BinParameters
    for i, bin_parameter in enumerate(BinParameters):
        if bin_parameter == BinParameters.GLOBAL:
            continue
        factor = 2 ** i
        matched_table[bin_parameter.name] = np.where(indices % factor < factor / 2, ones, zeros)

    # Generate random noise for output data
    l_extra_g_err = EXTRA_EST_G_ERR + EXTRA_EST_G_ERR_ERR * rng.standard_normal(NUM_TEST_POINTS)
    l_g_err = np.sqrt(EST_G_ERR ** 2 + l_extra_g_err ** 2)
    l_g1_deviates = l_g_err * rng.standard_normal(NUM_TEST_POINTS)
    l_g2_deviates = l_g_err * rng.standard_normal(NUM_TEST_POINTS)

    # Save the error in the table
    matched_table[tf.g1_err] = l_g_err
    matched_table[tf.g2_err] = l_g_err
    matched_table[tf.weight] = 0.5 * l_g_err ** -2

    # Fill in rows with mock output data - this bit depends on which method we're using
    if method == ShearEstimationMethods.LENSMC:
        bias_0m2 = d_l_input_bias[BinParameters.GLOBAL][0]
        bias_1m2 = d_l_input_bias[BinParameters.GLOBAL][0]
    else:
        bias_0m2 = d_l_input_bias[BinParameters.SNR][0]
        bias_1m2 = d_l_input_bias[BinParameters.SNR][1]

    g1_0m2 = bias_0m2["c1"] + (1 + bias_0m2["m1"]) * -matched_table[tf.tu_gamma1] + l_g1_deviates
    g1_1m2 = bias_1m2["c1"] + (1 + bias_1m2["m1"]) * -matched_table[tf.tu_gamma1] + l_g1_deviates

    g2_0m2 = bias_0m2["c2"] + (1 + bias_0m2["m2"]) * matched_table[tf.tu_gamma1] + l_g2_deviates
    g2_1m2 = bias_1m2["c2"] + (1 + bias_1m2["m2"]) * matched_table[tf.tu_gamma1] + l_g2_deviates

    # Add to table, flipping g1 due to SIM's format
    matched_table[tf.g1] = np.where(indices % 2 < 1, g1_0m2, g1_1m2)
    matched_table[tf.g2] = np.where(indices % 2 < 1, g2_0m2, g2_1m2)

    # Flag the last bit of data as bad or zero weight
    matched_table[tf.g1][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:-NUM_ZERO_WEIGHT_TEST_POINTS] = np.NaN
    matched_table[tf.g1_err][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:] = np.NaN
    matched_table[tf.g2][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:-NUM_ZERO_WEIGHT_TEST_POINTS] = np.NaN
    matched_table[tf.g2_err][-NUM_NAN_TEST_POINTS - NUM_ZERO_WEIGHT_TEST_POINTS:] = np.NaN

    matched_table[tf.g1_err][-NUM_ZERO_WEIGHT_TEST_POINTS:] = np.inf
    matched_table[tf.g2_err][-NUM_ZERO_WEIGHT_TEST_POINTS:] = np.inf
    matched_table[tf.weight][-NUM_ZERO_WEIGHT_TEST_POINTS:] = 0

    # Set the fit flags
    matched_table[tf.fit_flags] = np.where(indices < NUM_GOOD_TEST_POINTS, 0,
                                           np.where(indices < NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS, 1, 0))

    return matched_table


def write_mock_matched_tables(workdir: str) -> str:
    """ Returns filename of the matched table product.
    """

    lensmc_matched_table = make_mock_matched_table(method = ShearEstimationMethods.LENSMC,
                                                   seed = EST_SEED)
    ksb_matched_table = make_mock_matched_table(method = ShearEstimationMethods.KSB,
                                                seed = EST_SEED + 1)

    lensmc_matched_table.write(os.path.join(workdir, LENSMC_MATCHED_CATALOG_FILENAME))
    ksb_matched_table.write(os.path.join(workdir, KSB_MATCHED_CATALOG_FILENAME))

    # Set up and write the data product
    matched_table_product = products.she_validated_measurements.create_dpd_she_validated_measurements()
    matched_table_product.set_LensMC_filename(LENSMC_MATCHED_CATALOG_FILENAME)
    matched_table_product.set_KSB_filename(KSB_MATCHED_CATALOG_FILENAME)

    write_xml_product(matched_table_product, MATCHED_CATALOG_PRODUCT_FILENAME, workdir = workdir)

    return MATCHED_CATALOG_PRODUCT_FILENAME


def cleanup_mock_matched_tables(workdir: str):
    """TODO: Add a docstring to this class."""

    os.remove(os.path.join(workdir, LENSMC_MATCHED_CATALOG_FILENAME))
    os.remove(os.path.join(workdir, KSB_MATCHED_CATALOG_FILENAME))
    os.remove(os.path.join(workdir, MATCHED_CATALOG_PRODUCT_FILENAME))


def make_mock_bin_limits() -> Dict[BinParameters, np.ndarray]:
    """TODO: Add a docstring to this class."""

    d_l_bin_limits: Dict[BinParameters, np.ndarray] = {}
    for bin_parameter in BinParameters:
        if bin_parameter == BinParameters.SNR:
            d_l_bin_limits[bin_parameter] = np.array([-0.5, 0.5, 1.5])
        else:
            d_l_bin_limits[bin_parameter] = np.array(DEFAULT_BIN_LIMITS)

    return d_l_bin_limits


@dataclass
class MockShearBiasArgs(Namespace):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    # Workdir and logdir need to be set in setup_class
    workdir: Optional[str] = None
    logdir: Optional[str] = None

    bootstrap_errors: Optional[bool] = None
    max_g_in: Optional[float] = None
    require_fitclass_zero: Optional[bool] = None

    matched_catalog: str = MATCHED_CATALOG_PRODUCT_FILENAME
    pipeline_config: str = PIPELINE_CONFIG_FILENAME
    shear_bias_validation_test_results_product: str = SHE_BIAS_TEST_RESULT_FILENAME

    profile: bool = False
    dry_run: bool = True

    def __post_init__(self):

        for test_case_info in FULL_L_SHEAR_BIAS_TEST_CASE_M_INFO:
            bin_limits_cline_arg = test_case_info.bins_cline_arg
            if bin_limits_cline_arg is not None:
                setattr(self, bin_limits_cline_arg, None)
