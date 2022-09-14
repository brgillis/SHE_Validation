""" @file utility.py

    Created 12 April 2022 by Bryan Gillis

    Utility functions and classes for testing of SHE_Validation_PSF code
"""

__updated__ = "2021-10-05"

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
from typing import Dict, Optional

import numpy as np
from astropy.table import Table

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.file_io import read_product_and_table
from SHE_PPT.testing.mock_data import NUM_TEST_POINTS
from SHE_Validation.binning.bin_data import add_bin_columns
from SHE_Validation.binning.utility import get_d_l_bin_limits
from SHE_Validation.testing.utility import SheValTestCase
from SHE_Validation_PSF.constants.psf_res_sp_test_info import L_PSF_RES_SP_BIN_PARAMETERS
from SHE_Validation_PSF.testing.mock_data import MockRefValStarCatTableGenerator, MockValStarCatTableGenerator
from SHE_Validation_PSF.validate_psf_res_star_pos import D_PSF_RES_SP_BIN_KEYS


class SheValPsfTestCase(SheValTestCase):
    """ Test case base class which defines attribute getters and setters to automatically generate needed data
        on-demand.
    """

    _workdir: Optional[str] = None

    _d_l_bin_limits: Optional[Dict[BinParameters, np.ndarray]] = None

    _NUM_TEST_POINTS: int = NUM_TEST_POINTS

    _mock_starcat_table_gen: Optional[MockValStarCatTableGenerator] = None
    _mock_ref_starcat_table_gen: Optional[MockRefValStarCatTableGenerator] = None

    _mock_starcat_table: Optional[Table] = None
    _mock_ref_starcat_table: Optional[Table] = None

    # Attribute getters and setters

    @property
    def workdir(self) -> Optional[str]:
        """ Basic getter for workdir.
        """
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: Optional[str]) -> None:
        """ Setter for workdir, which passes the set value to the table_gen attrs, as long as it isn't None (which
            they aren't set up to handle).
        """
        self._workdir = workdir
        if workdir is not None:
            self.mock_starcat_table_gen.workdir = workdir
            self.mock_ref_starcat_table_gen.workdir = workdir

    def make_d_l_bin_limits(self) -> Dict[BinParameters, np.ndarray]:
        """ Getter for d_l_bin_limits, which generates it from self.pipeline_config and self.mock_starcat_table.
        """

        return get_d_l_bin_limits(self.pipeline_config,
                                  bin_data_table=self.mock_starcat_table,
                                  l_bin_parameters=L_PSF_RES_SP_BIN_PARAMETERS,
                                  d_local_bin_keys=D_PSF_RES_SP_BIN_KEYS)

    @property
    def mock_starcat_table_gen(self) -> MockValStarCatTableGenerator:
        """ Getter for mock_starcat_table_gen which generates it on-demand.
        """
        if self._mock_starcat_table_gen is None:
            self._mock_starcat_table_gen = MockValStarCatTableGenerator(workdir = self.workdir,
                                                                        num_test_points = self._NUM_TEST_POINTS)
        return self._mock_starcat_table_gen

    @mock_starcat_table_gen.setter
    def mock_starcat_table_gen(self, mock_starcat_table_gen: MockValStarCatTableGenerator) -> None:
        """ Basic setter for mock_starcat_table_gen.
        """
        self._mock_starcat_table_gen = mock_starcat_table_gen

    @property
    def mock_ref_starcat_table_gen(self) -> MockRefValStarCatTableGenerator:
        """ Getter for mock_ref_starcat_table_gen which generates it on-demand.
        """
        if self._mock_ref_starcat_table_gen is None:
            self._mock_ref_starcat_table_gen = MockRefValStarCatTableGenerator(workdir = self.workdir,
                                                                               num_test_points = self._NUM_TEST_POINTS)
        return self._mock_ref_starcat_table_gen

    @mock_ref_starcat_table_gen.setter
    def mock_ref_starcat_table_gen(self, mock_ref_starcat_table_gen: MockRefValStarCatTableGenerator) -> None:
        """ Basic setter for mock_ref_starcat_table_gen.
        """
        self._mock_ref_starcat_table_gen = mock_ref_starcat_table_gen

    @property
    def mock_starcat_table(self) -> Table:
        """ Getter for mock_starcat_table which generates it on-demand.
        """
        if self._mock_starcat_table is None:
            self._mock_starcat_table = self.mock_starcat_table_gen.get_mock_table()
            add_bin_columns(self._mock_starcat_table,
                            data_stack = None,
                            l_bin_parameters = L_PSF_RES_SP_BIN_PARAMETERS)
        return self._mock_starcat_table

    @mock_starcat_table.setter
    def mock_starcat_table(self, mock_starcat_table: Table) -> None:
        """ Basic setter for mock_starcat_table.
        """
        self._mock_starcat_table = mock_starcat_table

    @property
    def mock_ref_starcat_table(self) -> Table:
        """ Getter for mock_ref_starcat_table which generates it on-demand.
        """
        if self._mock_ref_starcat_table is None:
            self._mock_ref_starcat_table = self.mock_ref_starcat_table_gen.get_mock_table()
        return self._mock_ref_starcat_table

    @mock_ref_starcat_table.setter
    def mock_ref_starcat_table(self, mock_ref_starcat_table: Table) -> None:
        """ Basic setter for mock_ref_starcat_table.
        """
        self._mock_ref_starcat_table = mock_ref_starcat_table

    # Convenience methods

    def _write_mock_starcat_product(self):
        """ Convenience method to write out a mock star catalog product, and set the mock product and table to their
            respective attributes.
        """
        mock_starcat_product_filename = self.mock_starcat_table_gen.write_mock_product()
        (self.mock_starcat_product,
         self.mock_starcat_table) = read_product_and_table(mock_starcat_product_filename,
                                                           workdir = self.workdir)

    def _write_mock_ref_starcat_product(self):
        """ Convenience method to write out a mock reference star catalog product, and set the mock product and table
            to their respective attributes.
        """
        mock_ref_starcat_product_filename = self.mock_ref_starcat_table_gen.write_mock_product()
        (self.mock_ref_starcat_product,
         self.mock_ref_starcat_table) = read_product_and_table(mock_ref_starcat_product_filename,
                                                               workdir = self.workdir)
