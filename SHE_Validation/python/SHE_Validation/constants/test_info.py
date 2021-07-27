""" @file test_info.py

    Created 27 July 2021

    Default values for information about tests and test cases, generic across multiple tests.
"""

__updated__ = "2021-07-27"

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

from copy import deepcopy
from enum import Enum
from typing import Iterable, Union, List

from SHE_PPT.constants.shear_estimation_methods import METHODS as SHEAR_ESTIMATION_METHODS
from SHE_PPT.pipeline_utility import ValidationConfigKeys


# Bin units and definitions
BACKGROUND_LEVEL_UNITS = "ADU/pixel"
COLOUR_DEFINITION = "2.5*log10(FLUX_VIS_APER/FLUX_NIR_STACK_APER)"
SIZE_UNITS = "pixels"
SIZE_DEFINITION = "area of segmentation map"


class BinParameters(Enum):
    """ Enum of possible binning parameters for test cases.
    """
    GLOBAL = "global"
    SNR = "snr"
    BG = "bg"
    COLOUR = "colour"
    SIZE = "size"
    EPOCH = "epoch"


NUM_BIN_PARAMETERS = len(BinParameters)


class BinParameterMeta():
    """ Data class to store metadata about a bin parameter.
    """

    # Values set directly from init
    _enum = None
    _long_name = None
    _id_tail = None
    _units = None
    _definition = None
    _extra_help_text = None
    _config_key = None

    # Values derived from init
    _name = None
    _value = None
    _cline_arg = None

    # Values determined on-demand
    _help_text = None

    def __init__(self,
                 bin_parameter_enum: BinParameters,
                 long_name: str = None,
                 id_tail: str = None,
                 units: str = None,
                 definition: str = None,
                 extra_help_text: str = None,
                 config_key: str = None):

        # Set values directly from init
        self._enum = bin_parameter_enum
        self._units = units
        self._definition = definition
        self._extra_help_text = extra_help_text
        self._config_key = config_key

        # Set values derived from init
        self._name = bin_parameter_enum.name
        self._value = bin_parameter_enum.value
        self._cline_arg = f"{self.value}_bin_limits"
        if long_name is not None:
            self._long_name = long_name
        else:
            self._long_name = self.name
        if id_tail is not None:
            self._id_tail = id_tail
        else:
            self._long_name = self.name

    # Accessors for attributes
    @property
    def enum(self):
        return self._enum

    @property
    def units(self):
        return self._units

    @property
    def definition(self):
        return self._definition

    @property
    def extra_help_text(self):
        return self._extra_help_text

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def cline_arg(self):
        return self._cline_arg

    @property
    def help_text(self):
        # Generate help_text on demand if not already generated
        if self._help_text is None:
            self._determine_help_text()
        return self._help_text

    # Private and protected methods
    def _determine_help_text(self):
        """Construct self._help_text in pieces depending on what information is available.
        """

        help_text = (f"The bin limits for the {self.long_name} test case, expressed as a string of space-separated "
                     f"float values")

        if self.units is not None:
            help_text += f", in units of {self.units}"

        if self.definition is not None:
            help_text += f", expressing {self.long_name} as {self.definition}"

        help_text += ". If used, overrides values in the pipeline_config file."

        if self.extra_help_text is not None:
            help_text += self.extra_help_text

        self._help_text = help_text


# Set up BinParameterMeta for each binning parameter
D_BIN_PARAMETER_META = {}

D_BIN_PARAMETER_META[BinParameters.GLOBAL] = BinParameterMeta(bin_parameter_enum=BinParameters.GLOBAL)

D_BIN_PARAMETER_META[BinParameters.SNR] = BinParameterMeta(bin_parameter_enum=BinParameters.SNR,
                                                           long_name="SNR",
                                                           id_tail="SNR",
                                                           config_key=ValidationConfigKeys.VAL_SNR_BIN_LIMITS)

D_BIN_PARAMETER_META[BinParameters.BG] = BinParameterMeta(bin_parameter_enum=BinParameters.BG,
                                                          long_name="background level",
                                                          units=BACKGROUND_LEVEL_UNITS,
                                                          config_key=ValidationConfigKeys.VAL_BG_BIN_LIMITS)

D_BIN_PARAMETER_META[BinParameters.COLOUR] = BinParameterMeta(bin_parameter_enum=BinParameters.COLOUR,
                                                              definition=COLOUR_DEFINITION,
                                                              config_key=ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS)

D_BIN_PARAMETER_META[BinParameters.SIZE] = BinParameterMeta(bin_parameter_enum=BinParameters.SIZE,
                                                            units=SIZE_UNITS,
                                                            definition=SIZE_DEFINITION,
                                                            config_key=ValidationConfigKeys.VAL_SIZE_BIN_LIMITS)

D_BIN_PARAMETER_META[BinParameters.EPOCH] = BinParameterMeta(bin_parameter_enum=BinParameters.EPOCH)


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
                 test_info=None,
                 base_test_case_id=None,
                 base_description=None,
                 bins=None,
                 method=None):

        self._test_info = test_info
        self._base_test_case_id = base_test_case_id
        self._base_description = base_description
        self._bins = bins
        self._method = method

    @property
    def test_info(self):
        return self._test_info

    @property
    def base_test_case_id(self):
        return self._base_test_case_id

    @property
    def test_case_id(self):
        # Construct the full test_case_id if needed
        if self._test_case_id is None:
            self._test_case_id = self._base_test_case_id
            if self.bins is not None:
                self._test_case_id += f"-{D_BIN_PARAMETER_META[self.bins].id_tail}"
            if self.method is not None:
                self._test_case_id += f"-{self.method}"
        return self._test_case_id

    @property
    def id(self):
        # Alias to test_case_id
        return self.test_case_id

    @property
    def base_description(self):
        return self._base_description

    @property
    def description(self):
        # Construct the full description if needed
        if self._description is None:
            self._description = self._base_description
            if self.bins is not None:
                self._description += f" Binned by {D_BIN_PARAMETER_META[self.bins].long_name}."
            if self.method is not None:
                self._description += f" Shear estimation method: {self.method}."
        return self._description

    @property
    def bins(self):
        return self._bins

    @bins.setter()
    def bins(self, bins):

        self._bins = bins

        # Unset cached values which depend on self.bins
        self._bins_cline_arg = None
        self._bins_config_key = None
        self._name = None
        self._description = None

    @property
    def method(self):
        return self._method

    @method.setter()
    def method(self, method):

        self._method = method

        # Unset cached values which depend on self.methods
        self._name = None
        self._description = None

    @property
    def bins_cline_arg(self):
        if self._bins_cline_arg is None and self.bins is not None:
            self._bins_cline_arg = D_BIN_PARAMETER_META[self.bins].cline_arg
        return self._bins_cline_arg

    @property
    def bins_config_key(self):
        if self._bins_config_key is None and self.bins is not None:
            self._bins_config_key = D_BIN_PARAMETER_META[self.bins].config_key
        return self._bins_config_key

    @property
    def name(self):
        if self._name is None:
            if self.bins is not None:
                if self.method is not None:
                    self._name = f"{self.bins.value}-{self.method}"
                else:
                    self._name = self.bins.value
            else:
                # self.bins is not set in this branch
                if self.method is not None:
                    self._name = self.method
                else:
                    self._name = None
        return self._name

    @property
    def comment(self):
        return self._comment


def make_test_case_info_for_bins(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                 l_bin_parameters: Iterable[BinParameters] = BinParameters):
    """ Takes as input a test case or list of test cases, then creates versions of it for each bin parameter in the provided
        list.
    """

    # Silently coerce test_case_info into a list
    if isinstance(test_case_info, TestCaseInfo):
        l_test_case_info = [test_case_info]
    else:
        l_test_case_info = test_case_info

    l_bin_test_case_info = {}

    for test_case_info in l_test_case_info:
        for bin_parameter in l_bin_parameters:

            # Copy the test case info and modify the bins attribute of it
            bin_test_case_info = deepcopy(test_case_info)
            bin_test_case_info.bins = bin_parameter

            l_bin_test_case_info.append(bin_test_case_info)

    return l_bin_test_case_info


def make_test_case_info_for_methods(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                    l_methods: Iterable[str] = SHEAR_ESTIMATION_METHODS):
    """ Takes as input a test case or list of test cases, then creates versions of it for each shear estimation method
        in the provided list.
    """

    # Silently coerce test_case_info into a list
    if isinstance(test_case_info, TestCaseInfo):
        l_test_case_info = [test_case_info]
    else:
        l_test_case_info = test_case_info

    l_method_test_case_info = {}

    for test_case_info in l_test_case_info:
        for method in l_methods:

            # Copy the test case info and modify the bins attribute of it
            method_test_case_info = deepcopy(test_case_info)
            method_test_case_info.method = method

            l_method_test_case_info.append(method_test_case_info)

    return l_method_test_case_info


def make_test_case_info_for_bins_and_methods(test_case_info: Union[TestCaseInfo, List[TestCaseInfo]],
                                             l_bin_parameters: Iterable[BinParameters] = BinParameters,
                                             l_methods: Iterable[str] = SHEAR_ESTIMATION_METHODS):
    """ Takes as input a test case or list of test cases, then creates versions of it for each bin parameter in the
        provided list, for each shear estimation method in the provided list.
    """

    return make_test_case_info_for_methods(make_test_case_info_for_bins(test_case_info, l_bin_parameters), l_methods)
