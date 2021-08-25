""" @file binning_test.py

    Created 14 December 2020

    Unit tests of the bin_constraints.py module
"""

__updated__ = "2021-08-25"

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

from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_formats.she_lensmc_measurements import 
from astropy.table import Table, Column

from ElementsServices.DataSync import DataSync
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint
from SHE_Validation.binning.bin_data import TF as BIN_TF
from SHE_Validation.constants.test_info import BinParameters, NON_GLOBAL_BIN_PARAMETERS
import numpy as np


class TestCase:
    """ Test case for applying bin constraints to a table
    """

    TABLE_SIZE = 100
    ID_OFFSET = 1024
    NUM_ROWS_IN_BIN = 40
    BASE_BIN_LIMITS = np.array((0, NUM_ROWS_IN_BIN))

    D_PAR_OFFSETS = {BinParameters.GLOBAL: 0.,
                     BinParameters.BG: 1000.,
                     BinParameters.SNR: 2000.,
                     BinParameters.COLOUR: 3000.,
                     BinParameters.SIZE: 4000.,
                     BinParameters.EPOCH: 5000., }

    @classmethod
    def setup_class(cls):

        # Set up a mock table
        cls.t = MFC_TF.init_table(size=cls.TABLE_SIZE)

        # Set IDs sequentially, but with an offset
        cls.t[MFC_TF.ID] = np.arange(cls.TABLE_SIZE) + cls.ID_OFFSET

        # Set up columns for each bin parameter except GLOBAL
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:

            bin_colnmae = getattr(BIN_TF, bin_parameter.value)

            parameter_data = np.arange(cls.TABLE_SIZE) + cls.D_PAR_OFFSETS[bin_parameter]
            parameter_col = Column(data=parameter_data, name=bin_colnmae, dtype=BIN_TF.dtypes[bin_colnmae])

            cls.t.add_column(parameter_col)

    @classmethod
    def teardown_class(cls):

        del cls.t

    def test_bin_on_parameters(self):
        """ Test applying a bin constraint with each bin parameter.
        """

        # Test each bin parameter other than GLOBAL
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:

            bin_limits = self.BASE_BIN_LIMITS + self.D_PAR_OFFSETS[bin_parameter]
            bin_constraint = BinParameterBinConstraint(bin_parameter=bin_parameter,
                                                       bin_limits=bin_limits)

            # Apply the constraint
            l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t)
            rows_in_bin = bin_constraint.get_rows_in_bin(self.t)
            ids_in_bin = bin_constraint.get_ids_in_bin(self.t)

            # Check the outputs are consistent
            assert (self.t[l_is_row_in_bin] == rows_in_bin).all()
            assert (rows_in_bin[MFC_TF.ID] == ids_in_bin).all()

            # Check the outputs are as expected
            assert l_is_row_in_bin.sum() == self.NUM_ROWS_IN_BIN
            assert len(rows_in_bin) == self.NUM_ROWS_IN_BIN
            assert (ids_in_bin < self.NUM_ROWS_IN_BIN + self.ID_OFFSET).all()
            assert (self.t[~l_is_row_in_bin][MFC_TF.ID] >= self.NUM_ROWS_IN_BIN).all()

        # Special check for GLOBAL test case
        bin_constraint = BinParameterBinConstraint(bin_parameter=BinParameters.GLOBAL)

        # Apply the constraint
        l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t)
        rows_in_bin = bin_constraint.get_rows_in_bin(self.t)
        ids_in_bin = bin_constraint.get_ids_in_bin(self.t)

        # Check the outputs are consistent
        assert (self.t[l_is_row_in_bin] == rows_in_bin).all()
        assert (rows_in_bin[MFC_TF.ID] == ids_in_bin).all()

        # Check the outputs are as expected
        assert l_is_row_in_bin.sum() == self.TABLE_SIZE
        assert len(rows_in_bin) == self.TABLE_SIZE
        assert (ids_in_bin == self.t[MFC_TF.ID]).all()
