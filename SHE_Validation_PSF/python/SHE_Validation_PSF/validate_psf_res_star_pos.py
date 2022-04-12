""" @file validate_psf_res_star_pos.py

    Created 08 March 2022 by Bryan Gillis

    Main function for running PSF residual validation.
"""

__updated__ = "2022-04-08"

#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
from typing import Any, Dict, Optional

import numpy as np
from astropy.table import Table
from dataclasses import dataclass

from SHE_PPT import logging as log
from SHE_PPT.argument_parser import CA_PIPELINE_CONFIG, CA_SHE_STAR_CAT, CA_WORKDIR
from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.constants.config import ConfigKeys
from SHE_PPT.file_io import read_product_and_table, write_xml_product
from SHE_PPT.products.she_validation_test_results import create_dpd_she_validation_test_results
from SHE_Validation.argument_parser import CA_SHE_TEST_RESULTS
from SHE_Validation.config_utility import get_d_l_bin_limits
from SHE_Validation_PSF.argument_parser import CA_REF_SHE_STAR_CAT
from SHE_Validation_PSF.constants.psf_res_sp_test_info import NUM_PSF_RES_SP_TEST_CASES
from SHE_Validation_PSF.data_processing import run_psf_res_val_test
from SHE_Validation_PSF.results_reporting import PsfResValidationResultsWriter
from ST_DataModelBindings.dpd.she.raw.starcatalog_stub import dpdSheStarCatalog

logger = log.getLogger(__name__)


@dataclass
class PsfResSPInputData():
    d_l_bin_limits: Dict[BinParameters, np.ndarray]
    p_star_cat: Any
    star_cat: Table
    p_ref_star_cat: Optional[Any] = None
    ref_star_cat: Optional[Table] = None


def run_validate_psf_res_from_args(d_args: Dict[ConfigKeys, Any]) -> None:
    """ Main function for running PSF Residual validation.
    """

    # Load in the input data and configuration

    workdir = d_args[CA_WORKDIR]

    psf_res_sp_input = load_psf_res_input(d_args, workdir)

    # Process the data, getting the results of the test
    d_l_psf_res_test_results = run_psf_res_val_test(star_cat = psf_res_sp_input.star_cat,
                                                    ref_star_cat = psf_res_sp_input.ref_star_cat,
                                                    d_l_bin_limits = psf_res_sp_input.d_l_bin_limits)

    # Create and fill the output data product to contain the results
    test_result_product = create_dpd_she_validation_test_results(reference_product = psf_res_sp_input.p_star_cat,
                                                                 num_tests = NUM_PSF_RES_SP_TEST_CASES)
    test_results_writer = PsfResValidationResultsWriter(test_object = test_result_product,
                                                        workdir = workdir,
                                                        d_l_bin_limits = psf_res_sp_input.d_l_bin_limits,
                                                        d_l_test_results = d_l_psf_res_test_results, )

    test_results_writer.write()

    # Output the results to the desired location
    write_xml_product(test_result_product, d_args[CA_SHE_TEST_RESULTS], workdir = workdir)


def load_psf_res_input(d_args: Dict[ConfigKeys, Any], workdir: str) -> PsfResSPInputData:
    """Function to load in required input data for the PSF Residual validation test.
    """

    # Get the bin limits dictionary from the config
    d_l_bin_limits = get_d_l_bin_limits(d_args[CA_PIPELINE_CONFIG])

    # Load the star catalog table
    logger.info("Loading star catalog.")
    p_star_cat, star_cat = read_product_and_table(product_filename = d_args[CA_SHE_STAR_CAT],
                                                  workdir = workdir,
                                                  product_type = dpdSheStarCatalog)

    p_ref_star_cat_filename = d_args[CA_REF_SHE_STAR_CAT]

    # If we don't have a reference star catalog, return without it
    if p_ref_star_cat_filename is None:
        return PsfResSPInputData(d_l_bin_limits = d_l_bin_limits,
                                 p_star_cat = p_star_cat,
                                 star_cat = star_cat)

    # Load the reference star catalog and return with it
    p_ref_star_cat, ref_star_cat = read_product_and_table(product_filename = d_args[CA_REF_SHE_STAR_CAT],
                                                          workdir = workdir,
                                                          product_type = dpdSheStarCatalog)

    return PsfResSPInputData(d_l_bin_limits = d_l_bin_limits,
                             p_star_cat = p_star_cat,
                             star_cat = star_cat,
                             p_ref_star_cat = p_ref_star_cat,
                             ref_star_cat = ref_star_cat)
