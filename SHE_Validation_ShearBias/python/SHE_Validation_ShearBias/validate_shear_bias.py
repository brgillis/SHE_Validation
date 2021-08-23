""" @file validate_shear_bias.py

    Created 8 July 2021

    Code to implement shear bias validation test.
"""

__updated__ = "2021-08-12"

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
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import ValidationConfigKeys

from SHE_Validation.config_utility import get_d_bin_limits
from SHE_Validation.constants.default_config import ExecutionMode
from SHE_Validation_ShearBias.constants.shear_bias_test_info import (L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                                                     L_SHEAR_BIAS_TEST_CASE_C_INFO,
                                                                     NUM_SHEAR_BIAS_TEST_CASES)

from SHE_Validation_ShearBias.plotting import ShearBiasPlotter
from .results_reporting import fill_shear_bias_validation_results

logger = getLogger(__name__)


def fix_pipeline_config_types(pipeline_config):
    """ Fixes data types in the pipeline config so they aren't all just strings.
    """

    pipeline_config[ValidationConfigKeys.SBV_MAX_G_IN] = float(
        pipeline_config[ValidationConfigKeys.SBV_MAX_G_IN])
    if not isinstance(pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS], bool):
        pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS] = (
            pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS].lower() in ['true', 't'])
    if not isinstance(pipeline_config[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO], bool):
        pipeline_config[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO] = (
            pipeline_config[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO].lower() in ['true', 't'])

    return pipeline_config


def validate_shear_bias_from_args(args, mode):
    """ @TODO Fill in docstring
    """

    # Fix types in the pipeline_config
    pipeline_config = fix_pipeline_config_types(args.pipeline_config)

    # Get the list of matched catalog products to be read in, depending on mode
    if mode == ExecutionMode.LOCAL:
        # In local mode, read in the one product and put it in a list of one item
        logger.info(f"Using matched data from product {args.matched_catalog}")
        l_matched_catalog_product_filenames = [args.matched_catalog]
    elif mode == ExecutionMode.GLOBAL:
        # In global mode, read in the listfile to get the list of filenames
        logger.info(f"Using matched data from products in listfile {args.matched_catalog_listfile}")
        qualified_matched_catalog_listfile_filename = file_io.find_file(args.matched_catalog_listfile,
                                                                        path=args.workdir)
        l_matched_catalog_product_filenames = file_io.read_listfile(qualified_matched_catalog_listfile_filename)
    else:
        raise ValueError(f"Unrecognized operation mode: {mode}")

    num_matched_catalogs = len(l_matched_catalog_product_filenames)

    # Init lists of filenames for each method
    d_method_l_table_filenames = {}
    for method in ShearEstimationMethods:
        d_method_l_table_filenames[method] = [None] * num_matched_catalogs

    # Read in the table filenames from each product, for each method
    for matched_cat_index, matched_catalog_product_filename in enumerate(l_matched_catalog_product_filenames):

        qualified_matched_catalog_product_filename = os.path.join(args.workdir, matched_catalog_product_filename)
        logger.info("Reading in Matched Catalog product from " + qualified_matched_catalog_product_filename)
        matched_catalog_product = file_io.read_xml_product(qualified_matched_catalog_product_filename)

        # Get the list of table filenames for each method and store it
        method_matched_catalog_filename = matched_catalog_product.get_method_filename(method)
        d_method_l_table_filenames[method][matched_cat_index] = method_matched_catalog_filename

    # Keep a dict of filenames for all plots, which we'll tarball up at the end. We'll only save the plots
    # in the M test case, to avoid duplication
    d_d_plot_filenames = {}
    d_bias_measurements = {}

    # Keep track if we have valid data for any method
    data_exists = False

    # Perform validation for each shear estimation method
    for test_case_index, test_case_info in enumerate(L_SHEAR_BIAS_TEST_CASE_M_INFO):

        test_case_name = test_case_info.name
        method = test_case_info.method
        bin_parameter = test_case_info.bins

        test_case_plot_filenames = {}
        d_d_plot_filenames[test_case_name] = test_case_plot_filenames

        l_method_matched_catalog_filenames = d_method_l_table_filenames[method]

        # Failsafe block for each method
        try:
            # Perform a linear regression for e1 and e2 to get bias measurements and make plots

            shear_bias_plotter = ShearBiasPlotter(l_method_matched_catalog_filenames,
                                                  method=method,
                                                  workdir=args.workdir)
            shear_bias_plotter.plotting(pipeline_config=pipeline_config)

            d_method_bias_plot_filename = shear_bias_plotter.d_bias_plot_filename

            d_bias_measurements[test_case_name] = shear_bias_plotter.d_bias_measurements

            # Get the name of the corresponding C test case, and store the info for that too
            c_test_case_name = L_SHEAR_BIAS_TEST_CASE_C_INFO[test_case_index].name
            d_bias_measurements[c_test_case_name] = shear_bias_plotter.d_bias_measurements

            # Save the filename for each component plot
            for i in d_method_bias_plot_filename:
                plot_label = f"{method.value}-{bin_parameter.value}-g{i}"
                test_case_plot_filenames[plot_label] = d_method_bias_plot_filename[i]
        except Exception as e:
            import traceback
            logger.warning("Failsafe exception block triggered with exception: " + str(e) + ".\n"
                           "Traceback: " + "".join(traceback.format_tb(e.__traceback__)))
        else:
            data_exists = True

    # Create the observation test results product. We don't have a reference product for this, so we have to
    # fill it out manually
    test_result_product = products.she_validation_test_results.create_validation_test_results_product(
        num_tests=NUM_SHEAR_BIAS_TEST_CASES)
    test_result_product.Data.TileId = None
    test_result_product.Data.PointingId = None
    test_result_product.Data.ExposureProductId = None
    # Use the last observation ID, having checked they're all the same above
    test_result_product.Data.ObservationId = matched_catalog_product.Data.ObservationId

    # Fill in the products with the results
    if not args.dry_run:

        d_bin_limits = get_d_bin_limits(args.pipeline_config)

        # And fill in the observation product
        fill_shear_bias_validation_results(test_result_product=test_result_product,
                                           workdir=args.workdir,
                                           d_bin_limits=d_bin_limits,
                                           d_bias_measurements=d_bias_measurements,
                                           pipeline_config=pipeline_config,
                                           dl_l_figures=d_d_plot_filenames,
                                           method_data_exists=data_exists,
                                           mode=mode)

    # Write out test results product
    file_io.write_xml_product(test_result_product,
                              args.shear_bias_validation_test_results_product, workdir=args.workdir)

    logger.info("Output shear bias validation test results to: " +
                os.path.join(args.workdir, args.shear_bias_validation_test_results_product))

    logger.info("Execution complete.")
