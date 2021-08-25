""" @file binning_test.py

    Created 14 December 2020

    Unit tests of the bin_constraints.py module
"""
from math import ceil

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_formats.she_lensmc_measurements import tf as LMC_TF
from astropy.table import Table, Column

from ElementsServices.DataSync import DataSync
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint,\
    FitclassZeroBinConstraint
from SHE_Validation.binning.bin_data import TF as BIN_TF
from SHE_Validation.constants.test_info import BinParameters, NON_GLOBAL_BIN_PARAMETERS
import numpy as np


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


ID_COLNAME = LMC_TF.ID


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
        cls.t_mfc = MFC_TF.init_table(size=cls.TABLE_SIZE)
        cls.t_lmc = LMC_TF.init_table(size=cls.TABLE_SIZE,
                                      optional_columns=[LMC_TF.fit_class, LMC_TF.fit_flags])

        # Set IDs sequentially, but with an offset
        cls.t_mfc[ID_COLNAME] = np.arange(cls.TABLE_SIZE) + cls.ID_OFFSET
        cls.t_lmc[ID_COLNAME] = np.arange(cls.TABLE_SIZE) + cls.ID_OFFSET

        # Set up columns in the MFC catalog for each bin parameter except GLOBAL
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:

            bin_colname = getattr(BIN_TF, bin_parameter.value)

            parameter_data = np.arange(cls.TABLE_SIZE) + cls.D_PAR_OFFSETS[bin_parameter]
            parameter_col = Column(data=parameter_data, name=bin_colname, dtype=BIN_TF.dtypes[bin_colname])

            cls.t_mfc.add_column(parameter_col)

        # Set up columns in the LMC catalog

        indices = np.arange(cls.TABLE_SIZE)

        fitclass_data = np.ones(cls.TABLE_SIZE, dtype=int) * indices % 3
        cls.t_lmc[LMC_TF.fit_class] = fitclass_data

        fitflags_data = np.ones(cls.TABLE_SIZE, dtype=int) * indices % 4
        cls.t_lmc[LMC_TF.fit_flags] = fitflags_data

    @classmethod
    def teardown_class(cls):

        del cls.t_mfc

    def test_bin_on_parameters(self):
        """ Test applying a bin constraint with each bin parameter.
        """

        # Test each bin parameter other than GLOBAL
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:

            bin_limits = self.BASE_BIN_LIMITS + self.D_PAR_OFFSETS[bin_parameter]
            bin_constraint = BinParameterBinConstraint(bin_parameter=bin_parameter,
                                                       bin_limits=bin_limits)

            # Apply the constraint
            l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t_mfc)
            rows_in_bin = bin_constraint.get_rows_in_bin(self.t_mfc)
            ids_in_bin = bin_constraint.get_ids_in_bin(self.t_mfc)

            # Check the outputs are consistent
            assert (self.t_mfc[l_is_row_in_bin] == rows_in_bin).all()
            assert (rows_in_bin[ID_COLNAME] == ids_in_bin).all()

            # Check the outputs are as expected
            assert l_is_row_in_bin.sum() == self.NUM_ROWS_IN_BIN
            assert len(rows_in_bin) == self.NUM_ROWS_IN_BIN
            assert (ids_in_bin < self.NUM_ROWS_IN_BIN + self.ID_OFFSET).all()
            assert (self.t_mfc[~l_is_row_in_bin][ID_COLNAME] >= self.NUM_ROWS_IN_BIN).all()

        # Special check for GLOBAL test case
        bin_constraint = BinParameterBinConstraint(bin_parameter=BinParameters.GLOBAL)

        # Apply the constraint
        l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t_mfc)
        rows_in_bin = bin_constraint.get_rows_in_bin(self.t_mfc)
        ids_in_bin = bin_constraint.get_ids_in_bin(self.t_mfc)

        # Check the outputs are consistent
        assert (self.t_mfc[l_is_row_in_bin] == rows_in_bin).all()
        assert (rows_in_bin[ID_COLNAME] == ids_in_bin).all()

        # Check the outputs are as expected
        assert l_is_row_in_bin.sum() == self.TABLE_SIZE
        assert len(rows_in_bin) == self.TABLE_SIZE
        assert (ids_in_bin == self.t_mfc[ID_COLNAME]).all()

    def test_fitclass_zero_bin(self):
        """ Test applying a bin constraint of fitclass == zero.
        """

        # Set up the bin constraint
        bin_constraint = FitclassZeroBinConstraint(method=ShearEstimationMethods.LENSMC)

        # Apply the constraint
        l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t_lmc)
        rows_in_bin = bin_constraint.get_rows_in_bin(self.t_lmc)
        ids_in_bin = bin_constraint.get_ids_in_bin(self.t_lmc)

        # Check the outputs are consistent
        assert (self.t_lmc[l_is_row_in_bin] == rows_in_bin).all()
        assert (rows_in_bin[ID_COLNAME] == ids_in_bin).all()

        # Check the outputs are as expected - only the first of every three should be in the bin
        assert l_is_row_in_bin.sum() == int(ceil(self.TABLE_SIZE / 3))
        assert len(rows_in_bin) == int(ceil(self.TABLE_SIZE / 3))
        assert (ids_in_bin % 3 == self.ID_OFFSET % 3).all()
