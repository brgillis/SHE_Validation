""" @file utility.py

    Created 18 Oct 2021

    Utility functions related to requirement, test, and test case info.
"""

__updated__ = "2021-08-06"

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

from typing import Any, Dict, Optional, Union

import numpy as np
from astropy.table import Table
from scipy.stats.mstats_basic import mquantiles

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.constants.config import ConfigKeys
from SHE_Validation.binning.bin_data import BIN_TF
from SHE_Validation.constants.test_info import D_BIN_PARAMETER_META

STR_AUTO_BIN_LIMITS_HEAD = "auto"
DEFAULT_N_BIN_LIMITS_QUANTILES = 4
DEFAULT_AUTO_BIN_LIMITS = f"{STR_AUTO_BIN_LIMITS_HEAD}-{DEFAULT_N_BIN_LIMITS_QUANTILES}"
MSG_BAD_BIN_LIMITS_VALUE = ("Provided bin limits value ('%s') is of unrecognized format. It should either be a list of "
                            f"bin limits, or a string of the format '{STR_AUTO_BIN_LIMITS_HEAD}-N', where N is an "
                            f"integer giving the desired number of quantiles to use as bin limits.")


def get_d_l_bin_limits(pipeline_config: Dict[ConfigKeys, Any],
                       bin_data_table: Optional[Table] = None) -> Dict[BinParameters, np.ndarray]:
    """ Convert the bin limits in a pipeline_config (after type conversion) into a dict of arrays.
    """

    d_bin_limits = {}
    for bin_parameter in BinParameters:
        bin_limits_key = D_BIN_PARAMETER_META[bin_parameter].config_key
        if bin_limits_key is None or bin_limits_key not in pipeline_config:
            # This signifies not relevant to this test or not yet set up. Fill in with the default limits just in case
            bin_limits_value: Union[np.ndarray, str] = DEFAULT_AUTO_BIN_LIMITS
        else:
            bin_limits_value: Union[np.ndarray, str] = pipeline_config[bin_limits_key]

        if isinstance(bin_limits_value, str):

            # Raise an exception if no table was provided
            if bin_data_table is None:
                raise ValueError(f"'{STR_AUTO_BIN_LIMITS_HEAD}' bin limits were requested, but no bin_data_table was "
                                 f"provided.")
            d_bin_limits[bin_parameter] = get_auto_bin_limits_from_table(bin_parameter = bin_parameter,
                                                                         bin_limits_value = bin_limits_value,
                                                                         bin_data_table = bin_data_table)
        else:
            d_bin_limits[bin_parameter] = pipeline_config[bin_limits_key]

    return d_bin_limits


def get_auto_bin_limits_from_table(bin_parameter: BinParameters,
                                   bin_data_table: Table,
                                   bin_limits_value: str = DEFAULT_AUTO_BIN_LIMITS) -> np.ndarray:
    """ Determines bin limits automatically from data for the relevant bin parameter in the provided data table.
    """

    # Interpret the provided value to get the number of quantiles
    num_quantiles = _get_n_quantiles(bin_limits_value)

    # Get the data we'll be binning from the provided data table
    l_data = bin_data_table[getattr(BIN_TF, bin_parameter.value)]

    l_quantiles = get_auto_bin_limits_from_data(l_data, num_quantiles)

    return l_quantiles


def get_auto_bin_limits_from_data(l_data: np.ndarray,
                                  num_quantiles: int = DEFAULT_N_BIN_LIMITS_QUANTILES) -> np.ndarray:
    """ Determines bin limits from an array of data and the desired number of quantiles to split the data into.
    """

    # Use scipy to calculate bin limits via empirical qunatiles
    l_prob: np.ndarray = np.linspace(0, 1, num_quantiles + 1, endpoint = True)
    l_quantiles: np.ndarray = mquantiles(l_data, prob = l_prob, alphap = 0, betap = 1)

    # Override the first and last limit with -1e99 and 1e99 respectively
    l_quantiles[0] = -1e99
    l_quantiles[-1] = 1e99

    return l_quantiles


def _get_n_quantiles(bin_limits_value: str) -> int:
    """ Parse a provided string to check for validity and determine the desired number of quantiles.
    """

    # Check that the provided value is properly formatted
    l_split_bin_limits_value = bin_limits_value.split('-')
    if len(l_split_bin_limits_value) != 2 or l_split_bin_limits_value[0] != STR_AUTO_BIN_LIMITS_HEAD:
        raise ValueError(MSG_BAD_BIN_LIMITS_VALUE % bin_limits_value)

    try:
        n_quantiles = int(l_split_bin_limits_value[1])
    except ValueError:
        raise ValueError(MSG_BAD_BIN_LIMITS_VALUE % bin_limits_value)

    return n_quantiles
