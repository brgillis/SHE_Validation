""" @file MatchToTUExtend.py

    Created 10 May 2019

    Executable for matching the output of the Analysis pipeline to SIM's True Universe catalogs. This specialized
    versions assumes that bin data columns won't be added, allowing some input ports to be left out.
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
from copy import deepcopy

from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_PPT.executor import ReadConfigArgs
from SHE_PPT.logging import getLogger
from SHE_Validation.MatchToTU import (D_TUM_CONFIG_CLINE_ARGS, D_TUM_CONFIG_DEFAULTS, D_TUM_CONFIG_TYPES,
                                      S_TUM_CONFIG_KEYS, S_TUM_STORE_TRUE, TUMatchArgumentParser, )
from SHE_Validation.executor import ValLogOptions
from SHE_Validation.match_to_tu import match_to_tu_from_args
from SHE_Validation_ShearBias.executor import ShearBiasValExecutor

logger = getLogger(__name__)

EXEC_NAME = "SHE_Validation_MatchToTUExtend"


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

    parser = TUMatchArgumentParser()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """ Main entry point method
    """

    # From the base method, change default for adding bin columns
    d_tum_extend_config_defaults = deepcopy(D_TUM_CONFIG_DEFAULTS)
    d_tum_extend_config_defaults[ValidationConfigKeys.TUM_ADD_BIN_COLUMNS] = True

    executor = ShearBiasValExecutor(run_from_args_function = match_to_tu_from_args,
                                    log_options = ValLogOptions(executable_name = EXEC_NAME,
                                                                s_store_true = S_TUM_STORE_TRUE),
                                    config_args = ReadConfigArgs(d_config_defaults = d_tum_extend_config_defaults,
                                                                 d_config_types = D_TUM_CONFIG_TYPES,
                                                                 d_config_cline_args = D_TUM_CONFIG_CLINE_ARGS,
                                                                 s_config_keys_types = S_TUM_CONFIG_KEYS,
                                                                 ))

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