"""
:file: python/SHE_Validation/file_io.py

:date: 30 August 2021
:author: Bryan Gillis

Utility functions and classes related to I/O
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

import os
from typing import Optional

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.file_io import SheFileNamer, instance_id_maxlen
from SHE_PPT.utility import join_without_none
from . import __version__
from .constants.test_info import BinParameters, D_BIN_PARAMETER_META


class SheValFileNamer(SheFileNamer):
    """ SheFileNamer specialized for the SHE Validation project.
    """

    # Attributes from the base class we're overriding
    _type_name_head: str = "VAL"
    default_type_name: str = "SHE_VALIDATION_FILE"
    _version: str = __version__

    # New attributes
    _method: Optional[ShearEstimationMethods] = None
    _bin_parameter: Optional[BinParameters] = None
    _bin_index: Optional[int] = None
    _exp_index: Optional[int] = None

    def __init__(self,
                 method: Optional[ShearEstimationMethods] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_index: Optional[int] = None,
                 exp_index: Optional[int] = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        if method is not None:
            self._method = method

        if bin_parameter is not None:
            self._bin_parameter = bin_parameter

        if bin_index is not None:
            self._bin_index = bin_index

        if exp_index is not None:
            self._exp_index = exp_index

    @property
    def method(self) -> Optional[ShearEstimationMethods]:
        return self._method

    @method.setter
    def method(self, method: Optional[ShearEstimationMethods]) -> None:
        self._method = method
        self.instance_id_body = None

    @property
    def bin_parameter(self) -> Optional[BinParameters]:
        return self._bin_parameter

    @bin_parameter.setter
    def bin_parameter(self, bin_parameter: Optional[BinParameters]) -> None:
        self._bin_parameter = bin_parameter
        self.instance_id_body = None

    @property
    def bin_index(self) -> Optional[int]:
        return self._bin_index

    @bin_index.setter
    def bin_index(self, bin_index: Optional[int]) -> None:
        self._bin_index = bin_index
        self.instance_id_body = None

    @property
    def exp_index(self) -> Optional[int]:
        return self._exp_index

    @exp_index.setter
    def exp_index(self, exp_index: Optional[int]) -> None:
        self._exp_index = exp_index
        self.instance_id_body = None

    # Protected methods

    def _determine_instance_id_body(self):

        # Piece together the instance ID body from the components, leaving out Nones

        if self.method is not None:
            method_value: Optional[str] = self.method.value
        else:
            method_value: Optional[str] = None

        if self.bin_parameter is not None:
            bin_id_tail: Optional[str] = D_BIN_PARAMETER_META[self.bin_parameter].id_tail
        else:
            bin_id_tail: Optional[str] = None

        self._instance_id_body = join_without_none(l_s=[method_value,
                                                        self.exp_index,
                                                        bin_id_tail,
                                                        self.bin_index,
                                                        os.getpid()],
                                                   default=None)

    # Public methods

    def get(self):
        """ Wrapper for parent get to check for too-long filenames.
        """

        try:
            return super().get()
        except ValueError as e:
            if "instance_id including timestamp and release" not in str(e):
                raise
            # Instance ID is too long, so shorten it just enough to fit
            self.instance_id = self.instance_id[-instance_id_maxlen:]
            return super().get()
