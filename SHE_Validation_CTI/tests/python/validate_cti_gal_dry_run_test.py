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
from SHE_PPT.argument_parser import (CA_DRY_RUN, CA_LOGDIR, CA_MDB, CA_MER_CAT, CA_PIPELINE_CONFIG, CA_SHE_MEAS,
                                     CA_VIS_CAL_FRAME,
                                     CA_WORKDIR, )
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME, TEST_DATA_LOCATION,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory
from SHE_Validation.argument_parser import CA_SHE_EXP_TEST_RESULTS_LIST, CA_SHE_OBS_TEST_RESULTS
from SHE_Validation_CTI.ValidateCTIGal import defineSpecificProgramOptions, mainMethod
from SHE_Validation_CTI.results_reporting import CTI_GAL_DIRECTORY_FILENAME

# Output data filenames

SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME = "she_observation_validation_test_results.xml"
SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME = "she_exposure_validation_test_results.json"


def make_mock_args() -> Namespace:
    """ Get a mock argument parser we can use.
    """
    parser = defineSpecificProgramOptions()
    args = parser.parse_args([])

    setattr(args, CA_VIS_CAL_FRAME, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME)
    setattr(args, CA_MER_CAT, MER_FINAL_CATALOG_LISTFILE_FILENAME)
    setattr(args, CA_SHE_MEAS, SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME)
    setattr(args, CA_MDB, MDB_PRODUCT_FILENAME)
    setattr(args, CA_SHE_OBS_TEST_RESULTS, SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME)
    setattr(args, CA_SHE_EXP_TEST_RESULTS_LIST, SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME)

    return args


class TestCase:
    """
    """

    workdir: str
    logdir: str
    args: Namespace
    mock_pipeline_config_factory: MockPipelineConfigFactory

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
        cls.args = make_mock_args()
        setattr(cls.args, CA_WORKDIR, cls.workdir)
        setattr(cls.args, CA_LOGDIR, cls.logdir)

        # Write the pipeline config we'll be using and note its filename
        cls.mock_pipeline_config_factory = MockPipelineConfigFactory(workdir = cls.workdir)
        cls.mock_pipeline_config_factory.write(cls.workdir)
        setattr(cls.args, CA_PIPELINE_CONFIG, cls.mock_pipeline_config_factory.file_namer.filename)

    @classmethod
    def teardown_class(cls):

        # Delete the pipeline config file
        cls.mock_pipeline_config_factory.cleanup()

    @pytest.mark.skip()
    def test_cti_gal_dry_run(self):

        # Ensure this is a dry run
        setattr(self.args, CA_DRY_RUN, True)

        # Call to validation function
        mainMethod(self.args)

    def test_cti_gal_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run
        setattr(self.args, CA_DRY_RUN, False)

        # Call to validation function
        mainMethod(self.args)

        # Check the resulting data product and plot exist

        workdir = self.workdir
        output_filename = getattr(self.args, CA_SHE_OBS_TEST_RESULTS)
        qualified_output_filename = os.path.join(workdir, output_filename)

        assert os.path.isfile(qualified_output_filename)

        p = read_xml_product(xml_filename = qualified_output_filename)

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
