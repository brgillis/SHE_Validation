"""
:file: python/SHE_Validation_PSF/SHE_Validation_ValidatePSFResInterp.py

:date: 10/06/22
:author: Bryan Gillis

"""

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

from argparse import ArgumentParser, Namespace

from SHE_Validation_PSF.validate_psf_res_interp import run_validate_psf_res_interp_from_args

from SHE_PPT import logging as log
from SHE_PPT.constants.config import (D_GLOBAL_CONFIG_CLINE_ARGS, D_GLOBAL_CONFIG_DEFAULTS,
                                      D_GLOBAL_CONFIG_TYPES, ValidationConfigKeys, )
from SHE_PPT.executor import ReadConfigArgs
from SHE_Validation.argument_parser import ValidationArgumentParser
from SHE_Validation.executor import SheValExecutor, ValLogOptions

EXEC_NAME = "SHE_Validation_ValidatePSFResInterp"

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
    parser = ValidationArgumentParser()

    # Input arguments

    # Output arguments
    parser.add_test_result_arg()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


def mainMethod(args):
    """Main entry point function for program.

    Parameters
    ----------
    args : Namespace
        The parsed arguments for this program, as would be obtained through e.g. `args = parser.parse_args()`
    """

    config_args = ReadConfigArgs(d_config_defaults=D_GLOBAL_CONFIG_DEFAULTS,
                                 d_config_types=D_GLOBAL_CONFIG_TYPES,
                                 d_config_cline_args=D_GLOBAL_CONFIG_CLINE_ARGS,
                                 s_config_keys_types={ValidationConfigKeys})

    executor = SheValExecutor(run_from_args_function=run_validate_psf_res_interp_from_args,
                              log_options=ValLogOptions(executable_name=EXEC_NAME),
                              config_args=config_args)

    executor.run(args, logger=logger, pass_args_as_dict=True)


def main():
    """Alternate entry point for non-Elements execution.
    """

    parser = defineSpecificProgramOptions()

    args = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
