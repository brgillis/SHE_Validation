""" @file data_processing_test.py

    Created 15 December 2020

    Unit tests of the data_processing.py module
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

from copy import deepcopy
from typing import Any, Dict, List, Optional

import numpy as np
import pytest
from astropy import table
from astropy.table import Row, Table

from SHE_PPT import mdb
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_formats.she_lensmc_measurements import tf as LMC_TF
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint, get_ids_for_test_cases
from SHE_Validation.binning.bin_data import TF as BIN_TF
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.test_info_utility import make_test_case_info_for_bins
from SHE_Validation.testing.mock_data import MockBinDataGenerator, TEST_L_GOOD, TEST_L_NAN, TEST_L_ZERO
from SHE_Validation_CTI.data_processing import add_readout_register_distance, calculate_regression_results
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF
from SHE_Validation_CTI.table_formats.regression_results import TF as RR_TF

# Constants to describe mock data used here
TEST_M = 1e-5
TEST_B = -0.2
TEST_G1_ERR = 0.25

TEST_SIGMA_L_TOL = 5  # Pass test if calculations are within 5 sigma


class MockCtiDataGenerator(MockBinDataGenerator):
    """ Data generator which generates data suitable for binning with various bin parameters.
    """

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        super()._generate_unique_data()

        self.data["indices"] = self._indices

        self.data["g1_err"] = TEST_G1_ERR * self._ones
        self.data["weight"] = np.power(self.data["g1_err"], -2)
        self.data["readout_dist"] = np.linspace(0, 2100, self.num_test_points, dtype='>f4')

        self.data["g1"] = (TEST_M * self.data["readout_dist"] + TEST_B + self.data["g1_err"] *
                           self._rng.standard_normal(size=self.num_test_points)).astype('>f4')

        # Make the last bit of data bad or zero weight
        self.data["weight"][-TEST_L_NAN - TEST_L_ZERO:-TEST_L_ZERO] = np.NaN
        self.data["readout_dist"][-TEST_L_NAN - TEST_L_ZERO:-TEST_L_ZERO] = np.NaN
        self.data["g1"][-TEST_L_NAN - TEST_L_ZERO:-TEST_L_ZERO] = np.NaN
        self.data["weight"][-TEST_L_ZERO:] = 0


class TestCtiGalDataProcessing(SheTestCase):
    """ Unit tests for CTI validation data processing.
    """

    def setup_workdir(self) -> None:

        self._download_mdb()

        self.mock_data = MockCtiDataGenerator().get_data()
        self.indices = self.mock_data["indices"]

    @pytest.fixture(scope="class")
    def measurements_table(self, class_setup):
        measurements_table = LMC_TF.init_table(init_cols={LMC_TF.ID: self.indices})
        return measurements_table

    @pytest.fixture(scope="class")
    def detections_table(self, class_setup):
        detections_table = MFC_TF.init_table(init_cols={MFC_TF.ID: self.indices})
        detections_table[BIN_TF.snr] = self.mock_data[BIN_TF.snr]
        detections_table[BIN_TF.bg] = self.mock_data[BIN_TF.bg]
        detections_table[BIN_TF.colour] = self.mock_data[BIN_TF.colour]
        detections_table[BIN_TF.size] = self.mock_data[BIN_TF.size]
        return detections_table

    @pytest.fixture(scope="class")
    def object_data_table(self, class_setup):
        object_data_table = CGOD_TF.init_table(init_cols={CGOD_TF.ID: self.indices,
                                                          CGOD_TF.weight_LensMC: self.mock_data["weight"],
                                                          CGOD_TF.readout_dist: self.mock_data["readout_dist"],
                                                          CGOD_TF.g1_image_LensMC: self.mock_data["g1"]})
        return object_data_table

    def test_add_rr_distance(self):

        # Get the detector y-size from the MDB
        det_size_y: int = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
        assert det_size_y == 4136  # Calculations here rely on this being the value

        # Make some mock data
        mock_y_data = np.array([-100., 0., 500., 1000., 2000., 3000., 4000., 5000.], dtype='>f4')

        mock_data_table = CGOD_TF.init_table(init_cols={CGOD_TF.y: mock_y_data})

        # Run the function
        add_readout_register_distance(mock_data_table)

        # Check the results are as expected
        ro_dist = mock_data_table[CGOD_TF.readout_dist]

        assert np.allclose(ro_dist, np.array([-100., 0., 500., 1000., 2000., 1136., 136., -864.]))

    def test_calc_regression_results(self, object_data_table, detections_table, measurements_table):
        """ Test that the calculate_regression_results calculates the expected slope, intercept, and errors (for the
            non-bootstrap approach to errors).
        """

        d_measurements_tables = {ShearEstimationMethods.LENSMC: measurements_table}

        # Run the function
        rr_row = calculate_regression_results(object_data_table=object_data_table,
                                              l_ids_in_bin=detections_table[MFC_TF.ID],
                                              method=ShearEstimationMethods.LENSMC,
                                              product_type="EXP",
                                              bootstrap=False)

        # Check the results

        assert rr_row.meta[RR_TF.m.product_type] == "EXP"

        ex_slope_err = self._check_rr_row(rr_row, self.mock_data, err_rtol=0.01)

        # Test the calculation is sensible for each binning

        d_bin_limits = {}
        l_test_case_info = make_test_case_info_for_bins(TestCaseInfo(method=ShearEstimationMethods.LENSMC))
        for test_case_info in l_test_case_info:
            d_bin_limits[test_case_info.bin_parameter] = (-0.5, 0.5, 1.5)

        # Get IDs for all bins
        d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info=l_test_case_info,
                                                            d_bin_limits=d_bin_limits,
                                                            detections_table=detections_table,
                                                            d_measurements_tables=d_measurements_tables,
                                                            bin_constraint_type=BinParameterBinConstraint,
                                                            data_stack=None)

        for test_case_info in l_test_case_info:
            if test_case_info.bins == BinParameters.TOT or test_case_info.bins == BinParameters.EPOCH:
                continue
            l_l_test_case_object_ids = d_l_l_test_case_object_ids[test_case_info.name]
            for bin_index in range(2):
                l_test_case_object_ids = l_l_test_case_object_ids[bin_index]
                rr_row = calculate_regression_results(object_data_table=object_data_table,
                                                      l_ids_in_bin=l_test_case_object_ids,
                                                      method=ShearEstimationMethods.LENSMC,
                                                      product_type="OBS", )

                # Just check the slope here. Give root-2 times the tolerance since we're only using half the data
                assert np.isclose(rr_row[RR_TF.slope], TEST_M, atol=np.sqrt(2.) * TEST_SIGMA_L_TOL * ex_slope_err)

    def _check_rr_row(self,
                      rr_row: Row,
                      mock_data: Dict[str, Any],
                      err_rtol=0.1) -> float:
        """ Checks that the regression results row contains results matching what we expect from the mock data.

            Returns the expected slope error, which is used for other calculations.
        """
        readout_dist_mean = np.mean(mock_data["readout_dist"][:TEST_L_GOOD])
        ex_slope_err = TEST_G1_ERR / np.sqrt(
            np.sum((mock_data["readout_dist"][:TEST_L_GOOD] - readout_dist_mean) ** 2))
        ex_intercept_err = ex_slope_err * np.sqrt(np.sum(mock_data["readout_dist"][:TEST_L_GOOD] ** 2) / TEST_L_GOOD)

        assert rr_row[RR_TF.weight] == TEST_L_GOOD / TEST_G1_ERR ** 2
        assert np.isclose(rr_row[RR_TF.slope], TEST_M, atol=TEST_SIGMA_L_TOL * ex_slope_err)
        assert np.isclose(rr_row[RR_TF.slope_err], ex_slope_err, rtol=err_rtol)
        assert np.isclose(rr_row[RR_TF.intercept], TEST_B, atol=TEST_SIGMA_L_TOL * ex_intercept_err)
        assert np.isclose(rr_row[RR_TF.intercept_err], ex_intercept_err, rtol=err_rtol)
        assert np.isclose(rr_row[RR_TF.slope_intercept_covar], 0, atol=5 * ex_slope_err * ex_intercept_err)

        return ex_slope_err

    def test_calc_regression_results_bootstrap(self, object_data_table, detections_table, measurements_table):
        """ Test that the calculate_regression_results calculates the expected slope, intercept, and errors (for the
            bootstrap approach to errors).
        """

        # Run the function with bootstrap error calculation on the regular data
        exp_rr_row = calculate_regression_results(object_data_table=object_data_table,
                                                  l_ids_in_bin=detections_table[MFC_TF.ID],
                                                  method=ShearEstimationMethods.LENSMC,
                                                  product_type="OBS",
                                                  bootstrap=True)

        # Check the results

        self._check_rr_row(exp_rr_row, self.mock_data, err_rtol=0.1)

        # Now test with a modified object data type, with multiple entries for each object

        num_exposures = 4

        l_object_data_tables: List[Optional[Table]] = [None] * num_exposures
        for exp_i in range(num_exposures):
            exp_object_data_table = deepcopy(object_data_table)

            l_object_data_tables[exp_i] = exp_object_data_table

        obs_object_data_table = table.vstack(l_object_data_tables)

        # Run the function with bootstrap error calculation on the regular data
        obs_rr_row = calculate_regression_results(object_data_table=obs_object_data_table,
                                                  l_ids_in_bin=detections_table[MFC_TF.ID],
                                                  method=ShearEstimationMethods.LENSMC,
                                                  product_type="OBS",
                                                  bootstrap=True)

        # Check that the slope and intercept errors from this are about the same as for the individual exposure (
        # since there's no actual new data)

        assert np.isclose(exp_rr_row[RR_TF.slope_err], obs_rr_row[RR_TF.slope_err], rtol=0.1)
        assert np.isclose(exp_rr_row[RR_TF.intercept_err], obs_rr_row[RR_TF.intercept_err], rtol=0.1)
