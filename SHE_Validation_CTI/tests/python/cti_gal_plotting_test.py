"""
:file: tests/python/cti_gal_plotting_test.py

:date: 12 July 2021
:author: Bryan Gillis

Unit tests of the plot_cti.py module
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

import os

import numpy as np

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_Validation.constants.default_config import TOT_BIN_LIMITS
from SHE_Validation.constants.test_info import BinParameters
from SHE_Validation.testing.utility import SheValTestCase
from SHE_Validation_CTI.file_io import CtiGalPlotFileNamer
from SHE_Validation_CTI.plot_cti import CtiPlotter
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF


class TestPlotCti(SheValTestCase):
    """ Test case for CTI validation test plotting.
    """

    def test_plot_cti_gal(self, local_setup):
        method = ShearEstimationMethods.LENSMC

        # Make some mock data
        m = 1e-4
        b = -0.2
        g1_err = 0.25

        l_good = 100000  # Length of good data
        l_nan = 5  # Length of bad data
        l_zero = 5  # Length of zero-weight data
        l_tot = l_good + l_nan + l_zero

        rng = np.random.default_rng(seed=12545)

        g1_err_data = g1_err * np.ones(l_tot, dtype='>f4')
        weight_data = np.power(g1_err_data, -2)
        readout_dist_data = np.linspace(0, 2100, l_good + l_nan + l_zero, dtype='>f4')
        g1_data = (m * readout_dist_data + b + g1_err_data * rng.standard_normal(size=l_tot)).astype('>f4')

        # Make the last bit of data bad or zero weight
        weight_data[-l_nan - l_zero:-l_zero] = np.NaN
        readout_dist_data[-l_nan - l_zero:-l_zero] = np.NaN
        g1_data[-l_nan - l_zero:-l_zero] = np.NaN
        weight_data[-l_zero:] = 0

        indices = np.indices((l_tot,), dtype=int, )[0]
        object_data_table = CGOD_TF.init_table(init_cols={CGOD_TF.ID: indices,
                                                          CGOD_TF.weight_LensMC: weight_data,
                                                          CGOD_TF.readout_dist: readout_dist_data,
                                                          CGOD_TF.g1_image_LensMC: g1_data})

        # Run the plotting
        file_namer = CtiGalPlotFileNamer(method=method,
                                         bin_parameter=BinParameters.TOT,
                                         bin_index=0,
                                         workdir=self.workdir)
        plotter = CtiPlotter(file_namer=file_namer,
                             object_table=object_data_table,
                             bin_limits=TOT_BIN_LIMITS,
                             l_ids_in_bin=indices[:l_good], )
        plotter.plot()

        # Check the results

        qualified_plot_filename = os.path.join(self.workdir, plotter.plot_filename)

        assert "LENSMC" in qualified_plot_filename
        assert os.path.isfile(qualified_plot_filename)
