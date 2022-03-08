""" @file binning_test.py

    Created 14 December 2020

    Unit tests of the bin_constraints.py module
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
from copy import deepcopy
from math import ceil
from typing import Dict

import numpy as np
from astropy.table import Column, Row, Table

from ElementsServices.DataSync import DataSync
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.test_data import (LENSMC_MEASUREMENTS_TABLE_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         MER_FINAL_CATALOG_TABLE_FILENAME, SYNC_CONF, TEST_DATA_LOCATION,
                                         TEST_FILES_DATA_STACK, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_formats.she_lensmc_measurements import tf as LMC_TF
from SHE_PPT.table_utility import is_in_format
from SHE_Validation.binning.bin_constraints import (BinParameterBinConstraint, FitclassZeroBinConstraint,
                                                    FitflagsBinConstraint, HeteroBinConstraint, MultiBinConstraint,
                                                    get_ids_for_bins, get_ids_for_test_cases, get_table_of_ids, )
from SHE_Validation.binning.bin_data import (TF as BIN_TF, add_bg_column, add_colour_column, add_epoch_column,
                                             add_size_column, add_snr_column, )
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters, NON_GLOBAL_BIN_PARAMETERS, TestCaseInfo
from SHE_Validation.test_info_utility import make_test_case_info_for_bins

ID_COLNAME = LMC_TF.ID


class TestBinConstraints:
    """ Test case for applying bin constraints to a table
    """

    TABLE_SIZE = 100
    ID_OFFSET = 1024
    NUM_ROWS_IN_BIN = 40
    BASE_BIN_LIMITS = np.array((0, NUM_ROWS_IN_BIN))

    D_PAR_OFFSETS = {BinParameters.TOT   : 0.,
                     BinParameters.BG    : 1000.,
                     BinParameters.SNR   : 2000.,
                     BinParameters.COLOUR: 3000.,
                     BinParameters.SIZE  : 4000.,
                     BinParameters.EPOCH : 5000., }

    D_PAR_NUM_BINS = {BinParameters.BG    : 1,
                      BinParameters.SNR   : 3,
                      BinParameters.COLOUR: 5,
                      BinParameters.SIZE  : 4,
                      BinParameters.EPOCH : 2, }

    t_mfc: Table
    t_lmc: Table
    d_l_bin_limits: Dict[BinParameters, np.ndarray]

    @classmethod
    def setup_class(cls):

        # Set up a mock table
        cls.t_mfc = MFC_TF.init_table(size = cls.TABLE_SIZE)
        cls.t_lmc = LMC_TF.init_table(size = cls.TABLE_SIZE,
                                      optional_columns = [LMC_TF.fit_class, LMC_TF.fit_flags])

        # Set IDs sequentially, but with an offset
        cls.t_mfc[ID_COLNAME] = np.arange(cls.TABLE_SIZE) + cls.ID_OFFSET
        cls.t_lmc[ID_COLNAME] = np.arange(cls.TABLE_SIZE) + cls.ID_OFFSET

        # Set up columns in the MFC catalog for each bin parameter except TOT
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:

            bin_colname = getattr(BIN_TF, bin_parameter.value)

            parameter_data = np.arange(cls.TABLE_SIZE) + cls.D_PAR_OFFSETS[bin_parameter]
            parameter_col = Column(data = parameter_data, name = bin_colname, dtype = BIN_TF.dtypes[bin_colname])

            cls.t_mfc.add_column(parameter_col)

        # Set up columns in the LMC catalog

        indices = np.arange(cls.TABLE_SIZE)

        fitclass_data = np.ones(cls.TABLE_SIZE, dtype = int) * indices % 3
        cls.t_lmc[LMC_TF.fit_class] = fitclass_data

        fitflags_data = np.ones(cls.TABLE_SIZE, dtype = int) * indices % 4
        cls.t_lmc[LMC_TF.fit_flags] = fitflags_data

        # Set up d_bin_limits
        cls.d_l_bin_limits = {BinParameters.TOT: DEFAULT_BIN_LIMITS}
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:
            cls.d_l_bin_limits[bin_parameter] = np.linspace(start = cls.D_PAR_OFFSETS[bin_parameter],
                                                            stop = cls.D_PAR_OFFSETS[bin_parameter] + cls.TABLE_SIZE,
                                                            num = cls.D_PAR_NUM_BINS[bin_parameter] + 1,
                                                            endpoint = True)

    @classmethod
    def teardown_class(cls):

        del cls.t_mfc

    def test_bin_on_parameters(self):
        """ Test applying a bin constraint with each bin parameter.
        """

        # Test each bin parameter other than TOT
        for bin_parameter in NON_GLOBAL_BIN_PARAMETERS:

            bin_limits = self.BASE_BIN_LIMITS + self.D_PAR_OFFSETS[bin_parameter]
            bin_constraint = BinParameterBinConstraint(bin_parameter = bin_parameter,
                                                       bin_limits = bin_limits)

            # Apply the constraint
            l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t_mfc)
            rows_in_bin = bin_constraint.get_rows_in_bin(self.t_mfc)
            ids_in_bin = bin_constraint.get_ids_in_bin(self.t_mfc)

            # Check the outputs are consistent
            assert (self.t_mfc[l_is_row_in_bin] == rows_in_bin).all()
            # noinspection PyUnresolvedReferences
            assert (rows_in_bin[ID_COLNAME] == ids_in_bin).all()

            # Check the outputs are as expected
            assert l_is_row_in_bin.sum() == self.NUM_ROWS_IN_BIN
            assert len(rows_in_bin) == self.NUM_ROWS_IN_BIN
            assert (ids_in_bin < self.NUM_ROWS_IN_BIN + self.ID_OFFSET).all()
            assert (self.t_mfc[~l_is_row_in_bin][ID_COLNAME] >= self.NUM_ROWS_IN_BIN).all()

        # Special check for TOT test case
        bin_constraint = BinParameterBinConstraint(bin_parameter = BinParameters.TOT)

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
        bin_constraint = FitclassZeroBinConstraint(method = ShearEstimationMethods.LENSMC)

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

    def test_bit_flags_bins(self):
        """ Test applying a bin constraint on fit_flags
        """

        # Set up the bin constraint
        bin_constraint = FitflagsBinConstraint(method = ShearEstimationMethods.LENSMC)

        # Apply the constraint
        l_is_row_in_bin = bin_constraint.get_l_is_row_in_bin(self.t_lmc)
        rows_in_bin = bin_constraint.get_rows_in_bin(self.t_lmc)
        ids_in_bin = bin_constraint.get_ids_in_bin(self.t_lmc)

        # Check the outputs are consistent
        assert (self.t_lmc[l_is_row_in_bin] == rows_in_bin).all()
        assert (rows_in_bin[ID_COLNAME] == ids_in_bin).all()

        # Check the outputs are as expected - only the first of every four should be in the bin
        assert l_is_row_in_bin.sum() == int(ceil(self.TABLE_SIZE / 4))
        assert len(rows_in_bin) == int(ceil(self.TABLE_SIZE / 4))
        assert (ids_in_bin % 4 == self.ID_OFFSET % 4).all()

    def test_combine_flags(self):

        # Set up multiple bin constraints
        bin_limits = self.BASE_BIN_LIMITS + self.D_PAR_OFFSETS[BinParameters.SNR]
        bin_parameter_constraint = BinParameterBinConstraint(bin_parameter = BinParameters.SNR,
                                                             bin_limits = bin_limits)
        fitclass_zero_bin_constraint = FitclassZeroBinConstraint(method = ShearEstimationMethods.LENSMC)
        fitflags_bin_constraint = FitflagsBinConstraint(method = ShearEstimationMethods.LENSMC)

        # Set up multi and hetero bin constraints
        fit_multi_bin_constraint = MultiBinConstraint(l_bin_constraints = [fitclass_zero_bin_constraint,
                                                                           fitflags_bin_constraint])
        full_bin_constraint = HeteroBinConstraint(l_bin_constraints = [bin_parameter_constraint,
                                                                       fitclass_zero_bin_constraint,
                                                                       fitflags_bin_constraint])

        # Apply the multi constraint
        l_is_row_in_bin = fit_multi_bin_constraint.get_l_is_row_in_bin(self.t_lmc)
        rows_in_bin = fit_multi_bin_constraint.get_rows_in_bin(self.t_lmc)
        ids_in_bin = fit_multi_bin_constraint.get_ids_in_bin(self.t_lmc)

        # Check the outputs are consistent
        assert (self.t_lmc[l_is_row_in_bin] == rows_in_bin).all()
        assert (rows_in_bin[ID_COLNAME] == ids_in_bin).all()

        # Check the outputs are as expected - only the first of every four should be in the bin
        assert l_is_row_in_bin.sum() == int(ceil(self.TABLE_SIZE / 12))
        assert len(rows_in_bin) == int(ceil(self.TABLE_SIZE / 12))
        assert (ids_in_bin % 12 == self.ID_OFFSET % 12).all()

        # Apply the full constraint
        ids_in_bin = full_bin_constraint.get_ids_in_bin([self.t_mfc, self.t_lmc, self.t_lmc])

        # Check the outputs are as expected - only the first of every four should be in the bin
        assert len(ids_in_bin) == int(ceil(self.NUM_ROWS_IN_BIN / 12))
        # noinspection PyTypeChecker
        assert (ids_in_bin % 12 == self.ID_OFFSET % 12).all()

    def test_get_ids_for_bins(self):
        """ Tests the get_ids_for_bins function.
        """

        d_l_l_ids = get_ids_for_bins(d_bin_limits = self.d_l_bin_limits,
                                     detections_table = self.t_mfc,
                                     bin_constraint_type = BinParameterBinConstraint)

        # Check that everything is as expected
        for bin_parameter in BinParameters:

            l_l_ids = d_l_l_ids[bin_parameter]

            # Special check for tot case
            if bin_parameter == BinParameters.TOT:
                assert len(l_l_ids) == 1
                assert len(l_l_ids[0]) == self.TABLE_SIZE
                continue

            # Check the number of bins is right
            ex_num_bins = self.D_PAR_NUM_BINS[bin_parameter]
            assert len(l_l_ids) == ex_num_bins

            # Check the number of IDs per bin is right
            min_num_per_bin = self.TABLE_SIZE // ex_num_bins
            max_num_per_bin = min_num_per_bin + 1
            for i in range(ex_num_bins):
                l_ids = l_l_ids[i]
                assert len(l_ids) >= min_num_per_bin
                assert len(l_ids) <= max_num_per_bin

    def test_get_ids_for_test_cases(self):
        """ Tests the get_ids_for_test_cases function.
        """

        base_test_case_info = TestCaseInfo(base_test_case_id = "MOCK-ID",
                                           base_description = "mock description",
                                           method = ShearEstimationMethods.LENSMC)

        l_test_case_info = make_test_case_info_for_bins(base_test_case_info)

        d_l_l_ids = get_ids_for_test_cases(l_test_case_info = l_test_case_info,
                                           d_bin_limits = self.d_l_bin_limits,
                                           detections_table = self.t_mfc,
                                           d_measurements_tables = {ShearEstimationMethods.LENSMC: self.t_lmc},
                                           bin_constraint_type = BinParameterBinConstraint)

        # Check that everything is as expected
        for test_case_info in l_test_case_info:

            bin_parameter = test_case_info.bin_parameter

            l_l_ids = d_l_l_ids[test_case_info.name]

            # Special check for tot case
            if bin_parameter == BinParameters.TOT:
                assert len(l_l_ids) == 1
                assert len(l_l_ids[0]) == self.TABLE_SIZE
                continue

            # Check the number of bins is right
            ex_num_bins = self.D_PAR_NUM_BINS[bin_parameter]
            assert len(l_l_ids) == ex_num_bins

            # Check the number of IDs per bin is right
            min_num_per_bin = self.TABLE_SIZE // ex_num_bins
            max_num_per_bin = min_num_per_bin + 1
            for i in range(ex_num_bins):
                l_ids = l_l_ids[i]
                assert len(l_ids) >= min_num_per_bin
                assert len(l_ids) <= max_num_per_bin

    def test_get_table_of_ids(self):
        """ Unit test for the get_table_of_ids function.
        """

        empty_ids = []
        one_id_in = [self.ID_OFFSET]
        all_ids_in = [self.ID_OFFSET, self.ID_OFFSET + 1]
        some_ids_in = [*all_ids_in, self.ID_OFFSET - 1]

        assert len(get_table_of_ids(self.t_mfc, empty_ids)) == 0
        assert isinstance(get_table_of_ids(self.t_mfc, one_id_in), Row)
        assert len(get_table_of_ids(self.t_mfc, all_ids_in)) == 2
        assert len(get_table_of_ids(self.t_mfc, some_ids_in)) == 2


class TestBinData:
    """ Class to perform tests on bin data tables and adding columns.
    """

    workdir: str
    logdir: str
    data_stack: SHEFrameStack
    mfc_t: Table
    lmc_t: Table

    # Set up some expected values
    EX_BG_LEVEL = 45.71

    @classmethod
    def setup_class(cls):
        # Download the data stack files from WebDAV
        sync_datastack = DataSync(SYNC_CONF, TEST_FILES_DATA_STACK)
        sync_datastack.download()
        qualified_vis_calibrated_frames_filename = sync_datastack.absolutePath(
            os.path.join(TEST_DATA_LOCATION, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME))
        assert os.path.isfile(
            qualified_vis_calibrated_frames_filename), f"Cannot find file: {qualified_vis_calibrated_frames_filename}"

        # Get the workdir based on where the data images listfile is
        cls.workdir = os.path.split(qualified_vis_calibrated_frames_filename)[0]
        cls.logdir = os.path.join(cls.workdir, "logs")

        # Read in the test data
        cls.data_stack = SHEFrameStack.read(exposure_listfile_filename = VIS_CALIBRATED_FRAME_LISTFILE_FILENAME,
                                            detections_listfile_filename = MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                            workdir = cls.workdir,
                                            clean_detections = False,
                                            memmap = True,
                                            mode = 'denywrite')
        cls.mfc_t = Table.read(os.path.join(cls.workdir, "data", MER_FINAL_CATALOG_TABLE_FILENAME))
        cls.lmc_t = Table.read(os.path.join(cls.workdir, "data", LENSMC_MEASUREMENTS_TABLE_FILENAME))

    @classmethod
    def teardown_class(cls):
        return

    def test_table_format(self):
        """ Runs tests of the bin data table format.
        """

        bin_table = BIN_TF.init_table()

        assert is_in_format(bin_table, BIN_TF)

    def test_add_columns(self):
        """ Runs tests of the functions to add columns of bin data to tables.
        """

        mfc_t_copy = deepcopy(self.mfc_t)

        # Try adding columns for each bin parameter
        add_snr_column(mfc_t_copy, self.data_stack)
        np.isnan(mfc_t_copy[BIN_TF.snr]).all()

        add_colour_column(mfc_t_copy, self.data_stack)
        np.isnan(mfc_t_copy[BIN_TF.colour]).all()

        add_size_column(mfc_t_copy, self.data_stack)
        assert np.allclose(mfc_t_copy[BIN_TF.size], mfc_t_copy[MFC_TF.SEGMENTATION_AREA].data)

        add_bg_column(mfc_t_copy, self.data_stack)
        assert np.allclose(mfc_t_copy[BIN_TF.bg], self.EX_BG_LEVEL)

        add_epoch_column(mfc_t_copy, self.data_stack)
        assert np.allclose(mfc_t_copy[BIN_TF.epoch], 0.)
