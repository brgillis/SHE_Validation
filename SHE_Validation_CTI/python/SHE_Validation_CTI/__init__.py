"""
:file: python/SHE_Validation_CTI/__init__.py

:date: 24 April 2020
:author: Bryan Gillis

SHE_Validation_CTI package, for validation tests and documentation related to CTI
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

from SHE_Validation.__init__ import (__authors__, __copyright__, __credits__, __email__, __license__,  # noqa F401
                                     __maintainer__, __status__, __url__, __version__, )  # noqa F401

if '__path__' in locals():
    # noinspection PyUnboundLocalVariable
    __path__ = extend_path(__path__, __name__)

__description__ = 'Python package for unit tests relating to CTI.'

del extend_path
