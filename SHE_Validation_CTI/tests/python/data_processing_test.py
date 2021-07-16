""" @file data_processing_test.py

    Created 15 December 2020

    Unit tests of the data_processing.py module
"""

__updated__ = "2021-07-16"

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

from SHE_PPT import mdb
from SHE_PPT.constants.test_data import SYNC_CONF, TEST_FILES_MDB, TEST_DATA_LOCATION, MDB_PRODUCT_FILENAME

from ElementsServices.DataSync import DataSync
from SHE_Validation_CTI.constants.cti_gal_test_info import CtiGalTestCases
from SHE_Validation_CTI.data_processing import add_readout_register_distance, calculate_regression_results
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF, initialise_cti_gal_object_data_table
from SHE_Validation_CTI.table_formats.regression_results import TF as RR_TF
import numpy as np


class TestCase:
    """


    """

    @classmethod
    def setup_class(cls):

        # Download the MDB from WebDAV
        sync_mdb = DataSync(SYNC_CONF, TEST_FILES_MDB)
        sync_mdb.download()
        qualified_mdb_filename = sync_mdb.absolutePath(
            os.path.join(TEST_DATA_LOCATION, MDB_PRODUCT_FILENAME))
        assert os.path.isfile(
            qualified_mdb_filename), f"Cannot find file: {qualified_mdb_filename}"

        mdb.init(mdb_files=qualified_mdb_filename)

        # Get the workdir based on where the mdb file is
        cls.workdir = os.path.split(qualified_mdb_filename)[0]
        cls.logdir = os.path.join(cls.workdir, "logs")

        return

    @classmethod
    def teardown_class(cls):

        return

    def test_add_readout_register_distance(self):

        # Get the detector y-size from the MDB
        det_size_y = mdb.get_mdb_value(mdb.mdb_keys.vis_detector_pixel_long_dimension_format)
        assert det_size_y == 4136  # Calculations here rely on this being the value

        # Make some mock data
        mock_y_data = np.array([-100., 0., 500., 1000., 2000., 3000., 4000., 5000.], dtype='>f4')

        mock_data_table = initialise_cti_gal_object_data_table(init_cols={CGOD_TF.y: mock_y_data})

        # Run the function
        add_readout_register_distance(mock_data_table)

        # Check the results are as expected
        ro_dist = mock_data_table[CGOD_TF.readout_dist]

        assert np.allclose(ro_dist, np.array([-100., 0., 500., 1000., 2000., 1136., 136., -864.]))

        return

    def test_calculate_regression_results(self):

        # Make some mock data
        m = 1e-5
        b = -0.2
        g1_err = 0.25

        sigmal_tol = 5  # Pass test if calculations are within 5 sigma

        l = 200  # Length of good data
        lnan = 5  # Length of bad data
        lzero = 5  # Length of zero-weight data
        ltot = l + lnan + lzero

        rng = np.random.default_rng(seed=12345)

        g1_err_data = g1_err * np.ones(ltot, dtype='>f4')
        weight_data = np.power(g1_err_data, -2)
        readout_dist_data = np.linspace(0, 2100, l + lnan + lzero, dtype='>f4')
        g1_data = (m * readout_dist_data + b + g1_err_data * rng.standard_normal(size=ltot)).astype('>f4')

        # Set mock snr, bg, colour, and size values to test different bins

        indices = np.indices((ltot,), dtype=int,)[0]
        zeros = np.zeros(ltot, dtype='>f4')
        ones = np.ones(ltot, dtype='>f4')

        snr_data = np.where(indices % 2 < 1, ones, zeros)
        bg_data = np.where(indices % 4 < 2, ones, zeros)
        colour_data = np.where(indices % 8 < 4, ones, zeros)
        size_data = np.where(indices % 16 < 8, ones, zeros)

        # Make the last bit of data bad or zero weight
        weight_data[-lnan - lzero:-lzero] = np.NaN
        readout_dist_data[-lnan - lzero:-lzero] = np.NaN
        g1_data[-lnan - lzero:-lzero] = np.NaN
        weight_data[-lzero:] = 0

        object_data_table = initialise_cti_gal_object_data_table(init_cols={CGOD_TF.weight_LensMC: weight_data,
                                                                            CGOD_TF.readout_dist: readout_dist_data,
                                                                            CGOD_TF.snr: snr_data,
                                                                            CGOD_TF.bg: bg_data,
                                                                            CGOD_TF.colour: colour_data,
                                                                            CGOD_TF.size: size_data,
                                                                            CGOD_TF.g1_image_LensMC: g1_data})

        # Run the function
        regression_results_table = calculate_regression_results(object_data_table=object_data_table,
                                                                product_type="EXP",
                                                                test_case=CtiGalTestCases.GLOBAL,)

        # Check the results

        assert regression_results_table.meta[RR_TF.m.product_type] == "EXP"
        assert len(regression_results_table) == 1

        rr_row = regression_results_table[0]

        assert rr_row[RR_TF.weight_KSB] == 0
        assert np.isnan(rr_row[RR_TF.slope_KSB])

        readout_dist_mean = np.mean(readout_dist_data[:l])
        ex_slope_err = g1_err / np.sqrt(np.sum((readout_dist_data[:l] - readout_dist_mean)**2))
        ex_intercept_err = ex_slope_err * np.sqrt(np.sum(readout_dist_data[:l]**2) / l)

        assert rr_row[RR_TF.weight_LensMC] == l / g1_err**2
        assert np.isclose(rr_row[RR_TF.slope_LensMC], m, atol=sigmal_tol * ex_slope_err)
        assert np.isclose(rr_row[RR_TF.slope_err_LensMC], ex_slope_err, rtol=0.1)
        assert np.isclose(rr_row[RR_TF.intercept_LensMC], b, atol=sigmal_tol * ex_intercept_err)
        assert np.isclose(rr_row[RR_TF.intercept_err_LensMC], ex_intercept_err, rtol=0.1)
        assert np.isclose(rr_row[RR_TF.slope_intercept_covar_LensMC], 0, atol=5 * ex_slope_err * ex_intercept_err)

        # Test the calculation is sensible for each binning
        for test_case in CtiGalTestCases:
            if test_case == CtiGalTestCases.GLOBAL or test_case == CtiGalTestCases.EPOCH:
                continue
            for bin_limits in ((-0.5, 0.5), (0.5, 1.5)):
                bin_regression_results_table = calculate_regression_results(object_data_table=object_data_table,
                                                                            product_type="OBS",
                                                                            test_case=test_case,
                                                                            bin_limits=bin_limits)
                rr_row = bin_regression_results_table[0]

                # Just check the slope here. Give root-2 times the tolerance since we're only using half the data
                assert np.isclose(rr_row[RR_TF.slope_LensMC], m, atol=np.sqrt(2.) * sigmal_tol * ex_slope_err)

        return
