""" @file validate_shear_bias_dry_run_test.py

    Created 10 December 2020

    Unit tests the input/output interface of the Shear Bias validation task.
"""

__updated__ = "2021-08-11"

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
import subprocess

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        )
from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.pipeline_utility import write_config, read_config
from SHE_PPT.table_utility import SheTableFormat
from astropy.table import Table
import pytest

from SHE_Validation.constants.default_config import (ValidationConfigKeys,
                                                     ExecutionMode)
from SHE_Validation_ShearBias.constants.shear_bias_default_config import (D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                                                          D_SHEAR_BIAS_CONFIG_CLINE_ARGS, D_SHEAR_BIAS_CONFIG_TYPES)
from SHE_Validation_ShearBias.constants.shear_bias_test_info import L_SHEAR_BIAS_TEST_CASE_INFO
from SHE_Validation_ShearBias.results_reporting import SHEAR_BIAS_DIRECTORY_FILENAME
from SHE_Validation_ShearBias.validate_shear_bias import validate_shear_bias_from_args
import numpy as np

# Input data filenames
PIPELINE_CONFIG_FILENAME = "shear_bias_pipeline_config.xml"
MATCHED_CATALOG_PRODUCT_FILENAME = "shear_bias_matched_catalog.xml"
MATCHED_CATALOG_FILENAME = "data/shear_bias_matched_catalog.fits"

# Output data filename
SHE_BIAS_TEST_RESULT_FILENAME = "she_observation_validation_test_results.xml"

# Test data description

# Info about the shear estimation method and its associated tables
TEST_METHOD = ShearEstimationMethods.LENSMC
MATCHED_TF = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD]
MATCHED_INIT = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD].init_table

# Input shear info
NUM_TEST_POINTS = 1000
INPUT_G_MIN = -0.7
INPUT_G_MAX = 0.7

# Estimated shear info
EST_SEED = 6413
EST_G_ERR = 0.025
EXTRA_EST_G_ERR = 0.005
EXTRA_EST_G_ERR_ERR = 0.005
G1_M = 0.05
G1_C = -0.2
G2_M = -0.1
G2_C = 0.01


def make_mock_matched_table(tf: SheTableFormat = MATCHED_TF,
                            seed: int = EST_SEED) -> Table:
    """ Function to generate a mock matched catalog table.
    """

    # Seed the random number generator
    rng = np.random.default_rng(seed)

    # Create the table
    matched_table = tf.init_table(size=NUM_TEST_POINTS)

    # Fill in rows with input data
    matched_table[tf.tu_gamma1] = -np.linspace(INPUT_G_MIN, INPUT_G_MAX, NUM_TEST_POINTS)
    matched_table[tf.tu_gamma2] = np.linspace(INPUT_G_MAX, INPUT_G_MIN, NUM_TEST_POINTS)
    matched_table[tf.tu_kappa] = np.zeros_like(matched_table[MATCHED_TF.tu_gamma1])

    # Generate random noise for output data
    l_extra_g_err = EXTRA_EST_G_ERR + EXTRA_EST_G_ERR_ERR * rng.standard_normal(NUM_TEST_POINTS)
    l_g_err = np.sqrt(EST_G_ERR**2 + l_extra_g_err**2)
    l_g1_deviates = l_g_err * rng.standard_normal(NUM_TEST_POINTS)
    l_g2_deviates = l_g_err * rng.standard_normal(NUM_TEST_POINTS)

    # Fill in rows with mock output data
    matched_table[tf.g1] = G1_C + G1_M * matched_table[tf.tu_gamma1] + l_g1_deviates
    matched_table[tf.g2] = G2_C + G2_M * matched_table[tf.tu_gamma2] + l_g2_deviates
    matched_table[tf.g1_err] = l_g_err
    matched_table[tf.g2_err] = l_g_err
    matched_table[tf.weight] = 0.5 * l_g_err**-2

    return matched_table


class Args(object):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    def __init__(self):
        self.matched_catalog = MATCHED_CATALOG_PRODUCT_FILENAME
        self.pipeline_config = PIPELINE_CONFIG_FILENAME
        self.shear_bias_validation_test_results_product = SHE_BIAS_TEST_RESULT_FILENAME

        self.profile = False
        self.dry_run = True

        for test_case_info in L_SHEAR_BIAS_TEST_CASE_INFO:
            bin_limits_cline_arg = test_case_info.bins_cline_arg
            if bin_limits_cline_arg is not None:
                setattr(self, bin_limits_cline_arg, None)

        self.workdir = None  # Needs to be set in setup_class
        self.logdir = None  # Needs to be set in setup_class


class TestCase:
    """


    """

    @classmethod
    def setup_class(cls):
        cls.args = Args()

    @classmethod
    def teardown_class(cls):

        # Delete the pipeline config file
        if cls.args.workdir:
            os.remove(os.path.join(cls.args.workdir, PIPELINE_CONFIG_FILENAME))
            os.remove(os.path.join(cls.args.workdir, MATCHED_CATALOG_FILENAME))
            os.remove(os.path.join(cls.args.workdir, MATCHED_CATALOG_PRODUCT_FILENAME))

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok=True)

        # Set up the args to pass to the task
        self.args.workdir = self.workdir
        self.args.logdir = self.logdir

        # Write the pipeline config we'll be using
        write_config(config_dict={ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA: 4.,
                                  ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA: 10.},
                     config_filename=PIPELINE_CONFIG_FILENAME,
                     workdir=self.args.workdir,
                     config_keys=ValidationConfigKeys)

        # Write the matched catalog we'll be using and its data product
        matched_table = make_mock_matched_table()
        matched_table.write(os.path.join(self.workdir, MATCHED_CATALOG_FILENAME))

        matched_table_product = products.she_measurements.create_dpd_she_measurements()
        matched_table_product.set_method_filename(method=TEST_METHOD.value, filename=MATCHED_CATALOG_FILENAME)
        write_xml_product(matched_table_product, MATCHED_CATALOG_PRODUCT_FILENAME, workdir=self.workdir)

    def test_shear_bias_dry_run(self):

        # Ensure this is a dry run and set up the pipeline config with defaults
        self.args.dry_run = True
        self.args.pipeline_config = read_config(None,
                                                workdir=self.args.workdir,
                                                defaults=D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                                d_cline_args=D_SHEAR_BIAS_CONFIG_CLINE_ARGS,
                                                parsed_args=self.args,
                                                config_keys=ValidationConfigKeys,
                                                d_types=D_SHEAR_BIAS_CONFIG_TYPES)

        # Call to validation function
        validate_shear_bias_from_args(self.args, mode=ExecutionMode.LOCAL)

    def test_shear_bias_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run, and use the pipeline config
        self.args.dry_run = False
        self.args.pipeline_config = read_config(PIPELINE_CONFIG_FILENAME,
                                                workdir=self.args.workdir,
                                                defaults=D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                                d_cline_args=D_SHEAR_BIAS_CONFIG_CLINE_ARGS,
                                                parsed_args=self.args,
                                                config_keys=ValidationConfigKeys,
                                                d_types=D_SHEAR_BIAS_CONFIG_TYPES)

        # Call to validation function
        validate_shear_bias_from_args(self.args, mode=ExecutionMode.LOCAL)

        # Check the resulting data product and plot exist

        workdir = self.args.workdir
        output_filename = os.path.join(workdir, self.args.shear_bias_validation_test_results_product)

        assert os.path.isfile(output_filename)

        p = read_xml_product(xml_filename=output_filename)

        test_list = p.Data.ValidationTestList
        plot_filename = None

        for test in test_list:

            if not test.AnalysisResult.AnalysisFiles.TextFiles or not test.AnalysisResult.AnalysisFiles.Figures:
                continue

            textfiles_tarball_filename = test.AnalysisResult.AnalysisFiles.TextFiles.FileName
            figures_tarball_filename = test.AnalysisResult.AnalysisFiles.Figures.FileName

            for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
                subprocess.call(f"cd {workdir} && tar xf {tarball_filename}", shell=True)

            qualified_directory_filename = os.path.join(workdir, SHEAR_BIAS_DIRECTORY_FILENAME)
            with open(qualified_directory_filename, "r") as fi:
                for line in fi:
                    if line[0] == "#":
                        continue
                    key, value = line.strip().split(": ")
                    if key == "LensMC-global-g1":
                        plot_filename = value

        assert plot_filename is not None
        assert os.path.isfile(os.path.join(workdir, plot_filename))
