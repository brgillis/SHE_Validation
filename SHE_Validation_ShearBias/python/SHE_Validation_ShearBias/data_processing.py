""" @file data_processing.py

    Created 8 July 2021

    Code to process data for shear bias validation tests
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from typing import Any, Dict, List, Optional, Sequence

import numpy as np
from astropy.table import Column, Table

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import TableLoader
from SHE_PPT.logging import getLogger
from SHE_PPT.math import (BiasMeasurements, LinregressResults, linregress_with_errors)
from SHE_PPT.pipeline_utility import ConfigKeys, ValidationConfigKeys
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat
from SHE_PPT.table_utility import SheTableFormat
from SHE_Validation.binning.bin_constraints import (BinConstraint, BinnedMultiTableLoader,
                                                    GoodBinnedMeasurementBinConstraint, )
from SHE_Validation.constants.test_info import BinParameters, TestCaseInfo

logger = getLogger(__name__)

# Data display constants
C_DIGITS: int = 5
M_DIGITS: int = 3
SIGMA_DIGITS: int = 1

# Messages
ERR_MUST_LOAD = "Most load data with load_ids or load_all before accessing this attribute."


class ShearBiasDataLoader:
    """ Class to load in needed data for shear bias data processing.
    """

    # Attributes set directly at init
    l_filenames: Sequence[str]
    workdir: str
    method: ShearEstimationMethods

    # Attributes determined at init
    _table_loader: BinnedMultiTableLoader
    _sem_tf: SheTUMatchedFormat

    # Attributes set when loaded
    table: Optional[Table] = None
    table_loaded: bool = False

    # Output attributes
    _d_g_in: Optional[Dict[int, Sequence[float]]] = None
    _d_g_out: Optional[Dict[int, Sequence[float]]] = None
    _d_g_out_err: Optional[Dict[int, Sequence[float]]] = None

    def __init__(self,
                 l_filenames: Sequence[str],
                 workdir: str,
                 method: ShearEstimationMethods, ):

        # Set attributes from args
        self.l_filenames = l_filenames
        self.workdir = workdir
        self.method = method

        # Create a table loader with this list of filenames
        self._table_loader = BinnedMultiTableLoader(l_filenames=self.l_filenames,
                                                    workdir=self.workdir,
                                                    file_loader_type=TableLoader)

        # Determine the table format
        self._sem_tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[self.method]

    # Output properties

    @property
    def d_g_in(self) -> Dict[int, Sequence[float]]:
        if not self.table_loaded:
            raise ValueError(ERR_MUST_LOAD)
        if not self._d_g_in:
            self._calc()
        return self._d_g_in

    @d_g_in.setter
    def d_g_in(self, d_g_in) -> None:
        self._d_g_in = d_g_in

    @property
    def d_g_out(self) -> Dict[int, Sequence[float]]:
        if not self.table_loaded:
            raise ValueError(ERR_MUST_LOAD)
        if not self._d_g_out:
            self._calc()
        return self._d_g_out

    @d_g_out.setter
    def d_g_out(self, d_g_out) -> None:
        self._d_g_out = d_g_out

    @property
    def d_g_out_err(self) -> Dict[int, Sequence[float]]:
        if not self.table_loaded:
            raise ValueError(ERR_MUST_LOAD)
        if not self._d_g_out_err:
            self._calc()
        return self._d_g_out_err

    @d_g_out_err.setter
    def d_g_out_err(self, d_g_out_err) -> None:
        self._d_g_out_err = d_g_out_err

    # Private methods

    def __decache(self) -> None:
        self.d_g_in = None
        self.d_g_out = None
        self.d_g_out_err = None

    # Protected methods

    def _calc(self):
        """ Calculate the shear bias columns we need.
        """

        if not self.table_loaded:
            raise ValueError("Most load data with load_ids or load_all before calculating properties.")

        # If no tables were loaded, set up empty data
        if self.table is None:

            self._d_g_in = {1: np.array([], dtype=float),
                            2: np.array([], dtype=float)}
            self._d_g_out = {1: np.array([], dtype=float),
                             2: np.array([], dtype=float)}
            self._d_g_out_err = {1: np.array([], dtype=float),
                                 2: np.array([], dtype=float)}

            return

        # Get the data we need out of the table
        # noinspection PyTypeChecker
        l_g1_in: Column = -(self.table[self._sem_tf.tu_gamma1] / (1 - self.table[self._sem_tf.tu_kappa]))
        l_g2_in: Column = (self.table[self._sem_tf.tu_gamma2] / (1 - self.table[self._sem_tf.tu_kappa]))
        l_g1_out: Column = self.table[self._sem_tf.g1]
        l_g2_out: Column = self.table[self._sem_tf.g2]
        l_g1_out_err: Column = self.table[self._sem_tf.g1_err]
        l_g2_out_err: Column = self.table[self._sem_tf.g2_err]

        # Combine the data into the output dicts
        self._d_g_in = {1: l_g1_in,
                        2: l_g2_in}
        self._d_g_out = {1: l_g1_out,
                         2: l_g2_out}
        self._d_g_out_err = {1: l_g1_out_err,
                             2: l_g2_out_err}

    # Public methods

    def load_ids(self,
                 l_ids: Sequence[int],
                 *args, **kwargs) -> None:
        self.__decache()
        self.table = self.get_ids(l_ids=l_ids, *args, **kwargs)
        self.table_loaded = True

    def load_all(self, *args, **kwargs):
        self.__decache()
        self.table = self.get_all(*args, **kwargs)
        self.table_loaded = True

    def load_for_bin_constraint(self,
                                bin_constraint: BinConstraint,
                                *args, **kwargs):
        self.__decache()
        self.table = self.get_for_bin_constraint(bin_constraint=bin_constraint, *args, **kwargs)
        self.table_loaded = True

    def get_all(self, *args, **kwargs) -> Table:
        return self._table_loader.get_table_for_all(*args, **kwargs)

    def get_ids(self,
                l_ids: Sequence[int],
                *args, **kwargs) -> Table:
        return self._table_loader.get_table_for_ids(l_ids=l_ids, *args, **kwargs)

    def get_for_bin_constraint(self,
                               bin_constraint: BinConstraint,
                               *args, **kwargs) -> Table:
        return self._table_loader.get_table_for_bin_constraint(bin_constraint=bin_constraint, *args, **kwargs)

    def clear(self):
        if self.table_loaded:
            self.table_loaded = False
            self._table_loader.close_all()
            self.__decache()


class ShearBiasTestCaseDataProcessor:
    """ Class to handle and perform calculations for an individual Shear Bias Test Case.
    """

    # Attributes with fixed values
    bootstrap_seed: int = 12345
    n_bootstrap: int = 1000

    # Attributes set directly at init
    data_loader: ShearBiasDataLoader
    test_case_info: TestCaseInfo
    l_bin_limits: Sequence[float]
    bootstrap_errors: bool = False
    max_g_in: float = 1.0

    # Attributes determined at init
    method: ShearEstimationMethods
    bin_parameter: BinParameters
    num_bins: int

    # Flag for whether or not we've calculated data
    _calculated: bool = False

    # Intermediate attributes set when loading data
    _bin_index: Optional[int] = None
    _bin_limits: Sequence[float]
    _gal_matched_table: Table

    # Intermediate attributes determined when processing data
    _sem_tf: SheTableFormat
    _good_rows: Sequence[bool]
    _fitclass_zero_rows: Sequence[bool]

    # Output attributes - each are list (for bin limits): component index: value
    _l_d_g_in: Optional[List[Dict[int, Sequence[float]]]] = None
    _l_d_g_out: Optional[List[Dict[int, Sequence[float]]]] = None
    _l_d_g_out_err: Optional[List[Dict[int, Sequence[float]]]] = None
    _l_d_bias_measurements: Optional[List[Dict[int, BiasMeasurements]]] = None
    _l_d_linregress_results: Optional[List[Dict[int, LinregressResults]]] = None

    # list (for bin limits): component string: value
    _l_d_bias_strings: Optional[List[Dict[str, str]]] = None

    def __init__(self,
                 data_loader: ShearBiasDataLoader,
                 test_case_info: TestCaseInfo,
                 l_bin_limits: Sequence[float],
                 pipeline_config: Optional[Dict[ConfigKeys, Any]] = None, ) -> None:

        # Set attrs directly
        self.data_loader = data_loader
        self.test_case_info = test_case_info
        self.l_bin_limits = l_bin_limits
        if pipeline_config:
            self.bootstrap_errors = pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS]
            self.max_g_in = pipeline_config[ValidationConfigKeys.SBV_MAX_G_IN]

        # Sanity check on method
        if self.test_case_info.method != self.data_loader.method:
            raise ValueError(f"Method from test_case_info ({self.test_case_info.method}) differs from method from "
                             f"data loader ({self.data_loader.method}).")

        # Get values from the input
        self.method = test_case_info.method
        self.bin_parameter = test_case_info.bin_parameter
        self.num_bins = len(self.l_bin_limits) - 1
        assert self.num_bins >= 1

        # Determine table format
        self._sem_tf: SheTableFormat = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[self.method]

    # Getters and setters for output attributes, which calculate if needed

    @property
    def workdir(self) -> str:
        return self.data_loader.workdir

    @property
    def d_g_in(self) -> Dict[int, Sequence[float]]:
        return self.data_loader.d_g_in

    @property
    def d_g_out(self) -> Dict[int, Sequence[float]]:
        return self.data_loader.d_g_out

    @property
    def d_g_out_err(self) -> Dict[int, Sequence[float]]:
        return self.data_loader.d_g_out_err

    @property
    def l_d_bias_measurements(self) -> List[Dict[int, BiasMeasurements]]:
        if not self._l_d_bias_measurements:
            self.calc()
        return self._l_d_bias_measurements

    @property
    def l_d_linregress_results(self) -> List[Dict[int, LinregressResults]]:
        if not self._l_d_linregress_results:
            self.calc()
        return self._l_d_linregress_results

    @property
    def l_d_bias_strings(self) -> List[Dict[str, str]]:
        if not self._l_d_bias_strings:
            self.calc()
        return self._l_d_bias_strings

    # Private methods

    def _calc_component_shear_bias(self,
                                   bin_index: int,
                                   component_index: int):
        """ Calculate shear bias for an individual component.
        """

        # Limit the data to that in the current bin
        bin_constraint = GoodBinnedMeasurementBinConstraint(test_case_info=self.test_case_info,
                                                            bin_limits=self.l_bin_limits[bin_index:bin_index + 2])
        self.data_loader.load_for_bin_constraint(bin_constraint=bin_constraint)

        # Get data limited to the rows where g_in is less than the allowed max
        # noinspection PyTypeChecker
        g = np.sqrt(self.d_g_in[1] ** 2 + self.d_g_in[2] ** 2)
        good_g_in_rows = g < self.max_g_in

        g_in = self.d_g_in[component_index][good_g_in_rows]
        g_out = self.d_g_out[component_index][good_g_in_rows]
        g_out_err = self.d_g_out_err[component_index][good_g_in_rows]

        # Perform the linear regression, calculate bias, and save it in the bias dict
        if not self.bootstrap_errors:

            linregress_results = linregress_with_errors(x=g_in,
                                                        y=g_out,
                                                        y_err=g_out_err)

        else:

            g_table = Table([g_in, g_out, g_out_err], names=("g_in", "g_out", "g_out_err"))

            # Seed the random number generator
            np.random.seed(self.bootstrap_seed)

            # Get a base object for the m and c calculations
            linregress_results = linregress_with_errors(x=g_table["g_in"],
                                                        y=g_table["g_out"],
                                                        y_err=g_table["g_out_err"])

            # Bootstrap to get errors on slope and intercept
            n_sample = len(g_table)

            slope_bs = np.empty(self.n_bootstrap)
            intercept_bs = np.empty(self.n_bootstrap)
            for b_i in range(self.n_bootstrap):
                u = np.random.randint(0, n_sample, n_sample)
                linregress_results_bs = linregress_with_errors(x=g_table[u]["g_in"],
                                                               y=g_table[u]["g_out"],
                                                               y_err=g_table[u]["g_out_err"])
                slope_bs[b_i] = linregress_results_bs.slope
                intercept_bs[b_i] = linregress_results_bs.intercept

            # Update the bias measurements in the output object
            linregress_results.slope_err = np.std(slope_bs)
            linregress_results.intercept_err = np.std(intercept_bs)

        self._l_d_linregress_results[bin_index][component_index] = linregress_results

        bias = BiasMeasurements(linregress_results)
        self._l_d_bias_measurements[bin_index][component_index] = bias

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Bias measurements for method {self.method.value}:")
        for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
            self._l_d_bias_strings[bin_index][f"{a}{component_index}"] = (
                f"{a}{component_index} = {getattr(bias, a):.{d}f} +/- {getattr(bias, f'{a}_err'):.{d}f} "
                f"({getattr(bias, f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(self._l_d_bias_strings[bin_index][f"{a}{component_index}"])

    # Public methods

    def calc(self) -> None:
        """ Performs data processing, calculating bias measurements and other output data.
        """

        if self._calculated:
            return

        # Init empty lists for output data
        self._l_d_bias_measurements = [{}] * self.num_bins
        self._l_d_linregress_results = [{}] * self.num_bins
        self._l_d_bias_strings = [{}] * self.num_bins

        for bin_index in range(self.num_bins):

            # Init empty dicts for output data for this bin
            self._l_d_bias_measurements[bin_index] = {}
            self._l_d_linregress_results[bin_index] = {}
            self._l_d_bias_strings[bin_index] = {}

            for component_index in (1, 2):

                self._calc_component_shear_bias(bin_index=bin_index,
                                                component_index=component_index, )

        self._calculated = True
