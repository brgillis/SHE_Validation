""" @file validate_cti_gal.py

    Created 24 November 2020 by Bryan Gillis

    Primary function code for performing CTI-Gal validation
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

from os.path import join
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import numpy as np
from astropy.table import Row, Table, vstack as table_vstack

from EL_CoordsUtils import telescope_coords
from SHE_PPT import mdb
from SHE_PPT.argument_parser import (CA_DRY_RUN, CA_MDB, CA_PIPELINE_CONFIG, CA_SHE_MEAS, CA_VIS_CAL_FRAME,
                                     CA_WORKDIR, )
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.file_io import (get_allowed_filename, read_d_method_tables, read_listfile,
                             read_xml_product, write_listfile,
                             write_xml_product, )
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_validation_test_results import create_validation_test_results_product
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.utility import join_without_none
from SHE_Validation.argument_parser import CA_SHE_EXP_TEST_RESULTS_LIST, CA_SHE_EXT_CAT, CA_SHE_OBS_TEST_RESULTS
from SHE_Validation.binning.bin_constraints import get_ids_for_test_cases
from SHE_Validation.config_utility import get_d_l_bin_limits
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo
from SHE_Validation.utility import get_object_id_list_from_se_tables
from ST_DataModelBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
from . import __version__
from .constants.cti_gal_test_info import (L_CTI_GAL_TEST_CASE_INFO,
                                          NUM_CTI_GAL_TEST_CASES, )
from .data_processing import calculate_regression_results
from .file_io import CtiGalPlotFileNamer
from .input_data import get_raw_cti_gal_object_data, sort_raw_object_data_into_table
from .plot_cti import CtiPlotter
from .results_reporting import fill_cti_gal_validation_results
from .table_formats.regression_results import TF as RR_TF

MSG_COMPLETE = "Complete!"

logger = getLogger(__name__)


def run_validate_cti_gal_from_args(d_args: Dict[str, Any]):
    """
        Main function for CTI-Gal validation
    """

    # Get commonly-used variables from the args
    workdir = d_args[CA_WORKDIR]

    # Load in the files in turn to make sure there aren't any issues with them.

    # Load the MDB
    qualified_mdb_filename = join(workdir, d_args[CA_MDB])
    logger.info(f"Loading MDB from {qualified_mdb_filename}.")
    mdb.init(qualified_mdb_filename)
    telescope_coords.load_vis_detector_specs(mdb_dict = mdb.full_mdb)
    logger.info(MSG_COMPLETE)

    # Get the bin limits dictionary from the config
    d_l_bin_limits = get_d_l_bin_limits(d_args[CA_PIPELINE_CONFIG])

    # Load the shear measurements

    logger.info("Loading validated shear measurements.")

    # Read in the shear estimates data product, and get the filenames of the tables for each method from it
    d_shear_estimate_tables, _ = read_d_method_tables(d_args[CA_SHE_MEAS],
                                                      workdir = workdir,
                                                      log_info = True)

    # Load the image data as a SHEFrameStack. Limit to object IDs we have shear estimates for
    logger.info("Loading in calibrated frames, exposure segmentation maps, and MER final catalogs as a SHEFrameStack.")
    s_object_ids: Set[int] = get_object_id_list_from_se_tables(d_shear_estimate_tables)
    data_stack = SHEFrameStack.read(exposure_listfile_filename = d_args[CA_VIS_CAL_FRAME],
                                    detections_listfile_filename = d_args[CA_SHE_EXT_CAT],
                                    object_id_list = s_object_ids,
                                    workdir = workdir,
                                    load_images = False,
                                    prune_images = False,
                                    mode = 'denywrite')
    logger.info(MSG_COMPLETE)

    # TODO: Use products from the frame stack
    # Load the exposure products, to get needed metadata for output
    l_vis_calibrated_frame_filename = read_listfile(join(workdir, d_args[CA_VIS_CAL_FRAME]),
                                                    log_info = True)
    l_vis_calibrated_frame_product = []
    for vis_calibrated_frame_filename in l_vis_calibrated_frame_filename:
        vis_calibrated_frame_prod = read_xml_product(vis_calibrated_frame_filename,
                                                     workdir = workdir,
                                                     log_info = True)
        if not isinstance(vis_calibrated_frame_prod, dpdVisCalibratedFrame):
            raise ValueError("Vis calibrated frame product from " + vis_calibrated_frame_filename
                             + " is invalid type.")
        l_vis_calibrated_frame_product.append(vis_calibrated_frame_prod)

    # Log a warning if no data from any method and set a flag for later code to refer to
    if all(value is None for value in d_shear_estimate_tables.values()):
        logger.warning("No method has any data associated with it.")
        method_data_exists = False
    else:
        method_data_exists = True

    logger.info(MSG_COMPLETE)

    # Run the validation
    if not d_args[CA_DRY_RUN]:
        (d_exposure_regression_results_tables,
         d_observation_regression_results_tables,
         plot_filenames) = validate_cti_gal(data_stack = data_stack,
                                            shear_estimate_tables = d_shear_estimate_tables,
                                            d_bin_limits = d_l_bin_limits,
                                            workdir = workdir)
    else:
        d_exposure_regression_results_tables = None
        d_observation_regression_results_tables = None
        plot_filenames = None

    logger.info("Creating and outputting validation test result data products.")

    # Set up output product, using the VIS Calibrated Frame product as a reference
    (l_exp_test_result_filename,
     l_exp_test_result_product,
     obs_test_result_product,
     vis_calibrated_frame_product) = load_from_vis_calibrated_frame(l_vis_calibrated_frame_product)

    # Fill in the products with the results
    if not d_args[CA_DRY_RUN]:

        # Get the regression results tables for this test case

        # Fill in each exposure product in turn with results
        for product_index, exp_test_result_product in enumerate(l_exp_test_result_product):
            fill_cti_gal_validation_results(test_result_product = exp_test_result_product,
                                            workdir = workdir,
                                            regression_results_row_index = product_index,
                                            d_l_test_results = d_exposure_regression_results_tables,
                                            pipeline_config = d_args[CA_PIPELINE_CONFIG],
                                            d_l_bin_limits = d_l_bin_limits,
                                            method_data_exists = method_data_exists)

        # And fill in the observation product
        fill_cti_gal_validation_results(test_result_product = obs_test_result_product,
                                        workdir = workdir,
                                        regression_results_row_index = 0,
                                        d_l_test_results = d_observation_regression_results_tables,
                                        pipeline_config = d_args[CA_PIPELINE_CONFIG],
                                        d_l_bin_limits = d_l_bin_limits,
                                        dl_dl_figures = plot_filenames,
                                        method_data_exists = method_data_exists)

    # Write out the exposure test results products and listfile
    for exp_test_result_product, exp_test_result_filename in zip(l_exp_test_result_product,
                                                                 l_exp_test_result_filename):
        write_xml_product(exp_test_result_product,
                          exp_test_result_filename,
                          workdir = workdir,
                          log_info = True)

    qualified_exp_test_results_filename = join(workdir, d_args[CA_SHE_EXP_TEST_RESULTS_LIST])
    write_listfile(qualified_exp_test_results_filename,
                   l_exp_test_result_filename,
                   log_info = True)

    # Write out observation test results product
    write_xml_product(product = obs_test_result_product,
                      xml_filename = d_args[CA_SHE_OBS_TEST_RESULTS],
                      workdir = workdir,
                      log_info = True)

    logger.info("Execution complete.")


def load_from_vis_calibrated_frame(l_vis_calibrated_frame_product: Sequence[Any]) -> Tuple[List[str],
                                                                                           List[Any],
                                                                                           Any,
                                                                                           Optional[Any]]:
    """ Load in the image data and create validation test result products based off of it.
    """

    l_exp_test_result_product: List[Any] = []
    l_exp_test_result_filename: List[str] = []

    obs_id_check = -1

    vis_calibrated_frame_product: Optional[Any] = None
    for vis_calibrated_frame_product in l_vis_calibrated_frame_product:

        exp_test_result_product: Any = create_validation_test_results_product(
            reference_product = vis_calibrated_frame_product,
            num_tests = NUM_CTI_GAL_TEST_CASES)

        # Get the Observation ID and Pointing ID, and put them in the filename
        obs_id = vis_calibrated_frame_product.Data.ObservationSequence.ObservationId
        pnt_id = vis_calibrated_frame_product.Data.ObservationSequence.PointingId
        exp_test_result_filename = get_allowed_filename(type_name = "EXP-CTI-GAL-VAL-TEST-RESULT",
                                                        instance_id = f"{obs_id}-{pnt_id}",
                                                        extension = ".xml",
                                                        version = __version__,
                                                        subdir = "data")

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
    obs_test_result_product = create_validation_test_results_product(
        num_exposures = len(l_vis_calibrated_frame_product),
        num_tests = NUM_CTI_GAL_TEST_CASES)
    obs_test_result_product.Data.TileId = None
    obs_test_result_product.Data.PointingId = None
    obs_test_result_product.Data.ExposureProductId = None
    if vis_calibrated_frame_product is not None:
        # Use the last observation ID, having checked they're all the same above
        obs_test_result_product.Data.ObservationId = vis_calibrated_frame_product.Data.ObservationSequence.ObservationId

    return (l_exp_test_result_filename,
            l_exp_test_result_product,
            obs_test_result_product,
            vis_calibrated_frame_product)


def validate_cti_gal(data_stack: SHEFrameStack,
                     shear_estimate_tables: Dict[ShearEstimationMethods, Table],
                     d_bin_limits: Dict[BinParameters, np.ndarray],
                     workdir: str) -> Tuple[Dict[str, List[Union[Table, Row]]],
                                            Dict[str, List[Union[Table, Row]]],
                                            Dict[str, Dict[str, str]]]:
    """ Perform CTI-Gal validation tests on a loaded-in data_stack (SHEFrameStack object) and shear estimates tables
        for each shear estimation method.
    """

    # First, we'll need to get the pixel coords of each object in the table in each exposure, along with the detector
    # and quadrant where it's found and e1/2 in world coords. We'll start by
    # getting them in a raw format by looping over objects
    l_raw_object_data = get_raw_cti_gal_object_data(data_stack = data_stack,
                                                    d_shear_estimate_tables = shear_estimate_tables)

    # Now sort the raw data into tables (one for each exposure)
    l_object_data_table = sort_raw_object_data_into_table(l_raw_object_data = l_raw_object_data)

    # Loop over each test case, filling in results tables for each and adding them to the results dict
    d_l_exposure_regression_results_tables: Dict[str, List[Table]] = {}
    d_l_observation_regression_results_tables: Dict[str, List[Table]] = {}
    plot_filenames: Dict[str, Dict[str, str]] = {}

    # Get IDs for all bins
    d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = L_CTI_GAL_TEST_CASE_INFO,
                                                        d_bin_limits = d_bin_limits,
                                                        detections_table = data_stack.detections_catalogue,
                                                        d_measurements_tables = shear_estimate_tables,
                                                        data_stack = data_stack)

    for test_case_info in L_CTI_GAL_TEST_CASE_INFO:

        # Initialise for this test case
        method = test_case_info.method
        plot_filenames[test_case_info.name] = {}
        test_case_bin_limits = d_bin_limits[test_case_info.bins]
        num_bins = len(test_case_bin_limits) - 1
        l_l_test_case_object_ids = d_l_l_test_case_object_ids[test_case_info.name]

        # Double check we have at least one bin
        assert num_bins >= 1

        l_exposure_regression_results_tables: List[Optional[Union[Table, Row]]] = [None] * num_bins
        l_observation_regression_results_tables: List[Optional[Union[Table, Row]]] = [None] * num_bins

        for bin_index in range(num_bins):

            # Get info for this bin
            l_test_case_object_ids = l_l_test_case_object_ids[bin_index]
            bin_limits = test_case_bin_limits[bin_index:bin_index + 2]

            # We'll now loop over the table for each exposure, eventually getting regression results and plots
            # for each

            exposure_regression_results_table = RR_TF.init_table(product_type = "EXP")

            for exp_index, object_data_table in enumerate(l_object_data_table):

                # Calculate the results of the regression and add it to the results table
                exposure_regression_results_row = calculate_regression_results(object_data_table = object_data_table,
                                                                               l_ids_in_bin = l_test_case_object_ids,
                                                                               method = method,
                                                                               index = exp_index,
                                                                               product_type = "EXP",
                                                                               bootstrap = False)
                exposure_regression_results_table.add_row(exposure_regression_results_row)

                # Make a plot for each exposure
                make_and_save_cti_gal_plot(method = method,
                                           test_case_info = test_case_info,
                                           bin_index = bin_index,
                                           exp_index = exp_index,
                                           object_data_table = object_data_table,
                                           bin_limits = bin_limits,
                                           l_test_case_object_ids = l_test_case_object_ids,
                                           d_d_plot_filenames = plot_filenames,
                                           workdir = workdir)

            # With the exposures done, we'll now do a test for the observation as a whole on a merged table
            merged_object_table = table_vstack(tables = l_object_data_table)

            # We use bootstrap error calculations for the observation, since y errors aren't fully independent (due
            # to most objects being in the table multiple times at different x positions, but the same y position)
            observation_regression_results_table = calculate_regression_results(object_data_table = merged_object_table,
                                                                                l_ids_in_bin = l_test_case_object_ids,
                                                                                method = method,
                                                                                product_type = "OBS",
                                                                                bootstrap = True)

            # Make a plot for the observation
            make_and_save_cti_gal_plot(method = method,
                                       test_case_info = test_case_info,
                                       bin_index = bin_index,
                                       exp_index = None,
                                       object_data_table = merged_object_table,
                                       bin_limits = bin_limits,
                                       l_test_case_object_ids = l_test_case_object_ids,
                                       d_d_plot_filenames = plot_filenames,
                                       workdir = workdir)

            l_exposure_regression_results_tables[bin_index] = exposure_regression_results_table
            l_observation_regression_results_tables[bin_index] = observation_regression_results_table

        # Fill in the results of this test case in the output dict
        d_l_exposure_regression_results_tables[test_case_info.name] = l_exposure_regression_results_tables
        d_l_observation_regression_results_tables[
            test_case_info.name] = l_observation_regression_results_tables

    # And we're done here, so return the results and object tables
    return d_l_exposure_regression_results_tables, d_l_observation_regression_results_tables, plot_filenames


def make_and_save_cti_gal_plot(method: ShearEstimationMethods,
                               test_case_info: TestCaseInfo,
                               bin_index: int,
                               exp_index: Optional[int],
                               object_data_table: Table,
                               bin_limits: Sequence[float],
                               l_test_case_object_ids: Sequence[int],
                               d_d_plot_filenames: Dict[str, Dict[str, str]],
                               workdir: str) -> None:
    """ Creates a CTI-Gal regression plot for a given data slice, saves it, and records the filename of the saved
        plot in the provided d_d_plot_filenames dict.
    """

    # Create a file namer, and use dependency injection to provide it to the created plotter
    file_namer = CtiGalPlotFileNamer(method = method,
                                     bin_parameter = test_case_info.bins,
                                     bin_index = bin_index,
                                     exp_index = exp_index,
                                     workdir = workdir)
    plotter = CtiPlotter(file_namer = file_namer,
                         object_table = object_data_table,
                         bin_limits = bin_limits,
                         l_ids_in_bin = l_test_case_object_ids, )

    plotter.plot()

    # Save the name of the created plot in the d_d_plot_filenames dict
    plot_label = join_without_none([method.value, exp_index, test_case_info.bins.value, bin_index])
    d_d_plot_filenames[test_case_info.name][plot_label] = plotter.plot_filename
