""" @file processing_plotting_test.py

    Created 12 July 2021

    Unit tests of the Shear Bias data processing and plotting.
"""

__updated__ = "2021-08-31"

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
from typing import Any, Dict, List, NamedTuple, Sequence

import numpy as np
import pytest
from astropy.table import Table

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.math import BiasMeasurements, LinregressResults, linregress_with_errors
from SHE_Validation.binning.bin_constraints import GoodMeasurementBinConstraint
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.test_info_utility import find_test_case_info
from SHE_Validation_ShearBias.constants.shear_bias_test_info import (L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                     )
from SHE_Validation_ShearBias.data_processing import (C_DIGITS, M_DIGITS, SIGMA_DIGITS, ShearBiasDataLoader,
                                                      ShearBiasTestCaseDataProcessor, )
from SHE_Validation_ShearBias.plotting import ShearBiasPlotter
from SHE_Validation_ShearBias.testing.mock_shear_bias_data import (EST_SEED, NUM_GOOD_TEST_POINTS, NUM_NAN_TEST_POINTS,
                                                                   NUM_TEST_POINTS,
                                                                   NUM_ZERO_WEIGHT_TEST_POINTS, TEST_METHODS,
                                                                   cleanup_mock_matched_tables,
                                                                   make_mock_bin_limits, make_mock_matched_table, )


class MockDataLoader(NamedTuple):
    d_g_in: Dict[int, Sequence[float]]
    d_g_out: Dict[int, Sequence[float]]
    d_g_out_err: Dict[int, Sequence[float]]
    method: ShearEstimationMethods
    workdir: str

    def load_for_bin_constraint(self, *args, **kwargs):
        """ Mock version of the load_for_bin_constraint method so it can be called without raising an exception."""
        pass


class MockDataProcessor(NamedTuple):
    method: ShearEstimationMethods
    bin_parameter: BinParameters
    bin_index: int
    workdir: str

    d_g_in: Dict[int, Sequence[float]]
    d_g_out: Dict[int, Sequence[float]]
    d_g_out_err: Dict[int, Sequence[float]]

    l_d_bias_measurements: List[Dict[int, BiasMeasurements]]
    l_d_linregress_results: List[Dict[int, LinregressResults]]
    l_d_bias_strings: List[Dict[str, str]]

    l_bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS

    def calc(self, *args, **kwargs):
        """ Mock version of the calc method so it can be called without raising an exception."""
        pass


class TestShearBias:
    """ Unit tests for plotting shear bias results
    """

    workdir: str = ""
    logdir: str = ""

    rng: Any

    d_l_bin_limits: Dict[BinParameters, np.ndarray]

    good_ids: np.ndarray

    d_matched_tables: Dict[ShearEstimationMethods, Table]
    d_mock_data_loaders: Dict[ShearEstimationMethods, MockDataLoader]
    d_d_l_mock_data_processors: Dict[ShearEstimationMethods, Dict[BinParameters, List[MockDataProcessor]]]
    d_d_m_test_case_info: Dict[ShearEstimationMethods, Dict[BinParameters, TestCaseInfo]]
    d_d_c_test_case_info: Dict[ShearEstimationMethods, Dict[BinParameters, TestCaseInfo]]

    @classmethod
    def setup_class(cls):
        """ Setup is handled in setup method due to use of tmpdir fixture.
        """
        pass

    @classmethod
    def teardown_class(cls):
        """ Necessary presence alongside setup_class.
        """

        # Delete the created data
        if cls.workdir:
            cleanup_mock_matched_tables(cls.workdir)

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir):
        """ Sets up workdir and data for our use.
        """

        # Set up workdir
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok = True)

        # Set up the data we'll be processing

        self.d_l_bin_limits = make_mock_bin_limits()

        full_indices = np.arange(NUM_TEST_POINTS, dtype = int)
        self.good_ids = full_indices[:NUM_GOOD_TEST_POINTS]

        # Set up dicts for each method and bin we'll be testing
        self.d_matched_tables = {}
        self.d_mock_data_loaders = {}
        self.d_d_l_mock_data_processors = {}
        self.d_d_m_test_case_info = {}
        self.d_d_c_test_case_info = {}

        for method_index, method in enumerate([ShearEstimationMethods.LENSMC,
                                               ShearEstimationMethods.KSB]):
            tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]

            matched_table = make_mock_matched_table(method = method,
                                                    seed = EST_SEED + method_index)
            self.d_matched_tables[method] = matched_table

            # Make a mock data loader we can use for tests which assume data has already been loaded in
            self.d_mock_data_loaders[method] = MockDataLoader(method = method,
                                                              workdir = self.workdir,
                                                              d_g_in = {1: -matched_table[tf.tu_gamma1][
                                                                            :NUM_GOOD_TEST_POINTS],
                                                                        2: matched_table[tf.tu_gamma2][
                                                                           :NUM_GOOD_TEST_POINTS]},
                                                              d_g_out = {1: matched_table[tf.g1][
                                                                            :NUM_GOOD_TEST_POINTS],
                                                                         2: matched_table[tf.g2][
                                                                            :NUM_GOOD_TEST_POINTS]},
                                                              d_g_out_err = {1: matched_table[tf.g1_err][
                                                                                :NUM_GOOD_TEST_POINTS],
                                                                             2: matched_table[tf.g2_err][
                                                                                :NUM_GOOD_TEST_POINTS]}, )

            # Similarly, make a mock data processor to use for tests

            g1_linregress_results = linregress_with_errors(x = -matched_table[tf.tu_gamma1],
                                                           y = matched_table[tf.g1],
                                                           y_err = matched_table[tf.g1_err])
            g1_bias_measurements = BiasMeasurements(g1_linregress_results)

            g2_linregress_results = linregress_with_errors(x = matched_table[tf.tu_gamma2],
                                                           y = matched_table[tf.g2],
                                                           y_err = matched_table[tf.g2_err])
            g2_bias_measurements = BiasMeasurements(g2_linregress_results)

            # Get a separate data processors and test case info for each bin parameter
            self.d_d_m_test_case_info[method] = {}
            self.d_d_c_test_case_info[method] = {}
            self.d_d_l_mock_data_processors[method] = {}

            for bin_parameter in [BinParameters.GLOBAL, BinParameters.SNR]:

                # Make mock test case info to use

                self.d_d_m_test_case_info[method][bin_parameter] = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                                       methods = method,
                                                                                       bin_parameters = bin_parameter,
                                                                                       return_one = True)

                self.d_d_c_test_case_info[method][bin_parameter] = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                                       methods = method,
                                                                                       bin_parameters = bin_parameter,
                                                                                       return_one = True)

                self.d_d_l_mock_data_processors[method][bin_parameter] = []

                for bin_index in range(len(self.d_l_bin_limits[bin_parameter]) - 1):

                    mock_data_processor = MockDataProcessor(method = method,
                                                            bin_parameter = bin_parameter,
                                                            bin_index = bin_index,
                                                            workdir = self.workdir,
                                                            d_g_in = {1: -matched_table[tf.tu_gamma1],
                                                                      2: matched_table[tf.tu_gamma2]},
                                                            d_g_out = {1: matched_table[tf.g1],
                                                                       2: matched_table[tf.g2]},
                                                            d_g_out_err = {1: matched_table[tf.g1_err],
                                                                           2: matched_table[tf.g2_err]},
                                                            l_d_bias_measurements = [{1: g1_bias_measurements,
                                                                                      2: g2_bias_measurements}],
                                                            l_d_linregress_results = [{
                                                                1: g1_linregress_results,
                                                                2: g2_linregress_results}],
                                                            l_d_bias_strings = [{"m1": "m1 bias string",
                                                                                 "m2": "m2 bias string",
                                                                                 "c1": "c1 bias string",
                                                                                 "c2": "c2 bias string"}], )
                    self.d_d_l_mock_data_processors[method][bin_parameter].append(mock_data_processor)

    @staticmethod
    def _check_loaded_data(data_loader: ShearBiasDataLoader, mock_data_loader: MockDataLoader):
        # Check that the loaded data is correct
        i: int
        for i in range(1, 2):
            np.testing.assert_allclose(data_loader.d_g_in[i], mock_data_loader.d_g_in[i])
            np.testing.assert_allclose(data_loader.d_g_out[i], mock_data_loader.d_g_out[i])
            np.testing.assert_allclose(data_loader.d_g_out_err[i], mock_data_loader.d_g_out_err[i])

    def test_data_loader(self):
        """ Tests loading in shear bias data.
        """

        # Set up filenames
        tu_matched_table_filename = "tu_matched_table.fits"
        qualified_tu_matched_table_filename = os.path.join(self.workdir, tu_matched_table_filename)

        for method in TEST_METHODS:

            # Write out the table
            self.d_matched_tables[method].write(qualified_tu_matched_table_filename,
                                                overwrite = True)

            # Create a data loader object and load in the data
            data_loader = ShearBiasDataLoader(l_filenames = [tu_matched_table_filename],
                                              workdir = self.workdir,
                                              method = method)
            data_loader.load_ids(self.good_ids)

            self._check_loaded_data(data_loader = data_loader,
                                    mock_data_loader = self.d_mock_data_loaders[method])

            # Try loading with a bin constraint
            bin_constraint = GoodMeasurementBinConstraint(method = method)
            data_loader.load_for_bin_constraint(bin_constraint = bin_constraint)

            self._check_loaded_data(data_loader = data_loader,
                                    mock_data_loader = self.d_mock_data_loaders[method])

            # Try loading all data, and check that NaN values were read in
            data_loader.load_all()
            assert np.isnan(data_loader.d_g_out[1][NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS - 1])
            assert np.isinf(data_loader.d_g_out_err[1][NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS +
                                                       NUM_ZERO_WEIGHT_TEST_POINTS - 1])

    def test_data_processor(self):
        """ Tests processing shear bias data.
        """

        # Process the data and check that it matches the mock processor
        data_processor = ShearBiasTestCaseDataProcessor(data_loader = self.mock_data_loader,
                                                        test_case_info = self.m_test_case_info,
                                                        l_bin_limits = DEFAULT_BIN_LIMITS)

        # Check basic attributes
        assert data_processor.method == self.mock_data_processor.method
        assert data_processor.bin_parameter == self.mock_data_processor.bin_parameter
        assert data_processor.workdir == self.mock_data_processor.workdir

        # Check input attributes
        i: int
        for i in range(1, 2):
            np.testing.assert_allclose(data_processor.d_g_in[i], self.mock_data_processor.d_g_in[i])
            np.testing.assert_allclose(data_processor.d_g_out[i], self.mock_data_processor.d_g_out[i])
            np.testing.assert_allclose(data_processor.d_g_out_err[i], self.mock_data_processor.d_g_out_err[i])

        # Check output attributes
        i: int
        for i in range(1, 2):

            # Check linregress results
            lr: LinregressResults = data_processor.l_d_linregress_results[0][i]
            ex_lr: LinregressResults = self.mock_data_processor.l_d_linregress_results[0][i]
            a: str
            for a in ("slope", "intercept", "slope_err", "intercept_err"):
                np.testing.assert_allclose(getattr(lr, a), getattr(ex_lr, a))

            # Check bias measurements
            bm: BiasMeasurements = data_processor.l_d_bias_measurements[0][i]
            ex_bm: BiasMeasurements = self.mock_data_processor.l_d_bias_measurements[0][i]
            a: str
            for a in ("m", "c", "m_err", "c_err", "mc_covar"):
                np.testing.assert_allclose(getattr(bm, a), getattr(ex_bm, a))

            # Check bias strings
            a: str
            d: int
            for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
                ai = f"{a}{i}"
                bias_string = data_processor.l_d_bias_strings[0][ai]

                assert ai in bias_string

                meas = getattr(bm, a)
                meas_err = getattr(bm, f"{a}_err")
                meas_sigma = getattr(bm, f"{a}_sigma")

                assert f"{meas:.{d}f}" in bias_string
                assert f"{meas_err:.{d}f}" in bias_string
                assert f"{meas_sigma:.{SIGMA_DIGITS}f}" in bias_string

    def test_plotter(self):
        """ Runs a test of plotting the results of a shear bias test.
        """

        # Run the plotting

        plotter = ShearBiasPlotter(data_processor = self.mock_data_processor,
                                   bin_index = 0)
        plotter.plot()

        # Check the results

        d_qualified_plot_filenames = {}

        for i in (1, 2):

            qualified_plot_filename = os.path.join(self.workdir, plotter.d_bias_plot_filename[i])
            d_qualified_plot_filenames[i] = qualified_plot_filename

            assert self.METHOD.name in qualified_plot_filename
            assert self.BINS.name in qualified_plot_filename
            assert os.path.isfile(qualified_plot_filename)

        assert d_qualified_plot_filenames[1] != d_qualified_plot_filenames[2]
