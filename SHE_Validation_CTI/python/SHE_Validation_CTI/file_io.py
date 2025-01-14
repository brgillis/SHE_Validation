"""
:file: python/SHE_Validation_CTI/file_io.py

:date: 30 August 2021
:author: Bryan Gillis

Utility functions and classes related to I/O for the CTI-Gal test case
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

from SHE_Validation.file_io import SheValFileNamer


class CtiPlotFileNamer(SheValFileNamer):
    """ SheFileNamer specialized for CTI plotting.
    """

    # Attributes from the base class we're overriding
    _extension: str = "png"


class CtiGalPlotFileNamer(CtiPlotFileNamer):
    """ SheFileNamer specialized for Shear Bias test cases.
    """

    # Attributes from the base class we're overriding
    _type_name_body: str = "CTI-GAL-PLOT"


class CtiPsfPlotFileNamer(CtiPlotFileNamer):
    """ SheFileNamer specialized for Shear Bias test cases.
    """

    # Attributes from the base class we're overriding
    _type_name_body: str = "CTI-PSF-PLOT"
