"""
:file: python/SHE_Validation_PSF/__init__.py

:date: 24 Mar 2021
:author: Bryan Gillis

SHE_Validation_PSF package, for validation tests and documentation related to PSF
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

from pkgutil import extend_path

__description__ = 'Python package for unit tests relating to PSF.'

if '__path__' in locals():
    # noinspection PyUnboundLocalVariable
    __path__ = extend_path(__path__, __name__)

del extend_path
