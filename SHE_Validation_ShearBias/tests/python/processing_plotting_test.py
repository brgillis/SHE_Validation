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
from astropy.table import Table

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.math import BiasMeasurements, LinregressResults, linregress_with_errors
from SHE_PPT.testing.mock_data import (NUM_GOOD_TEST_POINTS, NUM_NAN_TEST_POINTS, NUM_TEST_POINTS,
                                       NUM_ZERO_WEIGHT_TEST_POINTS, )
from SHE_PPT.testing.mock_tum_cat import MockTUMatchedTableGenerator
from SHE_PPT.testing.utility import SheTestCase
from SHE_Validation.binning.bin_constraints import GoodBinnedMeasurementBinConstraint, GoodMeasurementBinConstraint
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.test_info_utility import find_test_case_info
from SHE_Validation.testing.constants import TEST_BIN_PARAMETERS, TEST_METHODS
from SHE_Validation.testing.mock_data import make_mock_bin_limits
from SHE_Validation_ShearBias.constants.shear_bias_test_info import (L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                     )
from SHE_Validation_ShearBias.data_processing import (C_DIGITS, M_DIGITS, SIGMA_DIGITS, ShearBiasDataLoader,
                                                      ShearBiasTestCaseDataProcessor, )
from SHE_Validation_ShearBias.plotting import ShearBiasPlotter


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


class TestShearBias(SheTestCase):
    """ Unit tests for plotting shear bias results
    """

    workdir: str = ""
    logdir: str = ""

    rng: Any

    d_l_bin_limits: Dict[BinParameters, np.ndarray]

    good_ids: np.ndarray

    d_matched_tables: Dict[ShearEstimationMethods, Table]

    d_mock_data_loaders: Dict[ShearEstimationMethods, MockDataLoader]
    d_d_l_mock_data_loaders: Dict[ShearEstimationMethods, Dict[BinParameters, List[MockDataLoader]]]

    d_d_mock_data_processors: Dict[ShearEstimationMethods, Dict[BinParameters, MockDataProcessor]]
    d_d_l_mock_data_processors: Dict[ShearEstimationMethods, Dict[BinParameters, List[MockDataProcessor]]]

    d_d_m_test_case_info: Dict[ShearEstimationMethods, Dict[BinParameters, TestCaseInfo]]
    d_d_c_test_case_info: Dict[ShearEstimationMethods, Dict[BinParameters, TestCaseInfo]]

    def post_setup(self):
        """ Sets up workdir and data for our use.
        """

        # Set up the data we'll be processing

        self.d_l_bin_limits = make_mock_bin_limits()

        full_indices = np.arange(NUM_TEST_POINTS, dtype = int)
        self.good_ids = full_indices[:NUM_GOOD_TEST_POINTS]

        # Set up dicts for each method and bin we'll be testing
        self.d_matched_tables = {}
        self.d_mock_data_loaders = {}
        self.d_d_l_mock_data_loaders = {}
        self.d_d_mock_data_processors = {}
        self.d_d_l_mock_data_processors = {}
        self.d_d_m_test_case_info = {}
        self.d_d_c_test_case_info = {}

        for method_index, method in enumerate([ShearEstimationMethods.LENSMC,
                                               ShearEstimationMethods.KSB]):
            tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]

            matched_table_gen = MockTUMatchedTableGenerator(method = method,
                                                            workdir = self.workdir)

            matched_table = matched_table_gen.get_mock_table()
            self.d_matched_tables[method] = matched_table

            l_good_g1_in: Sequence[float] = -matched_table[tf.tu_gamma1][:NUM_GOOD_TEST_POINTS]
            l_good_g2_in: Sequence[float] = matched_table[tf.tu_gamma2][:NUM_GOOD_TEST_POINTS]
            l_good_g1_out: Sequence[float] = matched_table[tf.g1][:NUM_GOOD_TEST_POINTS]
            l_good_g2_out: Sequence[float] = matched_table[tf.g2][:NUM_GOOD_TEST_POINTS]
            l_good_g1_out_err: Sequence[float] = matched_table[tf.g1_err][:NUM_GOOD_TEST_POINTS]
            l_good_g2_out_err: Sequence[float] = matched_table[tf.g2_err][:NUM_GOOD_TEST_POINTS]

            # Make a mock data loader we can use for tests which assume data has already been loaded in
            self.d_mock_data_loaders[method] = MockDataLoader(method = method,
                                                              workdir = self.workdir,
                                                              d_g_in = {1: l_good_g1_in,
                                                                        2: l_good_g2_in},
                                                              d_g_out = {1: l_good_g1_out,
                                                                         2: l_good_g2_out},
                                                              d_g_out_err = {1: l_good_g1_out_err,
                                                                             2: l_good_g2_out_err}, )

            # Make mock regression results and bias measurements

            g1_linregress_results = linregress_with_errors(x = l_good_g1_in,
                                                           y = l_good_g1_out,
                                                           y_err = l_good_g1_out_err)
            g1_bias_measurements = BiasMeasurements(g1_linregress_results)

            g2_linregress_results = linregress_with_errors(x = l_good_g2_in,
                                                           y = l_good_g2_out,
                                                           y_err = l_good_g2_out_err)
            g2_bias_measurements = BiasMeasurements(g2_linregress_results)

            # Get a separate data processors and test case info for each bin parameter
            self.d_d_m_test_case_info[method] = {}
            self.d_d_c_test_case_info[method] = {}
            self.d_d_l_mock_data_loaders[method] = {}
            self.d_d_mock_data_processors[method] = {}
            self.d_d_l_mock_data_processors[method] = {}

            for bin_parameter in [BinParameters.TOT, BinParameters.SNR]:

                # Make mock test case info to use

                self.d_d_m_test_case_info[method][bin_parameter] = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                                       methods = method,
                                                                                       bin_parameters = bin_parameter,
                                                                                       return_one = True)

                self.d_d_c_test_case_info[method][bin_parameter] = find_test_case_info(L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                                       methods = method,
                                                                                       bin_parameters = bin_parameter,
                                                                                       return_one = True)

                mock_data_processor = MockDataProcessor(method = method,
                                                        bin_parameter = bin_parameter,
                                                        bin_index = 0,
                                                        workdir = self.workdir,
                                                        d_g_in = {1: l_good_g1_in,
                                                                  2: l_good_g2_in},
                                                        d_g_out = {1: l_good_g1_out,
                                                                   2: l_good_g2_out},
                                                        d_g_out_err = {1: l_good_g1_out_err,
                                                                       2: l_good_g2_out_err},
                                                        l_d_bias_measurements = [{1: g1_bias_measurements,
                                                                                  2: g2_bias_measurements}],
                                                        l_d_linregress_results = [{
                                                            1: g1_linregress_results,
                                                            2: g2_linregress_results}],
                                                        l_d_bias_strings = [{"m1": "m1 bias string",
                                                                             "m2": "m2 bias string",
                                                                             "c1": "c1 bias string",
                                                                             "c2": "c2 bias string"}], )
                self.d_d_mock_data_processors[method][bin_parameter] = mock_data_processor

                # noinspection PyTypeChecker
                self.d_d_l_mock_data_loaders[method][bin_parameter] = [None] * (
                        len(self.d_l_bin_limits[bin_parameter]) - 1)
                # noinspection PyTypeChecker
                self.d_d_l_mock_data_processors[method][bin_parameter] = [None] * (
                        len(self.d_l_bin_limits[bin_parameter]) - 1)

                for bin_index in range(len(self.d_l_bin_limits[bin_parameter]) - 1):

                    l_true = np.ones_like(l_good_g1_in, dtype = bool)
                    l_false = np.zeros_like(l_good_g1_in, dtype = bool)

                    bin_slice: np.ndarray
                    if bin_parameter != BinParameters.SNR:
                        bin_slice = l_true
                    else:
                        # Get a slice of alternating true/false, depending on the bin index
                        bin_slice = np.where(matched_table[tf.ID][:NUM_GOOD_TEST_POINTS] % 2 < 1, l_true, l_false)

                        if bin_index == 1:
                            bin_slice = np.logical_not(bin_slice)

                    bin_g1_linregress_results = linregress_with_errors(x = l_good_g1_in[bin_slice],
                                                                       y = l_good_g1_out[bin_slice],
                                                                       y_err = l_good_g1_out_err[bin_slice])
                    bin_g1_bias_measurements = BiasMeasurements(bin_g1_linregress_results)

                    bin_g2_linregress_results = linregress_with_errors(x = l_good_g2_in[bin_slice],
                                                                       y = l_good_g2_out[bin_slice],
                                                                       y_err = l_good_g2_out_err[bin_slice])
                    bin_g2_bias_measurements = BiasMeasurements(bin_g2_linregress_results)

                    mock_data_loader = MockDataLoader(method = method,
                                                      workdir = self.workdir,
                                                      d_g_in = {1: l_good_g1_in[bin_slice],
                                                                2: l_good_g2_in[bin_slice]},
                                                      d_g_out = {1: l_good_g1_out[bin_slice],
                                                                 2: l_good_g2_out[bin_slice]},
                                                      d_g_out_err = {1: l_good_g1_out_err[bin_slice],
                                                                     2: l_good_g2_out_err[bin_slice]}, )
                    self.d_d_l_mock_data_loaders[method][bin_parameter][bin_index] = mock_data_loader

                    mock_data_processor = MockDataProcessor(method = method,
                                                            bin_parameter = bin_parameter,
                                                            bin_index = bin_index,
                                                            workdir = self.workdir,
                                                            d_g_in = {1: l_good_g1_in[bin_slice],
                                                                      2: l_good_g2_in[bin_slice]},
                                                            d_g_out = {1: l_good_g1_out[bin_slice],
                                                                       2: l_good_g2_out[bin_slice]},
                                                            d_g_out_err = {1: l_good_g1_out_err[bin_slice],
                                                                           2: l_good_g2_out_err[bin_slice]},
                                                            l_d_bias_measurements = [{1: bin_g1_bias_measurements,
                                                                                      2: bin_g2_bias_measurements}],
                                                            l_d_linregress_results = [{
                                                                1: bin_g1_linregress_results,
                                                                2: bin_g2_linregress_results}],
                                                            l_d_bias_strings = [{"m1": "m1 bias string",
                                                                                 "m2": "m2 bias string",
                                                                                 "c1": "c1 bias string",
                                                                                 "c2": "c2 bias string"}], )
                    self.d_d_l_mock_data_processors[method][bin_parameter][bin_index] = mock_data_processor

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

        # Test loading, binned on the mock SNR data
        bin_test_method = ShearEstimationMethods.KSB
        bin_test_bin_parameter = BinParameters.SNR

        self.d_matched_tables[bin_test_method].write(qualified_tu_matched_table_filename,
                                                     overwrite = True)

        # Create a data loader object and load in the data
        data_loader = ShearBiasDataLoader(l_filenames = [tu_matched_table_filename],
                                          workdir = self.workdir,
                                          method = bin_test_method)

        bin_constraint_0 = GoodBinnedMeasurementBinConstraint(method = bin_test_method,
                                                              bin_parameter = bin_test_bin_parameter,
                                                              bin_limits = self.d_l_bin_limits[bin_test_bin_parameter][
                                                                           0:2])
        data_loader.load_for_bin_constraint(bin_constraint = bin_constraint_0)
        bin_0_data = set(data_loader.d_g_out[1])

        bin_constraint_1 = GoodBinnedMeasurementBinConstraint(method = bin_test_method,
                                                              bin_parameter = bin_test_bin_parameter,
                                                              bin_limits = self.d_l_bin_limits[bin_test_bin_parameter][
                                                                           1:3])
        data_loader.load_for_bin_constraint(bin_constraint = bin_constraint_1)
        bin_1_data = set(data_loader.d_g_out[1])

        # Make sure the data from the two bins adds up
        assert len(bin_0_data) + len(bin_1_data) == NUM_GOOD_TEST_POINTS

        # Make sure the data from the two bins is non-overlapping
        for x in bin_0_data:
            assert x not in bin_1_data
        for x in bin_1_data:
            assert x not in bin_0_data

    def test_data_processor(self):
        """ Tests processing shear bias data.
        """

        for method in TEST_METHODS:

            mock_data_loader = self.d_mock_data_loaders[method]

            for bin_parameter in TEST_BIN_PARAMETERS:

                m_test_case_info = self.d_d_m_test_case_info[method][bin_parameter]
                l_bin_limits = self.d_l_bin_limits[bin_parameter]

                # Test first for default bin limits

                mock_data_processor = self.d_d_mock_data_processors[method][bin_parameter]

                self._test_specific_data_processor(bin_limits = DEFAULT_BIN_LIMITS,
                                                   test_case_info = m_test_case_info,
                                                   mock_data_loader = mock_data_loader,
                                                   mock_data_processor = mock_data_processor)

                # Now test for actual bin limits
                for bin_index in range(len(l_bin_limits) - 1):

                    bin_limits = l_bin_limits[bin_index: bin_index + 2]

                    # Use a specific mock data loader and processor for this bin
                    bin_mock_data_loader = self.d_d_l_mock_data_loaders[method][bin_parameter][bin_index]
                    bin_mock_data_processor = self.d_d_l_mock_data_processors[method][bin_parameter][bin_index]

                    self._test_specific_data_processor(bin_limits = bin_limits,
                                                       test_case_info = m_test_case_info,
                                                       mock_data_loader = bin_mock_data_loader,
                                                       mock_data_processor = bin_mock_data_processor)

    @staticmethod
    def _test_specific_data_processor(bin_limits: Sequence[float],
                                      test_case_info: TestCaseInfo,
                                      mock_data_loader: MockDataLoader,
                                      mock_data_processor: MockDataProcessor):

        # Process the data and check that it matches the mock processor
        # noinspection PyTypeChecker
        data_processor = ShearBiasTestCaseDataProcessor(data_loader = mock_data_loader,
                                                        test_case_info = test_case_info,
                                                        l_bin_limits = bin_limits)
        # Check basic attributes
        assert data_processor.method == mock_data_processor.method
        assert data_processor.bin_parameter == mock_data_processor.bin_parameter
        assert data_processor.workdir == mock_data_processor.workdir

        # Check input attributes
        i: int
        for i in range(1, 2):
            np.testing.assert_allclose(data_processor.d_g_in[i], mock_data_processor.d_g_in[i])
            np.testing.assert_allclose(data_processor.d_g_out[i], mock_data_processor.d_g_out[i])
            np.testing.assert_allclose(data_processor.d_g_out_err[i],
                                       mock_data_processor.d_g_out_err[i])

        # Check output attributes
        i: int
        for i in range(1, 2):

            # Check linregress results
            lr: LinregressResults = data_processor.l_d_linregress_results[0][i]
            ex_lr: LinregressResults = mock_data_processor.l_d_linregress_results[0][i]
            a: str
            for a in ("slope", "intercept", "slope_err", "intercept_err"):
                np.testing.assert_allclose(getattr(lr, a), getattr(ex_lr, a))

            # Check bias measurements
            bm: BiasMeasurements = data_processor.l_d_bias_measurements[0][i]
            ex_bm: BiasMeasurements = mock_data_processor.l_d_bias_measurements[0][i]
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

        # Test for each bin of each bin parameter of each method

        for method in TEST_METHODS:
            for bin_parameter in TEST_BIN_PARAMETERS:

                l_bin_limits = self.d_l_bin_limits[bin_parameter]

                # Now test for actual bin limits
                for bin_index in range(len(l_bin_limits) - 1):

                    mock_data_processor = self.d_d_l_mock_data_processors[method][bin_parameter][bin_index]

                    # Run the plotting

                    # noinspection PyTypeChecker
                    plotter = ShearBiasPlotter(data_processor = mock_data_processor,
                                               bin_index = 0)
                    plotter.plot()

                    # Check the results

                    d_qualified_plot_filenames = {}

                    for i in (1, 2):

                        qualified_plot_filename = os.path.join(self.workdir, plotter.d_bias_plot_filename[i])
                        d_qualified_plot_filenames[i] = qualified_plot_filename

                        assert method.name in qualified_plot_filename
                        assert f"{bin_parameter.name}-0" in qualified_plot_filename
                        assert os.path.isfile(qualified_plot_filename)

                    assert d_qualified_plot_filenames[1] != d_qualified_plot_filenames[2]
