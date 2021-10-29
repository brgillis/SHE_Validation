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

import pytest

from SHE_PPT.argument_parser import (CA_DRY_RUN, CA_MDB, CA_MER_CAT, CA_SHE_MEAS,
                                     CA_VIS_CAL_FRAME,
                                     )
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.argument_parser import CA_SHE_EXP_TEST_RESULTS_LIST, CA_SHE_OBS_TEST_RESULTS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_CTI.ValidateCTIGal import defineSpecificProgramOptions, mainMethod
from SHE_Validation_CTI.results_reporting import CTI_GAL_DIRECTORY_FILENAME

# Output data filenames

SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME = "she_observation_validation_test_results.xml"
SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME = "she_exposure_validation_test_results.json"


class CtiGalTestCase(SheTestCase):
    """ Test case for CTI-Gal validation test code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> None:
        """ Get a mock argument parser we can use.
        """
        parser = defineSpecificProgramOptions()
        self.args = parser.parse_args([])

        setattr(self.args, CA_VIS_CAL_FRAME, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME)
        setattr(self.args, CA_MER_CAT, MER_FINAL_CATALOG_LISTFILE_FILENAME)
        setattr(self.args, CA_SHE_MEAS, SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME)
        setattr(self.args, CA_MDB, MDB_PRODUCT_FILENAME)
        setattr(self.args, CA_SHE_OBS_TEST_RESULTS, SHE_OBS_TEST_RESULTS_PRODUCT_FILENAME)
        setattr(self.args, CA_SHE_EXP_TEST_RESULTS_LIST, SHE_EXP_TEST_RESULTS_PRODUCT_FILENAME)

    @classmethod
    def setup_class(cls):

        cls._download_mdb()
        cls._download_datastack()

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
