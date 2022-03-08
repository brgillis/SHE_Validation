""" @file CalcCommonValData.py

    Created 10 May 2019

    Executable for collecting data common to validation executables and outputting it in a data table.
"""

__updated__ = "2021-08-12"

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

from SHE_PPT.argument_parser import ClineArgType
from SHE_PPT.constants.config import AnalysisConfigKeys, ValidationConfigKeys
from SHE_PPT.executor import ReadConfigArgs
from SHE_PPT.logging import getLogger
from .argument_parser import ValidationArgumentParser
from .calc_common_val_data import calc_common_val_data_from_args
from .constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                       D_VALIDATION_CONFIG_TYPES, )
from .executor import SheValExecutor, ValLogOptions

# Create the default config dicts for this task by extending the tot default config dicts
EXEC_NAME = "SHE_Validation_CalcCommonValData"

S_CCVD_CONFIG_KEYS = {AnalysisConfigKeys,
                      ValidationConfigKeys}
D_CCVD_CONFIG_DEFAULTS = {**D_VALIDATION_CONFIG_DEFAULTS}
D_CCVD_CONFIG_TYPES = {**D_VALIDATION_CONFIG_TYPES}
D_CCVD_CONFIG_CLINE_ARGS = {**D_VALIDATION_CONFIG_CLINE_ARGS}

logger = getLogger(__name__)


class CCVDArgumentParser(ValidationArgumentParser):

    def __init__(self):
        super().__init__()

        # Input filenames
        self.add_calibrated_frame_arg()
        self.add_final_catalog_arg()
        self.add_measurements_arg()

        # Output filenames
        self.add_extended_catalog_arg(arg_type = ClineArgType.OUTPUT)


# noinspection PyPep8Naming
def defineSpecificProgramOptions() -> ArgumentParser:
    """
    @brief
        Defines options for this program, using all possible configurations.

    @return
        An  ArgumentParser.
    """

    logger.debug('#')
    logger.debug(f'# Entering {EXEC_NAME} defineSpecificProgramOptions()')
    logger.debug('#')

    parser = CCVDArgumentParser()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """ Main entry point method
    """

    executor = SheValExecutor(run_from_args_function = calc_common_val_data_from_args,
                              log_options = ValLogOptions(executable_name = EXEC_NAME),
                              config_args = ReadConfigArgs(d_config_defaults = D_CCVD_CONFIG_DEFAULTS,
                                                           d_config_types = D_CCVD_CONFIG_TYPES,
                                                           d_config_cline_args = D_CCVD_CONFIG_CLINE_ARGS,
                                                           s_config_keys_types = S_CCVD_CONFIG_KEYS,
                                                           ))

    executor.run(args, logger = logger, pass_args_as_dict = True)


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
