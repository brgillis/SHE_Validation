"""
:file: tests/python/cti_gal_integration_test.py

:date: 10 December 2020
:author: Bryan Gillis

Unit tests the input/output interface of the CTI-Gal validation task
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

import os
import subprocess
from argparse import Namespace
from typing import List, Optional

import pytest

from SHE_PPT.argument_parser import (CA_DRY_RUN, CA_MDB, CA_SHE_MEAS,
                                     CA_VIS_CAL_FRAME,
                                     )
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, SHE_EXTENDED_CATALOG_PRODUCT_FILENAME,
                                         SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.file_io import DATA_SUBDIR, read_xml_product
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.argument_parser import CA_SHE_EXP_TEST_RESULTS_LIST, CA_SHE_EXT_CAT, CA_SHE_OBS_TEST_RESULTS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation.testing.utility import SheValTestCase
from SHE_Validation_CTI.ValidateCTIGal import defineSpecificProgramOptions, mainMethod
from SHE_Validation_CTI.results_reporting import CtiTest, D_CTI_DIRECTORY_FILENAMES

CTI_GAL_DIRECTORY_FILENAME = D_CTI_DIRECTORY_FILENAMES[CtiTest.GAL]

# Output data filenames

SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME = "she_observation_validation_test_results.xml"
SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME = "she_exposure_validation_test_results.json"

EX_NUM_EXPOSURES = 4


class TestCtiGalRun(SheValTestCase):
    """ Test case for CTI-Gal validation test code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> Namespace:
        """ Get a mock argument parser we can use.

            This overrides the _make_mock_args() method of the SheTestCase class, which is called by the
            self.args property, setting the cached value self._args = self._make_mock_args() if self._args
            is None (which it will be when the object is initialized). This means that in each test case,
            self.args will return the result of this method (cached so that it only runs once).
        """
        parser = defineSpecificProgramOptions()
        args = parser.parse_args([])

        setattr(args, CA_VIS_CAL_FRAME, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME)
        setattr(args, CA_SHE_EXT_CAT, SHE_EXTENDED_CATALOG_PRODUCT_FILENAME)
        setattr(args, CA_SHE_MEAS, SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME)
        setattr(args, CA_MDB, MDB_PRODUCT_FILENAME)
        setattr(args, CA_SHE_OBS_TEST_RESULTS, SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME)
        setattr(args, CA_SHE_EXP_TEST_RESULTS_LIST, SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME)

        # The pipeline_config attribute of args isn't set here. This is because when parser.parse_args() is
        # called, it sets it to the default value of None. For the case of the pipeline_config, this is a
        # valid value, which will result in all defaults for configurable parameters being used.

        return args

    def setup_workdir(self):
        """ Override parent setup, downloading data to work with here.
        """

        self._download_mdb()
        self._download_datastack(read_in=False)

    @pytest.mark.skip()
    def test_cti_gal_dry_run(self, local_setup):

        # Ensure this is a dry run
        setattr(self.args, CA_DRY_RUN, True)

        # Call to validation function
        mainMethod(self.args)

    def test_cti_gal_integration(self, local_setup):
        """ "Integration" test of the full executable, using the unit-testing framework so it can be run automatically.
        """

        # Ensure this is not a dry run
        setattr(self.args, CA_DRY_RUN, False)

        # Call to validation function, which was imported directly from the entry-point file
        mainMethod(self.args)

        # Check the resulting data product and plots exist in the expected locations

        workdir = self.workdir
        output_filename = getattr(self.args, CA_SHE_OBS_TEST_RESULTS)
        qualified_output_filename = os.path.join(workdir, output_filename)

        assert os.path.isfile(qualified_output_filename)

        self._check_ana_files()

        p = read_xml_product(xml_filename=qualified_output_filename)

        # Find the index for the LensMC Tot test case. We'll check that for the presence of expected output data

        textfiles_tarball_filename: str = ""
        figures_tarball_filename: str = ""
        for val_test in p.Data.ValidationTestList:
            if "tot-lensmc" not in val_test.TestId.lower():
                continue
            textfiles_tarball_filename = val_test.AnalysisResult.AnalysisFiles.TextFiles.FileName
            figures_tarball_filename = val_test.AnalysisResult.AnalysisFiles.Figures.FileName

        assert textfiles_tarball_filename
        assert figures_tarball_filename

        # Unpack the tarballs containing both the textfiles and the figures
        for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
            subprocess.call(f"cd {workdir} && tar xf {DATA_SUBDIR}/{tarball_filename}", shell=True)

        # The "directory" file, which is contained in the textfiles tarball, is a file with a predefined name,
        # containing with in the filenames of all other files which were tarred up. We open this first, and use
        # it to guide us on the filenames of other files that were tarred up, and test for their existence.

        qualified_directory_filename = os.path.join(workdir, CTI_GAL_DIRECTORY_FILENAME)

        # Search for the line in the directory file which contains the plot for the LensMC-tot test, for bin 0
        obs_plot_filename = None
        l_exp_plot_filenames: List[Optional[str]] = [None] * EX_NUM_EXPOSURES

        # Search for the line in the directory file which contails the plot for the LensMC-tot test, for bin 0
        with open(qualified_directory_filename, "r") as fi:
            for line in fi:
                if line[0] == "#":
                    continue
                key, value = line.strip().split(": ")
                if key == "LensMC-tot-0":
                    obs_plot_filename = value
                else:
                    for exp_index in range(4):
                        if key == f"LensMC-{exp_index}-tot-0":
                            l_exp_plot_filenames[exp_index] = value

        # Check that we found the filenames for the plots and they all exist
        assert obs_plot_filename is not None
        assert os.path.isfile(os.path.join(workdir, obs_plot_filename))
