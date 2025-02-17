"""
:file: python/SHE_Validation_PSF/file_io.py

:date: 28 April 2022
:author: Bryan Gillis

Classes and functions related to file I/O for PSF validation tests
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


class PsfResSPPlotFileNamer(SheValFileNamer):
    """ SheFileNamer specialized for PSF-Res (Star Pos) plotting.
    """

    # Attributes from the base class we're overriding
    _extension: str = "png"


class PsfResSPHistFileNamer(PsfResSPPlotFileNamer):
    """ SheFileNamer specialized for PSF-Res (Star Pos) histogram plotting.
    """

    # Attributes from the base class we're overriding
    _type_name_body: str = "PRSP-HIST"


class PsfResSPCumHistFileNamer(PsfResSPHistFileNamer):
    """ SheFileNamer specialized for PSF-Res (Star Pos) cumulative histogram plotting.
    """

    # Attributes from the base class we're overriding
    _type_name_tail: str = "CUM"


class PsfResSPScatterFileNamer(PsfResSPPlotFileNamer):
    """ SheFileNamer specialized for PSF-Res (Star Pos) scatterplot plotting.
    """

    # Attributes from the base class we're overriding
    _type_name_body: str = "PRSP-SCATTER"
