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

from copy import deepcopy
import os
from typing import NamedTuple, Dict, Sequence

from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods, D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS)
from SHE_PPT.math import BiasMeasurements, LinregressResults, linregress_with_errors
from SHE_PPT.table_formats.she_lensmc_tu_matched import tf as TF
from SHE_PPT.table_utility import SheTableFormat
import pytest

from ElementsServices.DataSync import DataSync
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation_ShearBias.constants.shear_bias_test_info import BASE_SHEAR_BIAS_TEST_CASE_M_INFO,\
    BASE_SHEAR_BIAS_TEST_CASE_C_INFO
from SHE_Validation_ShearBias.data_processing import ShearBiasTestCaseDataProcessor,\
    C_DIGITS, M_DIGITS, SIGMA_DIGITS
from SHE_Validation_ShearBias.plotting import ShearBiasPlotter
import numpy as np


class MockDataLoader(NamedTuple):
    d_g_in: Dict[int, Sequence[float]]
    d_g_out: Dict[int, Sequence[float]]
    d_g_out_err: Dict[int, Sequence[float]]
    method: ShearEstimationMethods
    workdir: str


class MockDataProcessor(NamedTuple):

    method: ShearEstimationMethods
    bin_parameter: BinParameters
    bin_index: int
    workdir: str

    d_g_in: Dict[int, Sequence[float]]
    d_g_out: Dict[int, Sequence[float]]
    d_g_out_err: Dict[int, Sequence[float]]

    d_bias_measurements: Dict[int, BiasMeasurements]
    d_linregress_results: Dict[int, LinregressResults]
    d_bias_strings: Dict[int, str]

    def calc(self, *args, **kwargs):
        """ Mock version of the calc method so it can be called without raising an exception."""
        pass


class TestShearBias:
    """ Unit tests for plotting shear bias results
    """

    METHOD: ShearEstimationMethods = ShearEstimationMethods.LENSMC
    BINS: BinParameters = BinParameters.GLOBAL
    BIN_INDEX: int = 0

    # Details of mock data
    M1 = 2e-4
    M2 = -1e-3
    C1 = -0.2
    C2 = 0.01

    G1_IN_ERR = 0.02
    G1_OUT_ERR = 0.25

    G2_IN_ERR = 0.03
    G2_OUT_ERR = 0.35

    L = 100000  # Length of good data
    LNAN = 5  # Length of bad data
    LZERO = 5  # Length of zero-weight data
    LTOT = L + LNAN + LZERO

    @classmethod
    def setup_class(cls):
        """ Setup is handled in setup method due to use of tmpdir fixture.
        """
        pass

    @classmethod
    def teardown_class(cls):
        """ Necessary presence alongside setup_class.
        """
        pass

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        """ Sets up workdir and data for our use.
        """

        # Set up workdir
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok=True)

        # Set up an RNG
        self.rng = np.random.default_rng(seed=54352)

        # Set up the data we'll be processing

        full_g1_in_data = self.G1_IN_ERR * self.rng.standard_normal(size=self.LTOT)
        full_g1_out_err_data = self.G1_OUT_ERR * np.ones(self.LTOT, dtype='>f4')
        full_g1_out_data = (self.M1 * full_g1_in_data + self.C1 +
                            full_g1_out_err_data * self.rng.standard_normal(size=self.LTOT))

        full_g2_in_data = self.G2_IN_ERR * self.rng.standard_normal(size=self.LTOT)
        full_g2_out_err_data = self.G2_OUT_ERR * np.ones(self.LTOT, dtype='>f4')
        full_g2_out_data = (self.M2 * full_g2_in_data + self.C2 +
                            full_g2_out_err_data * self.rng.standard_normal(size=self.LTOT))

        # Get arrays of just the good data
        g1_in_data = full_g1_in_data[:self.L]
        g1_out_err_data = full_g1_out_err_data[:self.L]
        g1_out_data = full_g1_out_data[:self.L]

        g2_in_data = full_g2_in_data[:self.L]
        g2_out_err_data = full_g2_out_err_data[:self.L]
        g2_out_data = full_g2_out_data[:self.L]

        # Put the data into a table

        self.matched_table = TF.init_table(size=self.LTOT)

        self.matched_table[TF.tu_gamma1] = full_g1_in_data
        self.matched_table[TF.tu_gamma2] = full_g2_in_data
        self.matched_table[TF.tu_kappa] = np.zeros_like(full_g1_in_data)

        self.matched_table[TF.g1] = full_g1_out_data
        self.matched_table[TF.g1_err] = full_g1_out_err_data
        self.matched_table[TF.g2] = full_g2_out_data
        self.matched_table[TF.g2_err] = full_g2_out_err_data
        self.matched_table[TF.weight] = 0.5 * full_g1_out_err_data**-2

        # Make a mock data loader we can use for tests which assume data has already been loaded in
        self.mock_data_loader: MockDataLoader = MockDataLoader(method=self.METHOD,
                                                               workdir=self.workdir,
                                                               d_g_in={1: g1_in_data,
                                                                       2: g2_in_data},
                                                               d_g_out={1: g1_out_data,
                                                                        2: g2_out_data},
                                                               d_g_out_err={1: g1_out_err_data,
                                                                            2: g2_out_err_data},)

        # Similarly, make a mock data processor to use for tests

        g1_linregress_results = linregress_with_errors(x=g1_in_data,
                                                       y=g1_out_data,
                                                       y_err=g1_out_err_data)
        g1_bias_measurements = BiasMeasurements(g1_linregress_results)

        g2_linregress_results = linregress_with_errors(x=g2_in_data,
                                                       y=g2_out_data,
                                                       y_err=g2_out_err_data)
        g2_bias_measurements = BiasMeasurements(g2_linregress_results)

        self.mock_data_processor: MockDataProcessor = MockDataProcessor(method=self.METHOD,
                                                                        bin_parameter=BinParameters.GLOBAL,
                                                                        bin_index=self.BIN_INDEX,
                                                                        workdir=self.workdir,
                                                                        d_g_in={1: g1_in_data,
                                                                                2: g2_in_data},
                                                                        d_g_out={1: g1_out_data,
                                                                                 2: g2_out_data},
                                                                        d_g_out_err={1: g1_out_err_data,
                                                                                     2: g2_out_err_data},
                                                                        d_bias_measurements={1: g1_bias_measurements,
                                                                                             2: g2_bias_measurements},
                                                                        d_linregress_results={1: g1_linregress_results,
                                                                                              2: g2_linregress_results},
                                                                        d_bias_strings={"m1": "m1 bias string",
                                                                                        "m2": "m2 bias string",
                                                                                        "c1": "c1 bias string",
                                                                                        "c2": "c2 bias string"},)

        # Make mock test case info to use

        self.m_test_case_info: TestCaseInfo = deepcopy(BASE_SHEAR_BIAS_TEST_CASE_M_INFO)
        self.m_test_case_info.method = self.METHOD
        self.m_test_case_info.bins = self.BINS

        self.c_test_case_info: TestCaseInfo = deepcopy(BASE_SHEAR_BIAS_TEST_CASE_C_INFO)
        self.c_test_case_info.method = self.METHOD
        self.c_test_case_info.bins = self.BINS

    def test_data_loader(self):
        """ Tests loading in shear bias data.
        """
        pass

    def test_data_processor(self):
        """ Tests processing shear bias data.
        """

        # Process the data and check that it matches the mock processor
        data_processor = ShearBiasTestCaseDataProcessor(data_loader=self.mock_data_loader,
                                                        test_case_info=self.m_test_case_info,
                                                        bin_index=self.BIN_INDEX)

        # Check basic attributes
        assert data_processor.method == self.mock_data_processor.method
        assert data_processor.bin_parameter == self.mock_data_processor.bin_parameter
        assert data_processor.bin_index == self.mock_data_processor.bin_index
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
            lr: LinregressResults = data_processor.d_linregress_results[i]
            ex_lr: LinregressResults = self.mock_data_processor.d_linregress_results[i]
            a: str
            for a in ("slope", "intercept", "slope_err", "intercept_err"):
                np.testing.assert_allclose(getattr(lr, a), getattr(ex_lr, a))

            # Check bias measurements
            bm: BiasMeasurements = data_processor.d_bias_measurements[i]
            ex_bm: BiasMeasurements = self.mock_data_processor.d_bias_measurements[i]
            a: str
            for a in ("m", "c", "m_err", "c_err", "mc_covar"):
                np.testing.assert_allclose(getattr(bm, a), getattr(ex_bm, a))

            # Check bias strings
            a: str
            d: int
            for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
                ai = f"{a}{i}"
                bias_string = data_processor.d_bias_strings[ai]

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

        plotter = ShearBiasPlotter(data_processor=self.mock_data_processor)
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
