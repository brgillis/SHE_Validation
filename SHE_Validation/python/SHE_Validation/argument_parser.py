""" @file argument_parser.py

    Created 29 July 2021

    Base class for an argument parser for SHE Validation executables.
"""

__updated__ = "2021-08-27"

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

from SHE_PPT.argument_parser import SheArgumentParser
from .constants.test_info import BinParameterMeta, BinParameters, D_BIN_PARAMETER_META


class ValidationArgumentParser(SheArgumentParser):
    """ Argument parser specialized for SHE Validation executables.
    """

    # Convenience functions to add input filename cline-args

    def add_bin_parameter_args(self):
        for bin_parameter in BinParameters:
            bin_parameter_meta: BinParameterMeta = D_BIN_PARAMETER_META[bin_parameter]
            self.add_argument('--' + bin_parameter_meta.cline_arg, type = str, default = None,
                              help = bin_parameter_meta.help_text)

    def add_mdb_arg(self):
        self.add_argument('--mdb', type = str, default = None,
                          help = 'INPUT: Mission Database .xml file')

    def add_measurements_arg(self):
        self.add_argument('--she_validated_measurements_product', type = str,
                          help = 'INPUT: Filename of the cross-validated shear measurements .xml data product.')

    def add_final_catalog_arg(self):
        self.add_argument('--mer_final_catalog_listfile', type = str,
                          help = 'INPUT: .json listfile containing filenames of mer final catalogs.')

    def add_calibrated_frame_arg(self):
        self.add_argument('--vis_calibrated_frame_listfile', type = str,
                          help = 'INPUT: .json listfile containing filenames of exposure image products.')

    def add_matched_catalog_arg(self) -> None:
        self.add_argument('--matched_catalog', type = str,
                          help = 'INPUT: .xml data product for Shear Estimates catalog matched to TU catalog.')

    def add_matched_catalog_listfile_arg(self) -> None:
        self.add_argument('--matched_catalog_listfile', type = str,
                          help = 'INPUT: .json listfile containing filenames of matched catalog products.')

    # Convenience functions to add output filename cline-args

    def add_test_result_arg(self) -> None:
        self.add_argument('--she_validation_test_results_product', type = str,
                          default = "she_validation_test_results_product.xml",
                          help = 'OUTPUT: Desired filename of output .xml data product for validation test results.')

    def add_obs_test_result_arg(self) -> None:
        self.add_argument('--she_observation_validation_test_results_product', type = str,
                          default = "she_observation_validation_test_results_product.xml",
                          help = 'OUTPUT: Desired filename of output .xml data product for observation validation '
                                 'test results.')

    def add_exp_test_result_listfile_arg(self) -> None:
        self.add_argument('--she_exposure_validation_test_results_listfile', type = str,
                          default = "she_exposure_validation_test_results_listfile.xml",
                          help = 'OUTPUT: Desired filename of output .json listfile for exposure validation test '
                                 'results.')
