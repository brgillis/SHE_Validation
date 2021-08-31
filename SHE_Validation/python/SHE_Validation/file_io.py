""" @file file_io.py

    Created 30 August 2021

    Utility functions and classes related to I/O
"""

__updated__ = "2021-08-31"

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

from SHE_Validation.constants.test_info import BinParameters

from . import __version__


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

    def __init__(self,
                 method: Optional[ShearEstimationMethods] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_index: Optional[int] = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        if method is not None:
            self._method = method

        if bin_parameter is not None:
            self._bin_parameter = bin_parameter

        if bin_index is not None:
            self._bin_index = bin_index

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

    # Protected methods

    def _determine_instance_id_body(self):

        # Piece together the instance ID body from the components, leaving out Nones
        self._instance_id_body = join_without_none(l_s=[self.method.value,
                                                        self.bin_parameter.value,
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
            if not "instance_id including timestamp and release" in str(e):
                raise
            # Instance ID is too long, so shorten it just enough to fit
            self.instance_id = self.instance_id[-instance_id_maxlen:]
            return super().get()
