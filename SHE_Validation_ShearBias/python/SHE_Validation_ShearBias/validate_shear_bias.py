""" @file validate_shear_bias.py

    Created 8 July 2021

    Code to implement shear bias validation test.
"""

__updated__ = "2021-07-08"

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

from SHE_PPT import file_io
from SHE_PPT import products
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, linregress_with_errors
from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf
from astropy.table import Table
from matplotlib import pyplot

import SHE_Validation
import numpy as np


logger = getLogger(__name__)

methods = ("KSB", "LensMC", "MomentsML", "REGAUSS")

shear_estimation_method_table_formats = {"KSB": ksbm_tf,
                                         "REGAUSS": regm_tf,
                                         "MomentsML": mmlm_tf,
                                         "LensMC": lmcm_tf}

galcat_gamma1_colname = "GAMMA1"
galcat_gamma2_colname = "GAMMA2"
galcat_kappa_colname = "KAPPA"


def validate_shear_bias_from_args(args):
    """ @TODO Fill in docstring
    """

    # Read in the shear estimates data product, and get the filenames of the tables for each method from it.
    qualified_matched_catalog_product_filename = file_io.find_file(args.matched_catalog,
                                                                   path=args.workdir)
    logger.info("Reading in Matched Catalog product from " + qualified_matched_catalog_product_filename)
    matched_catalog_product = file_io.read_xml_product(qualified_matched_catalog_product_filename)

    for method in methods:

        sem_tf = shear_estimation_method_table_formats[method]

        qualified_method_matched_catalog_filename = os.path.join(
            args.workdir, matched_catalog_product.get_method_filename(method))
        logger.info(f"Reading in matched catalog for method {method} from {qualified_method_matched_catalog_filename}.")
        gal_matched_table = Table.read(qualified_method_matched_catalog_filename)

        # Perform a linear regression for e1 and e2 to get bias measurements and make plots

        try:

            good_rows = gal_matched_table[sem_tf.fit_flags] == 0

            g1_in = -gal_matched_table[galcat_gamma1_colname] / (1 - gal_matched_table[galcat_kappa_colname])
            g2_in = gal_matched_table[galcat_gamma2_colname] / (1 - gal_matched_table[galcat_kappa_colname])

            logger.info(f"Bias measurements for method {method}:")
            for i, g_in, g_out, g_out_err in ((1, g1_in[good_rows], gal_matched_table[sem_tf.g1][good_rows],
                                               gal_matched_table[sem_tf.g1_err][good_rows]),
                                              (2, g2_in[good_rows], gal_matched_table[sem_tf.g2][good_rows],
                                               gal_matched_table[sem_tf.g2_err][good_rows])):

                bias = BiasMeasurements(linregress_with_errors(x=g_in,
                                                               y=g_out,
                                                               y_err=g_out_err))

                d_bias_strings = {}
                for a, d in (("c", 5),
                             ("m", 3)):
                    d_bias_strings[f"{a}{i}"] = (f"{a}{i} = {getattr(bias,a):.{d}f} +/- {getattr(bias,f'{a}_err'):.{d}f} "
                                                 f"({getattr(bias,f'{a}_sigma'):.2f}$\\sigma$)")
                    logger.info(d_bias_strings[f"{a}{i}"])

                # Make a plot of the shear estimates

                TITLE_FONTSIZE = 12
                AXISLABEL_FONTSIZE = 12
                TEXT_SIZE = 12
                PLOT_FORMAT = "png"

                # Set up the figure
                fig = pyplot.figure()

                plot_title = f"{method} Shear Estimates: g{i}"

                pyplot.title(plot_title, fontsize=TITLE_FONTSIZE)

                fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

                ax = fig.add_subplot(1, 1, 1, label=plot_title)
                ax.set_xlabel(f"True g{i}", fontsize=AXISLABEL_FONTSIZE)
                ax.set_ylabel(f"Estimated g{i}", fontsize=AXISLABEL_FONTSIZE)

                ax.scatter(g_in, g_out, label=None,
                           marker=".", color="r",
                           s=1)

                # Draw the zero-axes
                xlim = deepcopy(ax.get_xlim())
                ax.plot(xlim, [0, 0], label=None, color="k", linestyle="solid")

                ylim = deepcopy(ax.get_ylim())
                ax.plot([0, 0], ylim, label=None, color="k", linestyle="solid")

                # Draw the line of best-fit
                bestfit_x = np.array(xlim)
                bestfit_y = (1 + bias.m) * bestfit_x + bias.c
                ax.plot(bestfit_x, bestfit_y, label=None, color="b", linestyle="solid")

                # Reset the axes
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)

                # Write the bias
                ax.text(0.02, 0.98, d_bias_strings[f"c{i}"],
                        horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,
                        fontsize=TEXT_SIZE)
                ax.text(0.02, 0.93, d_bias_strings[f"m{i}"],
                        horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,
                        fontsize=TEXT_SIZE)

                # Save and show it

                qualified_bias_plot_filename = os.path.join(args.workdir, f"{method}_g{i}.{PLOT_FORMAT}")
                pyplot.savefig(qualified_bias_plot_filename, format=PLOT_FORMAT,
                               bbox_inches="tight", pad_inches=0.05)
                logger.info(f"Saved {method} g{i} bias plot to {qualified_bias_plot_filename}")
                pyplot.close()

        except Exception as e:
            import traceback
            logger.warning("Failsafe exception block triggered with exception: " + str(e) + ".\n"
                           "Traceback: " + "".join(traceback.format_tb(e.__traceback__)))
