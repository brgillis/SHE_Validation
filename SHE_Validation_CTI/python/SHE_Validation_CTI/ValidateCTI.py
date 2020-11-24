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


"""
File: python/SHE_Validation_CTI/ValidateCTI.py

Created on: 11/24/20
Author: user
"""

import argparse
from SHE_PPT import logging as log

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

    parser = argparse.ArgumentParser()

    # Required input arguments

    parser.add_argument('--vis_calibrated_frame_listfile', type=str,
                        help='.json listfile containing filenames of exposure image products.')

    parser.add_argument('--she_exposure_segmentation_map_listfile', type=str,
                        help='.json listfile containing filenames of remapped exposure segmentation maps.')

    parser.add_argument('--mer_final_catalog_listfile', type=str,
                        help='.json listfile containing filenames of mer final catalogs.')

    parser.add_argument('--she_validated_measurements', type=str,
                        help='Filename of the cross-validated shear measurements .xml data product.')

    parser.add_argument("--pipeline_config", default=None, type=str,
                        help="Pipeline-wide configuration file.")

    parser.add_argument('--mdb', type=str, default=None,  # Use default to allow simple running with default values
                        help='Mission Database .xml file')

    # Output arguments

    parser.add_argument('--she_validation_test_results', type=str,
                        help='Desired filename of output .xml data product for validation test results')

    # Arguments needed by the pipeline runner
    parser.add_argument('--workdir', type=str, default=".")
    parser.add_argument('--logdir', type=str, default=".")

    logger.debug('# Exiting SHE_CTE_EstimateShear defineSpecificProgramOptions()')

    return parser


def mainMethod(args):
    """
    @brief The "main" method.
    @details
        This method is the entry point to the program. In this sense, it is
        similar to a main (and it is why it is called mainMethod()).
    """

    logger.info('#')
    logger.info('# Entering ValidateCTI mainMethod()')
    logger.info('#')

    # !! Getting the option from the example option in defineSpecificProgramOption
    # !! e.g string_option = args.string_value

    #
    # !!! Write you main code here !!!
    #

    logger.info('#')
    logger.info('# Exiting ValidateCTI mainMethod()')
    logger.info('#')
