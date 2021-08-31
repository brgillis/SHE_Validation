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

from typing import Dict, Sequence, Optional, Any

from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS)
from SHE_PPT.logging import getLogger
from SHE_PPT.math import (BiasMeasurements, linregress_with_errors,
                          LinregressResults)
from SHE_PPT.pipeline_utility import ValidationConfigKeys, ConfigKeys
from SHE_PPT.table_utility import SheTableFormat
from astropy.table import Column, Table
from SHE_Validation.binning.bin_constraints import BinnedMultiTableLoader,\
    BinConstraint

from SHE_Validation.constants.test_info import TestCaseInfo, BinParameters
import numpy as np


logger = getLogger(__name__)

# Data display constants
C_DIGITS: int = 5
M_DIGITS: int = 3
SIGMA_DIGITS: int = 1

# Messages
ERR_MUST_LOAD = "Most load data with load_ids or load_all before accessing this attribute."


class ShearBiasDataLoader():
    """ Class to load in needed data for shear bias data processing.
    """

    # Attributes set directly at init
    l_filenames: Sequence[str]
    workdir: str
    method: ShearEstimationMethods

    # Attributes determined at init
    _table_loader: BinnedMultiTableLoader
    _sem_tf: SheTableFormat

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
                 method: ShearEstimationMethods):

        # Set attributes from args
        self.l_filenames = l_filenames
        self.workdir = workdir
        self.method = method

        # Create a table loader with this list of filenames
        self._table_loader = BinnedMultiTableLoader(l_filenames=self.l_filenames,
                                                    workdir=self.workdir)

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
    def __clear(self):
        if self.table_loaded:
            self.table_loaded = False
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

    # Public loading methods

    def load_ids(self,
                 l_ids: Sequence[int],
                 *args, **kwargs) -> None:
        self.__clear()
        self.table = self.get_ids(l_ids=l_ids, *args, **kwargs)
        self.table_loaded = True

    def load_all(self, *args, **kwargs):
        self.__clear()
        self.table = self.get_all(*args, **kwargs)
        self.table_loaded = True

    def load_for_bin_constraint(self,
                                bin_constraint: BinConstraint,
                                *args, **kwargs):
        self.__clear()
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


class ShearBiasTestCaseDataProcessor():
    """ Class to handle and perform calculations for an individual Shear Bias Test Case.
    """

    # Attributes with fixed values
    bootstrap_seed: int = 12345
    n_bootstrap: int = 1000

    # Attributes set directly at init
    data_loader: ShearBiasDataLoader
    test_case_info: TestCaseInfo
    bootstrap_errors: bool = False
    max_g_in: float = 1.0

    # Attributes determined at init
    method: ShearEstimationMethods
    bin_parameter: BinParameters

    # Intermediate attributes set when loading data
    bin_index: Optional[int] = None
    gal_matched_table: Table

    # Intermediate attributes determined when processing data
    _sem_tf: SheTableFormat
    _good_rows: Sequence[bool]
    _fitclass_zero_rows: Sequence[bool]

    # Output attributes
    _d_g_in: Optional[Dict[int, Sequence[float]]] = None
    _d_g_out: Optional[Dict[int, Sequence[float]]] = None
    _d_g_out_err: Optional[Dict[int, Sequence[float]]] = None
    _d_bias_measurements: Optional[Dict[int, BiasMeasurements]] = None
    _d_linregress_results: Optional[Dict[int, LinregressResults]] = None
    _d_bias_strings: Optional[Dict[str, str]] = None

    def __init__(self,
                 data_loader: ShearBiasDataLoader,
                 test_case_info: TestCaseInfo,
                 bin_index: int = 0,
                 pipeline_config: Optional[Dict[ConfigKeys, Any]] = None,) -> None:

        # Set attrs directly
        self.data_loader = data_loader
        self.test_case_info = test_case_info
        if pipeline_config:
            self.bootstrap_errors = pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS]
            self.max_g_in = pipeline_config[ValidationConfigKeys.SBV_MAX_G_IN]

        # Sanity check on method
        assert self.test_case_info.method == self.data_loader.method

        # Get values from the test_case_info
        self.method = test_case_info.method
        self.bin_parameter = test_case_info.bin_parameter
        self.bin_index = bin_index

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
    def d_bias_measurements(self) -> Dict[int, BiasMeasurements]:
        if not self._d_bias_measurements:
            self.calc()
        return self._d_bias_measurements

    @d_bias_measurements.setter
    def d_bias_measurements(self, d_bias_measurements) -> None:
        self._d_bias_measurements = d_bias_measurements

    @property
    def d_linregress_results(self) -> Dict[int, LinregressResults]:
        if not self._d_linregress_results:
            self.calc()
        return self._d_linregress_results

    @property
    def d_bias_strings(self) -> Dict[str, str]:
        if not self._d_bias_strings:
            self.calc()
        return self._d_bias_strings

    @d_bias_strings.setter
    def d_bias_strings(self, d_bias_strings) -> None:
        self._d_bias_strings = d_bias_strings

    # Private methods

    def _calc_component_shear_bias(self,
                                   i: int):
        """ Calculate shear bias for an individual component.
        """

        # Get data limited to the rows where g_in is less than the allowed max
        g = np.sqrt(self.d_g_in[1]**2 + self.d_g_in[2]**2)
        good_g_in_rows = g < self.max_g_in

        g_in = self.d_g_in[i][good_g_in_rows]
        g_out = self.d_g_out[i][good_g_in_rows]
        g_out_err = self.d_g_out_err[i][good_g_in_rows]

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

        self._d_linregress_results[i] = linregress_results

        bias = BiasMeasurements(linregress_results)
        self._d_bias_measurements[i] = bias

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Bias measurements for method {self.method.value}:")
        if self._d_bias_strings is None:
            self._d_bias_strings = {}
        for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
            self._d_bias_strings[f"{a}{i}"] = (f"{a}{i} = {getattr(bias,a):.{d}f} +/- {getattr(bias,f'{a}_err'):.{d}f} "
                                               f"({getattr(bias,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(self._d_bias_strings[f"{a}{i}"])

    # Public methods

    def load_all(self, *args, **kwargs) -> None:
        self.data_loader.load_all(*args, **kwargs)

    def load_ids(self,
                 l_ids: Sequence[int],
                 *args, **kwargs) -> None:
        self.data_loader.load_ids(l_ids=l_ids, *args, **kwargs)

    def calc(self) -> None:
        """ Performs data processing, calculating bias measurements and other output data.
        """

        # Init empty dicts for intermediate data used when plotting
        self._d_bias_measurements: Dict[int, BiasMeasurements] = {}

        # Init empty dicts for output data
        self._d_linregress_results = {}
        self._d_bias_measurements = {}

        for i in (1, 2):

            self._calc_component_shear_bias(i)
