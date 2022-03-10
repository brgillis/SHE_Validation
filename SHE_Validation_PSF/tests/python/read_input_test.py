""" @file read_input_test.py

    Created 10 March 2022 by Bryan Gillis

    Unit tests of reading in input data for the PSF Residual validation test.
"""

__updated__ = "2022-04-10"

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

from SHE_PPT.testing.utility import SheTestCase

# Output data filenames
from SHE_Validation.testing.mock_tables import write_mock_starcat_table
from SHE_Validation_PSF.validate_psf_res import load_psf_res_input


class TestPsfResReadInput(SheTestCase):
    """ Test case for PSF-Res validation test code.
    """

    def post_setup(self):
        """ Override parent setup, setting up data to work with here.
        """

        write_mock_starcat_table(workdir = self.workdir)

        return

    def test_read_input(self, local_setup):
        """ "Integration" test of the full executable, using the unit-testing framework so it can be run automatically.
        """

        (d_l_bin_limits,
         p_star_cat,
         star_cat) = load_psf_res_input(self.d_args, self.workdir)
