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
from astropy.table import Table

from .plot_shear_bias import ShearBiasPlotter


logger = getLogger(__name__)

methods = ("KSB", "LensMC", "MomentsML", "REGAUSS")


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

        qualified_method_matched_catalog_filename = os.path.join(args.workdir, method_matched_catalog_filename)
        logger.info(f"Reading in matched catalog for method {method} from {qualified_method_matched_catalog_filename}.")
        gal_matched_table = Table.read(qualified_method_matched_catalog_filename, hdu=1)

        # Perform a linear regression for e1 and e2 to get bias measurements and make plots

        try:

            shear_bias_plotter = ShearBiasPlotter(gal_matched_table, method, workdir=args.workdir)

            shear_bias_plotter.plot_shear_bias()

            d_method_bias_measurements = shear_bias_plotter.d_bias_measurements
            d_method_bias_plot_filename = shear_bias_plotter.d_bias_plot_filename

            all_plot_filenames += d_method_bias_plot_filename.values()

        except Exception as e:
            import traceback
            logger.warning("Failsafe exception block triggered with exception: " + str(e) + ".\n"
                           "Traceback: " + "".join(traceback.format_tb(e.__traceback__)))