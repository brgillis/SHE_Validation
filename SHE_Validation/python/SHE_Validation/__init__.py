""" @file __init__.py

    Created 24 April 2020

    SHE_Validation package, for general-purpose code within the SHE_Validation project
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

__all__ = ["__authors__", "__copyright__", "__credits__", "__license__", "__version__", "__maintainer__", "__email__",
           "__status__", "__url__"]

from pkgutil import extend_path

# Get the version from the compiled file created by Elements
from SHE_VALIDATION_VERSION import SHE_VALIDATION_VERSION_STRING

BG = "Bryan Gillis"
RB = "Rob Blake"

__authors__ = [BG, RB]
__copyright__ = 'Copyright (C) 2012-2023 Euclid Science Ground Segment'
__credits__ = [BG, RB]
__license__ = "GNU LGPL 3.0"
__version__ = SHE_VALIDATION_VERSION_STRING
__maintainer__ = BG
__email__ = "b.gillis@roe.ac.uk"
__status__ = 'Development'

__description__ = 'Elements project for validation tests within PF-SHE.'
__url__ = 'https://gitlab.euclid-sgs.uk/PF-SHE/SHE_Validation'

# noinspection PyUnboundLocalVariable
__path__ = extend_path(__path__, __name__)

del SHE_VALIDATION_VERSION_STRING, BG, RB, extend_path
