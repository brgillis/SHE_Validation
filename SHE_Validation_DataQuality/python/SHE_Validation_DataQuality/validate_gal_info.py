"""
:file: python/SHE_Validation_DataQuality/validate_gal_info.py

:date: 09/26/22
:author: Bryan Gillis

Core code for GalInfo validation test
"""

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

from SHE_PPT.argument_parser import CA_WORKDIR
from SHE_PPT.file_io import write_xml_product
from SHE_PPT.products.she_validation_test_results import create_dpd_she_validation_test_results
from SHE_Validation.argument_parser import CA_MER_CAT_PROD, CA_SHE_CAT, CA_SHE_CHAINS, CA_SHE_TEST_RESULTS
from SHE_Validation_DataQuality.constants.gal_info_test_info import NUM_GAL_INFO_TEST_CASES
from SHE_Validation_DataQuality.gi_data_processing import get_gal_info_test_results
from SHE_Validation_DataQuality.gi_input import read_gal_info_input
from SHE_Validation_DataQuality.gi_results_reporting import GalInfoValidationResultsWriter


def run_validate_gal_info_from_args(d_args):
    """Dummy implementation of run function. TODO: Implement properly

    Parameters
    ----------
    d_args : Dict[str, Any]
        The command line arguments, parsed (e.g. via `args = parser.parse_args()` and turned into args dict (e.g. via
        `d_args = vars(args)`.
    """

    workdir = d_args[CA_WORKDIR]

    # Load in the input data
    gal_info_input = read_gal_info_input(p_she_cat_filename=d_args[CA_SHE_CAT],
                                         p_she_chains_filename=d_args[CA_SHE_CHAINS],
                                         p_mer_cat_filename=d_args[CA_MER_CAT_PROD],
                                         workdir=workdir)

    # This test requires the MER Final Catalog table, so raise an exception if it doesn't exist
    if not gal_info_input.p_mer_cat:
        raise ValueError(f"MER Final Catalog product could not be read. Exception was: {gal_info_input.err_p_mer_cat}")
    if not gal_info_input.mer_cat:
        raise ValueError(f"MER Final Catalog table could not be read. Exception was: {gal_info_input.err_mer_cat}")

    # Process the data to get the test results
    d_l_test_results = get_gal_info_test_results(gal_info_input, workdir=workdir)

    # Create and fill the output data product to contain the results
    test_result_product = create_dpd_she_validation_test_results(num_tests=NUM_GAL_INFO_TEST_CASES)
    test_result_product.Data.TileIndex = gal_info_input.p_she_cat.Data.TileList[0]

    test_results_writer = GalInfoValidationResultsWriter(test_object=test_result_product,
                                                         workdir=workdir,
                                                         d_l_test_results=d_l_test_results, )

    test_results_writer.write()

    # Output the results to the desired location
    write_xml_product(test_result_product, d_args[CA_SHE_TEST_RESULTS], workdir=workdir)
