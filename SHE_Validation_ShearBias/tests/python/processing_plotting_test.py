""" @file processing_plotting_test.py

    Created 12 July 2021

    Unit tests of the Shear Bias data processing and plotting.
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

import os

from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods, D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS)
from SHE_PPT.table_formats.she_lensmc_tu_matched import tf as TF
from SHE_PPT.table_utility import SheTableFormat
import pytest

from ElementsServices.DataSync import DataSync
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation_ShearBias.data_processing import ShearBiasTestCaseDataProcessor
from SHE_Validation_ShearBias.plotting import ShearBiasPlotter
import numpy as np


class TestShearBias:
    """ Unit tests for plotting shear bias results
    """

    METHOD: ShearEstimationMethods = ShearEstimationMethods.LENSMC

    # Details of mock data
    M1 = 2e-4
    M2 = -1e-3
    C1 = -0.2
    C2 = 0.01
    
    G1_IN_ERR = 0.3
    G1_OUT_ERR = 0.25

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
        
        self.g1_in_data = self.G1_IN_ERR * self.rng.standard_normal(size=self.LTOT)
        g1_out_err_data = self.G1_OUT_ERR * np.ones(self.LTOT, dtype='>f4')
        self.g1_out_data = self.M1 * self.g1_in_data + self.C1 + g1_out_err_data * self.rng.standard_normal(size=self.LTOT)
        
        self.g2_in_data = self.G2_IN_ERR * self.rng.standard_normal(size=self.LTOT)
        g2_out_err_data = self.G2_OUT_ERR * np.ones(self.LTOT, dtype='>f4')
        self.g2_out_data = self.M2 * self.g2_in_data + self.C2 + g2_out_err_data * self.rng.standard_normal(size=self.LTOT)

        # Make the last bit of data bad or zero weight
        
        self.g1_out_data[-self.LNAN - self.LZERO:-self.LZERO] = np.NaN
        self.g1_out_err_data[-self.LNAN - self.LZERO:-self.LZERO] = np.inf
        
        self.g2_out_data[-self.LNAN - self.LZERO:-self.LZERO] = np.NaN
        self.g2_out_err_data[-self.LNAN - self.LZERO:-self.LZERO] = np.inf
        
        # Put the data into a table
        
        self.matched_table = TF.init_table(size=self.LTOT)
        
        self.matched_table[TF.tu_gamma1] = self.g1_in_data
        self.matched_table[TF.tu_gamma2] = self.g2_in_data
        self.matched_table[TF.tu_kappa] = np.zeros_like(self.g1_in_data)
        
        self.matched_table[TF.g1] = self.g1_out_data
        self.matched_table[TF.g1_err] = self.g1_out_err_data
        self.matched_table[TF.g2] = self.g2_out_data
        self.matched_table[TF.g2_err] = self.g2_out_err_data
        self.matched_table[TF.weight] = 0.5*self.g1_out_err_data**-2

    def test_plot_shear_bias(self):
        
        # Process the data
        data_processor = ShearBiasTestCaseDataProcessor(l_method_matched_catalog_filenames:List[str], 
        test_case_info:TestCaseInfo, 
        workdir:str, 
        bin_limits:Optional[Sequence[float]]=None, 
        pipeline_config)

        # Run the plotting
        plotter = ShearBiasPlotter(data_processor=data_processor)
        plotter.plot_shear_bias()

        # Check the results

        qualified_plot_filename = os.path.join(self.workdir, plotter.cti_gal_plot_filename)

        assert "LENSMC" in qualified_plot_filename
        assert os.path.isfile(qualified_plot_filename)
