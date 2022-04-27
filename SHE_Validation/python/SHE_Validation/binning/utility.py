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

from copy import deepcopy
from typing import Any, Dict, Iterable, Optional, Union

import numpy as np
from astropy.table import Table
from scipy.stats.mstats_basic import mquantiles

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.constants.config import ConfigKeys, ValidationConfigKeys
from SHE_Validation.binning.bin_data import BIN_TF
from SHE_Validation.constants.default_config import (DEFAULT_AUTO_BIN_LIMITS, DEFAULT_N_BIN_LIMITS_QUANTILES,
                                                     STR_AUTO_BIN_LIMITS_HEAD,
                                                     TOT_BIN_LIMITS, )

MSG_BAD_BIN_LIMITS_VALUE = ("Provided bin limits value ('%s') is of unrecognized format. It should either be a list of "
                            f"bin limits, or a string of the format '{STR_AUTO_BIN_LIMITS_HEAD}-N', where N is an "
                            f"integer giving the desired number of quantiles to use as bin limits.")


class ConfigBinInterpreter:
    # Dict relating the "global" config key for each bin parameter - that is, the key for providing the default value of
    # bin limits if no overriding local key is provided.
    d_global_bin_keys = {BinParameters.TOT   : None,
                         BinParameters.SNR   : ValidationConfigKeys.VAL_SNR_BIN_LIMITS,
                         BinParameters.BG    : ValidationConfigKeys.VAL_BG_BIN_LIMITS,
                         BinParameters.COLOUR: ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS,
                         BinParameters.SIZE  : ValidationConfigKeys.VAL_SIZE_BIN_LIMITS,
                         BinParameters.EPOCH : ValidationConfigKeys.VAL_EPOCH_BIN_LIMITS}

    # Dict relating the "local" config key for each bin parameter - that is, the key for providing a value specifically
    # for an individual validation test. This should be overridden by any subclass of this with specific keys.
    d_local_bin_keys = {BinParameters.TOT   : None,
                        BinParameters.SNR   : ValidationConfigKeys.VAL_SNR_BIN_LIMITS,
                        BinParameters.BG    : ValidationConfigKeys.VAL_BG_BIN_LIMITS,
                        BinParameters.COLOUR: ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS,
                        BinParameters.SIZE  : ValidationConfigKeys.VAL_SIZE_BIN_LIMITS,
                        BinParameters.EPOCH : ValidationConfigKeys.VAL_EPOCH_BIN_LIMITS}

    @classmethod
    def get_d_l_bin_limits(cls,
                           pipeline_config: Dict[ConfigKeys, Any],
                           bin_data_table: Optional[Table] = None,
                           l_bin_parameters: Iterable[BinParameters] = BinParameters) -> Dict[
        BinParameters, np.ndarray]:
        """ Convert the bin limits in a pipeline_config (after type conversion) into a dict of arrays.
        """

        d_bin_limits = {}
        for bin_parameter in l_bin_parameters:
            global_bin_limits_key = cls.d_global_bin_keys[bin_parameter]
            local_bin_limits_key = cls.d_local_bin_keys[bin_parameter]

            # Determine if we should use the global or local key. If the local key is available and used, use that,
            # otherwise use the global key.
            if (local_bin_limits_key is not None and local_bin_limits_key in pipeline_config and
                    pipeline_config[local_bin_limits_key] is not None):
                bin_limits_key = local_bin_limits_key
            else:
                bin_limits_key = global_bin_limits_key

            if bin_limits_key is None or bin_limits_key not in pipeline_config:
                # This signifies not relevant to this test or not yet set up. Fill in with the default limits just in
                # case
                if bin_parameter == BinParameters.TOT:
                    bin_limits_value: Union[np.ndarray, str] = TOT_BIN_LIMITS
                else:
                    bin_limits_value: Union[np.ndarray, str] = DEFAULT_AUTO_BIN_LIMITS
            else:
                bin_limits_value: Union[np.ndarray, str] = pipeline_config[bin_limits_key]

            if isinstance(bin_limits_value, str):

                # Raise an exception if no table was provided
                if bin_data_table is None:
                    raise ValueError(
                        f"'{STR_AUTO_BIN_LIMITS_HEAD}' bin limits were requested, but no bin_data_table was "
                        f"provided.")
                d_bin_limits[bin_parameter] = get_auto_bin_limits_from_table(bin_parameter = bin_parameter,
                                                                             bin_limits_value = bin_limits_value,
                                                                             bin_data_table = bin_data_table)
            else:
                d_bin_limits[bin_parameter] = bin_limits_value

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

    # Check if any of the bin limits exactly equal a value in the data, and if so, slightly decrease that bin limit
    test_shifting: bool = False
    for bin_index in range(num_quantiles - 1):
        bin_max = l_quantiles[bin_index + 1]
        if np.any(bin_max == l_data):
            test_shifting = True

    # If no bin limits match data values, we can return here
    if not test_shifting:
        return l_quantiles

    # Since the mquantiles isn't consistent with how it sets quantiles, we have to test both shifting up and down, to
    # see which gives the better distribution of bin limits

    # Create lists of bin limits, shifted in each direction
    l_quantiles_down = deepcopy(l_quantiles)
    l_quantiles_up = deepcopy(l_quantiles)
    for bin_index in range(num_quantiles - 1):
        bin_max = l_quantiles[bin_index + 1]

        # Find the value closest to this limit, but below it
        dist_below: np.ndarray = np.where(l_data < bin_max, bin_max - l_data, 1e99)
        closest_value_below: float = bin_max - np.min(dist_below)

        # Find the value closest to this limit, but above it
        dist_above: np.ndarray = np.where(l_data > bin_max, l_data - bin_max, 1e99)
        closest_value_above: float = bin_max + np.min(dist_above)

        # Place the bin limit between this and where it was
        l_quantiles_down[bin_index + 1] = (closest_value_below + bin_max) / 2
        l_quantiles_up[bin_index + 1] = (closest_value_above + bin_max) / 2

    # Count the number in each bin, for each way to set quantiles
    l_num_in_bin_down = np.zeros(num_quantiles, dtype = int)
    l_num_in_bin_up = np.zeros(num_quantiles, dtype = int)
    for bin_index in range(num_quantiles):
        bin_down_lo: float = l_quantiles_down[bin_index]
        bin_down_hi: float = l_quantiles_down[bin_index + 1]

        l_num_in_bin_down[bin_index] = np.sum(np.logical_and(l_data >= bin_down_lo, l_data < bin_down_hi))

        bin_up_lo: float = l_quantiles_up[bin_index]
        bin_up_hi: float = l_quantiles_up[bin_index + 1]

        l_num_in_bin_up[bin_index] = np.sum(np.logical_and(l_data >= bin_up_lo, l_data < bin_up_hi))

    # Determine which is better, by having lower standard deviation in number, and use that
    if np.std(l_num_in_bin_down) < np.std(l_num_in_bin_up):
        return l_quantiles_down
    else:
        return l_quantiles_up


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
