""" @file ValidateGlobalShearBias.py

    Created 8 July 2021

    Executable for performing shear bias validation on data from one observation.
"""

__updated__ = "2021-08-03"

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

import argparse
import os

from EL_PythonUtils.utilities import get_arguments_string
from SHE_PPT import logging as log
from SHE_PPT.pipeline_utility import read_config, GlobalConfigKeys, ValidationConfigKeys

from SHE_Validation.constants.default_config import GLOBAL_MODE
from SHE_Validation.constants.test_info import add_bin_limits_cline_args

from . import __version__
from .constants.shear_bias_default_config import (D_SHEAR_BIAS_CONFIG_DEFAULTS, D_SHEAR_BIAS_CONFIG_TYPES,
                                                  D_SHEAR_BIAS_CONFIG_CLINE_ARGS, GLOBAL_PROFILING_FILENAME)
from .validate_shear_bias import validate_shear_bias_from_args


logger = log.getLogger(__name__)


def defineSpecificProgramOptions():
    """
    @brief
        Defines options for this program, using all possible configurations.

    @return
        An  ArgumentParser.
    """

    logger.debug('#')
    logger.debug('# Entering SHE_Validation_ValidateGlobalShearBias defineSpecificProgramOptions()')
    logger.debug('#')

    parser = argparse.ArgumentParser()

    # Input filenames
    parser.add_argument('--matched_catalog_listfile', type=str,
                        help='Filename of .json listfile pointing to matched catalog products.')
    parser.add_argument('--pipeline_config', type=str,
                        help='Pipeline configuration file.')

    # Output filenames
    parser.add_argument('--shear_bias_validation_test_results_product', type=str,
                        default="shear_bias_global_validation_test_results_product.xml",
                        help='Desired filename for output shear bias validation test results (XML data product).')

    # Arguments needed by the pipeline runner
    parser.add_argument('--workdir', type=str, default=".")
    parser.add_argument('--logdir', type=str, default=".")

    # Optional arguments (can't be used with pipeline runner)
    parser.add_argument('--profile', action='store_true',
                        help='Store profiling data for execution.')
    parser.add_argument('--dry_run', action='store_true',
                        help='Skip processing and just output dummy data.')

    add_bin_limits_cline_args(parser)

    logger.debug('Exiting SHE_Validation_ValidateGlobalShearBias defineSpecificProgramOptions()')

    return parser


def mainMethod(args):
    """
    @brief
        The "main" method for this program, to generate galaxy images.

    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger.debug('#')
    logger.debug('# Entering SHE_Validation_ValidateGlobalShearBias mainMethod()')
    logger.debug('#')

    exec_cmd = get_arguments_string(args, cmd=f"E-Run SHE_Validation {__version__} SHE_Validation_ValidateGlobalShearBias",
                                    store_true=["profile", "dry_run"])
    logger.info('Execution command for this step:')
    logger.info(exec_cmd)

    # load the pipeline config in
    pipeline_config = read_config(args.pipeline_config,
                                  workdir=args.workdir,
                                  defaults=D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                  config_keys=ValidationConfigKeys,
                                  d_types=D_SHEAR_BIAS_CONFIG_TYPES)

    # set args.pipeline_config to the read-in pipeline_config
    args.pipeline_config = pipeline_config

    # check if profiling is to be enabled from the pipeline config
    profiling = pipeline_config[GlobalConfigKeys.PIP_PROFILE]

    if args.profile or profiling:
        import cProfile

        logger.info("Profiling enabled")
        filename = os.path.join(args.workdir, args.logdir, GLOBAL_PROFILING_FILENAME)
        logger.info("Writing profiling data to %s", filename)

        cProfile.runctx("validate_shear_bias_from_args(args, mode=GLOBAL_MODE)", {},
                        {"validate_shear_bias_from_args": validate_shear_bias_from_args,
                         "args": args,
                         "GLOBAL_MODE": GLOBAL_MODE},
                        filename="validate_shear_bias_from_args.prof")
    else:
        logger.info("Profiling disabled")
        validate_shear_bias_from_args(args,
                                      mode=GLOBAL_MODE)

    logger.info('#')
    logger.debug('Exiting SHE_Validation_ValidateGlobalShearBias mainMethod()')
    logger.info('#')


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = defineSpecificProgramOptions()

    args = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
