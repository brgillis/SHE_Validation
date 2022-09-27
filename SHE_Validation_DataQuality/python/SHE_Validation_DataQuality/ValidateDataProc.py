"""
:file: python/SHE_Validation_DataQuality/ValidateDataProc.py

:date: 09/21/22
:author: Bryan Gillis

"""

__updated__ = "2022-04-08"

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

from SHE_PPT import logging as log
from SHE_PPT.constants.config import (D_GLOBAL_CONFIG_CLINE_ARGS, D_GLOBAL_CONFIG_DEFAULTS,
                                      D_GLOBAL_CONFIG_TYPES, ReconciliationConfigKeys, )
from SHE_PPT.executor import ReadConfigArgs
from SHE_Validation.argument_parser import CA_SHE_REC_CAT, CA_SHE_REC_CHAINS, ValidationArgumentParser
from SHE_Validation.executor import SheValExecutor, ValLogOptions
from SHE_Validation_DataQuality.validate_data_proc import run_validate_data_proc_from_args

EXEC_NAME = "SHE_Validation_ValidateDataProc"

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
    parser.add_input_arg(f"--{CA_SHE_REC_CAT}",
                         type=str,
                         help="Filename of the input reconciled shear measurements .xml data product to be checked.")
    parser.add_input_arg(f"--{CA_SHE_REC_CHAINS}",
                         type=str,
                         default=None,
                         help="(Optional) Filename of the input reconciled shear measurement chains .xml data product "
                              "to be checked.")

    # Output arguments
    parser.add_test_result_arg()

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

    config_args = ReadConfigArgs(d_config_defaults=D_GLOBAL_CONFIG_DEFAULTS,
                                 d_config_types=D_GLOBAL_CONFIG_TYPES,
                                 d_config_cline_args=D_GLOBAL_CONFIG_CLINE_ARGS,
                                 s_config_keys_types={ReconciliationConfigKeys})

    executor = SheValExecutor(run_from_args_function=run_validate_data_proc_from_args,
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
