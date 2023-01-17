""" @file argument_parser.py

    Created 29 July 2021

    Base class for an argument parser for SHE Validation executables
"""

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

from typing import Iterable

from SHE_PPT.argument_parser import ClineArgType, SheArgumentParser
from .constants.test_info import BinParameterMeta, BinParameters, D_BIN_PARAMETER_META

CA_MER_CAT_PROD = "mer_final_catalog"

CA_PHZ_CAT_LIST = "phz_catalog_listfile"

CA_SHE_EXT_CAT = "extended_catalog"
CA_SHE_MATCHED_CAT = "matched_catalog"
CA_SHE_MATCHED_CAT_LIST = "matched_catalog_listfile"
CA_SHE_REC_CAT = "reconciled_catalog"
CA_SHE_REC_CHAINS = "reconciled_chains"
CA_SHE_TEST_RESULTS = "she_validation_test_results_product"
CA_SHE_OBS_TEST_RESULTS = "she_observation_cti_gal_validation_test_results_product"
CA_SHE_EXP_TEST_RESULTS_LIST = "she_exposure_cti_gal_validation_test_results_listfile"


class ValidationArgumentParser(SheArgumentParser):
    """ Argument parser specialized for SHE Validation executables.
    """

    # Convenience functions to add input filename cline-args

    def add_extended_catalog_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f'--{CA_SHE_EXT_CAT}', type=str, arg_type=arg_type,
                               help='.xml data product for extended MER Final Catalog, containing binning '
                                    'data.')

    def add_matched_catalog_arg(self, arg_type: ClineArgType = ClineArgType.INPUT) -> None:
        self.add_arg_with_type(f'--{CA_SHE_MATCHED_CAT}', type=str, arg_type=arg_type,
                               help='.xml data product for Shear Estimates catalog matched to TU catalog.')

    def add_matched_catalog_listfile_arg(self, arg_type: ClineArgType = ClineArgType.INPUT) -> None:
        self.add_arg_with_type(f'--{CA_SHE_MATCHED_CAT_LIST}', type=str, arg_type=arg_type,
                               help='.json listfile containing filenames of matched catalog products.')

    # Convenience functions to add output filename cline-args

    def add_test_result_arg(self, arg_type: ClineArgType = ClineArgType.INPUT) -> None:
        self.add_arg_with_type(f'--{CA_SHE_TEST_RESULTS}', type=str, arg_type=arg_type,
                               default="she_validation_test_results_product.xml",
                               help='Desired filename of output .xml data product for validation test '
                                    'results.')

    def add_obs_test_result_arg(self, arg_type: ClineArgType = ClineArgType.INPUT) -> None:
        self.add_arg_with_type(f'--{CA_SHE_OBS_TEST_RESULTS}', type=str, arg_type=arg_type,
                               default="she_observation_cti_gal_validation_test_results_product.xml",
                               help='Desired filename of output .xml data product for observation validation '
                                    'test results.')

    def add_exp_test_result_listfile_arg(self, arg_type: ClineArgType = ClineArgType.INPUT) -> None:
        self.add_arg_with_type(f'--{CA_SHE_EXP_TEST_RESULTS_LIST}', type=str, arg_type=arg_type,
                               default="she_exposure_cti_gal_validation_test_results_listfile.xml",
                               help='Desired filename of output .json listfile for exposure validation test '
                                    'results.')

    # Convenience functions to add options cline-args

    def add_bin_parameter_args(self,
                               arg_type: ClineArgType = ClineArgType.OPTION,
                               l_bin_parameters: Iterable[BinParameters] = BinParameters):
        for bin_parameter in l_bin_parameters:
            bin_parameter_meta: BinParameterMeta = D_BIN_PARAMETER_META[bin_parameter]
            self.add_arg_with_type(f'--{bin_parameter_meta.cline_arg}',
                                   type=str,
                                   default=None,
                                   arg_type=arg_type,
                                   help=bin_parameter_meta.help_text)
