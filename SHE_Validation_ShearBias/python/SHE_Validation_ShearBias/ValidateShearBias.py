""" @file ValidateShearBias.py

    Created 8 July 2021

    Executable for performing shear bias validation on data from one observation.
"""

__updated__ = "2021-07-08"

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

import argparse

from SHE_PPT.logging import getLogger
from SHE_PPT.utility import get_arguments_string

import SHE_Validation
from .validate_shear_bias import validate_shear_bias_from_args


def defineSpecificProgramOptions():
    """
    @brief
        Defines options for this program, using all possible configurations.

    @return
        An  ArgumentParser.
    """

    logger = getLogger(__name__)

    logger.debug('#')
    logger.debug('# Entering SHE_Validation_ValidateShearBias defineSpecificProgramOptions()')
    logger.debug('#')

    parser = argparse.ArgumentParser()

    # Input filenames
    parser.add_argument('--matched_catalog', type=str,
                        help='Desired filename for output matched catalog data product (XML data product).')

    # Output filenames
    parser.add_argument('--shear_bias_validation_test_results_product', type=str,
                        help='Desired filename for output shear bias validation test results (XML data product).')

    # Arguments needed by the pipeline runner
    parser.add_argument('--workdir', type=str, default=".")
    parser.add_argument('--logdir', type=str, default=".")

    # Optional arguments (can't be used with pipeline runner)
    parser.add_argument('--profile', action='store_true',
                        help='Store profiling data for execution.')

    logger.debug('Exiting SHE_Validation_ValidateShearBias defineSpecificProgramOptions()')

    return parser


def mainMethod(args):
    """
    @brief
        The "main" method for this program, to generate galaxy images.

    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger = getLogger(__name__)

    logger.debug('#')
    logger.debug('# Entering SHE_Validation_ValidateShearBias mainMethod()')
    logger.debug('#')

    exec_cmd = get_arguments_string(args, cmd=f"E-Run SHE_Validation {SHE_Validation.__version__} SHE_Validation_ValidateShearBias",
                                    store_true=["profile"])
    logger.info('Execution command for this step:')
    logger.info(exec_cmd)

    if args.profile:
        import cProfile
        cProfile.runctx("validate_shear_bias_from_args(args,dry_run=dry_run)", {},
                        {"validate_shear_bias_from_args": validate_shear_bias_from_args,
                         "args": args, },
                        filename="validate_shear_bias_from_args.prof")
    else:
        validate_shear_bias_from_args(args)

    logger.debug('Exiting SHE_Validation_ValidateShearBias mainMethod()')


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
