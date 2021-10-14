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

from argparse import ArgumentParser, Namespace

from SHE_PPT import logging as log
from SHE_PPT.executor import RunArgs
from SHE_Validation.constants.default_config import ExecutionMode
from SHE_Validation.executor import ValLogOptions
from SHE_Validation_ShearBias.executor import ShearBiasValExecutor
from .argument_parser import ShearValidationArgumentParser
from .validate_shear_bias import validate_shear_bias_from_args

logger = log.getLogger(__name__)


# noinspection PyPep8Naming
def defineSpecificProgramOptions() -> ArgumentParser:
    """
    @brief
        Defines options for this program, using all possible configurations.

    @return
        An  ArgumentParser.
    """

    logger.debug('#')
    logger.debug('# Entering SHE_Validation_ValidateGlobalShearBias defineSpecificProgramOptions()')
    logger.debug('#')

    parser: ShearValidationArgumentParser = ShearValidationArgumentParser()

    logger.debug('Exiting SHE_Validation_ValidateGlobalShearBias defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args) -> None:
    """ Main entry point method
    """

    executor = ShearBiasValExecutor(run_from_args_function = validate_shear_bias_from_args,
                                    log_options = ValLogOptions(executable_name =
                                                                "SHE_Validation_ValidateGlobalShearBias"),
                                    run_args = RunArgs(d_run_kwargs = {"mode": ExecutionMode.GLOBAL}))

    executor.run(args, logger = logger)


def main() -> None:
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser: ArgumentParser = defineSpecificProgramOptions()

    args: Namespace = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
