""" @file test_info.py

    Created 27 July 2021

    Default values for information about tests and test cases, generic across multiple tests.
"""

__updated__ = "2021-08-26"

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

from typing import Dict, List, Optional, Union

from SHE_PPT.constants.classes import AllowedEnum
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.pipeline_utility import ConfigKeys, ValidationConfigKeys

# Bin units and definitions
BACKGROUND_LEVEL_UNITS: str = "ADU/pixel"
COLOUR_DEFINITION: str = "2.5*log10(FLUX_VIS_APER/FLUX_NIR_STACK_APER)"
SIZE_UNITS: str = "pixels"
SIZE_DEFINITION: str = "area of segmentation map"

# Tags for replacement in test case ID strings
ID_NUMBER_REPLACE_TAG = "$ID_NUMBER"
NAME_REPLACE_TAG = "$NAME"


class BinParameters(AllowedEnum):
    """ Enum of possible binning parameters for test cases.
    """
    GLOBAL = "global"
    SNR = "snr"
    BG = "bg"
    COLOUR = "colour"
    SIZE = "size"
    EPOCH = "epoch"


NUM_BIN_PARAMETERS: int = len(BinParameters)
NON_GLOBAL_BIN_PARAMETERS: List[BinParameters] = [bin_parameter for bin_parameter in BinParameters
                                                  if bin_parameter != BinParameters.GLOBAL]

# Define dicts listing how ID numbers and names work within test cases with various bin parameters

# ID number offset is how much the test case ID differs from the lowest value for each test case
D_ID_NUMBER_OFFSETS: Dict[Union[BinParameters, None], int] = {None                : 0,
                                                              BinParameters.GLOBAL: -1,
                                                              BinParameters.SNR   : 0,
                                                              BinParameters.BG    : 1,
                                                              BinParameters.COLOUR: 3,
                                                              BinParameters.SIZE  : 2,
                                                              BinParameters.EPOCH : 4, }


class BinParameterMeta:
    """ Data class to store metadata about a bin parameter.
    """

    # Values set directly from init
    _enum: BinParameters = BinParameters.GLOBAL
    _long_name: Optional[str] = None
    _id_tail: Optional[str] = None
    _units: Optional[str] = None
    _definition: Optional[str] = None
    _extra_help_text: Optional[str] = None
    _config_key: Optional[ConfigKeys] = None

    # Values derived from init
    _name: str
    _value: str
    _cline_arg: str

    # Values determined on-demand
    _help_text: Optional[str] = None
    _comment: Optional[str] = None

    def __init__(self,
                 bin_parameter_enum: BinParameters,
                 long_name: str = None,
                 id_tail: str = None,
                 units: str = None,
                 definition: str = None,
                 extra_help_text: str = None,
                 config_key: ConfigKeys = None, ):

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
            self._id_tail = self.value

    # Accessors for attributes
    @property
    def enum(self) -> BinParameters:
        return self._enum

    @property
    def long_name(self) -> Optional[str]:
        return self._long_name

    @property
    def id_tail(self) -> Optional[str]:
        return self._id_tail

    @property
    def units(self) -> Optional[str]:
        return self._units

    @property
    def definition(self) -> Optional[str]:
        return self._definition

    @property
    def extra_help_text(self) -> Optional[str]:
        return self._extra_help_text

    @property
    def config_key(self) -> Optional[ConfigKeys]:
        return self._config_key

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value

    @property
    def cline_arg(self) -> str:
        return self._cline_arg

    @property
    def comment(self) -> str:
        # Generate comment on demand if not already generated
        if self._comment is None:
            self._determine_comment()
        return self._comment

    @property
    def help_text(self) -> str:
        # Generate help_text on demand if not already generated
        if self._help_text is None:
            self._determine_help_text()
        return self._help_text

    # Private and protected methods
    def _determine_comment(self) -> None:
        """Construct self._comment in pieces depending on what information is available.
        """

        comment: str = ""

        if self.definition is not None:
            comment += f"{self.definition}. "

        if self.units is not None:
            comment += f"Units: {self.units}. "

        self._comment = comment

    def _determine_help_text(self) -> None:
        """Construct self._help_text in pieces depending on what information is available.
        """

        help_text: str = (f"The bin limits for the {self.long_name} test case, expressed as a string of "
                          f"space-separated float values")

        if self.units is not None:
            help_text += f", in units of {self.units}"

        if self.definition is not None:
            help_text += f", expressing {self.long_name} as {self.definition}"

        help_text += ". If used, overrides values in the pipeline_config file."

        if self.extra_help_text is not None:
            help_text += self.extra_help_text

        self._help_text = help_text


# Set up BinParameterMeta for each binning parameter
D_BIN_PARAMETER_META: Dict[BinParameters, BinParameterMeta] = {}

D_BIN_PARAMETER_META[BinParameters.GLOBAL] = BinParameterMeta(bin_parameter_enum = BinParameters.GLOBAL, )

D_BIN_PARAMETER_META[BinParameters.SNR] = BinParameterMeta(bin_parameter_enum = BinParameters.SNR,
                                                           long_name = "SNR",
                                                           config_key = ValidationConfigKeys.VAL_SNR_BIN_LIMITS,
                                                           id_tail = "SNR")

D_BIN_PARAMETER_META[BinParameters.BG] = BinParameterMeta(bin_parameter_enum = BinParameters.BG,
                                                          long_name = "background level",
                                                          units = BACKGROUND_LEVEL_UNITS,
                                                          config_key = ValidationConfigKeys.VAL_BG_BIN_LIMITS)

D_BIN_PARAMETER_META[BinParameters.COLOUR] = BinParameterMeta(bin_parameter_enum = BinParameters.COLOUR,
                                                              definition = COLOUR_DEFINITION,
                                                              config_key = ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS, )

D_BIN_PARAMETER_META[BinParameters.SIZE] = BinParameterMeta(bin_parameter_enum = BinParameters.SIZE,
                                                            units = SIZE_UNITS,
                                                            definition = SIZE_DEFINITION,
                                                            config_key = ValidationConfigKeys.VAL_SIZE_BIN_LIMITS, )

D_BIN_PARAMETER_META[BinParameters.EPOCH] = BinParameterMeta(bin_parameter_enum = BinParameters.EPOCH)

# Set up the dict relating cline-args to config keys
D_BIN_LIMITS_CLINE_ARGS: Dict[ConfigKeys, str] = {}

for bin_parameter in BinParameters:
    bin_parameter_meta = D_BIN_PARAMETER_META[bin_parameter]
    D_BIN_LIMITS_CLINE_ARGS[bin_parameter_meta.config_key] = bin_parameter_meta.cline_arg


class RequirementInfo:
    """ Common class for info about a requirement.
    """

    _requirement_id: Optional[str] = None
    _description: Optional[str] = None
    _parameter: Optional[str] = None

    def __init__(self,
                 requirement_id: Optional[str] = None,
                 description: Optional[str] = None,
                 parameter: Optional[str] = None):
        self._requirement_id = requirement_id
        self._description = description
        self._parameter = parameter

    @property
    def requirement_id(self) -> Optional[str]:
        return self._requirement_id

    @property
    def id(self) -> Optional[str]:
        # Alias to requirement_id
        return self._requirement_id

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def parameter(self) -> Optional[str]:
        return self._parameter


class TestInfo:
    """ Common class for info about a test.
    """

    _test_id: Optional[str] = None
    _description: Optional[str] = None

    def __init__(self,
                 test_id: Optional[str] = None,
                 description: Optional[str] = None, ):
        self._test_id = test_id
        self._description = description

    @property
    def test_id(self) -> Optional[str]:
        return self._test_id

    @property
    def id(self) -> Optional[str]:
        # Alias to test_id
        return self._test_id

    @property
    def description(self) -> Optional[str]:
        return self._description


class TestCaseInfo:
    """ Common class for info about a test case.
    """

    # Attributes set at init
    _test_info: Optional[TestInfo] = None
    _base_test_case_id: Optional[str] = None
    _base_description: Optional[str] = None
    _base_name: str = ""
    base_id_number: Optional[int] = None
    _bins: Optional[BinParameters] = None
    _method: Optional[ShearEstimationMethods] = None

    # Attributes generated on-demand
    _test_case_id: Optional[str] = None
    _description: Optional[str] = None
    _bins_cline_arg: Optional[str] = None
    _bins_config_key: Optional[str] = None
    _name: Optional[str] = None
    _id_number_offset: Optional[int] = None
    _id_number: Optional[int] = None

    def __init__(self,
                 test_info: Optional[TestInfo] = None,
                 base_test_case_id: Optional[str] = None,
                 base_description: Optional[str] = None,
                 base_name: Optional[str] = None,
                 base_id_number: Optional[int] = None,
                 bins: Optional[BinParameters] = None,
                 method: Optional[ShearEstimationMethods] = None):

        self._test_info = test_info
        self._base_test_case_id = base_test_case_id
        self._base_description = base_description
        self.base_name = base_name
        self.base_id_number = base_id_number
        self._bins = bins
        self._method = method

    @property
    def test_info(self) -> Optional[TestInfo]:
        return self._test_info

    @property
    def base_test_case_id(self) -> Optional[str]:
        return self._base_test_case_id

    @property
    def test_case_id(self) -> Optional[str]:
        # Construct the full test_case_id if needed
        if self._test_case_id is None:
            self._test_case_id = self._base_test_case_id
            if self.bins is not None:
                self._test_case_id = self._test_case_id.replace(NAME_REPLACE_TAG,
                                                                D_BIN_PARAMETER_META[self.bins].id_tail)
            if self.id_number is not None:
                self._test_case_id = self._test_case_id.replace(ID_NUMBER_REPLACE_TAG,
                                                                str(self.id_number))
            if self.method is not None:
                self._test_case_id += f"-{self.method.value}"
        return self._test_case_id

    @property
    def id(self) -> Optional[str]:
        # Alias to test_case_id
        return self.test_case_id

    @property
    def base_description(self) -> Optional[str]:
        return self._base_description

    @property
    def description(self) -> Optional[str]:
        # Construct the full description if needed and possible
        if self._description is None:
            if not self._base_description:
                return None
            self._description = self._base_description
            if self.bins is not None:
                self._description += f" Binned by {D_BIN_PARAMETER_META[self.bins].long_name}."
            if self.method is not None:
                self._description += f" Shear estimation method: {self.method}."
        return self._description

    @property
    def bins(self) -> Optional[BinParameters]:
        return self._bins

    @bins.setter
    def bins(self, bins: BinParameters) -> None:

        self._bins = bins

        # Unset cached values which depend on self.bins
        self._bins_cline_arg = None
        self._bins_config_key = None
        self._name = None
        self._description = None

    @property
    def bin_parameter(self) -> Optional[BinParameters]:
        return self._bins

    @property
    def method(self) -> Optional[ShearEstimationMethods]:
        return self._method

    @method.setter
    def method(self, method: ShearEstimationMethods) -> None:

        self._method = method

        # Unset cached values which depend on self.methods
        self._name = None
        self._description = None

    @property
    def bins_cline_arg(self) -> Optional[str]:
        if self._bins_cline_arg is None and self.bins is not None:
            self._bins_cline_arg = D_BIN_PARAMETER_META[self.bins].cline_arg
        return self._bins_cline_arg

    @property
    def bins_config_key(self) -> Optional[str]:
        if self._bins_config_key is None and self.bins is not None:
            self._bins_config_key = D_BIN_PARAMETER_META[self.bins].config_key
        return self._bins_config_key

    @property
    def base_name(self) -> str:
        return self._base_name

    @base_name.setter
    def base_name(self, base_name: Optional[str]):
        if base_name:
            self._base_name = base_name
        else:
            self._base_name = self.base_test_case_id

    @property
    def name(self) -> Optional[str]:
        if self._name is None:
            self._name = f"{self.base_name}"
            if self.method is not None:
                self._name += f"-{self.method.value}"
            if self.bins is not None:
                self._name += f"-{self.bins.value}"
        return self._name

    @property
    def id_number_offset(self) -> int:
        if self._id_number_offset is None:
            self._id_number_offset = D_ID_NUMBER_OFFSETS[self.bins]
        return self._id_number_offset

    @property
    def id_number(self) -> Optional[int]:
        if self._id_number is None and self.base_id_number is not None and self.id_number_offset is not None:
            if self.id_number_offset == -1:
                # Value of -1 indicates no number is assigned for this test
                self._id_number = -1
            else:
                self._id_number = self.base_id_number + self.id_number_offset
        return self._id_number
