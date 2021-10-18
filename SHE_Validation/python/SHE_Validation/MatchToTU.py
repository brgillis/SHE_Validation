""" @file MatchToTu.py

    Created 10 May 2019

    Executable for matching the output of the Analysis pipeline to SIM's True Universe catalogs.
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
from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_PPT.executor import ReadConfigArgs
from SHE_PPT.logging import getLogger
from SHE_Validation.argument_parser import ValidationArgumentParser
from SHE_Validation.constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                                     D_VALIDATION_CONFIG_TYPES, )
from SHE_Validation.executor import ValLogOptions
from SHE_Validation.match_to_tu import match_to_tu_from_args
from SHE_Validation_ShearBias.executor import ShearBiasValExecutor

# Create the default config dicts for this task by extending the global default config dicts
D_TUM_CONFIG_DEFAULTS = {**D_VALIDATION_CONFIG_DEFAULTS,
                         ValidationConfigKeys.TUM_ADD_BIN_COLUMNS: False}
D_TUM_CONFIG_TYPES = {**D_VALIDATION_CONFIG_TYPES,
                      ValidationConfigKeys.TUM_ADD_BIN_COLUMNS: bool}
D_TUM_CONFIG_CLINE_ARGS = {**D_VALIDATION_CONFIG_CLINE_ARGS,
                           ValidationConfigKeys.TUM_ADD_BIN_COLUMNS: "add_bin_columns"}

logger = getLogger(__name__)


# noinspection PyPep8Naming
def defineSpecificProgramOptions():
    """
    @brief
        Defines options for this program, using all possible configurations.

    @return
        An  ArgumentParser.
    """

    logger.debug('#')
    logger.debug('# Entering SHE_Validation_MatchToTU defineSpecificProgramOptions()')
    logger.debug('#')

    parser = ValidationArgumentParser()

    # Input filenames
    parser.add_measurements_arg()
    parser.add_argument('--data_images', type = str, default = None,
                        help = 'INPUT (optional): .json listfile containing filenames of data image products.')
    parser.add_argument('--detections_tables', type = str, default = None,
                        help = 'INPUT (optional): .json listfile containing filenames of detections table products.')

    parser.add_argument('--tu_galaxy_catalog_list', type = str, default = None,
                        help = 'INPUT: Filename for True Universe Galaxy Catalog listfile (.json).')
    parser.add_argument('--tu_star_catalog_list', type = str, default = None,
                        help = 'INPUT: Filename for True Universe Star Catalog listfile (.json).')
    parser.add_argument('--tu_galaxy_catalog', type = str, default = None,
                        help = 'INPUT: Filename for True Universe Galaxy Catalog data product (XML data product)')
    parser.add_argument('--tu_star_catalog', type = str, default = None,
                        help = 'INPUT: Filename for True Universe Star Catalog data product (XML data product)')
    parser.add_argument('--tu_output_product', type = str, default = None,
                        help = 'INPUT: Filename for True Universe Output Product data product (XML data product)')

    # Output filenames
    parser.add_argument('--matched_catalog', type = str,
                        help = 'OUTPUT: Desired filename for output matched catalog data product (XML data product).')

    # Optional arguments (can't be used with pipeline runner)
    parser.add_argument('--sim_path', type = str, default = "/mnt/cephfs/share/SC8/SIM",
                        help = "OPTION: Path to where the SIM data is stored")
    parser.add_argument('--match_threshold', type = float, default = 0.3,
                        help = "OPTION: Maximum distance allowed for a match in units of arcsec.")
    parser.add_argument('--add_bin_columns', action = "store_true", default = False,
                        help = "OPTION: If set, will add columns to the output catalog with data used for binning.")

    logger.debug('Exiting SHE_Validation_MatchToTU defineSpecificProgramOptions()')

    return parser


# noinspection PyPep8Naming
def mainMethod(args):
    """ Main entry point method
    """

    executor = ShearBiasValExecutor(run_from_args_function = match_to_tu_from_args,
                                    log_options = ValLogOptions(executable_name = "SHE_Validation_MatchToTU",
                                                                s_store_true = {"add_bin_columns"}),
                                    config_args = ReadConfigArgs(d_config_defaults = D_TUM_CONFIG_DEFAULTS,
                                                                 d_config_types = D_TUM_CONFIG_TYPES,
                                                                 d_config_cline_args = D_TUM_CONFIG_CLINE_ARGS))

    executor.run(args, logger = logger)


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = defineSpecificProgramOptions()

    args = parser.parse_args()

    mainMethod(args)


if __name__ == "__main__":
    main()
