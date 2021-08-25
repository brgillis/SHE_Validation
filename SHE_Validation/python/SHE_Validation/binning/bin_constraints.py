""" @file binning.py

    Created 9 July 2021

    Common functions and classes to aid with binning data.
"""

__updated__ = "2021-08-25"

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

import abc
from typing import Optional,  Sequence, Union, Any, List

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods, D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.flags import failure_flags
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_utility import SheTableFormat
from astropy.table import Table, Row, Column

import numpy as np

from ..constants.default_config import DEFAULT_BIN_LIMITS
from ..constants.test_info import BinParameters, TestCaseInfo, D_BIN_PARAMETER_META
from .bin_data import TF as BIN_TF, D_COLUMN_ADDING_METHODS


class BinConstraint(abc.ABC):
    """ Abstract base class describing a single requirement for an object (row) to fall within a bin.

        Parameters
        ----------
        bin_parameter : Optional[BinParameters]
            Which bin parameter from the BinParameters enum (if any) this constraint applies to.
    """

    bin_parameter: Optional[BinParameters] = None

    def __init__(self, bin_parameter: Optional[BinParameters] = None):
        """ Inits values only if not None, to allow simple overriding in inherited classes.
        """
        if bin_parameter:
            self.bin_parameter = bin_parameter

    # Protected methods

    @abc.abstractmethod
    def _is_in_bin(self, data: Union[Row, Table],
                   *_args, **_kwargs) -> Union[bool, Sequence[bool]]:
        """ Method to return whether or not a row is in a bin. Should ideally be able to take either a row or table
            as input, but must at least be able to take a row as input.

            Parameters
            ----------
            data : astropy.table.Row or astropy.table.Table
                The table or row to assess the data of

            Return
            ------
            is_in_bin : Union[bool,Sequence[bool]]
                Whether or not the row is in the bin, or whether each row is in the bin.
        """
        pass

    # Public methods

    def get_l_is_row_in_bin(self, table: Table) -> Sequence[bool]:
        """ Method to return a sequence of bools for whether or not a row satisfies a bin constraint.

            Parameters
            ----------
            table : astropy.table.Table
                The table to assess the data of

            Return
            ------
            l_is_row_in_bin : Sequence[bool]
                Sequence of bools for whether or not a row is in the bin or not.
        """

        # Try to apply self._is_in_bin directly to the table. If that fails, vectorize and apply it
        try:
            l_is_row_in_bin: Sequence[bool] = self._is_in_bin(table)
        except TypeError:
            l_is_row_in_bin: Sequence[bool] = np.vectorize(self._is_in_bin)(table)

        return l_is_row_in_bin

    def get_rows_in_bin(self, table: Table) -> Table:
        """ Method to return a table with only rows satisfying a bin constraint.

            Parameters
            ----------
            table : astropy.table.Table
                The table to assess the data of

            Return
            ------
            binned_table : astropy.table.Table
                Table of only the rows in the bin.
        """

        l_is_row_in_bin: Sequence[bool] = self.get_l_is_row_in_bin(table)
        binned_table: Table = table[l_is_row_in_bin]

        return binned_table

    def get_ids_in_bin(self, table: Table) -> Column:
        """ Method to return a table with only rows satisfying a bin constraint.

            Parameters
            ----------
            table : astropy.table.Table
                The table to assess the data of

            Return
            ------
            binned_ids : astropy.table.Column
                Column of the object IDs which are in this bin
        """

        binned_table: Table = self.get_rows_in_bin(table)
        binned_ids: Column = binned_table[MFC_TF.ID]

        return binned_ids

# General types of bin constraints


class RangeBinConstraint(BinConstraint):
    """ Type of bin constraint which checks if the value in a column is within a range.

        Parameters (in addition to those inherited from BinConstraint)
        ----------
        bin_colname: str
            Name of the column that's being used for binning
        bin_limits: Sequence[float]
            Sequence of min and max of bin limits. Will check min <= val < max
    """

    bin_colname: str
    bin_limits: Sequence[float]

    def __init__(self,
                 bin_colname: Optional[str] = None,
                 bin_limits: Sequence[float] = None,
                 *args, **kwargs):
        """ Inits values only if not None, to allow simple overriding in inherited classes.
        """

        super().__init__(*args, **kwargs)

        if bin_colname:
            self.bin_colname = bin_colname
        if bin_limits:
            if not len(bin_limits) == 2:
                raise ValueError(
                    f"bin_limits must be a length-2 sequence. Got: {bin_limits}, of length {len(bin_limits)}.")
            self.bin_limits = bin_limits

    # Protected methods

    def _is_in_bin(self, data: Union[Row, Table],
                   *_args, **_kwargs) -> Union[bool, Sequence[bool]]:
        """ Checks if the data is within the bin limits.
        """
        return np.logical_and(self.bin_limits[0] <= data[self.colname],
                              data[self.colname] < self.bin_limits[1])


class ValueBinConstraint(BinConstraint):
    """ Type of bin constraint which checks if the value in a row exactly matches (or doesn't) a value.

        Parameters (in addition to those inherited from BinConstraint)
        ----------
        bin_colname: str
            Name of the column that's being used for binning
        value: Any
            The value that must (not) be matched to be in a bin
        invert: bool
            If False (default), will return True if the value is matched. If True, will return True if the
            value is not matched
    """

    bin_colname: str
    value: Any
    invert: bool = False

    def __init__(self,
                 bin_colname: Optional[str] = None,
                 value: Optional[Any] = None,
                 invert: Optional[bool] = None,
                 *args, **kwargs):
        """ Inits values only if not None, to allow simple overriding in inherited classes.
        """

        super().__init__(*args, **kwargs)

        if bin_colname:
            self.bin_colname = bin_colname
        if value:
            self.value = value
        if invert:
            self.invert = invert

    # Protected methods

    def _is_in_bin(self, data: Union[Row, Table],
                   *_args, **_kwargs) -> Union[bool, Sequence[bool]]:
        """ Checks if the data (does not) matches the desired value.
        """
        matches_value: bool = data[self.colname] == self.value

        if not self.invert:
            return matches_value
        else:
            return np.logical_not(matches_value)


class BitFlagsBinConstraint(BinConstraint):
    """ Type of bin constraint which checks if the value in a row matches (or doesn't) a set of bit flags.

        Parameters (in addition to those inherited from BinConstraint)
        ----------
        bin_colname: str
            Name of the column that's being used for binning
        bit_flags: int
            The bit flags that must (not) be matched to be in a bin
        invert: bool
            If False (default), will return True if the bit flags are matched. If True, will return True if the
            bit flags are not matched
    """

    bin_colname: str
    bit_flags: int
    invert: bool = False

    def __init__(self,
                 bin_colname: Optional[str] = None,
                 bit_flags: Optional[int] = None,
                 invert: Optional[bool] = None,
                 *args, **kwargs):
        """ Inits values only if not None, to allow simple overriding in inherited classes.
        """

        super().__init__(*args, **kwargs)

        if bin_colname:
            self.bin_colname = bin_colname
        if bit_flags:
            self.bit_flags = bit_flags
        if invert:
            self.invert = invert

    # Protected methods

    def _is_in_bin(self, data: Union[Row, Table],
                   *_args, **_kwargs) -> Union[bool, Sequence[bool]]:
        """ Checks if the data (does not) match the flags.
        """
        # Perform a bitwise and to check against the flags
        flag_match: int = np.bitwise_and(data[self.colname], self.bit_flags)

        # Convert to bool or array of bools
        if isinstance(flag_match, np.ndarray):
            bool_flag_match = flag_match.astype(bool)
        else:
            bool_flag_match = bool(flag_match)

        # Invert if desired and return
        if not self.invert:
            return bool_flag_match
        else:
            return np.logical_not(bool_flag_match)


class MultiBinConstraint(BinConstraint):
    """ Class for constraining on the intersection of multiple bins.
    """

    l_bin_constraints: Sequence[BinConstraint]

    def __init__(self, l_bin_constraints: Sequence[BinConstraint]) -> None:
        super().__init__()

        if l_bin_constraints:
            self.l_bin_constraints = l_bin_constraints
        else:
            self.l_bin_constraints = []

    # Protected methods

    def _is_in_bin(self, data: Union[Row, Table],
                   *args, **kwargs) -> Union[bool, Sequence[bool]]:
        """ Checks if the data is in all bin constraints.
        """

        l_is_in_bin: List[bool] = [bin_constraint._is_in_bin(data, *args, **kwargs)
                                   for bin_constraint in self.l_bin_constraints]
        return np.all(l_is_in_bin)

# Bin constraints for specific use cases


class GlobalBinConstraint(RangeBinConstraint):
    """ Global binning - everything is in the bin. Inherits from RangeBinConstraint for a consistent interface.
    """

    bin_parameter: BinParameters = BinParameters.GLOBAL
    bin_colname: Optional[str] = None
    bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS


class BinParameterBinConstraint(RangeBinConstraint):
    """ Range bin constraint generated based on a TestCaseInfo.
    """

    test_case_info: Optional[TestCaseInfo] = None
    method: Optional[ShearEstimationMethods] = None
    tf: SheTableFormat

    def __init__(self,
                 test_case_info: Optional[TestCaseInfo] = None,
                 method: Optional[ShearEstimationMethods] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS):

        super().__init__(bin_limits=bin_limits)

        # Set parameters from the test_case_info object
        if test_case_info:
            self.test_case_info = test_case_info
            self.method = test_case_info.method
            self.bin_parameter = test_case_info.bins
        else:
            self.method = method
            self.bin_parameter = bin_parameter

        # Check that the bin_parameter was somehow specified
        if not self.bin_parameter:
            raise ValueError("bin_parameter must be specified in init for BinParameterBinConstraint, either via "
                             "test_case_info or bin_parameter input. Supplied was: "
                             f"test_case_info = {test_case_info}, "
                             f"bin_parameter = {bin_parameter}.")

        # Get the table format that will be used based on the bin parameter and method
        if self.bin_parameter == BinParameters.SNR:
            self.tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[self.method]
        else:
            self.tf = MFC_TF

        # Set column name for this bin parameter if applicable
        bin_column = D_BIN_PARAMETER_META[self.bin_parameter].column
        if bin_column:
            self.bin_colname = getattr(self.tf, bin_column)

    # Protected methods

    def _is_in_bin(self,
                   data: Union[Row, Table],
                   data_stack: Optional[SHEFrameStack] = None,
                   *_args, **_kwargs) -> Union[bool, Sequence[bool]]:
        """ Need to check what implementation we need based on the bin parameter.
        """

        column_adding_method = D_COLUMN_ADDING_METHODS[self.bin_parameter]

        # Add a column to the table if necessary
        new_bin_column = D_BIN_PARAMETER_META[self.bin_parameter].value
        new_bin_colname = getattr(BIN_TF, new_bin_column)
        if not new_bin_colname in data.colnames:
            column_adding_method(data, data_stack)

        self.bin_colname = new_bin_colname

        return super()._is_in_bin(data)


class FitclassZeroBinConstraint(ValueBinConstraint):
    """ Bin constraints to make sure the fit class is 0 (galaxy).
    """

    bin_colname: str
    value: Any = 0
    invert: bool = False

    def __init__(self, method: ShearEstimationMethods):
        """ Get the bin colname from the shear estimation method.
        """
        tf: SheTableFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        self.bin_colname = tf.fit_class


class FitflagsBinConstraint(BitFlagsBinConstraint):
    """ Bin constraints to make sure the fit didn't fail.
    """

    bin_colname: str
    bit_flags: Any = failure_flags
    invert: bool = True

    def __init__(self, method: ShearEstimationMethods):
        """ Get the bin colname from the shear estimation method.
        """
        tf: SheTableFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        self.bin_colname = tf.fit_flags


class GoodBinParameterBinConstraint(MultiBinConstraint):
    """ Bin constraint that combines FitflagsBinConstraint and BinParameterBinConstraint.
    """

    def __init__(self,
                 test_case_info: TestCaseInfo,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS):

        fit_flags_bin_constraint = FitflagsBinConstraint(method=test_case_info.method)
        bin_parameter_bin_constraint = BinParameterBinConstraint(test_case_info=test_case_info,
                                                                 bin_limits=bin_limits)

        self.l_bin_constraints = [fit_flags_bin_constraint,
                                  bin_parameter_bin_constraint]


class GoodGalaxyBinParameterBinConstraint(MultiBinConstraint):
    """ Bin constraint that combines FitflagsBinConstraint, FitclassZeroBinConstraint and BinParameterBinConstraint.
    """

    def __init__(self,
                 test_case_info: TestCaseInfo,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS):

        fit_flags_bin_constraint = FitflagsBinConstraint(method=test_case_info.method)
        fitclass_zero_bin_constraint = FitclassZeroBinConstraint(method=test_case_info.method)
        bin_parameter_bin_constraint = BinParameterBinConstraint(test_case_info=test_case_info,
                                                                 bin_limits=bin_limits)

        self.l_bin_constraints = [fit_flags_bin_constraint,
                                  fitclass_zero_bin_constraint,
                                  bin_parameter_bin_constraint]
