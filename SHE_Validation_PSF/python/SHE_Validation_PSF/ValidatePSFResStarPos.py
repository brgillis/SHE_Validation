"""
:file: python/SHE_Validation_PSF/ValidatePSFResStarPos.py

:date: 8 March 2022
:author: Bryan Gillis

Entry-point module for the PSFResStarPos validation executable
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

from typing import TYPE_CHECKING

from SHE_PPT import logging as log
from SHE_Validation.executor import ValLogOptions
from SHE_Validation_PSF.argument_parser import PsfResArgumentParser
from SHE_Validation_PSF.executor import PsfResValExecutor
from SHE_Validation_PSF.validate_psf_res_star_pos import run_validate_psf_res_from_args

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace  # noqa F401

EXEC_NAME = "SHE_Validation_ValidatePSFResStarPos"

logger = log.getLogger(__name__)


# noinspection PyPep8Naming
def defineSpecificProgramOptions():
    """Allows one to define the (command line and configuration file) options specific to this program. See the
    Elements documentation for more details.

    Returns
    -------
    parser: ArgumentParser
    """

    logger.debug(f'# Entering {EXEC_NAME} defineSpecificProgramOptions()')

    # Set up the argument parser, using built-in methods where possible
    parser = PsfResArgumentParser()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args):
    """Main entry point function for program.

    Parameters
    ----------
    args : Namespace
        The parsed arguments for this program, as would be obtained through e.g. `args = parser.parse_args()`
    """

    executor = PsfResValExecutor(run_from_args_function=run_validate_psf_res_from_args,
                                 log_options=ValLogOptions(executable_name=EXEC_NAME), )

    executor.run(args, logger=logger,
                 pass_args_as_dict=True)


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
