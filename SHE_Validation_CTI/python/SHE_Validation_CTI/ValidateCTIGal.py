""" @file ValidateCTIGal.py

    Created 24 November 2020 by Bryan Gillis

    Entry-point file for CTI-Gal validation executable.
"""

__updated__ = "2021-08-20"

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

from argparse import ArgumentParser, Namespace

from SHE_PPT import logging as log
from SHE_PPT.pipeline_utility import AnalysisConfigKeys, ValidationConfigKeys
from SHE_Validation.argument_parser import ValidationArgumentParser
from SHE_Validation.executor import ValLogOptions, ValReadConfigArgs
from SHE_Validation_ShearBias.executor import ShearBiasValExecutor
from .constants.cti_gal_default_config import (D_CTI_GAL_CONFIG_CLINE_ARGS, D_CTI_GAL_CONFIG_DEFAULTS,
                                               D_CTI_GAL_CONFIG_TYPES, )
from .validate_cti_gal import run_validate_cti_gal_from_args

EXEC_NAME = "SHE_Validation_ValidateCTIGal"

logger = log.getLogger(__name__)


# noinspection PyPep8Naming
def defineSpecificProgramOptions() -> ArgumentParser:
    """
    @brief Allows to define the (command line and configuration file) options
    specific to this program

    @details
        See the Elements documentation for more details.
    @return
        An  ArgumentParser.
    """

    logger.debug(f'# Entering {EXEC_NAME} defineSpecificProgramOptions()')

    # Set up the argument parser, using built-in methods where possible
    parser = ValidationArgumentParser()

    parser.add_calibrated_frame_arg()
    parser.add_final_catalog_arg()
    parser.add_measurements_arg()
    parser.add_mdb_arg()
    parser.add_bin_parameter_args()

    # Output arguments

    parser.add_argument('--she_observation_validation_test_results_product', type = str,
                        help = 'OUTPUT: Desired filename of output .xml data product for observation validation test ' +
                               'results')

    parser.add_argument('--she_exposure_validation_test_results_listfile', type = str,
                        help = 'OUTPUT: Desired filename of output .json listfile for exposure validation test results')

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """ Main entry point method
    """

    executor = ShearBiasValExecutor(run_from_args_function = run_validate_cti_gal_from_args,
                                    config_args = ValReadConfigArgs(d_config_cline_args = D_CTI_GAL_CONFIG_CLINE_ARGS,
                                                                    d_config_defaults = D_CTI_GAL_CONFIG_DEFAULTS,
                                                                    d_config_types = D_CTI_GAL_CONFIG_TYPES,
                                                                    s_config_keys_types = {ValidationConfigKeys,
                                                                                           AnalysisConfigKeys}),
                                    log_options = ValLogOptions(executable_name = EXEC_NAME), )

    executor.run(args, logger = logger)


def main() -> None:
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = defineSpecificProgramOptions()

    args = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
