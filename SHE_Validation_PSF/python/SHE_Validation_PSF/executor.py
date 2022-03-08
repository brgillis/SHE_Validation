""" @file executor.py

    Created 08 March 2022 by Bryan Gillis

    Class to handle primary execution of SHE_Validation PSF executables.
"""

__updated__ = "2022-04-08"

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
from .constants.psf_res_default_config import (D_PSF_RES_CONFIG_CLINE_ARGS, D_PSF_RES_CONFIG_DEFAULTS,
                                               D_PSF_RES_CONFIG_TYPES, )


# ReadConfigArgs and Executor class for CTI-Gal validation

class PsfResReadConfigArgs(ValReadConfigArgs):
    """ Subclass of ReadConfigArgs which overrides defaults.
    """

    def __post_init__(self):
        """ Override __post_init__ to set different default values
        """

        self.d_config_defaults = default_value_if_none(self.d_config_defaults,
                                                       D_PSF_RES_CONFIG_DEFAULTS)
        self.d_config_types = default_value_if_none(self.d_config_types,
                                                    D_PSF_RES_CONFIG_TYPES)
        self.d_config_cline_args = default_value_if_none(self.d_config_cline_args,
                                                         D_PSF_RES_CONFIG_CLINE_ARGS)
        self.s_config_keys_types = default_value_if_none(self.s_config_keys_types,
                                                         {AnalysisConfigKeys,
                                                          ValidationConfigKeys})


class PsfResValExecutor(SheValExecutor):
    """ Subclass of SheValExecutor which further overrides attribute types.
    """

    # Attributes with different types from base class
    config_args: PsfResReadConfigArgs
    config_args_type: Type = PsfResReadConfigArgs
