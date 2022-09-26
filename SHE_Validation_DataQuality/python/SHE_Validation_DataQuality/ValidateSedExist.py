"""
:file: python/SHE_Validation_DataQuality/ValidateSedExist.py

:date: 09/21/22
:author: Bryan Gillis

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
from typing import Any, Dict, Type

from SHE_PPT import logging as log
from SHE_PPT.constants.config import AnalysisConfigKeys, ValidationConfigKeys
from SHE_Validation.argument_parser import ValidationArgumentParser
from SHE_Validation.executor import SheValExecutor, ValLogOptions, ValReadConfigArgs
from SHE_Validation_DataQuality.constants.sed_exist_config import (D_SED_EXIST_CONFIG_CLINE_ARGS,
                                                                   D_SED_EXIST_CONFIG_DEFAULTS,
                                                                   D_SED_EXIST_CONFIG_TYPES, )

EXEC_NAME = "SHE_Validation_ValidateSedExist"

logger = log.getLogger(__name__)


class SedExistReadConfigArgs(ValReadConfigArgs):
    """ Subclass of ReadConfigArgs which overrides defaults.
    """

    def __post_init__(self):
        """ Override __post_init__ to set different default values
        """

        self.d_config_defaults = (self.d_config_defaults if self.d_config_defaults is not None
                                  else D_SED_EXIST_CONFIG_DEFAULTS)
        self.d_config_defaults = (self.d_config_types if self.d_config_types is not None
                                  else D_SED_EXIST_CONFIG_TYPES)
        self.d_config_cline_args = (self.d_config_cline_args if self.d_config_cline_args is not None
                                    else D_SED_EXIST_CONFIG_CLINE_ARGS)
        self.s_config_keys_types = (self.s_config_keys_types if self.s_config_keys_types is not None
                                    else {ValidationConfigKeys, AnalysisConfigKeys})


class ShearBiasValExecutor(SheValExecutor):
    """ Subclass of SheValExecutor which further overrides attribute types.
    """

    # Attributes with different types from base class
    config_args: SedExistReadConfigArgs
    config_args_type: Type = SedExistReadConfigArgs


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
    parser = ValidationArgumentParser()

    logger.debug(f'# Exiting {EXEC_NAME} defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args: Namespace) -> None:
    """Main entry point function for program.
    """

    executor = ShearBiasValExecutor(run_from_args_function=run_validate_sed_exist_from_args,
                                    log_options=ValLogOptions(executable_name=EXEC_NAME), )

    executor.run(args, logger=logger, pass_args_as_dict=True)


def run_validate_sed_exist_from_args(d_args: Dict[str, Any]) -> None:
    """Dummy implementation of run function.
    """
    pass


def main() -> None:
    """Alternate entry point for non-Elements execution.
    """

    parser = defineSpecificProgramOptions()

    args = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
