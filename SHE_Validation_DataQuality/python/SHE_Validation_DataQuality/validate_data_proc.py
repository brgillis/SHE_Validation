"""
:file: python/SHE_Validation_DataQuality/validate_data_proc.py

:date: 09/26/22
:author: Bryan Gillis

Core code for DataProc validation test
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
from SHE_Validation.argument_parser import CA_SHE_REC_CAT, CA_SHE_REC_CHAINS, CA_SHE_TEST_RESULTS
from SHE_Validation_DataQuality.constants.data_proc_test_info import DATA_PROC_TEST_CASE_INFO, NUM_DATA_PROC_TEST_CASES
from SHE_Validation_DataQuality.dp_input import read_data_proc_input


def run_validate_data_proc_from_args(d_args):
    """Dummy implementation of run function. TODO: Implement properly

    Parameters
    ----------
    d_args : Dict[str, Any]
        The command line arguments, parsed (e.g. via `args = parser.parse_args()` and turned into args dict (e.g. via
        `d_args = vars(args)`.
    """

    workdir = d_args[CA_WORKDIR]

    # Load in the input data
    data_proc_input = read_data_proc_input(p_rec_cat_filename=d_args[CA_SHE_REC_CAT],
                                           p_rec_chains_filename=d_args[CA_SHE_REC_CHAINS],
                                           workdir=workdir)

    # This test is simple enough that the input can serve directly as the test results. We just need to put it in the
    # proper format
    d_l_test_results = {DATA_PROC_TEST_CASE_INFO.name: [data_proc_input]}

    # Create and fill the output data product to contain the results
    test_result_product = create_dpd_she_validation_test_results(reference_product=data_proc_input.p_rec_cat,
                                                                 num_tests=NUM_DATA_PROC_TEST_CASES)
    test_results_writer = DataProcValidationResultsWriter(test_object=test_result_product,
                                                          workdir=workdir,
                                                          d_l_test_results=d_l_test_results, )

    test_results_writer.write()

    # Output the results to the desired location
    write_xml_product(test_result_product, d_args[CA_SHE_TEST_RESULTS], workdir=workdir)
