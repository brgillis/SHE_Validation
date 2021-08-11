""" @file plot_shear_bias.py

    Created 8 July 2021

    Code to make plots for shear bias validation test.
"""

__updated__ = "2021-08-11"

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
from typing import Dict, List, Optional, Sequence

from SHE_PPT import file_io
from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS)
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, linregress_with_errors
from SHE_PPT.pipeline_utility import ValidationConfigKeys
from SHE_PPT.table_utility import SheTableFormat
from astropy.table import Column, Table
from matplotlib import pyplot as plt

import SHE_Validation
from SHE_Validation.plotting import ValidationPlotter
from SHE_Validation_ShearBias.constants.shear_bias_default_config import D_SHEAR_BIAS_CONFIG_DEFAULTS
import numpy as np


logger = getLogger(__name__)

TITLE_FONTSIZE: float = 12
AXISLABEL_FONTSIZE: float = 12
TEXT_SIZE: float = 12
PLOT_FORMAT: str = "png"
C_DIGITS: int = 5
M_DIGITS: int = 3
SIGMA_DIGITS: int = 1


class ShearBiasPlotter(ValidationPlotter):

    # Attributes with fixed values
    bootstrap_seed: int = 12345
    n_bootstrap: int = 1000

    # Attributes set directly at init
    gal_matched_table: Table
    method: ShearEstimationMethods
    workdir: str

    # Attributes calculated at init
    sem_tf: SheTableFormat
    good_rows: Sequence[bool]
    fitclass_zero_rows: Sequence[bool]
    _d_g_in = Dict[int, Sequence[float]]
    _d_g_out = Dict[int, Sequence[float]]
    _d_g_out_err = Dict[int, Sequence[float]]

    # Attributes calculated when plotting methods are called
    _d_bias_measurements: Dict[int, BiasMeasurements]
    _d_bias_plot_filename: Dict[int, str]

    def __init__(self,
                 l_method_matched_catalog_filenames: List[str],
                 method: ShearEstimationMethods,
                 workdir: str) -> None:

        super().__init__()

        # Set attrs directly
        self.l_method_matched_catalog_filenames = l_method_matched_catalog_filenames
        self.method = method
        self.workdir = workdir

        # Init empty dicts for intermediate data used when plotting
        self._d_bias_measurements = {}
        self._d_bias_plot_filename = {}

        # Determine attrs from kwargs
        self.sem_tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]

        # Read in each table and get the data we need out of it
        l_g1_in: List[Column] = []
        l_g2_in: List[Column] = []
        l_g1_out: List[Column] = []
        l_g2_out: List[Column] = []
        l_g1_out_err: List[Column] = []
        l_g2_out_err: List[Column] = []
        l_fitclass_zero_rows: List[Sequence[bool]] = []

        method_matched_catalog_filename: str
        for method_matched_catalog_filename in self.l_method_matched_catalog_filenames:

            if method_matched_catalog_filename is None:
                continue

            qualified_method_matched_catalog_filename: str = os.path.join(self.workdir, method_matched_catalog_filename)
            logger.info(
                f"Reading in matched catalog for method {method} from {qualified_method_matched_catalog_filename}.")
            gal_matched_table: Table = Table.read(qualified_method_matched_catalog_filename, hdu=1)

            good_rows: Sequence[bool] = gal_matched_table[self.sem_tf.fit_flags] == 0

            l_g1_in.append(-(gal_matched_table[self.sem_tf.tu_gamma1] /
                             (1 - gal_matched_table[self.sem_tf.tu_kappa]))[good_rows])
            l_g2_in.append((gal_matched_table[self.sem_tf.tu_gamma2] /
                            (1 - gal_matched_table[self.sem_tf.tu_kappa]))[good_rows])

            l_g1_out.append((gal_matched_table[self.sem_tf.g1])[good_rows])
            l_g2_out.append((gal_matched_table[self.sem_tf.g2])[good_rows])

            l_g1_out_err.append((gal_matched_table[self.sem_tf.g1_err])[good_rows])
            l_g2_out_err.append((gal_matched_table[self.sem_tf.g2_err])[good_rows])

            l_fitclass_zero_rows.append((gal_matched_table[self.sem_tf.fit_class] == 0)[good_rows])

        # Check if we have some data, otherwise use empty arrays
        if len(l_g1_in) > 0:
            self.d_g_in = {1: np.concatenate(l_g1_in),
                           2: np.concatenate(l_g2_in)}
            self.d_g_out = {1: np.concatenate(l_g1_out),
                            2: np.concatenate(l_g2_out)}
            self.d_g_out_err = {1: np.concatenate(l_g1_out_err),
                                2: np.concatenate(l_g2_out_err)}
            self.fitclass_zero_rows = np.concatenate(l_fitclass_zero_rows)
        else:
            self.d_g_in = {1: np.array([], dtype=float),
                           2: np.array([], dtype=float)}
            self.d_g_out = {1: np.array([], dtype=float),
                            2: np.array([], dtype=float)}
            self.d_g_out_err = {1: np.array([], dtype=float),
                                2: np.array([], dtype=float)}
            self.fitclass_zero_rows = np.array([], dtype=bool)

    # Property getters and setters

    @property
    def d_bias_measurements(self):
        return self._d_bias_measurements

    @d_bias_measurements.setter
    def d_bias_measurements(self, d_bias_measurements):
        if d_bias_measurements is None:
            self._d_bias_measurements = {}
        else:
            self._d_bias_measurements = d_bias_measurements

    @property
    def d_bias_plot_filename(self):
        return self._d_bias_plot_filename

    @d_bias_plot_filename.setter
    def d_bias_plot_filename(self, d_bias_plot_filename):
        if d_bias_plot_filename is None:
            self._d_bias_plot_filename = {}
        else:
            self._d_bias_plot_filename = d_bias_plot_filename

    @property
    def d_g_in(self):
        return self._d_g_in

    @d_g_in.setter
    def d_g_in(self, d_g_in):
        if d_g_in is None:
            self._d_g_in = {}
        else:
            self._d_g_in = d_g_in

    @property
    def d_g_out(self):
        return self._d_g_out

    @d_g_out.setter
    def d_g_out(self, d_g_out):
        if d_g_out is None:
            self._d_g_out = {}
        else:
            self._d_g_out = d_g_out

    @property
    def d_g_out_err(self):
        return self._d_g_out_err

    @d_g_out_err.setter
    def d_g_out_err(self, d_g_out_err):
        if d_g_out_err is None:
            self._d_g_out_err = {}
        else:
            self._d_g_out_err = d_g_out_err

    # Callable methods

    def _save_component_plot(self, i):
        """ Save the plot for bias component i.
        """

        # Get the filename to save to
        bias_plot_filename = file_io.get_allowed_filename(type_name="SHEAR-BIAS-VAL",
                                                          instance_id=f"{self.method.value}-g{i}-{os.getpid()}".upper(),
                                                          extension=PLOT_FORMAT,
                                                          version=SHE_Validation.__version__)
        qualified_bias_plot_filename = os.path.join(self.workdir, bias_plot_filename)

        # Save the figure and close it
        plt.savefig(qualified_bias_plot_filename, format=PLOT_FORMAT,
                    bbox_inches="tight", pad_inches=0.05)
        logger.info(f"Saved {self.method} g{i} bias plot to {qualified_bias_plot_filename}")

        # Record the filename for this plot in the filenams dict
        self.d_bias_plot_filename[i] = bias_plot_filename

    def plot_component_shear_bias(self,
                                  i,
                                  bootstrap_errors,
                                  require_fitclass_zero,
                                  max_g_in):
        """ Plot shear bias for an individual component.
        """

        # Get data limited to the rows where g_in is less than the allowed max
        g = np.sqrt(self.d_g_in[1]**2 + self.d_g_in[2]**2)
        good_g_in_rows = g < max_g_in

        g_in = self.d_g_in[i][good_g_in_rows]
        g_out = self.d_g_out[i][good_g_in_rows]
        g_out_err = self.d_g_out_err[i][good_g_in_rows]

        # Limit to FITCLASS==0 if desired
        if require_fitclass_zero:
            good_fitclass_zero_rows = self.fitclass_zero_rows[good_g_in_rows]
            g_in = g_in[good_fitclass_zero_rows]
            g_out = g_out[good_fitclass_zero_rows]
            g_out_err = g_out_err[good_fitclass_zero_rows]

        # Perform the linear regression, calculate bias, and save it in the bias dict
        if not bootstrap_errors:

            linregress_results = linregress_with_errors(x=g_in,
                                                        y=g_out,
                                                        y_err=g_out_err)

        else:

            g_table = Table([g_in, g_out, g_out_err], names=("g_in", "g_out", "g_out_err"))

            # Seed the random number generator
            np.random.seed(self.bootstrap_seed)

            # Get a base object for the m and c calculations
            linregress_results = linregress_with_errors(x=g_table["g_in"],
                                                        y=g_table["g_out"],
                                                        y_err=g_table["g_out_err"])

            # Bootstrap to get errors on slope and intercept
            n_sample = len(g_table)

            slope_bs = np.empty(self.n_bootstrap)
            intercept_bs = np.empty(self.n_bootstrap)
            for b_i in range(self.n_bootstrap):
                u = np.random.randint(0, n_sample, n_sample)
                linregress_results_bs = linregress_with_errors(x=g_table[u]["g_in"],
                                                               y=g_table[u]["g_out"],
                                                               y_err=g_table[u]["g_out_err"])
                slope_bs[b_i] = linregress_results_bs.slope
                intercept_bs[b_i] = linregress_results_bs.intercept

            # Update the bias measurements in the output object
            linregress_results.slope_err = np.std(slope_bs)
            linregress_results.intercept_err = np.std(intercept_bs)

        bias = BiasMeasurements(linregress_results)
        self.d_bias_measurements[i] = bias

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Bias measurements for method {self.method}:")
        d_bias_strings = {}
        for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
            d_bias_strings[f"{a}{i}"] = f"{a}{i} = {getattr(bias,a):.{d}f} +/- {getattr(bias,f'{a}_err'):.{d}f} "\
                f"({getattr(bias,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)"
            logger.info(d_bias_strings[f"{a}{i}"])

        # Make a plot of the shear estimates

        # Set up the figure, with a density scatter as a base

        self.fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

        self.density_scatter(g_in, g_out, sort=True, bins=20, colorbar=False, s=1)

        plot_title = f"{self.method} Shear Estimates: g{i}"
        plt.title(plot_title, fontsize=TITLE_FONTSIZE)

        self.ax.set_xlabel(f"True g{i}", fontsize=AXISLABEL_FONTSIZE)
        self.ax.set_ylabel(f"Estimated g{i}", fontsize=AXISLABEL_FONTSIZE)

        # Draw the zero-axes
        self.draw_axes()

        # Draw the line of best-fit
        self.draw_bestfit_line(linregress_results)

        # Reset the axes
        self.reset_axes()

        # Write the bias
        self.ax.text(0.02, 0.98, d_bias_strings[f"c{i}"], horizontalalignment='left', verticalalignment='top',
                     transform=self.ax.transAxes, fontsize=TEXT_SIZE)
        self.ax.text(0.02, 0.93, d_bias_strings[f"m{i}"], horizontalalignment='left', verticalalignment='top',
                     transform=self.ax.transAxes, fontsize=TEXT_SIZE)

        # Save the plot
        self._save_component_plot(i)

        # Clear the plot to make way for future plots
        self.clear_plots()

    def plot_shear_bias(self,
                        pipeline_config=None):
        """ Plot shear bias for both components.
        """

        if pipeline_config is None:
            pipeline_config = D_SHEAR_BIAS_CONFIG_DEFAULTS

        bootstrap_errors = pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS]
        require_fitclass_zero = pipeline_config[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO]
        max_g_in = pipeline_config[ValidationConfigKeys.SBV_MAX_G_IN]

        for i in (1, 2):

            self.plot_component_shear_bias(i,
                                           bootstrap_errors=bootstrap_errors,
                                           require_fitclass_zero=require_fitclass_zero,
                                           max_g_in=max_g_in)
