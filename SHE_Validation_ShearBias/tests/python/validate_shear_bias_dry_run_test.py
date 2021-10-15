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
from argparse import Namespace
from typing import Optional

import pytest
from dataclasses import dataclass

from SHE_PPT.file_io import read_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory
from SHE_Validation.testing.constants import PIPELINE_CONFIG_FILENAME, SHE_BIAS_TEST_RESULT_FILENAME
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
# noinspection PyPep8Naming
from SHE_Validation.testing.mock_tables import (MATCHED_TABLE_PRODUCT_FILENAME, cleanup_mock_matched_tables,
                                                write_mock_matched_tables, )
from SHE_Validation_ShearBias.ValidateShearBias import mainMethod as validate_shear_bias_main
from SHE_Validation_ShearBias.constants.shear_bias_test_info import FULL_L_SHEAR_BIAS_TEST_CASE_M_INFO
from SHE_Validation_ShearBias.results_reporting import SHEAR_BIAS_DIRECTORY_FILENAME

logger = getLogger(__name__)


@dataclass
class MockShearBiasArgs(Namespace):
    """ An object intended to mimic the parsed arguments for the CTI-gal validation test.
    """

    # Workdir and logdir need to be set in setup_class
    workdir: Optional[str] = None
    logdir: Optional[str] = None

    bootstrap_errors: Optional[bool] = None
    max_g_in: Optional[float] = None
    require_fitclass_zero: Optional[bool] = None

    matched_catalog: str = MATCHED_TABLE_PRODUCT_FILENAME
    pipeline_config: str = PIPELINE_CONFIG_FILENAME
    shear_bias_validation_test_results_product: str = SHE_BIAS_TEST_RESULT_FILENAME

    profile: bool = False
    dry_run: bool = True

    def __post_init__(self):

        for test_case_info in FULL_L_SHEAR_BIAS_TEST_CASE_M_INFO:
            bin_limits_cline_arg = test_case_info.bins_cline_arg
            if bin_limits_cline_arg is not None:
                setattr(self, bin_limits_cline_arg, None)


class TestCase:
    """
    """

    args: MockShearBiasArgs
    workdir: str = ""
    logdir: str = ""
    mock_pipeline_config_factory: Optional[MockPipelineConfigFactory] = None

    @classmethod
    def setup_class(cls):
        cls.args = MockShearBiasArgs()

    @classmethod
    def teardown_class(cls):

        # Delete the created data
        if cls.mock_pipeline_config_factory:
            cls.mock_pipeline_config_factory.cleanup()
        if cls.workdir:
            cleanup_mock_matched_tables(cls.workdir)

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok = True)

        # Set up the args to pass to the task
        self.args.workdir = self.workdir
        self.args.logdir = self.logdir

        # Write the pipeline config we'll be using and note its filename
        self.mock_pipeline_config_factory = MockValPipelineConfigFactory(workdir = self.workdir)
        self.mock_pipeline_config_factory.write(self.workdir)
        self.args.pipeline_config = self.mock_pipeline_config_factory.file_namer.filename

        # Write the matched catalog we'll be using and its data product
        write_mock_matched_tables(self.workdir)

    def test_shear_bias_dry_run(self):

        # Ensure this is a dry run
        self.args.dry_run = True

        # Call to validation function
        validate_shear_bias_main(self.args)

    def test_shear_bias_integration(self):
        """ Integration test of the full executable. Once we have a proper integration test set up,
            this should be skipped.
        """

        # Ensure this is not a dry run
        self.args.dry_run = False

        # Call to validation function
        validate_shear_bias_main(self.args)

        # Check the resulting data product and plot exist

        workdir = self.workdir
        output_filename = os.path.join(workdir, self.args.shear_bias_validation_test_results_product)

        assert os.path.isfile(output_filename)

        p = read_xml_product(xml_filename = output_filename)

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
