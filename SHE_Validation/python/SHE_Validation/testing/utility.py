"""
:file: python/SHE_Validation/testing/utility.py

:date: 12 April 2022
:author: Bryan Gillis

Utility functions and classes for testing of SHE_Validation code
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

import re

from SHE_PPT.testing.utility import SheTestCase

ESCAPE_CHARS = r"\[](){}*+?|^$."


def compile_regex(s: str):
    """Takes an input string which was intended to be human-readable, optionally with replacement keys %s, %i, %f,
    and convert it into a regex pattern, properly escaping characters and replacing any replacement strings with
    capturing groups.
    """

    # Escape all characters in the string which must be escaped
    s_escaped = s
    for c in ESCAPE_CHARS:
        s_escaped = s_escaped.replace(c, f"\\{c}")

    # Replace replacement keys with capturing groups
    s_capturing = s_escaped.replace(r"%s", r"(.+)")
    s_capturing = s_capturing.replace(r"%i", r"(\d+)")
    s_capturing = s_capturing.replace(r"%f", r"(\d+(?:\.\d+)?)")

    return re.compile(s_capturing)


class SheValTestCase(SheTestCase):
    """Test case base class which defines convenience methods to create test data.
    """
    pass
