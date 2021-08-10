""" @file validate_shear_bias_dry_run_test.py

    Created 10 December 2020

    Unit tests the input/output interface of the Shear Bias validation task.
"""

__updated__ = "2021-08-10"

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

from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods,
                                                        D_MATCHED_CATALOG_TABLE_FORMATS,
                                                        D_MATCHED_CATALOG_TABLE_INITIALISERS)
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.pipeline_utility import write_config
from astropy.table import Table
import pytest

from SHE_Validation.constants.default_config import (ValidationConfigKeys,
                                                     ExecutionMode)
from SHE_Validation_ShearBias.results_reporting import SHEAR_BIAS_DIRECTORY_FILENAME
from SHE_Validation_ShearBias.validate_shear_bias import validate_shear_bias_from_args


# Pipeline config filename
PIPELINE_CONFIG_FILENAME = "shear_bias_pipeline_config.xml"
MATCHED_CATALOG_FILENAME = "shear_bias_matched_catalog.xml"

# Output data filenames
SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME = "she_observation_validation_test_results.xml"
SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME = "she_exposure_validation_test_results.json"

# Test data description

# Info about the shear estimation method and its associated tables
TEST_METHOD = ShearEstimationMethods.LENSMC
MATCHED_TF = D_MATCHED_CATALOG_TABLE_FORMATS[TEST_METHOD]
MATCHED_INIT = D_MATCHED_CATALOG_TABLE_INITIALISERS[TEST_METHOD]

# Input shear info
INPUT_SEED = 124515
NUM_TEST_POINTS = 1000
INPUT_G_MIN = -0.9
INPUT_G_MAX = 0.9

# Estimated shear info
EST_SEED = 6413
EST_G_ERR = 0.25
EXTRA_EST_G_ERR = 0.05
EXTRA_EST_G_ERR_ERR = 0.05
G1_M = 0.05
G1_C = -0.2
G2_M = -0.1
G2_C = 0.01


def make_mock_matched_table() -> Table:
    """ Function to generate a mock matched catalog table.
    """
    # TODO: Fill in
    pass


class Args(object):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    def __init__(self):
        self.matched_catalog = None
        self.pipeline_config = None
        self.shear_bias_validation_test_results_product = None

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
        return

    @classmethod
    def teardown_class(cls):

        # Delete the pipeline config file
        os.remove(os.path.join(cls.args.workdir, PIPELINE_CONFIG_FILENAME))
        os.remove(os.path.join(cls.args.workdir, MATCHED_CATALOG_FILENAME))

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok=True)

        # Set up the args to pass to the task
        self.args = Args()
        self.args.workdir = self.workdir
        self.args.logdir = self.logdir

        # Write the pipeline config we'll be using
        write_config(config_dict={ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA: 4.,
                                  ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA: 10.},
                     config_filename=PIPELINE_CONFIG_FILENAME,
                     workdir=self.args.workdir,
                     config_keys=ValidationConfigKeys)

    def test_shear_bias_dry_run(self):

        # Ensure this is a dry run
        self.args.dry_run = True
        self.args.pipeline_config = None

        # Call to validation function
        validate_shear_bias_from_args(self.args, mode=ExecutionMode.LOCAL)

    def test_shear_bias_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run, and use the pipeline config
        self.args.dry_run = False
        self.args.pipeline_config = PIPELINE_CONFIG_FILENAME

        # Call to validation function
        validate_shear_bias_from_args(self.args)

        # Check the resulting data product and plot exist

        workdir = self.args.workdir
        output_filename = os.path.join(workdir, self.args.she_observation_validation_test_results_product)

        assert os.path.isfile(output_filename)

        p = read_xml_product(xml_filename=output_filename)

        textfiles_tarball_filename = p.Data.ValidationTestList[0].AnalysisResult.AnalysisFiles.TextFiles.FileName
        figures_tarball_filename = p.Data.ValidationTestList[0].AnalysisResult.AnalysisFiles.Figures.FileName

        for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
            subprocess.call(f"cd {workdir} && tar xf {tarball_filename}", shell=True)

        qualified_directory_filename = os.path.join(workdir, SHEAR_BIAS_DIRECTORY_FILENAME)
        plot_filename = None
        with open(qualified_directory_filename, "r") as fi:
            for line in fi:
                if line[0] == "#":
                    continue
                key, value = line.strip().split(": ")
                if key == "LensMC-global-0":
                    plot_filename = value

        assert plot_filename is not None
        assert os.path.isfile(os.path.join(workdir, plot_filename))
