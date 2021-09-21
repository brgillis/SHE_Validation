""" @file ValidateGlobalShearBias.py

    Created 8 July 2021

    Executable for performing shear bias validation on data from one observation.
"""

__updated__ = "2021-08-09"

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
from SHE_PPT.pipeline_utility import GlobalConfigKeys, ValidationConfigKeys, read_config
from SHE_Validation.constants.default_config import ExecutionMode
from SHE_Validation.constants.test_info import BinParameterMeta, BinParameters, D_BIN_PARAMETER_META
from SHE_Validation_ShearBias.argument_parser import ShearValidationArgumentParser
from . import __version__
from .constants.shear_bias_default_config import (D_SHEAR_BIAS_CONFIG_CLINE_ARGS, D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                                  D_SHEAR_BIAS_CONFIG_TYPES, GLOBAL_PROFILING_FILENAME, )
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

    parser = ShearValidationArgumentParser()

    for bin_parameter in BinParameters:


bin_parameter_meta: BinParameterMeta = D_BIN_PARAMETER_META[bin_parameter]
parser.add_argument('--' + bin_parameter_meta.cline_arg, type = str, default = None,
                    help = bin_parameter_meta.help_text)

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

    exec_cmd = get_arguments_string(args,
                                    cmd = f"E-Run SHE_Validation {__version__} SHE_Validation_ValidateGlobalShearBias",
                                    store_true = ["profile", "dry_run"])
    logger.info('Execution command for this step:')
    logger.info(exec_cmd)

    # load the pipeline config in
    pipeline_config = read_config(args.pipeline_config,
                                  workdir = args.workdir,
                                  defaults = D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                  d_cline_args = D_SHEAR_BIAS_CONFIG_CLINE_ARGS,
                                  parsed_args = args,
                                  config_keys = ValidationConfigKeys,
                                  d_types = D_SHEAR_BIAS_CONFIG_TYPES)

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
                         "args"                         : args,
                         "GLOBAL_MODE"                  : ExecutionMode.GLOBAL},
                        filename = "validate_shear_bias_from_args.prof")
    else:
        logger.info("Profiling disabled")
        validate_shear_bias_from_args(args,
                                      mode = ExecutionMode.GLOBAL)

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
