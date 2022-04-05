""" @file validate_psf_res_integration_test.py

    Created 08 March 2022 by Bryan Gillis

    Unit tests the input/output interface of the PSF-Res validation task.
"""

__updated__ = "2022-04-08"

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

from SHE_PPT.argument_parser import CA_SHE_STAR_CAT
from SHE_PPT.file_io import DATA_SUBDIR, read_xml_product
from SHE_PPT.testing.constants import STAR_CAT_PRODUCT_FILENAME
from SHE_PPT.testing.mock_she_star_cat import MockStarCatTableGenerator
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.argument_parser import CA_SHE_TEST_RESULTS
from SHE_Validation.testing.mock_pipeline_config import MockValPipelineConfigFactory
from SHE_Validation_PSF.ValidatePSFRes import defineSpecificProgramOptions, mainMethod
# Output data filenames
from SHE_Validation_PSF.results_reporting import PSF_RES_SP_DIRECTORY_FILENAME

SHE_TEST_RESULTS_PRODUCT_FILENAME = "she_validation_test_results.xml"


class TestPsfResRun(SheTestCase):
    """ Test case for PSF-Res validation test code.
    """

    pipeline_config_factory_type = MockValPipelineConfigFactory

    def _make_mock_args(self) -> Namespace:
        """ Get a mock argument parser we can use.

            This overrides the _make_mock_args() method of the SheTestCase class, which is called by the
            self.args property, setting the cached value self._args = self._make_mock_args() if self._args
            is None (which it will be when the object is initialized). This means that in each test case,
            self.args will return the result of this method (cached so that it only runs once).
        """
        args = defineSpecificProgramOptions().parse_args([])

        setattr(args, CA_SHE_STAR_CAT, STAR_CAT_PRODUCT_FILENAME)
        setattr(args, CA_SHE_TEST_RESULTS, SHE_TEST_RESULTS_PRODUCT_FILENAME)

        # The pipeline_config attribute of args isn't set here. This is because when parser.parse_args() is
        # called, it sets it to the default value of None. For the case of the pipeline_config, this is a
        # valid value, which will result in all defaults for configurable parameters being used.

        return args

    def post_setup(self) -> None:
        """ Override parent setup, setting up data to work with here.
        """

        mock_starcat_table_gen = MockStarCatTableGenerator(workdir = self.workdir)
        mock_starcat_table_gen.write_mock_product()

        return

    def test_psf_res_integration(self):
        """ "Integration" test of the full executable, using the unit-testing framework so it can be run automatically.
        """

        # Call to validation function, which was imported directly from the entry-point file
        mainMethod(self.args)

        # Check the resulting data product and plots exist in the expected locations

        workdir = self.workdir
        output_filename = getattr(self.args, CA_SHE_TEST_RESULTS)
        qualified_output_filename = os.path.join(workdir, output_filename)

        assert os.path.isfile(qualified_output_filename)

        p = read_xml_product(xml_filename = qualified_output_filename)

        # Find the index for the Tot test case. We'll check that for the presence of expected output data

        textfiles_tarball_filename: str = ""
        figures_tarball_filename: str = ""
        for val_test in p.Data.ValidationTestList:
            if "tot" not in val_test.TestId.lower():
                continue
            textfiles_tarball_filename = val_test.AnalysisResult.AnalysisFiles.TextFiles.FileName
            figures_tarball_filename = val_test.AnalysisResult.AnalysisFiles.Figures.FileName

        assert textfiles_tarball_filename
        assert figures_tarball_filename

        # Exit here for now - no textfiles or figures are created at present, so we can't test for them yet
        return

        # Unpack the tarballs containing both the textfiles and the figures
        for tarball_filename in (textfiles_tarball_filename, figures_tarball_filename):
            subprocess.call(f"cd {workdir} && tar xf {DATA_SUBDIR}/{tarball_filename}", shell = True)

        # The "directory" file, which is contained in the textfiles tarball, is a file with a predefined name,
        # containing with in the filenames of all other files which were tarred up. We open this first, and use
        # it to guide us on the filenames of other files that were tarred up, and test for their existence.

        qualified_directory_filename = os.path.join(workdir, PSF_RES_SP_DIRECTORY_FILENAME)

        # Search for the line in the directory file which contains the plot for the LensMC-tot test, for bin 0
        plot_filename = None
        with open(qualified_directory_filename, "r") as fi:
            for line in fi:
                if line[0] == "#":
                    continue
                key, value = line.strip().split(": ")
                if key == "tot-0":
                    plot_filename = value

        # Check that we found the filename for this plot
        assert plot_filename is not None

        # Check that this plot file exists
        assert os.path.isfile(os.path.join(workdir, plot_filename))
