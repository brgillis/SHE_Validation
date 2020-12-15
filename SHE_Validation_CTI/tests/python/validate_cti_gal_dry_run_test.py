""" @file validate_cti_gal_dry_run_test.py

    Created 10 December 2020

    Unit tests the input/output interface of the CTI-Gal validation task.
"""

__updated__ = "2020-12-15"

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


test_data_location = "SHE_PPT_8_5"

# Input data filenames

vis_calibrated_frames_filename = "vis_calibrated_frames.json"
mer_final_catalogs_filename = "mer_final_catalogs.json"
she_validated_measurements_filename = "she_validated_measurements.xml"
mdb_filename = "sample_mdb-SC8.xml"

# Output data filenames

she_observation_validation_test_results_filename = "she_observation_validation_test_results.xml"
she_exposure_validation_test_results_filename = "she_exposure_validation_test_results.json"


class Args(object):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    def __init__(self):
        self.vis_calibrated_frame_listfile = vis_calibrated_frames_filename
        self.mer_final_catalog_listfile = mer_final_catalogs_filename
        self.she_validated_measurements_product = she_validated_measurements_filename
        self.pipeline_config = None
        self.mdb = mdb_filename

        self.she_observation_validation_test_results_product = she_observation_validation_test_results_filename
        self.she_exposure_validation_test_results_listfile = she_exposure_validation_test_results_filename

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
            os.path.join(test_data_location, vis_calibrated_frames_filename))
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

        # Call to validation function
        run_validate_cti_gal_from_args(self.args)

        # TODO: Check output

        return
