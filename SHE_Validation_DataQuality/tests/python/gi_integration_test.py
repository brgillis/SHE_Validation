"""
:file: tests/python/gi_integration_test.py

:date: 09/26/22
:author: Bryan Gillis

Integration test of the GalInfo validation test
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

from SHE_PPT.constants.misc import DATA_SUBDIR
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.testing.mock_measurements_cat import EST_TABLE_PRODUCT_FILENAME
from SHE_PPT.testing.mock_mer_final_cat import MFC_TABLE_PRODUCT_FILENAME
from SHE_Validation.argument_parser import CA_MER_CAT_PROD, CA_SHE_CAT, CA_SHE_CHAINS, CA_SHE_TEST_RESULTS
from SHE_Validation.testing.mock_data import (SHE_CHAINS_PRODUCT_FILENAME,
                                              SHE_TEST_RESULTS_PRODUCT_FILENAME, )
from SHE_Validation_DataQuality.ValidateGalInfo import defineSpecificProgramOptions, mainMethod
from SHE_Validation_DataQuality.gi_data_processing import CHAINS_ATTR, MEAS_ATTR
from SHE_Validation_DataQuality.gi_results_reporting import GID_DIRECTORY_FILENAME
from SHE_Validation_DataQuality.testing.utility import SheDQTestCase


class TestGalInfoRun(SheDQTestCase):
    """Test case for GalInfo validation test integration tests.
    """

    def _make_mock_args(self) -> Namespace:
        """ Get a mock argument parser we can use.

            This overrides the _make_mock_args() method of the SheTestCase class, which is called by the
            self.args property, setting the cached value self._args = self._make_mock_args() if self._args
            is None (which it will be when the object is initialized). This means that in each test case,
            self.args will return the result of this method (cached so that it only runs once).
        """
        parser = defineSpecificProgramOptions()
        args = parser.parse_args([])

        setattr(args, CA_SHE_CAT, EST_TABLE_PRODUCT_FILENAME)
        setattr(args, CA_SHE_CHAINS, SHE_CHAINS_PRODUCT_FILENAME)
        setattr(args, CA_MER_CAT_PROD, MFC_TABLE_PRODUCT_FILENAME)
        setattr(args, CA_SHE_TEST_RESULTS, SHE_TEST_RESULTS_PRODUCT_FILENAME)

        # The pipeline_config attribute of args isn't set here. This is because when parser.parse_args() is
        # called, it sets it to the default value of None. For the case of the pipeline_config, this is a
        # valid value, which will result in all defaults for configurable parameters being used.

        return args

    def post_setup(self):
        """ Override parent setup, creating data to work with in the workdir
        """

        # Create mock products and data to test
        self.make_gal_info_input_files()

    def test_gal_info_run(self, local_setup):
        """Test that the program runs without raising any uncaught exceptions.
        """

        # Call the mainMethod, to ensure we're testing the full executable
        mainMethod(self.args)

        # Check that the expected output has been created

        # Check the data product exists
        qualified_test_results_filename = os.path.join(self.workdir, self.d_args[CA_SHE_TEST_RESULTS])
        assert os.path.isfile(qualified_test_results_filename)

        directory_filename = GID_DIRECTORY_FILENAME
        test_id_substring = "info-out-lensmc"
        l_ex_keys = [MEAS_ATTR, CHAINS_ATTR]

        # Parse the data product to find the output textfiles tarball for the desired test case, and check that it
        # exists

        p = read_xml_product(xml_filename=qualified_test_results_filename)

        textfiles_tarball_filename: str = ""
        figures_tarball_filename: str = ""
        for val_test in p.Data.ValidationTestList:
            if test_id_substring not in val_test.TestId.lower():
                continue
            textfiles_tarball_filename = os.path.join(DATA_SUBDIR,
                                                      val_test.AnalysisResult.AnalysisFiles.TextFiles.FileName)
            figures_tarball_filename = os.path.join(DATA_SUBDIR,
                                                    val_test.AnalysisResult.AnalysisFiles.Figures.FileName)

        # Unpack the tarballs containing both the textfiles and the figures
        for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
            assert tarball_filename
            assert os.path.exists(os.path.join(self.workdir, tarball_filename))
            subprocess.call(f"cd {self.workdir} && tar xf {tarball_filename}", shell=True)

        # The "directory" file, which is contained in the textfiles tarball, is a file with a predefined name,
        # containing with in the filenames of all other files which were tarred up. We open this first, and use
        # it to guide us on the filenames of other files that were tarred up, and test for their existence.

        qualified_directory_filename = os.path.join(self.workdir, directory_filename)

        # Search for the line in the directory file which contains the plot for the desired test
        d_ana_filenames = {}

        # Search for the line in the directory file which contails the plot for the LensMC-tot test, for bin 0
        with open(qualified_directory_filename, "r") as fi:
            for line in fi:
                if line[0] == "#":
                    continue
                key, value = line.strip().split(": ")
                if key in l_ex_keys:
                    d_ana_filenames[key] = value

        # Check that we found the filenames for the plots and that they all exist
        for key in l_ex_keys:
            ana_filename = d_ana_filenames.get(key)
            assert ana_filename is not None
            assert os.path.isfile(os.path.join(self.workdir, ana_filename))
