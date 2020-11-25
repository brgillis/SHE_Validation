""" @file validate_cti_gal.py

    Created 24 November 2020 by Bryan Gillis

    Primary function code for performing CTI-Gal validation
"""

__updated__ = "2020-11-25"

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

from astropy.table import Table

from SHE_PPT import mdb
from SHE_PPT import products
from SHE_PPT.file_io import (read_xml_product, write_xml_product, read_listfile,
                             get_allowed_filename, filename_exists)
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_validation_test_results import create_validation_test_results_product
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_measurements import tf as sm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf
from SHE_PPT.table_utility import is_in_format
import SHE_Validation

shear_estimation_method_table_formats = {"KSB": ksbm_tf,
                                         "REGAUSS": regm_tf,
                                         "MomentsML": mmlm_tf,
                                         "LensMC": lmcm_tf}

logger = log.getLogger(__name__)


def run_validate_cti_gal_from_args(args):
    """
        Main function for CTI-Gal validation
    """

    # Load in the files in turn to make sure there aren't any issues with them.

    # Load the MDB
    logger.info("Loading MDB.")
    mdb.init(args.mdb)
    logger.info("Complete!")

    # Load the image data as a SHEFrameStack
    logger.info("Loading in calibrated frames, exposure segmentation maps, and MER final catalogs as a SHEFrameStack.")
    data_stack = SHEFrameStack.read(exposure_listfile_filename=args.vis_calibrated_frame_listfile,
                                    seg_listfile_filename=args.she_exposure_segmentation_map_listfile,
                                    detections_listfile_filename=args.mer_final_catalog_listfile,
                                    workdir=args.workdir,
                                    memmap=True,
                                    mode='denywrite')
    logger.info("Complete!")

    # Load the exposure products, to get needed metadata for output
    l_vis_calibrated_frame_filename = read_listfile(join(args.workdir, args.vis_calibrated_frame_listfile))
    l_vis_calibrated_frame_product = []
    for vis_calibrated_frame_filename in l_vis_calibrated_frame_filename:
        vis_calibrated_frame_product.append(read_xml_product(vis_calibrated_frame_filename, workdir=args.workdir))

    # Load the shear measurements

    logger.info("Loading validated shear measurements.")

    qualified_she_validated_measurements_product_filename = join(args.workdir, args.she_validated_measurements_product)
    shear_estimates_prod = read_xml_product(qualified_she_validated_measurements_product_filename)

    if not isinstance(shear_estimates_prod, products.she_validated_measurements.dpdSheValidatedMeasurements):
        raise ValueError("Shear estimates product from " + qualified_she_validated_measurements_product_filename
                         + " is invalid type.")

    # Load the table for each method
    shear_estimate_table_dict = {}
    for method in shear_estimation_method_table_formats:

        filename = shear_estimates_prod.get_method_filename(method)

        if filename_exists(filename):
            shear_estimate_table_dict[method] = Table.read(join(args.workdir, filename), format='fits')
            if not is_in_format(shear_estimates_table, sm_tfs[method], strict=False):
                logger.warning("Shear estimates table from " +
                               join(args.workdir, filename) + " is in invalid format.")
                continue
        else:
            shear_estimate_table_dict[method] = None
    logger.info("Complete!")

    # TODO: Perform the validation

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
    # Use the last observation ID, assuming they're all the same
    obs_test_result_product.Data.ObservationId = reference_product.Data.obs_id

    # TODO: Fill in obs_test_result_product and l_exp_test_result_product with results

    # Write out the exposure test results products and listfile
    for exp_test_result_product, exp_test_result_filename in zip(l_exp_test_result_product, l_exp_test_result_filename):
        write_xml_product(exp_test_result_product, exp_test_result_filename, workdir=args.workdir)
    qualified_exp_test_results_filename = join(args.she_exposure_validation_test_results_listfile, args.workdir)
    write_listfile(qualified_exp_test_results_filename, l_exp_test_result_filename)

    logger.info("Output observation validation test results to: " +
                qualified_exp_test_results_filename)

    # Write out observation test results product
    write_xml_product(val_test_result_product,
                      args.she_observation_validation_test_results_product, workdir=args.workdir)

    logger.info("Output observation validation test results to: " +
                join(args.she_observation_validation_test_results_product, args.workdir))

    logger.info("Execution complete.")

    return
