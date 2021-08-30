""" @file plot_cti_gal_test.py

    Created 12 July 2021

    Unit tests of the plot_cti_gal.py module
"""

__updated__ = "2021-08-30"

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

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
import pytest

from ElementsServices.DataSync import DataSync
from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation_CTI.file_io import CtiGalPlotFileNamer
from SHE_Validation_CTI.plot_cti_gal import CtiGalPlotter
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF
import numpy as np


class TestCase:
    """


    """

    @classmethod
    def setup_class(cls):

        return

    @classmethod
    def teardown_class(cls):

        return

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok=True)

    def test_plot_cti_gal(self):

        method = ShearEstimationMethods.LENSMC

        # Make some mock data
        m = 1e-4
        b = -0.2
        g1_err = 0.25

        l = 100000  # Length of good data
        lnan = 5  # Length of bad data
        lzero = 5  # Length of zero-weight data
        ltot = l + lnan + lzero

        rng = np.random.default_rng(seed=12545)

        g1_err_data = g1_err * np.ones(ltot, dtype='>f4')
        weight_data = np.power(g1_err_data, -2)
        readout_dist_data = np.linspace(0, 2100, l + lnan + lzero, dtype='>f4')
        g1_data = (m * readout_dist_data + b + g1_err_data * rng.standard_normal(size=ltot)).astype('>f4')

        # Make the last bit of data bad or zero weight
        weight_data[-lnan - lzero:-lzero] = np.NaN
        readout_dist_data[-lnan - lzero:-lzero] = np.NaN
        g1_data[-lnan - lzero:-lzero] = np.NaN
        weight_data[-lzero:] = 0

        indices = np.indices((ltot,), dtype=int,)[0]
        object_data_table = CGOD_TF.init_table(init_cols={CGOD_TF.ID: indices,
                                                          CGOD_TF.weight_LensMC: weight_data,
                                                          CGOD_TF.readout_dist: readout_dist_data,
                                                          CGOD_TF.g1_image_LensMC: g1_data})

        # Run the plotting
        file_namer = CtiGalPlotFileNamer(method=method,
                                         bin_parameter=BinParameters.GLOBAL,
                                         bin_index=0,
                                         workdir=self.workdir)
        plotter = CtiGalPlotter(file_namer=file_namer,
                                object_table=object_data_table,
                                bin_limits=DEFAULT_BIN_LIMITS,
                                l_ids_in_bin=indices[:l],)
        plotter.plot()

        # Check the results

        qualified_plot_filename = os.path.join(self.workdir, plotter.plot_filename)

        assert "LENSMC" in qualified_plot_filename
        assert os.path.isfile(qualified_plot_filename)
