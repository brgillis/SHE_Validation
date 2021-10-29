""" @file validate_shear_bias_dry_run_test.py

    Created 10 December 2020

    Unit tests the input/output interface of the Shear Bias validation task.
"""

__updated__ = "2021-08-31"

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
from py._path.local import LocalPath

from SHE_PPT.argument_parser import CA_DRY_RUN, CA_PIPELINE_CONFIG
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.argument_parser import CA_SHE_MATCHED_CAT, CA_SHE_TEST_RESULTS
from SHE_Validation.testing.constants import PIPELINE_CONFIG_FILENAME, SHE_BIAS_TEST_RESULT_FILENAME
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation.testing.mock_tables import (MATCHED_TABLE_PRODUCT_FILENAME, cleanup_mock_matched_tables,
                                                write_mock_matched_tables, )
from SHE_Validation_ShearBias.ValidateShearBias import (defineSpecificProgramOptions,
                                                        mainMethod, )
from SHE_Validation_ShearBias.results_reporting import SHEAR_BIAS_DIRECTORY_FILENAME

logger = getLogger(__name__)


class ShearBiasTestCase(SheTestCase):
    """ Test case for Shear Bias validation test code
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> None:
        """ Get a mock argument parser we can use.
        """
        parser = defineSpecificProgramOptions()
        self.args = parser.parse_args([])

        setattr(self.args, CA_SHE_MATCHED_CAT, MATCHED_TABLE_PRODUCT_FILENAME)
        setattr(self.args, CA_PIPELINE_CONFIG, PIPELINE_CONFIG_FILENAME)
        setattr(self.args, CA_SHE_TEST_RESULTS, SHE_BIAS_TEST_RESULT_FILENAME)

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):

        super().teardown_class()
        if cls.workdir:
            cleanup_mock_matched_tables(cls.workdir)

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir: LocalPath):

        self._setup(tmpdir)

        # Write the matched catalog we'll be using and its data product
        write_mock_matched_tables(self.workdir)

    def test_shear_bias_dry_run(self):

        # Ensure this is a dry run
        setattr(self.args, CA_DRY_RUN, True)

        # Call to validation function
        mainMethod(self.args)

    def test_shear_bias_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run
        setattr(self.args, CA_DRY_RUN, False)

        # Call to validation function
        mainMethod(self.args)

        # Check the resulting data product and plot exist

        workdir = self.workdir
        output_filename = getattr(self.args, CA_SHE_TEST_RESULTS)
        qualified_output_filename = os.path.join(workdir, output_filename)

        assert os.path.isfile(qualified_output_filename)

        p = read_xml_product(xml_filename = qualified_output_filename)

        test_list = p.Data.ValidationTestList
        plot_filename = None

        for test in test_list:

            if not test.AnalysisResult.AnalysisFiles.TextFiles or not test.AnalysisResult.AnalysisFiles.Figures:
                continue

            textfiles_tarball_filename = test.AnalysisResult.AnalysisFiles.TextFiles.FileName
            figures_tarball_filename = test.AnalysisResult.AnalysisFiles.Figures.FileName

            for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
                subprocess.call(f"cd {workdir} && tar xf {tarball_filename}", shell = True)

            qualified_directory_filename = os.path.join(workdir, SHEAR_BIAS_DIRECTORY_FILENAME)
            logger.info(f"Opening file: {qualified_directory_filename}")
            with open(qualified_directory_filename, "r") as fi:
                for line in fi:
                    logger.info(f"Checking line: {line}")
                    if line[0] == "#":
                        continue
                    key, value = line.strip().split(": ")
                    if key == "LensMC-global-0-g1":
                        plot_filename = value

        assert plot_filename is not None
        assert os.path.isfile(os.path.join(workdir, plot_filename))
