""" @file executor.py

    Created 14 October 2021

    Class to handle primary execution of SHE_Validation executables
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

from dataclasses import dataclass
from typing import Type

from SHE_PPT.constants.config import ValidationConfigKeys
from SHE_PPT.executor import LogOptions, ReadConfigArgs, SheExecutor
from SHE_PPT.utility import default_value_if_none
from . import __version__
from .constants.default_config import (D_VALIDATION_CONFIG_CLINE_ARGS, D_VALIDATION_CONFIG_DEFAULTS,
                                       D_VALIDATION_CONFIG_TYPES, )


@dataclass
class ValLogOptions(LogOptions):
    """ Subclass of LogOptions which overrides defaults for project_name and project_version.
    """
    project_name: str = "SHE_Validation"
    project_version: str = __version__


class ValReadConfigArgs(ReadConfigArgs):
    """ Subclass of ReadConfigArgs which overrides defaults.
    """

    def __post_init__(self):
        """ Override __post_init__ to set different default values
        """

        self.d_config_defaults = default_value_if_none(self.d_config_defaults,
                                                       D_VALIDATION_CONFIG_DEFAULTS)
        self.d_config_types = default_value_if_none(self.d_config_types,
                                                    D_VALIDATION_CONFIG_TYPES)
        self.d_config_cline_args = default_value_if_none(self.d_config_cline_args,
                                                         D_VALIDATION_CONFIG_CLINE_ARGS)
        self.s_config_keys_types = default_value_if_none(self.s_config_keys_types,
                                                         {ValidationConfigKeys})


class SheValExecutor(SheExecutor):
    """ Subclass of SheExecutor which overrides attribute types.
    """

    # Attributes with different types from base class
    log_options: ValLogOptions
    config_args: ValReadConfigArgs
    config_args_type: Type = ValReadConfigArgs
