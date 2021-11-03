""" @file binning.py

    Created 9 July 2021

    Common functions and classes to aid with binning data.
"""

__updated__ = "2021-08-31"

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
from typing import Any, Dict, List, Optional, Sequence, Set, Type, Union

import numpy as np
from astropy.table import Column, Row, Table, vstack as table_vstack

from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS, ShearEstimationMethods
from SHE_PPT.file_io import MultiTableLoader, TableLoader
from SHE_PPT.flags import failure_flags
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.mer_final_catalog import tf as MFC_TF
from SHE_PPT.table_formats.she_measurements import SheMeasurementsFormat
from .bin_data import D_COLUMN_ADDING_METHODS, TF as BIN_TF
from ..constants.default_config import DEFAULT_BIN_LIMITS
from ..constants.test_info import BinParameters, TestCaseInfo


class BinConstraint(abc.ABC):
    """ Abstract base class describing a single requirement for an object (row) to fall within a bin.

        Parameters
        ----------
        bin_parameter : Optional[BinParameters]
            Which bin parameter from the BinParameters enum (if any) this constraint applies to.
    """

    bin_parameter: Optional[BinParameters] = None

    def __init__(self, bin_parameter: Optional[BinParameters] = None):
        """ Initializes values only if not None, to allow simple overriding in inherited classes.
        """
        if bin_parameter:
            self.bin_parameter = bin_parameter

    # Protected methods

    @abc.abstractmethod
    def is_in_bin(self, data: Union[Row, Table],
                  *_args, **_kwargs) -> Union[bool, np.ndarray]:
        """ Method to return whether or not a row is in a bin. Should ideally be able to take either a row or table
            as input, but must at least be able to take a row as input.

            Parameters
            ----------
            data : astropy.table.Row or astropy.table.Table
                The table or row to assess the data of

            Return
            ------
            is_in_bin : Union[bool,np.ndarray]
                Whether or not the row is in the bin, or whether each row is in the bin.
        """
        pass

    # Public methods

    def get_l_is_row_in_bin(self, t: Table,
                            *args, **kwargs) -> np.ndarray:
        """ Method to return a sequence of bools for whether or not a row satisfies a bin constraint.

            Parameters
            ----------
            t : astropy.table.Table
                The table to assess the data of

            Return
            ------
            l_is_row_in_bin : np.ndarray
                Sequence of bools for whether or not a row is in the bin or not.
        """

        l_is_row_in_bin: np.ndarray = self.is_in_bin(t, *args, **kwargs)

        return l_is_row_in_bin

    def get_rows_in_bin(self,
                        t: Table,
                        l_full_ids: Optional[Sequence[int]] = None,
                        *args, **kwargs) -> Table:
        """ Method to return a table with only rows satisfying a bin constraint.

            Parameters
            ----------
            t : astropy.table.Table
                The table to assess the data of
            l_full_ids : Optional[Sequence[int]]
                (Optional) A list of IDs to check. If not provided, will take IDs from the table.

            Return
            ------
            binned_table : astropy.table.Table
                Table of only the rows in the bin.
        """

        l_is_row_in_bin: np.ndarray = self.get_l_is_row_in_bin(t, *args, **kwargs)

        binned_table: Table
        if l_full_ids is None:
            binned_table = t[l_is_row_in_bin]
        else:
            l_is_id_in_full_ids: np.ndarray = np.isin(t[MFC_TF.ID], l_full_ids)
            l_use_row: np.ndarray = np.logical_and(l_is_row_in_bin, l_is_id_in_full_ids)
            binned_table = t[l_use_row]

        return binned_table

    def get_ids_in_bin(self,
                       t: Table,
                       l_full_ids: Optional[Sequence[int]] = None,
                       *args, **kwargs) -> Column:
        """ Method to return a table with only rows satisfying a bin constraint.

            Parameters
            ----------
            t : astropy.table.Table
                The table to assess the data of
            l_full_ids : Optional[Sequence[int]]
                (Optional) A list of IDs to check. If not provided, will take IDs from the table.

            Return
            ------
            binned_ids : astropy.table.Column
                Column of the object IDs which are in this bin
        """

        binned_table: Table = self.get_rows_in_bin(t, l_full_ids, *args, **kwargs)
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
            Sequence of min and max of bin limits. Will check min <(=) val <(=) max
        include_min: Sequence[float]
            If True (default), will check min <= val, otherwise will check min < val
        include_max: Sequence[float]
            If True, will check val <= max, otherwise (default) will check val < max
    """

    bin_colname: str
    bin_limits: Sequence[float]
    include_min: bool = True
    include_max: bool = False

    def __init__(self,
                 bin_colname: Optional[str] = None,
                 bin_limits: Sequence[float] = None,
                 *args, **kwargs):
        """ Initializes values only if not None, to allow simple overriding in inherited classes.
        """

        super().__init__(*args, **kwargs)

        if bin_colname:
            self.bin_colname = bin_colname
        if bin_limits is not None:
            if not len(bin_limits) == 2:
                raise ValueError(
                    f"bin_limits must be a length-2 sequence. Got: {bin_limits}, of length {len(bin_limits)}.")
            self.bin_limits = bin_limits

    # Protected methods

    def is_in_bin(self, data: Union[Row, Table],
                  *_args, **_kwargs) -> Union[bool, np.ndarray]:
        """ Checks if the data is within the bin limits.
        """
        # If the column is None, everything passes as no constraint is applied
        if self.bin_colname is None:
            if isinstance(data, Row):
                return True
            return True * np.ones(len(data), dtype = bool)

        # Check against min and max, based on whether they're included in the bin or not
        if self.include_min:
            min_check = self.bin_limits[0] <= data[self.bin_colname]
        else:
            min_check = self.bin_limits[0] < data[self.bin_colname]
        if self.include_max:
            max_check = self.bin_limits[1] >= data[self.bin_colname]
        else:
            max_check = self.bin_limits[1] > data[self.bin_colname]

        return np.logical_and(min_check, max_check)


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
        """ Initializes values only if not None, to allow simple overriding in inherited classes.
        """

        super().__init__(*args, **kwargs)

        if bin_colname:
            self.bin_colname = bin_colname
        if value:
            self.value = value
        if invert:
            self.invert = invert

    # Protected methods

    def is_in_bin(self, data: Union[Row, Table],
                  *_args, **_kwargs) -> Union[bool, np.ndarray]:
        """ Checks if the data (does not) matches the desired value.
        """
        matches_value: bool = data[self.bin_colname] == self.value

        if not self.invert:
            return matches_value
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
        """ Initializes values only if not None, to allow simple overriding in inherited classes.
        """

        super().__init__(*args, **kwargs)

        if bin_colname:
            self.bin_colname = bin_colname
        if bit_flags:
            self.bit_flags = bit_flags
        if invert:
            self.invert = invert

    # Protected methods

    def is_in_bin(self, data: Union[Row, Table],
                  *_args, **_kwargs) -> Union[bool, np.ndarray]:
        """ Checks if the data (does not) match the flags.
        """
        # Perform a bitwise and to check against the flags
        flag_match: Union[int, np.ndarray] = np.bitwise_and(data[self.bin_colname], self.bit_flags)

        # Convert to bool or array of bools
        if isinstance(flag_match, np.ndarray):
            bool_flag_match = flag_match.astype(bool)
        else:
            bool_flag_match = bool(flag_match)

        # Invert if desired and return
        if not self.invert:
            return bool_flag_match
        return np.logical_not(bool_flag_match)


class MultiBinConstraint(BinConstraint):
    """ Class for constraining on the intersection of multiple bins on a single table.
    """

    l_bin_constraints: Sequence[BinConstraint]

    def __init__(self, l_bin_constraints: Sequence[BinConstraint]) -> None:
        super().__init__()

        if l_bin_constraints:
            self.l_bin_constraints = l_bin_constraints
        else:
            self.l_bin_constraints = []

    # Protected methods

    def is_in_bin(self, data: Union[Row, Table],
                  *args, **kwargs) -> Union[bool, np.ndarray]:
        """ Checks if the data is in all bin constraints.
        """

        l_l_is_in_bin: List[np.ndarray] = [bin_constraint.is_in_bin(data, *args, **kwargs)
                                           for bin_constraint in self.l_bin_constraints]
        return np.logical_and.reduce(l_l_is_in_bin)


class HeteroBinConstraint:
    """ Class for constraining on the intersection of multiple bins on multiple tables.
    """

    l_bin_constraints: Sequence[BinConstraint]

    def __init__(self, l_bin_constraints: Sequence[BinConstraint]) -> None:

        if l_bin_constraints:
            self.l_bin_constraints = l_bin_constraints
        else:
            self.l_bin_constraints = []

    # Protected methods

    def get_ids_in_bin(self,
                       l_tables: Sequence[Table],
                       l_full_ids: Optional[Sequence[int]] = None,
                       *args, **kwargs) -> Sequence[int]:
        """ Checks if the data is in all bin constraints, where the list of tables
            is aligned with the list of bin constraints
        """

        l_s_ids_in_bin: List[Set[int]] = [
            set(bin_constraint.get_ids_in_bin(table, *args, l_full_ids = l_full_ids ** kwargs))
            for bin_constraint, table in zip(self.l_bin_constraints, l_tables)]
        return np.array(list(set.intersection(*l_s_ids_in_bin)))


# Bin constraints for specific use cases


class VisDetBinConstraint(ValueBinConstraint):
    """ Bin constraints to make sure the fit class is 0 (galaxy).
    """

    bin_colname: str = MFC_TF.vis_det
    value: Any = 1
    invert: bool = False


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
    bin_parameter: BinParameters
    bin_colname: Optional[str]

    def __init__(self,
                 test_case_info: Optional[TestCaseInfo] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS) -> None:

        super().__init__(bin_limits = bin_limits)

        # Set parameters from the test_case_info object
        if test_case_info:
            self.test_case_info = test_case_info
            self.bin_parameter = test_case_info.bins
        else:
            self.bin_parameter = bin_parameter

        # Check that the bin_parameter was somehow specified
        if not self.bin_parameter:
            raise ValueError("bin_parameter must be specified in init for BinParameterBinConstraint, either via "
                             "test_case_info or bin_parameter input. Supplied was: "
                             f"test_case_info = {test_case_info}, "
                             f"bin_parameter = {bin_parameter}.")

        # Set column name for this bin parameter if applicable, or else set to None
        if self.bin_parameter != BinParameters.GLOBAL:
            self.bin_colname = getattr(BIN_TF, self.bin_parameter.value)
        else:
            self.bin_colname = None

    # Protected methods

    def is_in_bin(self,
                  data: Union[Row, Table], *_args,
                  data_stack: Optional[SHEFrameStack] = None,
                  **_kwargs) -> Union[bool, np.ndarray]:
        """ Need to check what implementation we need based on the bin parameter.
        """

        # For GLOBAL case, we don't need any special setup
        if self.bin_parameter == BinParameters.GLOBAL:
            return super().is_in_bin(data)

        # For other cases, we need to make sure we have the needed data and add it if not
        new_bin_colname = getattr(BIN_TF, self.bin_parameter.value)
        if new_bin_colname not in data.colnames:
            D_COLUMN_ADDING_METHODS[self.bin_parameter](data, data_stack)

        self.bin_colname = new_bin_colname

        return super().is_in_bin(data)


class FitclassZeroBinConstraint(ValueBinConstraint):
    """ Bin constraints to make sure the fit class is 0 (galaxy).
    """

    bin_colname: str
    value: Any = 0
    invert: bool = False

    def __init__(self, method: ShearEstimationMethods) -> None:
        """ Get the bin colname from the shear estimation method.
        """
        tf: SheMeasurementsFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        super().__init__(bin_colname = tf.fit_class)


class FitflagsBinConstraint(BitFlagsBinConstraint):
    """ Bin constraints to make sure the fit didn't fail.
    """

    bin_colname: str
    bit_flags: Any = failure_flags
    invert: bool = True

    def __init__(self, method: ShearEstimationMethods) -> None:
        """ Get the bin colname from the shear estimation method.
        """
        tf: SheMeasurementsFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        super().__init__(bin_colname = tf.fit_flags)


class WeightBinConstraint(RangeBinConstraint):
    """ Bin constraints to make sure the fit didn't fail.
    """

    bin_colname: str
    bin_limits: Sequence[float] = (0, np.inf)
    include_min: bool = False
    include_max: bool = False

    def __init__(self, method: ShearEstimationMethods) -> None:
        """ Get the bin colname from the shear estimation method.
        """
        tf: SheMeasurementsFormat = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]
        super().__init__(bin_colname = tf.weight)


# Convenience multi bin constraints


class VisDetBinParameterBinConstraint(MultiBinConstraint):
    """ Bin constraint that combines being detected in VIS and being in a bin.
    """

    def __init__(self,
                 test_case_info: Optional[TestCaseInfo] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS) -> None:
        vis_det_bc = VisDetBinConstraint()
        bin_parameter_bc = BinParameterBinConstraint(test_case_info = test_case_info,
                                                     bin_parameter = bin_parameter,
                                                     bin_limits = bin_limits)

        super().__init__(l_bin_constraints = [vis_det_bc, bin_parameter_bc])


class GoodMeasurementBinConstraint(MultiBinConstraint):
    """ Bin constraint which combines Fitclass zero and fit flags bin constraints
    """

    def __init__(self, method: ShearEstimationMethods) -> None:
        fitflags_bc = FitflagsBinConstraint(method = method)
        weight_bc = WeightBinConstraint(method = method)

        super().__init__(l_bin_constraints = [fitflags_bc, weight_bc])


class GoodGalaxyMeasurementBinConstraint(MultiBinConstraint):
    """ Bin constraint which combines Fitclass zero and fit flags bin constraints
    """

    def __init__(self, method: ShearEstimationMethods) -> None:
        fitclass_zero_bc = FitclassZeroBinConstraint(method = method)
        fitflags_bc = FitflagsBinConstraint(method = method)
        weight_bc = WeightBinConstraint(method = method)

        super().__init__(l_bin_constraints = [fitclass_zero_bc, fitflags_bc, weight_bc])


class GoodBinnedMeasurementBinConstraint(MultiBinConstraint):
    """ Bin constrained which combines VisDetBinParameterBinConstraint and GoodMeasurementBinConstraint.
    """

    def __init__(self,
                 method: Optional[ShearEstimationMethods] = None,
                 test_case_info: Optional[TestCaseInfo] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS, ) -> None:

        det_bin_bc = BinParameterBinConstraint(test_case_info = test_case_info,
                                               bin_parameter = bin_parameter,
                                               bin_limits = bin_limits)
        if method is None:
            method = test_case_info.method

        good_meas_bc = GoodMeasurementBinConstraint(method = method)

        super().__init__(l_bin_constraints = [det_bin_bc, good_meas_bc])


class GoodBinnedGalaxyMeasurementBinConstraint(MultiBinConstraint):
    """ Bin constrained which combines VisDetBinParameterBinConstraint and GoodMeasurementBinConstraint.
    """

    def __init__(self,
                 method: ShearEstimationMethods,
                 test_case_info: Optional[TestCaseInfo] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS, ) -> None:
        det_bin_bc = BinParameterBinConstraint(test_case_info = test_case_info,
                                               bin_parameter = bin_parameter,
                                               bin_limits = bin_limits)
        good_meas_bc = GoodGalaxyMeasurementBinConstraint(method = method)

        super().__init__(l_bin_constraints = [det_bin_bc, good_meas_bc])


# Convenience hetero bin constraints


class GoodBinnedMeasurementHBC(HeteroBinConstraint):
    """ Bin constrained which combines VisDetBinParameterBinConstraint and GoodMeasurementBinConstraint.
    """

    def __init__(self,
                 method: ShearEstimationMethods,
                 test_case_info: Optional[TestCaseInfo] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS, ) -> None:
        det_bin_bc = VisDetBinParameterBinConstraint(test_case_info = test_case_info,
                                                     bin_parameter = bin_parameter,
                                                     bin_limits = bin_limits)
        good_meas_bc = GoodMeasurementBinConstraint(method = method)

        super().__init__(l_bin_constraints = [det_bin_bc, good_meas_bc])


class GoodBinnedGalaxyMeasurementHBC(HeteroBinConstraint):
    """ Bin constrained which combines VisDetBinParameterBinConstraint and GoodGalaxyMeasurementBinConstraint.
    """

    def __init__(self,
                 method: ShearEstimationMethods,
                 test_case_info: Optional[TestCaseInfo] = None,
                 bin_parameter: Optional[BinParameters] = None,
                 bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS, ) -> None:
        det_bin_bc = VisDetBinParameterBinConstraint(test_case_info = test_case_info,
                                                     bin_parameter = bin_parameter,
                                                     bin_limits = bin_limits)
        good_meas_bc = GoodGalaxyMeasurementBinConstraint(method = method)

        super().__init__(l_bin_constraints = [det_bin_bc, good_meas_bc])


# Functions to apply bin constraints


def _get_ids_in_bin(bin_parameter: BinParameters,
                    bin_constraint_type: Type,
                    full_bin_limits: Sequence[float],
                    bin_index: int,
                    detections_table: Table,
                    l_full_ids: Sequence[int],
                    data_stack: Optional[SHEFrameStack] = None,
                    ) -> Sequence[int]:
    # Get the bin limits, and make a bin constraint
    bin_limits: Sequence[float] = full_bin_limits[bin_index:bin_index + 2]
    bin_constraint: BinConstraint = bin_constraint_type(bin_parameter = bin_parameter, bin_limits = bin_limits)

    # Get IDs for this bin, and add it to the list
    l_binned_ids = bin_constraint.get_ids_in_bin(t = detections_table,
                                                 l_full_ids = l_full_ids,
                                                 data_stack = data_stack)

    return l_binned_ids


def _get_ids_in_hetero_bin(bin_parameter: BinParameters,
                           method: ShearEstimationMethods,
                           bin_constraint_type: Type,
                           full_bin_limits: Sequence[float],
                           bin_index: int,
                           detections_table: Table,
                           l_full_ids: Sequence[int],
                           measurements_table: Table,
                           data_stack: Optional[SHEFrameStack] = None,
                           ) -> Sequence[int]:
    # Get the bin limits, and make a bin constraint
    bin_limits: Sequence[float] = full_bin_limits[bin_index:bin_index + 2]
    bin_constraint: HeteroBinConstraint = bin_constraint_type(method = method,
                                                              bin_parameter = bin_parameter,
                                                              bin_limits = bin_limits, )

    # Get IDs for this bin, and add it to the list
    l_binned_ids = bin_constraint.get_ids_in_bin(l_tables = [detections_table, measurements_table],
                                                 l_full_ids = l_full_ids,
                                                 data_stack = data_stack)

    return l_binned_ids


def get_ids_for_bins(d_bin_limits: Dict[BinParameters, Sequence[float]],
                     detections_table: Table,
                     l_full_ids: Sequence[int],
                     l_bin_parameters: Sequence[BinParameters] = BinParameters,
                     data_stack: Optional[SHEFrameStack] = None,
                     bin_constraint_type: Type = VisDetBinParameterBinConstraint,
                     ) -> Dict[BinParameters, List[Sequence[int]]]:
    """ Creates a bin constraint for each bin parameter in a list (default all), then applies it to the detections
        table.

        Returns a dict of bin_parameter: List[np.ndarray<int> of IDs in each bin].
    """

    # Init output dict
    d_l_l_binned_ids: Dict[BinParameters, List[Sequence[int]]] = {}

    # For each test case info, create a bin constraint and apply it
    for bin_parameter in l_bin_parameters:

        # Get data relevant for this bin parameter
        full_bin_limits: Sequence[float] = d_bin_limits[bin_parameter]
        num_bins: int = len(full_bin_limits) - 1
        assert num_bins >= 1

        # Start a list of the ID lists for this test case
        l_l_binned_ids: List[Sequence[int]] = [[]] * num_bins

        # Loop over bins, getting IDs for each and adding them to the list
        for bin_index in range(num_bins):

            l_binned_ids: Sequence[int] = _get_ids_in_bin(bin_parameter = bin_parameter,
                                                          bin_constraint_type = bin_constraint_type,
                                                          full_bin_limits = full_bin_limits,
                                                          bin_index = bin_index,
                                                          detections_table = detections_table,
                                                          l_full_ids = l_full_ids,
                                                          data_stack = data_stack)
            l_l_binned_ids[bin_index] = l_binned_ids

        # Add the list to the output dictionary
        d_l_l_binned_ids[bin_parameter] = l_l_binned_ids

    return d_l_l_binned_ids


def get_ids_for_test_cases(l_test_case_info: Sequence[TestCaseInfo],
                           d_bin_limits: Dict[BinParameters, Sequence[float]],
                           detections_table: Table,
                           l_full_ids: Sequence[int],
                           d_measurements_tables: Optional[Dict[ShearEstimationMethods, Table]] = None,
                           data_stack: Optional[SHEFrameStack] = None,
                           bin_constraint_type: Type = GoodBinnedMeasurementHBC,
                           ) -> Dict[str, List[Sequence[int]]]:
    """ Creates a bin constraint for each test case, then applies it to the detections table.

        Returns a dict of test_case_info.name: List[np.ndarray<int> of IDs in each bin].
    """

    # Get a set of the bin parameters we want to use
    s_bin_parameters: Set[BinParameters] = set()
    for test_case_info in l_test_case_info:
        s_bin_parameters.add(test_case_info.bin_parameter)

    # Init output dict
    d_l_l_binned_ids: Dict[str, List[Sequence[int]]] = {}

    # For each test case info, create a bin constraint and apply it
    for test_case_info in l_test_case_info:

        # Get data relevant for this bin parameter
        bin_parameter = test_case_info.bin_parameter
        full_bin_limits: Sequence[float] = d_bin_limits[bin_parameter]
        num_bins: int = len(full_bin_limits) - 1
        assert num_bins >= 1

        # Start a list of the ID lists for this test case
        l_l_binned_ids: List[Sequence[int]] = [[]] * num_bins

        # Loop over bins, getting IDs for each and adding them to the list
        for bin_index in range(num_bins):

            l_l_binned_ids[bin_index] = _get_l_binned_ids(test_case_info = test_case_info,
                                                          bin_constraint_type = bin_constraint_type,
                                                          full_bin_limits = full_bin_limits,
                                                          bin_index = bin_index,
                                                          detections_table = detections_table,
                                                          l_full_ids = l_full_ids,
                                                          d_measurements_tables = d_measurements_tables,
                                                          data_stack = data_stack)

        # Add the list to the output dictionary
        d_l_l_binned_ids[test_case_info.name] = l_l_binned_ids

    return d_l_l_binned_ids


def _get_l_binned_ids(test_case_info: TestCaseInfo,
                      bin_constraint_type: Type,
                      full_bin_limits: np.ndarray,
                      bin_index: int,
                      detections_table: Table,
                      l_full_ids: Sequence[int],
                      d_measurements_tables: Dict[ShearEstimationMethods, Table],
                      data_stack: SHEFrameStack):
    # Special processing if we have a HeteroBinConstraint
    if issubclass(bin_constraint_type, HeteroBinConstraint):
        measurements_table: Optional[Table] = None
        if d_measurements_tables:
            measurements_table = d_measurements_tables[test_case_info.method]
        if measurements_table is None:
            # If we don't have data for a given method, return no IDs for it
            l_binned_ids: Sequence[int] = []
        else:
            l_binned_ids: Sequence[int] = _get_ids_in_hetero_bin(bin_parameter = test_case_info.bin_parameter,
                                                                 method = test_case_info.method,
                                                                 bin_constraint_type = bin_constraint_type,
                                                                 full_bin_limits = full_bin_limits,
                                                                 bin_index = bin_index,
                                                                 detections_table = detections_table,
                                                                 l_full_ids = l_full_ids,
                                                                 measurements_table = measurements_table,
                                                                 data_stack = data_stack)
    else:
        l_binned_ids: Sequence[int] = _get_ids_in_bin(bin_parameter = test_case_info.bin_parameter,
                                                      bin_constraint_type = bin_constraint_type,
                                                      full_bin_limits = full_bin_limits,
                                                      bin_index = bin_index,
                                                      detections_table = detections_table,
                                                      l_full_ids = l_full_ids,
                                                      data_stack = data_stack)
    return l_binned_ids


def get_table_of_ids(t: Table,
                     l_ids: Sequence[int],
                     id_colname: str = MFC_TF.ID) -> Table:
    """ Gets a version of a table with just the objects with IDs in the provided list, with handling for empty lists.
    """

    # Make sure the ID column name is set as an index for the table
    if id_colname not in t.indices:
        t.add_index(id_colname)

    # Make sure the IDs list is the proper type
    if not isinstance(l_ids, np.ndarray):
        l_ids = np.array(l_ids)

    # Return an empty table if the ID list is empty
    if len(l_ids) == 0:
        return t[np.zeros_like(t[id_colname], dtype = bool)]

    try:
        table_in_bin: Table = t.loc[l_ids]
    except KeyError:
        # If we get here, at least one ID in the list isn't in the table, so we'll have to prune the list
        l_ids_in_table = [object_id for object_id in l_ids if object_id in t[id_colname]]
        table_in_bin: Table = t.loc[l_ids_in_table]

    return table_in_bin


class BinnedTableLoader(TableLoader):
    """ Class to handle loading in binned data from a single tables.
    """

    id_colname: str = MFC_TF.ID

    def __init__(self,
                 id_colname: Optional[str] = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        if id_colname:
            self.id_colname = id_colname

    def get_table_for_ids(self,
                          l_ids: Sequence[int],
                          keep_open: bool = True) -> Table:
        """ Get a table with only objects with IDs in the list.
        """

        # Load the table, keeping it open if desired
        if keep_open:
            self.load()
            t = self.obj
        else:
            t = self.get()

        return get_table_of_ids(t = t,
                                l_ids = l_ids,
                                id_colname = self.id_colname)

    def get_table_for_all(self,
                          keep_open: bool = True,
                          *args, **kwargs) -> Table:
        """ Get a combined table of all objects.
        """

        # Load the table, keeping it open if desired
        if keep_open:
            self.load(*args, **kwargs)
            t = self.obj
        else:
            t = self.get(*args, **kwargs)

        return t


class BinnedMultiTableLoader(MultiTableLoader):
    """ Class to handle loading in binned data from multiple tables.
    """

    id_colname: str = MFC_TF.ID

    def __init__(self,
                 id_colname: Optional[str] = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        if id_colname:
            self.id_colname = id_colname

    # Private methods

    @staticmethod
    def __get_with_keep_open(file_loader: TableLoader,
                             keep_open: bool = True,
                             *args, **kwargs):
        """ Load a table, keeping it open if desired. """
        if keep_open:
            file_loader.load(*args, **kwargs)
            t = file_loader.obj
        else:
            t = file_loader.get(*args, **kwargs)
        return t

    # Public methods

    def get_table_for_ids(self,
                          l_ids: Sequence[int],
                          keep_open: bool = True,
                          *args, **kwargs) -> Optional[Table]:
        """ Get a table with only objects with IDs in the list.
        """

        l_binned_tables: List[Optional[Table]] = [None] * len(self.l_file_loaders)

        # Get a binned table from each file loader
        i: int
        file_loader: TableLoader
        for i, file_loader in enumerate(self.l_file_loaders):

            t: Table = self.__get_with_keep_open(file_loader, keep_open, *args, **kwargs)

            l_binned_tables[i] = get_table_of_ids(t = t,
                                                  l_ids = l_ids,
                                                  id_colname = self.id_colname)

        # Check that we have at least one table
        if len(l_binned_tables) == 0:
            return None

        return table_vstack(tables = l_binned_tables)

    def get_table_for_all(self,
                          keep_open: bool = True,
                          *args, **kwargs) -> Optional[Table]:
        """ Get a combined table of all objects.
        """

        if keep_open:
            self.load_all(*args, **kwargs)

        l_binned_tables: List[Table] = self.get_all(*args, **kwargs)

        # Check that we have at least one table
        if len(l_binned_tables) == 0:
            return None

        return table_vstack(tables = l_binned_tables)

    def get_table_for_bin_constraint(self,
                                     bin_constraint: BinConstraint,
                                     keep_open: bool = True,
                                     *args, **kwargs) -> Optional[Table]:
        """ Get a combined table of all objects which pass quality checks on shear estimates.

            Requires the table format to properly check estimates tables.
        """

        l_binned_tables: List[Optional[Table]] = [None] * len(self.l_file_loaders)

        # Get a binned table from each file loader
        i: int
        file_loader: TableLoader
        for i, file_loader in enumerate(self.l_file_loaders):

            t: Table = self.__get_with_keep_open(file_loader, keep_open, *args, **kwargs)

            # Get a list of IDs for this bin constraint
            l_binned_tables[i] = bin_constraint.get_rows_in_bin(t = t)

        # Check that we have at least one table
        if len(l_binned_tables) == 0:
            return None

        return table_vstack(tables = l_binned_tables)
