""" @file test_info.py

    Created 24 Mar 2021

    Common (base) classes for information about tests, test cases, and requirements
"""

__updated__ = "2021-03-24"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA


class RequirementInfo():
    """ Common class for info about a requirement.
    """

    def __init__(self,
                 requirement_id=None,
                 description=None,
                 parameter=None,):

        self._requirement_id = requirement_id
        self._description = description
        self._parameter = parameter

    @property
    def requirement_id(self):
        return self._requirement_id

    @property
    def id(self):
        # Alias to requirement_id
        return self._requirement_id

    @property
    def description(self):
        return self._description

    @property
    def parameter(self):
        return self._parameter


class TestInfo():
    """ Common class for info about a test.
    """

    def __init__(self,
                 test_id=None,
                 description=None,):

        self._test_id = test_id
        self._description = description

    @property
    def test_id(self):
        return self._test_id

    @property
    def id(self):
        # Alias to test_id
        return self._test_id

    @property
    def description(self):
        return self._description


class TestCaseInfo():
    """ Common class for info about a test case.
    """

    def __init__(self,
                 test_case_id=None,
                 description=None,
                 bins_cline_arg=None,
                 bins_config_key=None,
                 name=None,
                 comment=None):

        self._test_case_id = test_case_id
        self._description = description
        self._bins_cline_arg = bins_cline_arg
        self._bins_config_key = bins_config_key
        self._name = name
        self._comment = comment

    @property
    def test_case_id(self):
        return self._test_case_id

    @property
    def id(self):
        # Alias to test_case_id
        return self._test_case_id

    @property
    def description(self):
        return self._description

    @property
    def bins_cline_arg(self):
        return self._bins_cline_arg

    @property
    def bins_config_key(self):
        return self._bins_config_key

    @property
    def name(self):
        return self._name

    @property
    def comment(self):
        return self._comment
