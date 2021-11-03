""" @file validate_cti_psf.py

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
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from astropy.table import Row, Table

from EL_CoordsUtils import telescope_coords
from SHE_PPT import mdb
from SHE_PPT.argument_parser import (CA_DRY_RUN, CA_MDB, CA_PIPELINE_CONFIG, CA_SHE_STAR_CAT,
                                     CA_WORKDIR, )
from SHE_PPT.file_io import (read_product_and_table, read_table_from_product, write_xml_product, )
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_validation_test_results import create_dpd_she_validation_test_results
from SHE_PPT.table_formats.she_star_catalog import TF as SC_TF
from SHE_Validation.argument_parser import CA_SHE_TEST_RESULTS
from SHE_Validation.binning.bin_constraints import BinParameterBinConstraint, get_ids_for_test_cases
from SHE_Validation.config_utility import get_d_l_bin_limits
from SHE_Validation.constants.test_info import BinParameters
from ST_DataModelBindings.dpd.she.raw.starcatalog_stub import dpdSheStarCatalog
from .constants.cti_psf_test_info import L_CTI_PSF_TEST_CASE_INFO, NUM_CTI_PSF_TEST_CASES
from .data_processing import add_readout_register_distance, calculate_regression_results
from .file_io import CtiPsfPlotFileNamer
from .plot_cti import CtiPlotter
from .validate_cti_gal import MSG_COMPLETE

logger = getLogger(__name__)


def run_validate_cti_psf_from_args(d_args: Dict[str, Any]):
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
    d_l_bin_limits: Dict[BinParameters, np.ndarray] = get_d_l_bin_limits(d_args[CA_PIPELINE_CONFIG])

    # Load the star catalogue

    logger.info("Loading star catalog.")

    star_catalog_product: dpdSheStarCatalog
    star_catalog_product, star_catalog_table = read_product_and_table(d_args[CA_SHE_STAR_CAT],
                                                                      workdir = workdir,
                                                                      log_info = True)

    logger.info(MSG_COMPLETE)

    # Load the extended detections catalog
    extended_catalog_table = read_table_from_product(d_args[CA_SHE_STAR_CAT],
                                                     workdir = workdir,
                                                     log_info = True)

    # Calculate the data necessary for validation

    add_readout_register_distance(star_catalog_table, y_colname = SC_TF.y)

    d_regression_results_tables = validate_cti_psf(star_catalog_table = star_catalog_table,
                                                   extended_catalog_table = extended_catalog_table,
                                                   d_l_bin_limits = d_l_bin_limits,
                                                   workdir = workdir)

    # Set up output product, using the star catalog product as a reference
    test_result_product = create_dpd_she_validation_test_results(reference_product = star_catalog_product,
                                                                 num_tests = NUM_CTI_PSF_TEST_CASES)

    # Fill in the product with the results
    if not d_args[CA_DRY_RUN]:

        # Fill in the product with results
        fill_cti_psf_validation_results(test_result_product = test_result_product,
                                        workdir = workdir,
                                        d_regression_results_tables = d_regression_results_tables,
                                        pipeline_config = d_args[CA_PIPELINE_CONFIG],
                                        d_l_bin_limits = d_l_bin_limits, )

    # Write out the test results product
    write_xml_product(test_result_product,
                      xml_filename = d_args[CA_SHE_TEST_RESULTS],
                      workdir = workdir,
                      log_info = True)

    logger.info("Execution complete.")


def validate_cti_psf(star_catalog_table: Table,
                     extended_catalog_table: Table,
                     d_l_bin_limits: Dict[BinParameters, np.ndarray],
                     workdir: str) -> Tuple[Dict[str, List[Table]],
                                            Dict[str, Dict[str, str]]]:
    """ Perform CTI-Gal validation tests on a loaded-in data_stack (SHEFrameStack object) and shear estimates tables
        for each shear estimation method.
    """

    # Loop over each test case, filling in results tables for each and adding them to the results dict
    d_l_regression_results_tables: Dict[str, List[Table]] = {}
    plot_filenames: Dict[str, Dict[str, str]] = {}

    # Get IDs for all bins
    d_l_l_test_case_object_ids = get_ids_for_test_cases(l_test_case_info = L_CTI_PSF_TEST_CASE_INFO,
                                                        d_bin_limits = d_l_bin_limits,
                                                        detections_table = extended_catalog_table,
                                                        l_full_ids = star_catalog_table[SC_TF.id],
                                                        bin_constraint_type = BinParameterBinConstraint)

    for test_case_info in L_CTI_PSF_TEST_CASE_INFO:

        # Initialise for this test case
        plot_filenames[test_case_info.name] = {}
        l_test_case_bin_limits = d_l_bin_limits[test_case_info.bins]
        num_bins = len(l_test_case_bin_limits) - 1
        l_l_test_case_object_ids = d_l_l_test_case_object_ids[test_case_info.name]

        # Double check we have at least one bin
        assert num_bins >= 1

        l_regression_results_tables: List[Optional[Union[Table, Row]]] = [None] * num_bins

        for bin_index in range(num_bins):

            # Get info for this bin
            l_test_case_object_ids = l_l_test_case_object_ids[bin_index]
            bin_limits = l_test_case_bin_limits[bin_index:bin_index + 2]

            # We'll now loop over the table for each exposure, eventually getting regression results and plots
            # for each

            regression_results_table = calculate_regression_results(object_data_table = star_catalog_table,
                                                                    l_ids_in_bin = l_test_case_object_ids,
                                                                    product_type = "OBS", )

            l_regression_results_tables[bin_index] = regression_results_table

            # Make a plot
            file_namer = CtiPsfPlotFileNamer(bin_parameter = test_case_info.bins,
                                             bin_index = bin_index,
                                             workdir = workdir)
            plotter = CtiPlotter(file_namer = file_namer,
                                 object_table = star_catalog_table,
                                 bin_limits = bin_limits,
                                 l_ids_in_bin = l_test_case_object_ids, )
            plotter.plot()
            plot_label = f"{test_case_info.bins.value}-{bin_index}"
            plot_filenames[test_case_info.name][plot_label] = plotter.plot_filename

        # Fill in the results of this test case in the output dict
        d_l_regression_results_tables[test_case_info.name] = l_regression_results_tables

    # And we're done here, so return the results and object tables
    return d_l_regression_results_tables, plot_filenames
