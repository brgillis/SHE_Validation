"""
:file: python/SHE_Validation_DataQuality/ValidateSedExist.py

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
from typing import Any, Dict

from SHE_PPT import logging as log
from SHE_PPT.constants.config import AnalysisConfigKeys, ValidationConfigKeys
from SHE_Validation.argument_parser import CA_PHZ_CAT_LIST, ValidationArgumentParser
from SHE_Validation.constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                                     D_VALIDATION_CONFIG_TYPES, )
from SHE_Validation.executor import SheValExecutor, ValLogOptions, ValReadConfigArgs

# Use a constant string for each cline-arg
CA_PSF_NUM_STARS = "no_stars_to_fit"

# Create the default config dicts for this task by extending the tot default config dicts
D_SED_EXIST_CONFIG_DEFAULTS = {**D_VALIDATION_CONFIG_DEFAULTS,
                               AnalysisConfigKeys.PSF_NUM_STARS: 200}
D_SED_EXIST_CONFIG_TYPES = {**D_VALIDATION_CONFIG_TYPES,
                            AnalysisConfigKeys.PSF_NUM_STARS: int}
D_SED_EXIST_CONFIG_CLINE_ARGS = {**D_VALIDATION_CONFIG_CLINE_ARGS,
                                 AnalysisConfigKeys.PSF_NUM_STARS: CA_PSF_NUM_STARS}

EXEC_NAME = "SHE_Validation_ValidateSedExist"

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
    parser.add_input_arg(CA_PHZ_CAT_LIST,
                         type=str,
                         help=".json listfile containing filenames of PHZ catalog products for all tiles overlapping "
                              "the observation to be analysed.")
    parser.add_calibrated_frame_arg()
    parser.add_final_catalog_arg()

    # Output arguments
    parser.add_test_result_arg()

    # Options
    parser.add_option_arg(f"--{CA_PSF_NUM_STARS}",
                          type=D_SED_EXIST_CONFIG_TYPES[AnalysisConfigKeys.PSF_NUM_STARS],
                          help="Number of stars to be used by the PSF Fitter.")

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

    config_args = ValReadConfigArgs(d_config_defaults=D_SED_EXIST_CONFIG_DEFAULTS,
                                    d_config_types=D_SED_EXIST_CONFIG_TYPES,
                                    d_config_cline_args=D_SED_EXIST_CONFIG_CLINE_ARGS,
                                    s_config_keys_types={ValidationConfigKeys, AnalysisConfigKeys})

    executor = SheValExecutor(run_from_args_function=run_validate_sed_exist_from_args,
                              log_options=ValLogOptions(executable_name=EXEC_NAME),
                              config_args=config_args)

    executor.run(args, logger=logger, pass_args_as_dict=True)


def run_validate_sed_exist_from_args(d_args: Dict[str, Any]):
    """Dummy implementation of run function. TODO: Implement properly
    """
    pass


def main():
    """Alternate entry point for non-Elements execution.
    """

    parser = defineSpecificProgramOptions()

    args = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
