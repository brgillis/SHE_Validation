""" @file ValidatePSFRes.py

    Created 08 March 2022 by Bryan Gillis

    Entry-point file for PSF Residual validation executable.
"""

__updated__ = "2022-04-08"

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

from SHE_Validation_PSF.argument_parser import PsfResArgumentParser
from SHE_Validation_PSF.executor import PsfResValExecutor

from SHE_PPT import logging as log
from SHE_Validation.executor import ValLogOptions

EXEC_NAME = "SHE_Validation_ValidatePSFRes"

logger = log.getLogger(__name__)


# Dummy run_from_args_function until it's properly set up
def run_validate_psf_res_from_args(args: Namespace) -> None:
    return


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
    parser = PsfResArgumentParser()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """ Main entry point method
    """

    executor = PsfResValExecutor(run_from_args_function = run_validate_psf_res_from_args,
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
