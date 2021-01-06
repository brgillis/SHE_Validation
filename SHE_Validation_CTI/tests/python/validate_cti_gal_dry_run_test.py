""" @file validate_cti_gal_dry_run_test.py

    Created 10 December 2020

    Unit tests the input/output interface of the CTI-Gal validation task.
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

import os
import time

import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT.file_io import read_xml_product, find_file, read_listfile
from SHE_PPT.logging import getLogger
from SHE_Validation_CTI.validate_cti_gal import run_validate_cti_gal_from_args
import numpy as np


TEST_DATA_LOCATION = "SHE_PPT_8_5"

# Input data filenames

VIS_CALIBRATED_FRAME_LISTFILE_FILENAME = "vis_calibrated_frames.json"
MER_FINAL_CATALOG_LISTFILE_FILENAME = "mer_final_catalogs.json"
SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME = "she_validated_measurements.xml"
MDB_FILENAME = "sample_mdb-SC8.xml"

# Output data filenames

SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME = "she_observation_validation_test_results.xml"
SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME = "she_exposure_validation_test_results.json"


class Args(object):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    def __init__(self):
        self.vis_calibrated_frame_listfile = VIS_CALIBRATED_FRAME_LISTFILE_FILENAME
        self.mer_final_catalog_listfile = MER_FINAL_CATALOG_LISTFILE_FILENAME
        self.she_validated_measurements_product = SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME
        self.pipeline_config = None
        self.mdb = MDB_FILENAME

        self.she_observation_validation_test_results_product = SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME
        self.she_exposure_validation_test_results_listfile = SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME

        self.profile = False
        self.dry_run = True

        self.workdir = None  # Needs to be set in setup_class
        self.logdir = None  # Needs to be set in setup_class


class TestCase:
    """


    """

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

        return

    @classmethod
    def teardown_class(cls):

        return

    def test_cti_gal_dry_run(self):

        # Ensure this is a dry run
        self.args.dry_run = True

        # Call to validation function
        run_validate_cti_gal_from_args(self.args)

        return

    def test_cti_gal_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run
        self.args.dry_run = False

        # Call to validation function
        run_validate_cti_gal_from_args(self.args)

        return
