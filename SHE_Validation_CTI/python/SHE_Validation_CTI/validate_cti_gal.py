""" @file validate_cti_gal.py

    Created 24 November 2020 by Bryan Gillis

    Primary function code for performing CTI-Gal validation
"""
from os.path import join
from typing import Dict

from EL_CoordsUtils import telescope_coords
from SHE_PPT import mdb
from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import METHODS, D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.file_io import (read_xml_product, write_xml_product, read_listfile, write_listfile,
                             get_allowed_filename, filename_exists)
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import read_analysis_config
from SHE_PPT.products.she_validation_test_results import create_validation_test_results_product
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_utility import is_in_format
from astropy import table

from SHE_Validation_CTI.constants.cti_gal_test_info import NUM_CTI_GAL_TEST_CASES
from SHE_Validation_CTI.plot_cti_gal import CtiGalPlotter
import numpy as np

from . import __version__
from .constants.cti_gal_default_config import (AnalysisConfigKeys, FailSigmaScaling,
                                               CTI_GAL_DEFAULT_CONFIG, FAILSAFE_BIN_LIMITS)
from .constants.cti_gal_test_info import (NUM_METHOD_CTI_GAL_TEST_CASES, D_CTI_GAL_TEST_CASE_INFO,
                                          CtiGalTestCases)
from .data_processing import add_readout_register_distance, calculate_regression_results
from .input_data import get_raw_cti_gal_object_data, sort_raw_object_data_into_table
from .results_reporting import fill_cti_gal_validation_results
from .table_formats.regression_results import initialise_regression_results_table


__updated__ = "2021-07-14"

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


logger = getLogger(__name__)


def run_validate_cti_gal_from_args(args):
    """
        Main function for CTI-Gal validation
    """

    # Load in the files in turn to make sure there aren't any issues with them.

    # Load the MDB
    qualified_mdb_filename = join(args.workdir, args.mdb)
    logger.info(f"Loading MDB from {qualified_mdb_filename}.")
    mdb.init(qualified_mdb_filename)
    telescope_coords.load_vis_detector_specs(mdb_dict=mdb.full_mdb)
    logger.info("Complete!")

    # Load the configuration, and convert values in it to the proper type

    bin_limits_cline_args = {AnalysisConfigKeys.CGV_SNR_BIN_LIMITS.value:
                             getattr(args, D_CTI_GAL_TEST_CASE_INFO[CtiGalTestCases.SNR].bins_cline_arg),
                             AnalysisConfigKeys.CGV_BG_BIN_LIMITS.value:
                             getattr(args, D_CTI_GAL_TEST_CASE_INFO[CtiGalTestCases.BG].bins_cline_arg),
                             AnalysisConfigKeys.CGV_COLOUR_BIN_LIMITS.value:
                             getattr(args, D_CTI_GAL_TEST_CASE_INFO[CtiGalTestCases.COLOUR].bins_cline_arg),
                             AnalysisConfigKeys.CGV_SIZE_BIN_LIMITS.value:
                             getattr(args, D_CTI_GAL_TEST_CASE_INFO[CtiGalTestCases.SIZE].bins_cline_arg), }

    if type(args.pipeline_config) is str or args.pipeline_config is None:
        pipeline_config = read_analysis_config(args.pipeline_config,
                                               workdir=args.workdir,
                                               cline_args=bin_limits_cline_args,
                                               defaults=CTI_GAL_DEFAULT_CONFIG)
    elif type(args.pipeline_config) is dict:
        pipeline_config = args.pipeline_config
    else:
        raise TypeError("run_validate_cti_gal_from_args: args.pipeline_config is an unexpectedd type - %s" %
                        type(args.pipeline_config))

    # Check that the fail sigma scaling is in the enum (silently convert to lower case)
    fail_sigma_scaling_lower = pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value].lower()
    if not FailSigmaScaling.is_allowed_value(fail_sigma_scaling_lower):
        err_string = (f"Fail sigma scaling option {pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value]}" +
                      " is not recognized. Allowed options are:")
        for allowed_option in FailSigmaScaling:
            err_string += "\n  " + allowed_option.value
        raise ValueError(err_string)
    pipeline_config[AnalysisConfigKeys.CGV_FAIL_SIGMA_SCALING.value] = fail_sigma_scaling_lower

    # Convert to expected data types
    pipeline_config[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value] = float(
        pipeline_config[AnalysisConfigKeys.CGV_SLOPE_FAIL_SIGMA.value])
    pipeline_config[AnalysisConfigKeys.CGV_INTERCEPT_FAIL_SIGMA.value] = float(
        pipeline_config[AnalysisConfigKeys.CGV_INTERCEPT_FAIL_SIGMA.value])

    d_bin_limits = {}
    for test_case_label in CtiGalTestCases:
        bin_limits_key = D_CTI_GAL_TEST_CASE_INFO[test_case_label].bins_config_key
        if bin_limits_key is None:
            # None signifies not relevant to this test or not yet set up. Fill in with the failsafe limits just in case
            d_bin_limits[test_case_label] = np.array(list(map(float, FAILSAFE_BIN_LIMITS.strip().split())), dtype=float)
            continue
        bin_limits_string = pipeline_config[bin_limits_key]
        try:
            bin_limits_list = list(map(float, bin_limits_string.strip().split()))
            bin_limits_array = np.array(bin_limits_list, dtype=float)
            # Sort bin limits ascending
            np.sort(bin_limits_array)
            if len(bin_limits_array) < 2:
                raise ValueError("At least two bin limits must be provided.")
        except ValueError as e:
            logger.warning(f"Cannot interpret bin limits \"{bin_limits_string}\" for {test_case_label} - " +
                           f"must be list of floats separated by whitespace. Failsafe limits " +
                           f"({FAILSAFE_BIN_LIMITS}) will be used. Exception was: {e}")
            bin_limits_list = list(map(float, FAILSAFE_BIN_LIMITS.strip().split()))
            bin_limits_array = np.array(bin_limits_list, dtype=float)
        d_bin_limits[test_case_label] = bin_limits_array

    # Load the image data as a SHEFrameStack
    logger.info("Loading in calibrated frames, exposure segmentation maps, and MER final catalogs as a SHEFrameStack.")
    data_stack = SHEFrameStack.read(exposure_listfile_filename=args.vis_calibrated_frame_listfile,
                                    detections_listfile_filename=args.mer_final_catalog_listfile,
                                    workdir=args.workdir,
                                    memmap=True,
                                    mode='denywrite')
    logger.info("Complete!")

    # Load the exposure products, to get needed metadata for output
    l_vis_calibrated_frame_filename = read_listfile(join(args.workdir, args.vis_calibrated_frame_listfile))
    l_vis_calibrated_frame_product = []
    for vis_calibrated_frame_filename in l_vis_calibrated_frame_filename:
        vis_calibrated_frame_prod = read_xml_product(vis_calibrated_frame_filename, workdir=args.workdir)
        if isinstance(vis_calibrated_frame_prod, products.vis_calibrated_frame.dpdVisCalibratedFrame):
            l_vis_calibrated_frame_product.append(vis_calibrated_frame_prod)
        else:
            raise ValueError("Vis calibrated frame product from " + vis_calibrated_frame_filename
                             + " is invalid type.")

    # Load the shear measurements

    logger.info("Loading validated shear measurements.")

    qualified_she_validated_measurements_product_filename = join(args.workdir, args.she_validated_measurements_product)
    shear_estimates_prod = read_xml_product(qualified_she_validated_measurements_product_filename)

    if not isinstance(shear_estimates_prod, products.she_validated_measurements.dpdSheValidatedMeasurements):
        raise ValueError("Shear estimates product from " + qualified_she_validated_measurements_product_filename
                         + " is invalid type.")

    # Load the table for each method
    d_shear_estimate_tables = {}
    for method in METHODS:

        filename = shear_estimates_prod.get_method_filename(method)

        if filename_exists(filename):
            shear_measurements_table = table.Table.read(join(args.workdir, filename), format='fits')
            d_shear_estimate_tables[method] = shear_measurements_table
            if not is_in_format(shear_measurements_table,
                                D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method],
                                strict=False):
                logger.warning("Shear estimates table from " +
                               join(args.workdir, filename) + " is in invalid format.")
                d_shear_estimate_tables[method] = None
        else:
            d_shear_estimate_tables[method] = None

    # Log a warning if no data from any method and set a flag for later code to refer to
    if all(value is None for value in d_shear_estimate_tables.values()):
        logger.warning("No method has any data associated with it.")
        method_data_exists = False
    else:
        method_data_exists = True

    logger.info("Complete!")

    plot_filenames = [{}]

    # Run the validation
    if not args.dry_run:
        (d_exposure_regression_results_tables,
         d_observation_regression_results_tables) = validate_cti_gal(data_stack=data_stack,
                                                                     shear_estimate_tables=d_shear_estimate_tables,
                                                                     d_bin_limits=d_bin_limits,
                                                                     workdir=args.workdir)

    # Set up output product

    logger.info("Creating and outputting validation test result data products.")

    l_exp_test_result_product = []
    l_exp_test_result_filename = []

    obs_id_check = -1
    for vis_calibrated_frame_product in l_vis_calibrated_frame_product:

        exp_test_result_product = create_validation_test_results_product(reference_product=vis_calibrated_frame_product,
                                                                         num_tests=NUM_METHOD_CTI_GAL_TEST_CASES)

        # Get the Observation ID and Pointing ID, and put them in the filename
        obs_id = vis_calibrated_frame_product.Data.ObservationSequence.ObservationId
        pnt_id = vis_calibrated_frame_product.Data.ObservationSequence.PointingId
        exp_test_result_filename = get_allowed_filename(type_name="EXP-CTI-GAL-VAL-TEST-RESULT",
                                                        instance_id=f"{obs_id}-{pnt_id}",
                                                        extension=".xml",
                                                        version=__version__,
                                                        subdir="data")

        # Store the product and filename in lists
        l_exp_test_result_product.append(exp_test_result_product)
        l_exp_test_result_filename.append(exp_test_result_filename)

        # Check the obs_ids are all the same (important below)
        # First time
        if obs_id_check == -1:
            # Store the value in obs_id_check
            obs_id_check = obs_id
        else:
            if obs_id_check != obs_id:
                logger.warning("Inconsistent Observation IDs in VIS calibrated frame product.")

    # Create the observation test results product. We don't have a reference product for this, so we have to
    # fill it out manually
    obs_test_result_product = create_validation_test_results_product(num_exposures=len(l_vis_calibrated_frame_product),
                                                                     num_tests=NUM_METHOD_CTI_GAL_TEST_CASES)
    obs_test_result_product.Data.TileId = None
    obs_test_result_product.Data.PointingId = None
    obs_test_result_product.Data.ExposureProductId = None
    # Use the last observation ID, having checked they're all the same above
    obs_test_result_product.Data.ObservationId = vis_calibrated_frame_product.Data.ObservationSequence.ObservationId

    # Fill in the products with the results
    if not args.dry_run:

        # Get the regression results tables for this test case

        # Fill in each exposure product in turn with results
        for product_index, exp_test_result_product in enumerate(l_exp_test_result_product):
            fill_cti_gal_validation_results(test_result_product=exp_test_result_product,
                                            workdir=args.workdir,
                                            regression_results_row_index=product_index,
                                            d_regression_results_tables=d_exposure_regression_results_tables,
                                            pipeline_config=pipeline_config,
                                            d_bin_limits=d_bin_limits,
                                            method_data_exists=method_data_exists)

        # And fill in the observation product
        fill_cti_gal_validation_results(test_result_product=obs_test_result_product,
                                        workdir=args.workdir,
                                        regression_results_row_index=0,
                                        d_regression_results_tables=d_observation_regression_results_tables,
                                        pipeline_config=pipeline_config,
                                        d_bin_limits=d_bin_limits,
                                        figures=plot_filenames,
                                        method_data_exists=method_data_exists)

    # Write out the exposure test results products and listfile
    for exp_test_result_product, exp_test_result_filename in zip(l_exp_test_result_product,
                                                                 l_exp_test_result_filename):
        write_xml_product(exp_test_result_product, exp_test_result_filename, workdir=args.workdir)
    qualified_exp_test_results_filename = join(args.workdir, args.she_exposure_validation_test_results_listfile)
    write_listfile(qualified_exp_test_results_filename, l_exp_test_result_filename)

    logger.info("Output exposure validation test results to: " +
                qualified_exp_test_results_filename)

    # Write out observation test results product
    write_xml_product(obs_test_result_product,
                      args.she_observation_validation_test_results_product, workdir=args.workdir)

    logger.info("Output observation validation test results to: " +
                join(args.workdir, args.she_observation_validation_test_results_product))

    logger.info("Execution complete.")


def validate_cti_gal(data_stack: SHEFrameStack,
                     shear_estimate_tables: Dict[str, table.Table],
                     d_bin_limits: Dict[str, np.ndarray],
                     workdir: str):
    """ Perform CTI-Gal validation tests on a loaded-in data_stack (SHEFrameStack object) and shear estimates tables
        for each shear estimation method.
    """

    # First, we'll need to get the pixel coords of each object in the table in each exposure, along with the detector
    # and quadrant where it's found and e1/2 in world coords. We'll start by
    # getting them in a raw format by looping over objects
    l_raw_object_data = get_raw_cti_gal_object_data(data_stack=data_stack, shear_estimate_tables=shear_estimate_tables)

    # Now sort the raw data into tables (one for each exposure)
    l_object_data_table = sort_raw_object_data_into_table(raw_object_data_list=l_raw_object_data)

    # Loop over each test case, filling in results tables for each and adding them to the results dict
    d_exposure_regression_results_tables = {}
    d_observation_regression_results_tables = {}
    plot_filenames = [None] * NUM_CTI_GAL_TEST_CASES

    for test_case_index, test_case in enumerate(CtiGalTestCases):

        # Initialise for this test case
        plot_filenames[test_case_index] = {}
        test_case_bin_limits = d_bin_limits[test_case]
        num_bins = len(test_case_bin_limits) - 1

        # Double check we have at least one bin
        assert num_bins >= 1

        l_test_case_exposure_regression_results_tables = [None] * num_bins
        l_test_case_observation_regression_results_tables = [None] * num_bins

        for bin_index in range(num_bins):

            # We'll now loop over the table for each exposure, eventually getting regression results and plots
            # for each

            exposure_regression_results_table = initialise_regression_results_table(product_type="EXP")

            for object_data_table in l_object_data_table:

                # We'll need to calculate the distance from the readout register, so add columns for that as well
                add_readout_register_distance(object_data_table=object_data_table)

                # Calculate the results of the regression and add it to the results table
                exposure_regression_results_row = calculate_regression_results(object_data_table=object_data_table,
                                                                               test_case=test_case,
                                                                               bin_limits=test_case_bin_limits[
                                                                                   bin_index:bin_index + 2])[0]
                exposure_regression_results_table.add_row(exposure_regression_results_row)

                # Make a plot for each method
                for method in METHODS:
                    plotter = CtiGalPlotter(object_table=object_data_table,
                                            method=method,
                                            test_case=test_case,
                                            d_bin_limits=d_bin_limits,
                                            bin_index=bin_index,
                                            workdir=workdir,)
                    plotter.plot_cti_gal()
                    plot_label = f"{method}-{test_case.value}-{bin_index}"
                    plot_filenames[test_case_index][plot_label] = plotter.cti_gal_plot_filename

            # With the exposures done, we'll now do a test for the observation as a whole on a merged table
            merged_object_table = table.vstack(tables=l_object_data_table)

            observation_regression_results_table = calculate_regression_results(object_data_table=merged_object_table,
                                                                                product_type="OBS",
                                                                                test_case=test_case,
                                                                                bin_limits=test_case_bin_limits[
                                                                                    bin_index:bin_index + 2])

            l_test_case_exposure_regression_results_tables[bin_index] = exposure_regression_results_table
            l_test_case_observation_regression_results_tables[bin_index] = observation_regression_results_table

        # Fill in the results of this test case in the output dict
        d_exposure_regression_results_tables[test_case] = l_test_case_exposure_regression_results_tables
        d_observation_regression_results_tables[test_case] = l_test_case_observation_regression_results_tables

    # And we're done here, so return the results and object tables
    return (d_exposure_regression_results_tables, d_observation_regression_results_tables,
            l_object_data_table, merged_object_table)
