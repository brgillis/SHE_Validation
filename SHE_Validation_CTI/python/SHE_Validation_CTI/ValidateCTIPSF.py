""" @file ValidateCTIPSF.py

    Created 28 October 2021 by Bryan Gillis

    Entry-point file for CTI-PSF local validation executable
"""

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
from SHE_Validation.executor import ValLogOptions
from SHE_Validation_CTI.argument_parser import CtiPsfArgumentParser
from SHE_Validation_CTI.executor import CtiPsfValExecutor
from .validate_cti_gal import run_validate_cti_gal_from_args

EXEC_NAME = "SHE_Validation_ValidateCTIPSF"

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
    parser = CtiPsfArgumentParser()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """ Main entry point method
    """

    executor = CtiPsfValExecutor(run_from_args_function=run_validate_cti_gal_from_args,
                                 log_options=ValLogOptions(executable_name=EXEC_NAME), )

    executor.run(args, logger=logger)


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
