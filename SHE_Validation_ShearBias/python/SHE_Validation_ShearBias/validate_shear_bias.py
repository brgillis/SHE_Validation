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
from SHE_PPT import products
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, linregress_with_errors
from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf
from astropy.table import Table
from matplotlib import pyplot as plt

import SHE_Validation
from SHE_Validation.plotting import density_scatter, draw_axes, draw_bestfit_line


logger = getLogger(__name__)

methods = ("KSB", "LensMC", "MomentsML", "REGAUSS")

shear_estimation_method_table_formats = {"KSB": ksbm_tf,
                                         "REGAUSS": regm_tf,
                                         "MomentsML": mmlm_tf,
                                         "LensMC": lmcm_tf}

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


def validate_shear_bias_from_args(args):
    """ @TODO Fill in docstring
    """

    # Read in the shear estimates data product, and get the filenames of the tables for each method from it.
    qualified_matched_catalog_product_filename = file_io.find_file(args.matched_catalog,
                                                                   path=args.workdir)
    logger.info("Reading in Matched Catalog product from " + qualified_matched_catalog_product_filename)
    matched_catalog_product = file_io.read_xml_product(qualified_matched_catalog_product_filename)

    # Keep a list of filenams for all plots, which we'll tarball up at the end
    all_plot_filenames = []

    for method in methods:

        method_matched_catalog_filename = matched_catalog_product.get_method_filename(method)
        if method_matched_catalog_filename is None:
            continue

        sem_tf = shear_estimation_method_table_formats[method]

        qualified_method_matched_catalog_filename = os.path.join(args.workdir, method_matched_catalog_filename)
        logger.info(f"Reading in matched catalog for method {method} from {qualified_method_matched_catalog_filename}.")
        gal_matched_table = Table.read(qualified_method_matched_catalog_filename, hdu=1)

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

                linregress_results = linregress_with_errors(x=g_in,
                                                            y=g_out,
                                                            y_err=g_out_err)

                bias = BiasMeasurements(linregress_results)

                d_bias_strings = {}
                for a, d in (("c", C_DIGITS),
                             ("m", M_DIGITS)):
                    d_bias_strings[f"{a}{i}"] = (f"{a}{i} = {getattr(bias,a):.{d}f} +/- {getattr(bias,f'{a}_err'):.{d}f} "
                                                 f"({getattr(bias,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)")
                    logger.info(d_bias_strings[f"{a}{i}"])

                # Make a plot of the shear estimates

                # Set up the figure, with a density scatter as a base

                fig = plt.figure()

                plot_title = f"{method} Shear Estimates: g{i}"
                ax = fig.add_subplot(1, 1, 1, label=plot_title)

                density_scatter(g_in, g_out, fig=fig, ax=ax, sort=True, bins=20, colorbar=False, s=1)

                plt.title(plot_title, fontsize=TITLE_FONTSIZE)

                fig.subplots_adjust(wspace=0, hspace=0, bottom=0.1, right=0.95, top=0.95, left=0.12)

                ax = fig.add_subplot(1, 1, 1, label=plot_title)

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
                ax.text(0.02, 0.98, d_bias_strings[f"c{i}"],
                        horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,
                        fontsize=TEXT_SIZE)
                ax.text(0.02, 0.93, d_bias_strings[f"m{i}"],
                        horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,
                        fontsize=TEXT_SIZE)

                # Save the plot

                bias_plot_filename = file_io.get_allowed_filename(type_name="SHEAR-BIAS-VAL",
                                                                  instance_id=f"{method}-g{i}".upper(),
                                                                  extension=PLOT_FORMAT,
                                                                  version=SHE_Validation.__version__)
                qualified_bias_plot_filename = os.path.join(args.workdir, bias_plot_filename)

                plt.savefig(qualified_bias_plot_filename, format=PLOT_FORMAT,
                            bbox_inches="tight", pad_inches=0.05)
                logger.info(f"Saved {method} g{i} bias plot to {qualified_bias_plot_filename}")

                # Append to list only after the plot has been written, in case something goes wrong
                all_plot_filenames.append(bias_plot_filename)

                plt.close()

        except Exception as e:
            import traceback
            logger.warning("Failsafe exception block triggered with exception: " + str(e) + ".\n"
                           "Traceback: " + "".join(traceback.format_tb(e.__traceback__)))
