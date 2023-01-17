""" @file __init__.py

    Created 26 March 2021

    SHE_Validation_ShearBias package, for validation tests and documentation related to shear bias
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

# noinspection PyUnresolvedReferences
from SHE_Validation.__init__ import (__authors__, __copyright__, __credits__, __email__, __license__, __maintainer__,
                                     __status__, __url__, __version__, )

__description__ = 'Python package for unit tests relating to Shear Bias.'

# noinspection PyUnboundLocalVariable
__path__ = extend_path(__path__, __name__)

del extend_path
