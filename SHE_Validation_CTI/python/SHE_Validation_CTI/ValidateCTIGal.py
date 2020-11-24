""" @file ValidateCTIGal.py

    Created 24 November 2020 by Bryan Gillis

    Entry-point file for CTI-Gal validation executable.
"""

__updated__ = "2020-11-24"

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

import argparse
from SHE_PPT import logging as log
from SHE_PPT.utility import get_arguments_string

import SHE_Validation
from SHE_Validation_CTI.validate_cti_gal import run_validate_cti_gal_from_args

profiling_filename = "validate_cti_gal.prof"

logger = log.getLogger(__name__)


def defineSpecificProgramOptions():
    """
    @brief Allows to define the (command line and configuration file) options
    specific to this program

    @details
        See the Elements documentation for more details.
    @return
        An  ArgumentParser.
    """

    logger.debug('# Entering SHE_Validation_ValidateCTIGal defineSpecificProgramOptions()')

    parser = argparse.ArgumentParser()

    # Required input arguments

    parser.add_argument('--vis_calibrated_frame_listfile', type=str,
                        help='INPUT: .json listfile containing filenames of exposure image products.')

    parser.add_argument('--she_exposure_segmentation_map_listfile', type=str,
                        help='INPUT: .json listfile containing filenames of remapped exposure segmentation maps.')

    parser.add_argument('--mer_final_catalog_listfile', type=str,
                        help='INPUT: .json listfile containing filenames of mer final catalogs.')

    parser.add_argument('--she_validated_measurements_product', type=str,
                        help='INPUT: Filename of the cross-validated shear measurements .xml data product.')

    parser.add_argument("--pipeline_config", default=None, type=str,
                        help="INPUT: Pipeline-wide configuration file.")

    parser.add_argument('--mdb', type=str, default=None,  # Use default to allow simple running with default values
                        help='INPUT: Mission Database .xml file')

    # Output arguments

    parser.add_argument('--she_validation_test_results_product', type=str,
                        help='OUTPUT: Desired filename of output .xml data product for validation test results')

    # Optional input arguments (cannot be used in pipeline)

    parser.add_argument('--profile', action="store_true",
                        help=f'If set, will output profiling data to {profiling_filename}')

    # Arguments needed by the pipeline runner
    parser.add_argument('--workdir', type=str, default=".")
    parser.add_argument('--logdir', type=str, default=".")

    logger.debug('# Exiting SHE_Validation_ValidateCTIGal defineSpecificProgramOptions()')

    return parser


def mainMethod(args):
    """
    @brief The "main" method.
    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger.info('#')
    logger.info('# Entering ValidateCTIGal mainMethod()')
    logger.info('#')

    exec_cmd = get_arguments_string(args, cmd="E-Run SHE_Validation " + SHE_Validation.__version__ + " SHE_Validation_ValidateCTIGal",
                                    store_true=["profile"])
    logger.info('Execution command for this step:')
    logger.info(exec_cmd)

    if args.profile:
        import cProfile
        cProfile.runctx("run_validate_cti_gal_from_args(args)", {},
                        {"run_validate_cti_gal_from_args": run_validate_cti_gal_from_args,
                         "args": args},
                        filename=profiling_filename)
    else:
        run_validate_cti_gal_from_args(args)

    logger.info('#')
    logger.info('# Exiting ValidateCTIGal mainMethod()')
    logger.info('#')
