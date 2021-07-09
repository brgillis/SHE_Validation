""" @file validate_shear_bias.py

    Created 8 July 2021

    Code to implement shear bias validation test.
"""

__updated__ = "2021-07-09"

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

from SHE_PPT import file_io
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, linregress_with_errors
from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf
from matplotlib import pyplot as plt

import SHE_Validation
from SHE_Validation.plotting import density_scatter, draw_axes, draw_bestfit_line

logger = getLogger(__name__)


galcat_gamma1_colname = "GAMMA1"
galcat_gamma2_colname = "GAMMA2"
galcat_kappa_colname = "KAPPA"

TITLE_FONTSIZE = 12
AXISLABEL_FONTSIZE = 12
TEXT_SIZE = 12
PLOT_FORMAT = "png"
C_DIGITS = 5
M_DIGITS = 3
SIGMA_DIGITS = 1

shear_estimation_method_table_formats = {"KSB": ksbm_tf,
                                         "REGAUSS": regm_tf,
                                         "MomentsML": mmlm_tf,
                                         "LensMC": lmcm_tf}


class ShearBiasPlotter():

    # Attributes set directly at init
    gal_matched_table = None
    method = None
    workdir = None

    # Attributes calculated at init
    sem_tf = None
    good_rows = None
    _d_g_in = None
    _d_g_out = None
    _d_g_out_err = None

    # Attributes calculated when plotting methods are called
    _d_bias_measurements = None
    all_plot_filenames = None

    def __init__(self, gal_matched_table, method, workdir):

        # Set attrs directly
        self.gal_matched_table = gal_matched_table
        self.method = method
        self.workdir = workdir

        # Determine attrs from kwargs
        self.sem_tf = shear_estimation_method_table_formats[method]

        good_rows = gal_matched_table[self.sem_tf.fit_flags] == 0

        g1_in = -gal_matched_table[galcat_gamma1_colname] / (1 - gal_matched_table[galcat_kappa_colname])
        g2_in = gal_matched_table[galcat_gamma2_colname] / (1 - gal_matched_table[galcat_kappa_colname])

        self.d_g_in = {1: g1_in[good_rows],
                       2: g2_in[good_rows]}
        self.d_g_out = {1: gal_matched_table[self.sem_tf.g1][good_rows],
                        2: gal_matched_table[self.sem_tf.g2][good_rows]}
        self.d_g_out_err = {1: gal_matched_table[self.sem_tf.g1_err][good_rows],
                            2: gal_matched_table[self.sem_tf.g2_err][good_rows]}

        # Set as None attributes to be set when plotting methods are called
        self.d_bias_measurements = None

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

    def plot_component_shear_bias(self, i):
        """ Plot shear bias for an individual component.
        """

        g_in = self.d_g_in[i]
        g_out = self.d_g_out[i]
        g_out_err = self.d_g_out_err[i]

        # Perform the linear regression and calculate bias
        linregress_results = linregress_with_errors(x=g_in, y=g_out,
                                                    y_err=g_out_err)
        bias = BiasMeasurements(linregress_results)

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Bias measurements for method {self.method}:")
        d_bias_strings = {}
        for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
            d_bias_strings[f"{a}{i}"] = f"{a}{i} = {getattr(bias,a):.{d}f} +/- {getattr(bias,f'{a}_err'):.{d}f} "\
                f"({getattr(bias,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)"
            logger.info(d_bias_strings[f"{a}{i}"])

        # Make a plot of the shear estimates

        # Set up the figure, with a density scatter as a base

        fig = plt.figure()
        plot_title = f"{self.method} Shear Estimates: g{i}"
        ax = fig.add_subplot(1, 1, 1, label=plot_title)
        fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

        density_scatter(g_in, g_out, fig=fig, ax=ax, sort=True, bins=20, colorbar=False, s=1)

        plt.title(plot_title, fontsize=TITLE_FONTSIZE)

        ax.set_xlabel(f"True g{i}", fontsize=AXISLABEL_FONTSIZE)
        ax.set_ylabel(f"Estimated g{i}", fontsize=AXISLABEL_FONTSIZE)

        # Draw the zero-axes
        xlim, ylim = draw_axes(ax)

        # Draw the line of best-fit
        draw_bestfit_line(ax, linregress_results, xlim=xlim)

        # Reset the axes
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Write the bias
        ax.text(0.02, 0.98, d_bias_strings[f"c{i}"], horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,
                fontsize=TEXT_SIZE)
        ax.text(0.02, 0.93, d_bias_strings[f"m{i}"],
                horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,
                fontsize=TEXT_SIZE)

        # Save the plot
        bias_plot_filename = file_io.get_allowed_filename(type_name="SHEAR-BIAS-VAL",
                                                          instance_id=f"{self.method}-g{i}".upper(),
                                                          extension=PLOT_FORMAT,
                                                          version=SHE_Validation.__version__)
        qualified_bias_plot_filename = os.path.join(self.workdir, bias_plot_filename)
        plt.savefig(qualified_bias_plot_filename, format=PLOT_FORMAT,
                    bbox_inches="tight", pad_inches=0.05)
        logger.info(f"Saved {self.method} g{i} bias plot to {qualified_bias_plot_filename}")

        plt.close()

        self.d_bias_measurements[i] = bias

        return bias_plot_filename

    def plot_shear_bias(self):
        """ Plot shear bias for both components.
        """

        self.all_plot_filenames = []

        for i in (1, 2):

            component_plot_filename = self.plot_component_shear_bias(i)

            self.all_plot_filenames.append(component_plot_filename)
