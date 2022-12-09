""" @file utility.py

    Created 18 Oct 2021

    Utility functions related to binning.
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
from typing import Dict, TYPE_CHECKING, Union

import numpy as np
from astropy.table import Table
from scipy.stats.mstats_basic import mquantiles

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.utility import is_inf_nan_or_masked
from SHE_Validation.binning.bin_data import BIN_TF
from SHE_Validation.constants.default_config import (DEFAULT_AUTO_BIN_LIMITS, DEFAULT_N_BIN_LIMITS_QUANTILES,
                                                     STR_AUTO_BIN_LIMITS_HEAD,
                                                     TOT_BIN_LIMITS, )
from SHE_Validation.constants.test_info import D_BIN_PARAMETER_META

if TYPE_CHECKING:
    from SHE_PPT.constants.config import ConfigKeys  # noqa F401

# Dict relating the "global" config key for each bin parameter - that is, the key for providing the default value of
# bin limits if no overriding local key is provided.
D_GLOBAL_BIN_KEYS = {BinParameters.TOT: D_BIN_PARAMETER_META[BinParameters.TOT].config_key,
                     BinParameters.SNR: D_BIN_PARAMETER_META[BinParameters.SNR].config_key,
                     BinParameters.BG: D_BIN_PARAMETER_META[BinParameters.BG].config_key,
                     BinParameters.COLOUR: D_BIN_PARAMETER_META[BinParameters.COLOUR].config_key,
                     BinParameters.SIZE: D_BIN_PARAMETER_META[BinParameters.SIZE].config_key,
                     BinParameters.EPOCH: D_BIN_PARAMETER_META[BinParameters.EPOCH].config_key}

MSG_BAD_BIN_LIMITS_VALUE = ("Provided bin limits value ('%s') is of unrecognized format. It should either be a list of "
                            f"bin limits, or a string of the format '{STR_AUTO_BIN_LIMITS_HEAD}-N', where N is an "
                            f"integer giving the desired number of quantiles to use as bin limits.")


def get_d_l_bin_limits(pipeline_config,
                       bin_data_table=None,
                       l_bin_parameters=BinParameters,
                       d_local_bin_keys=None):
    """Convert the bin limits in a pipeline_config (after type conversion) into a dict of arrays.

    Parameters
    ----------
    pipeline_config : Dict[ConfigKeys, Any]
        Pipeline configuration dictionary, after processing to convert the input string values to their respective
        desired types. The entries specifying bin limits should be in the format of either an iterable of the
        bin_limits_key limits, or a string of the format "auto-N" (for some positive integer N). In the former case,
        this iterable will be converted into a np.ndarray. In the latter case, a np.ndarray will be created with bin
        limits to define N quantiles of the data to be binned, by referencing the data in the `bin_data_table` input
        parameter.
    bin_data_table : Table or None
        Table containing data to be binned, in case of automatic binning of any parameter. See description of
        `pipeline_config` above for details.
    l_bin_parameters : Iterable[BinParameters]
        An iterable of the bin parameters for which bin limits should be determined. The output dict will contain bin
        limits for only the BinParameters in this iterable.
    d_local_bin_keys : Mapping[BinParameters, ConfigKeys or None] or None
        Dict relating the "local" config key for each bin parameter - that is, the key for providing a value
        specifically for an individual validation test. If this is `None` (default), the keys for specifying bin limits
        globally will be used for all parameters. Similarly, if the entry for any bin parameter is `None`,
        the global key will be used for it.

    Returns
    -------
    d_l_bin_limits : Dict[BinParameters, np.ndarray]
        A dictionary of the bin limits for each bin parameter. Each parameter's bin limits will be expressed as a
        np.ndarray. This array will have N+1 elements when binning data into N bins, as it contains both the minimum
        and maximum value for each bin.
    """

    # We do this to use D_GLOBAL_BIN_KEYS (a constant) as the default argument for d_local_bin_keys, without risk
    # of it being indirectly modified
    if d_local_bin_keys is None:
        d_local_bin_keys = deepcopy(D_GLOBAL_BIN_KEYS)

    d_bin_limits: Dict[BinParameters, np.ndarray] = {}
    for bin_parameter in l_bin_parameters:
        global_bin_limits_key = D_GLOBAL_BIN_KEYS[bin_parameter]
        local_bin_limits_key = d_local_bin_keys[bin_parameter]

        # Determine if we should use the global or local key. If the local key is available and used, use that,
        # otherwise use the global key.
        if (local_bin_limits_key is not None and local_bin_limits_key in pipeline_config and
                pipeline_config[local_bin_limits_key] is not None):
            bin_limits_key = local_bin_limits_key
        else:
            bin_limits_key = global_bin_limits_key

        bin_limits_value: Union[np.ndarray, str]
        if bin_limits_key is None or bin_limits_key not in pipeline_config:
            # This signifies not relevant to this test or not yet set up. Fill in with the default limits just in
            # case
            if bin_parameter == BinParameters.TOT:
                bin_limits_value = np.array(TOT_BIN_LIMITS)
            else:
                bin_limits_value = DEFAULT_AUTO_BIN_LIMITS
        else:
            bin_limits_value = pipeline_config[bin_limits_key]

        if isinstance(bin_limits_value, str):

            # Raise an exception if no table was provided but we need one due to bin limits being specified via a string
            if bin_data_table is None:
                raise ValueError(
                    f"'{STR_AUTO_BIN_LIMITS_HEAD}' bin limits were requested, but no `bin_data_table` was provided.")
            d_bin_limits[bin_parameter] = get_auto_bin_limits_from_table(bin_parameter=bin_parameter,
                                                                         bin_limits_value=bin_limits_value,
                                                                         bin_data_table=bin_data_table)
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

    # Trim any inf, NaN, or masked values from l_data and coerce to an array
    l_l_is_good = np.where(np.logical_not(is_inf_nan_or_masked(np.asarray(l_data))))
    l_data = np.asarray(l_data)[l_l_is_good]

    # Check for no good data, and return dummy bins if so
    if len(l_data) == 0:
        return np.linspace(-1e99, 1e99, num_quantiles + 1)

    # Use scipy to calculate bin limits via empirical qunatiles
    l_prob: np.ndarray = np.linspace(0, 1, num_quantiles + 1, endpoint=True)
    l_quantiles: np.ndarray = mquantiles(l_data, prob=l_prob, alphap=0, betap=1)

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
    l_num_in_bin_down = np.zeros(num_quantiles, dtype=int)
    l_num_in_bin_up = np.zeros(num_quantiles, dtype=int)
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
