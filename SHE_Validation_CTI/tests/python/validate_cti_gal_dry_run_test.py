""" @file validate_cti_gal_dry_run_test.py

    Created 10 December 2020

    Unit tests the input/output interface of the CTI-Gal validation task.
"""

__updated__ = "2021-08-26"

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
from argparse import Namespace

import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME, TEST_DATA_LOCATION,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.pipeline_utility import ValidationConfigKeys, read_config, write_config
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS_STR
from SHE_Validation_CTI.constants.cti_gal_default_config import (D_CTI_GAL_CONFIG_CLINE_ARGS, D_CTI_GAL_CONFIG_DEFAULTS,
                                                                 D_CTI_GAL_CONFIG_TYPES, )
from SHE_Validation_CTI.constants.cti_gal_test_info import L_CTI_GAL_TEST_CASE_INFO
from SHE_Validation_CTI.results_reporting import CTI_GAL_DIRECTORY_FILENAME
from SHE_Validation_CTI.validate_cti_gal import run_validate_cti_gal_from_args

# Pipeline config filename
PIPELINE_CONFIG_FILENAME = "cti_gal_pipeline_config.xml"

# Output data filenames

SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME = "she_observation_validation_test_results.xml"
SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME = "she_exposure_validation_test_results.json"


class Args(Namespace):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    def __init__(self):
        super().__init__()
        self.vis_calibrated_frame_listfile = VIS_CALIBRATED_FRAME_LISTFILE_FILENAME
        self.mer_final_catalog_listfile = MER_FINAL_CATALOG_LISTFILE_FILENAME
        self.she_validated_measurements_product = SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME
        self.pipeline_config = None
        self.mdb = MDB_PRODUCT_FILENAME

        for test_case_info in L_CTI_GAL_TEST_CASE_INFO:
            bin_limits_cline_arg = test_case_info.bins_cline_arg
            if bin_limits_cline_arg is not None:
                setattr(self, bin_limits_cline_arg, DEFAULT_BIN_LIMITS_STR)

        self.she_observation_validation_test_results_product = SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME
        self.she_exposure_validation_test_results_listfile = SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME

        self.profile = False
        self.dry_run = True

        self.workdir = None  # Needs to be set in setup_class
        self.logdir = None  # Needs to be set in setup_class


class TestCase:
    """
    """

    workdir: str
    logdir: str
    args: Args

    @classmethod
    def setup_class(cls):

        # Download the MDB from WebDAV
        sync_mdb = DataSync("testdata/sync.conf", "testdata/test_mdb.txt")
        sync_mdb.download()

        # Download the data stack files from WebDAV
        sync_datastack = DataSync("testdata/sync.conf", "testdata/test_data_stack.txt")
        sync_datastack.download()
        qualified_vis_calibrated_frames_filename = sync_datastack.absolutePath(
            os.path.join(TEST_DATA_LOCATION, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME))
        assert os.path.isfile(
            qualified_vis_calibrated_frames_filename), f"Cannot find file: {qualified_vis_calibrated_frames_filename}"

        # Get the workdir based on where the data images listfile is
        cls.workdir = os.path.split(qualified_vis_calibrated_frames_filename)[0]
        cls.logdir = os.path.join(cls.workdir, "logs")

        # Set up the args to pass to the task
        cls.args = Args()
        cls.args.workdir = cls.workdir
        cls.args.logdir = cls.logdir

        # Write the pipeline config we'll be using
        write_config(config_dict = {ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA : 4.,
                                    ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA: 10.},
                     config_filename = PIPELINE_CONFIG_FILENAME,
                     workdir = cls.args.workdir,
                     config_keys = ValidationConfigKeys)

    @classmethod
    def teardown_class(cls):

        # Delete the pipeline config file
        os.remove(os.path.join(cls.args.workdir, PIPELINE_CONFIG_FILENAME))

    @pytest.mark.skip()
    def test_cti_gal_dry_run(self):

        # Ensure this is a dry run and set up the pipeline config with defaults
        self.args.dry_run = True
        self.args.pipeline_config = read_config(None,
                                                workdir = self.args.workdir,
                                                defaults = D_CTI_GAL_CONFIG_DEFAULTS,
                                                d_cline_args = D_CTI_GAL_CONFIG_CLINE_ARGS,
                                                parsed_args = self.args,
                                                config_keys = ValidationConfigKeys,
                                                d_types = D_CTI_GAL_CONFIG_TYPES)

        # Call to validation function
        run_validate_cti_gal_from_args(self.args)

    def test_cti_gal_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run, and use the pipeline config
        self.args.dry_run = False
        self.args.pipeline_config = read_config(PIPELINE_CONFIG_FILENAME,
                                                workdir = self.args.workdir,
                                                defaults = D_CTI_GAL_CONFIG_DEFAULTS,
                                                d_cline_args = D_CTI_GAL_CONFIG_CLINE_ARGS,
                                                parsed_args = self.args,
                                                config_keys = ValidationConfigKeys,
                                                d_types = D_CTI_GAL_CONFIG_TYPES)

        # Call to validation function
        run_validate_cti_gal_from_args(self.args)

        # Check the resulting data product and plot exist

        workdir = self.args.workdir
        output_filename = os.path.join(workdir, self.args.she_observation_validation_test_results_product)

        assert os.path.isfile(output_filename)

        p = read_xml_product(xml_filename = output_filename)

        # Find the index for the LensMC Global test case

        textfiles_tarball_filename: str = ""
        figures_tarball_filename: str = ""
        for val_test in p.Data.ValidationTestList:
            if "global-lensmc" not in val_test.TestId.lower():
                continue
            textfiles_tarball_filename = val_test.AnalysisResult.AnalysisFiles.TextFiles.FileName
            figures_tarball_filename = val_test.AnalysisResult.AnalysisFiles.Figures.FileName

        assert textfiles_tarball_filename
        assert figures_tarball_filename

        for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
            subprocess.call(f"cd {workdir} && tar xf {tarball_filename}", shell = True)

        qualified_directory_filename = os.path.join(workdir, CTI_GAL_DIRECTORY_FILENAME)
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
