""" @file data_processing_test.py

    Created 15 December 2020

    Unit tests of the data_processing.py module
"""

__updated__ = "2021-08-27"

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
from typing import Optional

import numpy as np
import pytest
from dataclasses import dataclass

from SHE_PPT import mdb
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_formats.she_lensmc_measurements import tf as LMC_TF
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint, get_ids_for_test_cases
from SHE_Validation.binning.bin_data import TF as BIN_TF
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.test_info_utility import make_test_case_info_for_bins
from SHE_Validation_CTI.data_processing import add_readout_register_distance, calculate_regression_results
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF
from SHE_Validation_CTI.table_formats.regression_results import TF as RR_TF


@dataclass
class MockData:
    """Dataclass for mock data used in testing."""

    l_tot: int = 0
    l_good: int = 0
    l_bad: int = 0

    # Meta arrays
    zeros: Optional[np.ndarray] = None
    indices: Optional[np.ndarray] = None
    ones: Optional[np.ndarray] = None

    def __post_init__(self):
        self.make_meta_arrays()

    def make_meta_arrays(self, l_tot: Optional[int] = None):
        if l_tot is not None:
            self.l_tot = l_tot

        if self.l_tot is not None:
            self.zeros = np.zeros(self.l_tot, dtype = '>f4')
            self.indices = np.indices((self.l_tot,), dtype = int, )[0]
            self.ones = np.ones(self.l_tot, dtype = '>f4')
        else:
            self.zeros = None
            self.indices = None
            self.ones = None


@dataclass
class MockCtiData(MockData):
    # Input data
    snr_data: Optional[np.ndarray] = None
    bg_data: Optional[np.ndarray] = None
    colour_data: Optional[np.ndarray] = None
    size_data: Optional[np.ndarray] = None

    # Output data
    weight_data: Optional[np.ndarray] = None
    readout_dist_data: Optional[np.ndarray] = None
    g1_data: Optional[np.ndarray] = None
    g1_err_data: Optional[np.ndarray] = None


class TestCtiGalDataProcessing(SheTestCase):
    """ Unit tests for CTI validation data processing.
    """

    def setup_workdir(self):

        self._download_mdb()

    @classmethod
    def teardown_class(cls):
        return

    def setup(self):

        # Make some mock data
        self.m = 1e-5
        self.b = -0.2
        self.g1_err = 0.25

        self.sigma_l_tol = 5  # Pass test if calculations are within 5 sigma

        self.l_good = 200  # Length of good data
        self.l_nan = 5  # Length of bad data
        self.l_zero = 5  # Length of zero-weight data
        self.l_tot = self.l_good + self.l_nan + self.l_zero

    def test_add_rr_distance(self):

        # Get the detector y-size from the MDB
        det_size_y: int = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
        assert det_size_y == 4136  # Calculations here rely on this being the value

        # Make some mock data
        mock_y_data = np.array([-100., 0., 500., 1000., 2000., 3000., 4000., 5000.], dtype = '>f4')

        mock_data_table = CGOD_TF.init_table(init_cols = {CGOD_TF.y: mock_y_data})

        # Run the function
        add_readout_register_distance(mock_data_table)

        # Check the results are as expected
        ro_dist = mock_data_table[CGOD_TF.readout_dist]

        assert np.allclose(ro_dist, np.array([-100., 0., 500., 1000., 2000., 1136., 136., -864.]))

    def test_calc_regression_results(self, mock_data, object_data_table, detections_table, measurements_table):

        d_measurements_tables = {ShearEstimationMethods.LENSMC: measurements_table}

        # Run the function
        rr_row = calculate_regression_results(object_data_table = object_data_table,
                                              l_ids_in_bin = detections_table[MFC_TF.ID],
                                              method = ShearEstimationMethods.LENSMC,
                                              product_type = "EXP", )

        # Check the results

        assert rr_row.meta[RR_TF.m.product_type] == "EXP"

        readout_dist_mean = np.mean(mock_data.readout_dist_data[:self.l_good])
        ex_slope_err = self.g1_err / np.sqrt(
            np.sum((mock_data.readout_dist_data[:self.l_good] - readout_dist_mean) ** 2))
        ex_intercept_err = ex_slope_err * np.sqrt(np.sum(mock_data.readout_dist_data[:self.l_good] ** 2) / self.l_good)

        assert rr_row[RR_TF.weight] == self.l_good / self.g1_err ** 2
        assert np.isclose(rr_row[RR_TF.slope], self.m, atol = self.sigma_l_tol * ex_slope_err)
        assert np.isclose(rr_row[RR_TF.slope_err], ex_slope_err, rtol = 0.1)
        assert np.isclose(rr_row[RR_TF.intercept], self.b, atol = self.sigma_l_tol * ex_intercept_err)
        assert np.isclose(rr_row[RR_TF.intercept_err], ex_intercept_err, rtol = 0.1)
        assert np.isclose(rr_row[RR_TF.slope_intercept_covar], 0, atol = 5 * ex_slope_err * ex_intercept_err)

        # Test the calculation is sensible for each binning

        d_bin_limits = {}
        l_test_case_info = make_test_case_info_for_bins(TestCaseInfo(method = ShearEstimationMethods.LENSMC))
        for test_case_info in l_test_case_info:
            d_bin_limits[test_case_info.bin_parameter] = (-0.5, 0.5, 1.5)

        # Get IDs for all bins
        d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = l_test_case_info,
                                                            d_bin_limits = d_bin_limits,
                                                            detections_table = detections_table,
                                                            d_measurements_tables = d_measurements_tables,
                                                            bin_constraint_type = BinParameterBinConstraint,
                                                            data_stack = None)

        for test_case_info in l_test_case_info:
            if test_case_info.bins == BinParameters.TOT or test_case_info.bins == BinParameters.EPOCH:
                continue
            l_l_test_case_object_ids = d_l_l_test_case_object_ids[test_case_info.name]
            for bin_index in range(2):
                l_test_case_object_ids = l_l_test_case_object_ids[bin_index]
                rr_row = calculate_regression_results(object_data_table = object_data_table,
                                                      l_ids_in_bin = l_test_case_object_ids,
                                                      method = ShearEstimationMethods.LENSMC,
                                                      product_type = "OBS", )

                # Just check the slope here. Give root-2 times the tolerance since we're only using half the data
                assert np.isclose(rr_row[RR_TF.slope], self.m, atol = np.sqrt(2.) * self.sigma_l_tol * ex_slope_err)

    @pytest.fixture(scope = "class")
    def mock_data(self, class_setup):

        mock_data = MockCtiData(self.l_tot)

        mock_data.g1_err_data = self.g1_err * np.ones(self.l_tot, dtype = '>f4')
        mock_data.weight_data = np.power(mock_data.g1_err_data, -2)
        mock_data.readout_dist_data = np.linspace(0, 2100, self.l_good + self.l_nan + self.l_zero, dtype = '>f4')

        mock_data.rng = np.random.default_rng(seed = 12345)

        mock_data.g1_data = (self.m * mock_data.readout_dist_data + self.b + mock_data.g1_err_data *
                             mock_data.rng.standard_normal(size = self.l_tot)).astype('>f4')

        # Set mock snr, bg, colour, and size values to test different bins

        mock_data.snr_data = np.where(mock_data.indices % 2 < 1, mock_data.ones, mock_data.zeros)
        mock_data.bg_data = np.where(mock_data.indices % 4 < 2, mock_data.ones, mock_data.zeros)
        mock_data.colour_data = np.where(mock_data.indices % 8 < 4, mock_data.ones, mock_data.zeros)
        mock_data.size_data = np.where(mock_data.indices % 16 < 8, mock_data.ones, mock_data.zeros)

        # Make the last bit of data bad or zero weight
        mock_data.weight_data[-self.l_nan - self.l_zero:-self.l_zero] = np.NaN
        mock_data.readout_dist_data[-self.l_nan - self.l_zero:-self.l_zero] = np.NaN
        mock_data.g1_data[-self.l_nan - self.l_zero:-self.l_zero] = np.NaN
        mock_data.weight_data[-self.l_zero:] = 0

        return mock_data

    @pytest.fixture(scope = "class")
    def measurements_table(self, class_setup, mock_data):
        measurements_table = LMC_TF.init_table(init_cols = {LMC_TF.ID: mock_data.indices})
        return measurements_table

    @pytest.fixture(scope = "class")
    def detections_table(self, class_setup, mock_data):
        detections_table = MFC_TF.init_table(init_cols = {MFC_TF.ID: mock_data.indices})
        detections_table[BIN_TF.snr] = mock_data.snr_data
        detections_table[BIN_TF.bg] = mock_data.bg_data
        detections_table[BIN_TF.colour] = mock_data.colour_data
        detections_table[BIN_TF.size] = mock_data.size_data
        return detections_table

    @pytest.fixture(scope = "class")
    def object_data_table(self, class_setup, mock_data):
        object_data_table = CGOD_TF.init_table(init_cols = {CGOD_TF.ID             : mock_data.indices,
                                                            CGOD_TF.weight_LensMC  : mock_data.weight_data,
                                                            CGOD_TF.readout_dist   : mock_data.readout_dist_data,
                                                            CGOD_TF.g1_image_LensMC: mock_data.g1_data})
        return object_data_table
