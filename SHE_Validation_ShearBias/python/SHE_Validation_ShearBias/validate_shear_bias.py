""" @file validate_shear_bias.py

    Created 8 July 2021

    Code to implement shear bias validation test.
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

import os
from argparse import Namespace
from typing import Dict, List

import numpy as np

from SHE_PPT import file_io, products
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements
from SHE_PPT.utility import is_any_type_of_none
from SHE_Validation.config_utility import get_d_bin_limits
from SHE_Validation.constants.default_config import ExecutionMode
from SHE_Validation.constants.test_info import BinParameters
from .constants.shear_bias_test_info import (L_SHEAR_BIAS_TEST_CASE_C_INFO, L_SHEAR_BIAS_TEST_CASE_M_INFO,
                                             NUM_SHEAR_BIAS_TEST_CASES, )
from .data_processing import ShearBiasDataLoader, ShearBiasTestCaseDataProcessor
from .plotting import ShearBiasPlotter
from .results_reporting import fill_shear_bias_test_results

logger = getLogger(__name__)


def validate_shear_bias_from_args(args: Namespace, mode: ExecutionMode) -> None:
    """ @TODO Fill in docstring
    """

    # Get the bin limits from the pipeline_config
    d_l_bin_limits: Dict[BinParameters, np.ndarray] = get_d_bin_limits(args.pipeline_config)

    # Get the list of matched catalog products to be read in, depending on mode
    if mode == ExecutionMode.LOCAL:
        # In local mode, read in the one product and put it in a list of one item
        logger.info(f"Using matched data from product {args.matched_catalog}")
        l_matched_catalog_product_filenames: List[str] = [args.matched_catalog]
    elif mode == ExecutionMode.GLOBAL:
        # In global mode, read in the listfile to get the list of filenames
        logger.info(f"Using matched data from products in listfile {args.matched_catalog_listfile}")
        qualified_matched_catalog_listfile_filename: str = file_io.find_file(args.matched_catalog_listfile,
                                                                             path = args.workdir)
        l_matched_catalog_product_filenames: List[str] = file_io.read_listfile(
            qualified_matched_catalog_listfile_filename)
    else:
        raise ValueError(f"Unrecognized operation mode: {mode}")

    # Init lists of filenames for each method
    d_method_l_table_filenames: Dict[ShearEstimationMethods, List[str]] = {}
    for method in ShearEstimationMethods:
        d_method_l_table_filenames[method] = []

    # Read in the table filenames from each product, for each method
    for matched_catalog_product_filename in l_matched_catalog_product_filenames:

        qualified_matched_catalog_product_filename: str = os.path.join(args.workdir, matched_catalog_product_filename)
        logger.info("Reading in Matched Catalog product from " + qualified_matched_catalog_product_filename)
        matched_catalog_product = file_io.read_xml_product(qualified_matched_catalog_product_filename)

        # Get the list of table filenames for each method and store it if it exists
        for method in ShearEstimationMethods:
            method_matched_catalog_filename = matched_catalog_product.get_method_filename(method)
            if not is_any_type_of_none(method_matched_catalog_filename):
                d_method_l_table_filenames[method].append(method_matched_catalog_filename)

    # Keep a dict of filenames for all plots, which we'll tarball up at the end. We'll only save the plots
    # in the M test case, to avoid duplication

    # Test case name: plot label: filename
    d_d_plot_filenames: Dict[str, Dict[str, str]] = {}

    # Test case name: bin index: component index: bias measurements
    d_l_d_bias_measurements: Dict[str, List[Dict[int, BiasMeasurements]]] = {}

    # Keep track if we have valid data for any method
    data_exists: bool = False

    # Make a data loader for each shear estimation method
    d_data_loaders: Dict[ShearEstimationMethods, ShearBiasDataLoader] = {}
    for method in ShearEstimationMethods:
        d_data_loaders[method] = ShearBiasDataLoader(l_filenames = d_method_l_table_filenames[method],
                                                     workdir = args.workdir,
                                                     method = method)

    # Perform validation for each shear estimation method
    for test_case_index, test_case_info in enumerate(L_SHEAR_BIAS_TEST_CASE_M_INFO):
        
        # Skip this section in a dry run
        if args.dry_run:
            break

        test_case_name: str = test_case_info.name
        method: ShearEstimationMethods = test_case_info.method
        bin_parameter: BinParameters = test_case_info.bins

        # Plot label: filename
        test_case_plot_filenames: Dict[str, str] = {}

        d_d_plot_filenames[test_case_name] = test_case_plot_filenames

        # Failsafe block for each method
        try:
            # Perform a linear regression for e1 and e2 to get bias measurements and make plots

            # Load the data for these bins
            data_loader: ShearBiasDataLoader = d_data_loaders[method]
            data_loader.load_all()

            l_bin_limits = d_l_bin_limits[test_case_info.bins]

            shear_bias_data_processor = ShearBiasTestCaseDataProcessor(data_loader = data_loader,
                                                                       test_case_info = test_case_info,
                                                                       l_bin_limits = l_bin_limits,
                                                                       pipeline_config = args.pipeline_config)
            shear_bias_data_processor.calc()

            # Plot for each bin index
            for bin_index in range(len(l_bin_limits) - 1):
                shear_bias_plotter = ShearBiasPlotter(data_processor = shear_bias_data_processor,
                                                      bin_index = bin_index)
                shear_bias_plotter.plot()

                # Component index: filename
                d_method_bias_plot_filename: Dict[int, str] = shear_bias_plotter.d_bias_plot_filename

                d_l_d_bias_measurements[test_case_name] = shear_bias_data_processor.l_d_bias_measurements

                # Get the name of the corresponding C test case, and store the info for that too
                c_test_case_name: str = L_SHEAR_BIAS_TEST_CASE_C_INFO[test_case_index].name
                d_l_d_bias_measurements[c_test_case_name] = shear_bias_data_processor.l_d_bias_measurements

                # Save the filename for each component plot
                for i in d_method_bias_plot_filename:
                    plot_label: str = f"{method.value}-{bin_parameter.value}-{bin_index}-g{i}"
                    test_case_plot_filenames[plot_label] = d_method_bias_plot_filename[i]

        except Exception as e:
            import traceback
            logger.warning("Failsafe exception block triggered with exception: " + str(e) + ".\n"
                                                                                            "Traceback: " + "".join(
                traceback.format_tb(e.__traceback__)))
        else:
            data_exists = True

    # Create the observation test results product. We don't have a reference product for this, so we have to
    # fill it out manually
    test_result_product = products.she_validation_test_results.create_validation_test_results_product(
        num_tests = NUM_SHEAR_BIAS_TEST_CASES)
    test_result_product.Data.TileId = None
    test_result_product.Data.PointingId = None
    test_result_product.Data.ExposureProductId = None
    # Use the last observation ID, having checked they're all the same above
    test_result_product.Data.ObservationId = matched_catalog_product.Data.ObservationId

    # Fill in the products with the results
    if not args.dry_run:
        # And fill in the observation product
        fill_shear_bias_test_results(test_result_product = test_result_product,
                                     d_l_d_bias_measurements = d_l_d_bias_measurements,
                                     pipeline_config = args.pipeline_config,
                                     d_l_bin_limits = d_l_bin_limits,
                                     workdir = args.workdir,
                                     dl_dl_plot_filenames = d_d_plot_filenames,
                                     method_data_exists = data_exists,
                                     mode = mode)

    # Write out test results product
    file_io.write_xml_product(test_result_product,
                              args.shear_bias_validation_test_results_product, workdir = args.workdir)

    logger.info("Output shear bias validation test results to: " +
                os.path.join(args.workdir, args.shear_bias_validation_test_results_product))

    logger.info("Execution complete.")
