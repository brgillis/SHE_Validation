""" @file ValidateShearBias.py

    Created 8 July 2021

    Executable for performing shear bias validation on data from one observation
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

from argparse import ArgumentParser, Namespace

from SHE_PPT import logging as log
from SHE_PPT.executor import RunArgs
from SHE_Validation.constants.default_config import ExecutionMode
from SHE_Validation.executor import ValLogOptions
from SHE_Validation_ShearBias.executor import ShearBiasValExecutor
from SHE_Validation_ShearBias.validate_shear_bias import validate_shear_bias_from_args
from .argument_parser import ShearValidationArgumentParser

EXEC_NAME = "SHE_Validation_ValidateShearBias"

logger = log.getLogger(__name__)


# noinspection PyPep8Naming
def defineSpecificProgramOptions() -> ArgumentParser:
    """
    @brief
        Defines options for this program, using all possible configurations.

    @return
        An  ArgumentParser.
    """

    logger.debug("#")
    logger.debug(f"# Entering {EXEC_NAME} defineSpecificProgramOptions()")
    logger.debug("#")

    parser: ShearValidationArgumentParser = ShearValidationArgumentParser()

    parser.add_matched_catalog_arg()

    logger.debug(f"# Exiting {EXEC_NAME} defineSpecificProgramOptions()")

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """ Main entry point method
    """

    executor = ShearBiasValExecutor(run_from_args_function=validate_shear_bias_from_args,
                                    log_options=ValLogOptions(executable_name=EXEC_NAME),
                                    run_args=RunArgs(d_run_kwargs={"mode": ExecutionMode.LOCAL}))

    executor.run(args, logger=logger, pass_args_as_dict=True)


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
