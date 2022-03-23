""" @file validate_psf_res.py

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
from typing import Any, Dict

from SHE_PPT import logging as log
from SHE_PPT.argument_parser import CA_PIPELINE_CONFIG, CA_SHE_STAR_CAT, CA_WORKDIR
from SHE_PPT.constants.config import ConfigKeys
from SHE_PPT.file_io import read_product_and_table
from SHE_Validation.config_utility import get_d_l_bin_limits
from ST_DataModelBindings.dpd.she.raw.starcatalog_stub import dpdSheStarCatalog

logger = log.getLogger(__name__)


# Dummy run_from_args_function until it's properly set up
def run_validate_psf_res_from_args(d_args: Dict[ConfigKeys, Any]) -> None:
    """ Main function for running PSF Residual validation.
    """

    # Load in the input data and configuration

    workdir = d_args[CA_WORKDIR]

    (d_l_bin_limits,
     p_star_cat,
     star_cat) = load_psf_res_input(d_args, workdir)

    # Process the data, getting the results of the test
    d_l_psf_res_test_results = test_psf_res(star_cat = star_cat,
                                            d_l_bin_limits = d_l_bin_limits)


def load_psf_res_input(d_args, workdir):
    """Function to load in required input data for the PSF Residual validation test.
    """

    # Get the bin limits dictionary from the config
    d_l_bin_limits = get_d_l_bin_limits(d_args[CA_PIPELINE_CONFIG])

    # Load the star catalog table
    logger.info("Loading star catalog.")
    p_star_cat, star_cat = read_product_and_table(product_filename = d_args[CA_SHE_STAR_CAT],
                                                  workdir = workdir,
                                                  product_type = dpdSheStarCatalog)

    return d_l_bin_limits, p_star_cat, star_cat
