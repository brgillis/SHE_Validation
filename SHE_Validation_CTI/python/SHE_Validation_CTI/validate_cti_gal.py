""" @file validate_cti_gal.py

    Created 24 November 2020 by Bryan Gillis

    Primary function code for performing CTI-Gal validation
"""

__updated__ = "2020-12-16"

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
from typing import Dict

from astropy import table

from SHE_PPT import mdb
from SHE_PPT import products
from SHE_PPT import telescope_coords
from SHE_PPT.file_io import (read_xml_product, write_xml_product, read_listfile, write_listfile,
                             get_allowed_filename, filename_exists)
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_validation_test_results import create_validation_test_results_product
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.she_measurements import tf as sm_tf
from SHE_PPT.table_utility import is_in_format
import SHE_Validation
from SHE_Validation_CTI.constants import d_shear_estimation_method_table_formats
from SHE_Validation_CTI.data_processing import add_readout_register_distance
from SHE_Validation_CTI.input_data import get_raw_cti_gal_object_data
from SHE_Validation_CTI.table_formats.regression_results import tf as cgrr_tf, initialise_regression_results_table


logger = getLogger(__name__)


def run_validate_cti_gal_from_args(args):
    """
        Main function for CTI-Gal validation
    """

    # Load in the files in turn to make sure there aren't any issues with them.

    # Load the MDB
    logger.info("Loading MDB.")
    qualified_mdb_filename = join(args.workdir, args.mdb)
    mdb.init(qualified_mdb_filename)
    telescope_coords.load_vis_detector_specs(mdb_dict=mdb.full_mdb)
    logger.info("Complete!")

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
        l_vis_calibrated_frame_product.append(read_xml_product(vis_calibrated_frame_filename, workdir=args.workdir))
        # TODO: Add check on data product type

    # Load the shear measurements

    logger.info("Loading validated shear measurements.")

    qualified_she_validated_measurements_product_filename = join(args.workdir, args.she_validated_measurements_product)
    shear_estimates_prod = read_xml_product(qualified_she_validated_measurements_product_filename)

    if not isinstance(shear_estimates_prod, products.she_validated_measurements.dpdSheValidatedMeasurements):
        raise ValueError("Shear estimates product from " + qualified_she_validated_measurements_product_filename
                         + " is invalid type.")

    # Load the table for each method
    d_shear_estimate_tables = {}
    for method in d_shear_estimation_method_table_formats:

        filename = shear_estimates_prod.get_method_filename(method)

        if filename_exists(filename):
            shear_measurements_table = table.Table.read(join(args.workdir, filename), format='fits')
            d_shear_estimate_tables[method] = shear_measurements_table
            if not is_in_format(shear_measurements_table, d_shear_estimation_method_table_formats[method], strict=False):
                logger.warning("Shear estimates table from " +
                               join(args.workdir, filename) + " is in invalid format.")
                d_shear_estimate_tables[method] = None
                continue
        else:
            d_shear_estimate_tables[method] = None
    # TODO: Add warning if no data from any method
    logger.info("Complete!")

    if not args.dry_run:
        exposure_regression_results_table, observation_regression_results_table = validate_cti_gal(data_stack=data_stack,
                                                                                                   shear_estimate_tables=d_shear_estimate_tables)

    # Set up output product

    logger.info("Creating and outputting validation test result data products.")

    l_exp_test_result_product = []
    l_exp_test_result_filename = []

    for vis_calibrated_frame_product in l_vis_calibrated_frame_product:

        exp_test_result_product = create_validation_test_results_product(reference_product=vis_calibrated_frame_product)

        # Get the Observation ID and Pointing ID, and put them in the filename
        obs_id = vis_calibrated_frame_product.Data.ObservationSequence.ObservationId
        pnt_id = vis_calibrated_frame_product.Data.ObservationSequence.PointingId
        exp_test_result_filename = get_allowed_filename(type_name="EXP-CTI-GAL-VAL-TEST-RESULT",
                                                        instance_id=f"{obs_id}-{pnt_id}",
                                                        extension=".xml",
                                                        version=SHE_Validation.__version__,
                                                        subdir="data")

        # Store the product and filename in lists
        l_exp_test_result_product.append(exp_test_result_product)
        l_exp_test_result_filename.append(exp_test_result_filename)

    # Create the observation test results product. We don't have a reference product for this, so we have to
    # fill it out manually
    obs_test_result_product = create_validation_test_results_product(num_exposures=len(l_vis_calibrated_frame_product))
    obs_test_result_product.Data.TileId = None
    obs_test_result_product.Data.PointingId = None
    obs_test_result_product.Data.ExposureProductId = None
    # Use the last observation ID, assuming they're all the same - TODO: Check to be sure
    obs_test_result_product.Data.ObservationId = vis_calibrated_frame_product.Data.ObservationSequence.ObservationId

    # Fill in the products with the results
    if not args.dry_run:

        # Fill in each exposure product in turn with results
        for exposure_regression_results_row, exp_test_result_product in zip(exposure_regression_results_table, l_exp_test_result_product):
            fill_cti_gal_validation_results(test_result_product=exp_test_result_product,
                                            regression_results_row=exposure_regression_results_row)

        # And fill in the observation product
        fill_cti_gal_validation_results(test_result_product=obs_test_result_product,
                                        regression_results_row=observation_regression_results_table)

    # Write out the exposure test results products and listfile
    for exp_test_result_product, exp_test_result_filename in zip(l_exp_test_result_product, l_exp_test_result_filename):
        write_xml_product(exp_test_result_product, exp_test_result_filename, workdir=args.workdir)
    qualified_exp_test_results_filename = join(args.workdir, args.she_exposure_validation_test_results_listfile)
    write_listfile(qualified_exp_test_results_filename, l_exp_test_result_filename)

    logger.info("Output observation validation test results to: " +
                qualified_exp_test_results_filename)

    # Write out observation test results product
    write_xml_product(obs_test_result_product,
                      args.she_observation_validation_test_results_product, workdir=args.workdir)

    logger.info("Output observation validation test results to: " +
                join(args.she_observation_validation_test_results_product, args.workdir))

    logger.info("Execution complete.")

    return


def validate_cti_gal(data_stack: SHEFrameStack,
                     shear_estimate_tables: Dict[str, table.Table]):
    """ Perform CTI-Gal validation tests on a loaded-in data_stack (SHEFrameStack object) and shear estimates tables
        for each shear estimation method.
    """

    # First, we'll need to get the pixel coords of each object in the table in each exposure, along with the detector
    # and quadrant where it's found and e1/2 in world coords. We'll start by
    # getting them in a raw format by looping over objects
    l_raw_object_data = get_raw_cti_gal_object_data(data_stack=data_stack, shear_estimate_tables=shear_estimate_tables)

    # Now sort the raw data into tables (one for each exposure)
    l_object_data_table = sort_raw_object_data_into_table(raw_object_data_list=l_raw_object_data)

    # We'll now loop over the table for each exposure, eventually getting regression results for each

    exposure_regression_results_table = initialise_regression_results_table()

    for object_data_table in l_object_data_table:

        # At this point, the only maths that's been done is converting world coords into image coords and detector/quadrant.
        # We'll also need to convert shear estimates into the image orientation,
        # so do that now by adding columns to the table
        add_image_shear_estimate_columns(object_data_table=object_data_table)

        # Next, we'll also need to calculate the distance from the readout register, so add columns for that as well
        add_readout_register_distance(object_data_table=object_data_table)

        # Calculate the results of the regression and add it to the results table
        exposure_regression_results = calculate_regression_results(object_data_table=object_data_table)
        exposure_regression_results_table.add_row(regression_results=exposure_regression_results)

    # With the exposures done, we'll now do a test for the observation as a whole on a merged table
    merged_object_table = table.vstack(tables=l_object_data_table)

    observation_regression_results = calculate_regression_results(object_data_table=merged_object_table)

    observation_regression_results_table = initialise_regression_results_table()
    observation_regression_results_table.add_row(regression_results=observation_regression_results)

    # And we're done here, so return the results
    return exposure_regression_results_table, observation_regression_results_table

# Placeholder function definitions to prevent a crash from them not being imported yet
# TODO: Fill in each of these functions and move to other modules


def fill_cti_gal_validation_results(*args, **kwargs):
    pass


def add_image_shear_estimate_columns(*args, **kwargs):
    pass


def calculate_regression_results(*args, **kwargs):
    pass
