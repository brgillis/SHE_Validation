""" @file executor.py

    Created 14 October 2021

    Class to handle primary execution of SHE_Validation Shear Bias executables
"""

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

from typing import Type

from SHE_PPT.constants.config import AnalysisConfigKeys, ValidationConfigKeys
from SHE_PPT.utility import default_value_if_none
from SHE_Validation.executor import SheValExecutor, ValReadConfigArgs
from .constants.shear_bias_default_config import (D_SHEAR_BIAS_CONFIG_CLINE_ARGS, D_SHEAR_BIAS_CONFIG_DEFAULTS,
                                                  D_SHEAR_BIAS_CONFIG_TYPES, )


class ShearBiasReadConfigArgs(ValReadConfigArgs):
    """ Subclass of ReadConfigArgs which overrides defaults.
    """

    def __post_init__(self):
        """ Override __post_init__ to set different default values
        """

        self.d_config_defaults = default_value_if_none(self.d_config_defaults,
                                                       D_SHEAR_BIAS_CONFIG_DEFAULTS)
        self.d_config_types = default_value_if_none(self.d_config_types,
                                                    D_SHEAR_BIAS_CONFIG_TYPES)
        self.d_config_cline_args = default_value_if_none(self.d_config_cline_args,
                                                         D_SHEAR_BIAS_CONFIG_CLINE_ARGS)
        self.s_config_keys_types = default_value_if_none(self.s_config_keys_types,
                                                         {ValidationConfigKeys,
                                                          AnalysisConfigKeys})


class ShearBiasValExecutor(SheValExecutor):
    """ Subclass of SheValExecutor which further overrides attribute types.
    """

    # Attributes with different types from base class
    config_args: ShearBiasReadConfigArgs
    config_args_type: Type = ShearBiasReadConfigArgs
