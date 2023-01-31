"""
:file: python/SHE_Validation/testing/utility.py

:date: 12 April 2022
:author: Bryan Gillis

Utility functions and classes for testing of SHE_Validation code
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
import re
import subprocess

from SHE_PPT.constants.misc import DATA_SUBDIR
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.testing.utility import SheTestCase

ESCAPE_CHARS = r"\[](){}*+?|^$."


def compile_regex(s: str):
    """Takes an input string which was intended to be human-readable, optionally with replacement keys %s, %i, %f,
    and convert it into a regex pattern, properly escaping characters and replacing any replacement strings with
    capturing groups.
    """

    # Escape all characters in the string which must be escaped
    s_escaped = s
    for c in ESCAPE_CHARS:
        s_escaped = s_escaped.replace(c, f"\\{c}")

    # Replace replacement keys with capturing groups
    s_capturing = s_escaped.replace(r"%s", r"(.+)")
    s_capturing = s_capturing.replace(r"%i", r"(\d+)")
    s_capturing = s_capturing.replace(r"%f", r"(\d+(?:\.\d+)?)")

    return re.compile(s_capturing)


class SheValTestCase(SheTestCase):
    """Test case providing utilities common across tests in the SHE_Validation project.
    """

    def _check_ana_files(self, qualified_test_results_filename, test_id_substring, directory_filename, l_ex_keys):
        """Parse the data product to find the output tarballs for the desired test case, and check that they all exist.
        """

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
