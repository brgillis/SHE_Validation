""" @file data_processing.py

    Created 8 July 2021

    Code to process data for shear bias validation tests
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
from typing import Dict, List, Sequence, Optional, Any

from SHE_PPT.constants.shear_estimation_methods import (ShearEstimationMethods,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS)
from SHE_PPT.logging import getLogger
from SHE_PPT.math import BiasMeasurements, linregress_with_errors,\
    LinregressResults
from SHE_PPT.pipeline_utility import ValidationConfigKeys, ConfigKeys
from SHE_PPT.table_utility import SheTableFormat
from astropy.table import Column, Table

from SHE_Validation.constants.default_config import DEFAULT_BIN_LIMITS
from SHE_Validation.constants.test_info import TestCaseInfo, BinParameters
from SHE_Validation_ShearBias.constants.shear_bias_default_config import D_SHEAR_BIAS_CONFIG_DEFAULTS
import numpy as np

logger = getLogger(__name__)

# Data display constants
C_DIGITS: int = 5
M_DIGITS: int = 3
SIGMA_DIGITS: int = 1


class ShearBiasTestCaseDataProcessor():
    """ Class to handle and perform calculations for an individual Shear Bias Test Case.
    """

    # Attributes with fixed values
    bootstrap_seed: int = 12345
    n_bootstrap: int = 1000

    # Attributes set directly at init
    gal_matched_table: Table
    workdir: str
    test_case_info: TestCaseInfo
    bin_limits: Sequence[float] = DEFAULT_BIN_LIMITS
    pipeline_config: Optional[Dict[ConfigKeys, Any]] = D_SHEAR_BIAS_CONFIG_DEFAULTS

    # Attributes calculated at init
    method: ShearEstimationMethods
    bin_parameter: BinParameters

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
                 l_method_matched_catalog_filenames: List[str],
                 test_case_info: TestCaseInfo,
                 workdir: str,
                 bin_limits: Optional[Sequence[float]] = None,
                 pipeline_config: Optional[Dict[ConfigKeys, Any]] = None,) -> None:

        # Set attrs directly
        self.l_method_matched_catalog_filenames = l_method_matched_catalog_filenames
        self.test_case_info = test_case_info
        self.workdir = workdir
        if bin_limits:
            self.bin_limits = bin_limits
        self.pipeline_config = pipeline_config

        # Get values from the test_case_info
        self.method = test_case_info.method
        self.bin_parameter = test_case_info.bin_parameter

    # Getters and setters for output attributes, which calculate if needed

    @property
    def d_g_in(self) -> Dict[int, Sequence[float]]:
        if not self._d_g_in:
            self.calc()
        return self._d_g_in

    @d_g_in.setter
    def d_g_in(self, d_g_in) -> None:
        self._d_g_in = d_g_in

    @property
    def d_g_out(self) -> Dict[int, Sequence[float]]:
        if not self._d_g_out:
            self.calc()
        return self._d_g_out

    @d_g_out.setter
    def d_g_out(self, d_g_out) -> None:
        self._d_g_out = d_g_out

    @property
    def d_g_out_err(self) -> Dict[int, Sequence[float]]:
        if not self._d_g_out_err:
            self.calc()
        return self._d_g_out_err

    @d_g_out_err.setter
    def d_g_out_err(self, d_g_out_err) -> None:
        self._d_g_out_err = d_g_out_err

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

    def _load_data(self):
        """ Initializes and loads in data we'll be calculating.
        """

        # Init empty dicts for intermediate data used when plotting
        self._d_bias_measurements: Dict[int, BiasMeasurements] = {}

        # Determine attrs from kwargs
        self._sem_tf: SheTableFormat = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[self.method]

        # Read in each table and get the data we need out of it
        l_g1_in: List[Column] = []
        l_g2_in: List[Column] = []
        l_g1_out: List[Column] = []
        l_g2_out: List[Column] = []
        l_g1_out_err: List[Column] = []
        l_g2_out_err: List[Column] = []
        l_fitclass_zero_rows: List[Sequence[bool]] = []

        method_matched_catalog_filename: str
        for method_matched_catalog_filename in self.l_method_matched_catalog_filenames:

            if method_matched_catalog_filename is None:
                continue

            qualified_method_matched_catalog_filename: str = os.path.join(self.workdir, method_matched_catalog_filename)
            logger.info(
                f"Reading in matched catalog for method {self.method} from {qualified_method_matched_catalog_filename}.")

            gal_matched_table: Table = Table.read(qualified_method_matched_catalog_filename, hdu=1)
            self._good_rows: Sequence[bool] = gal_matched_table[self._sem_tf.fit_flags] == 0

            l_g1_in.append(-(gal_matched_table[self._sem_tf.tu_gamma1] /
                             (1 - gal_matched_table[self._sem_tf.tu_kappa]))[self._good_rows])
            l_g2_in.append((gal_matched_table[self._sem_tf.tu_gamma2] /
                            (1 - gal_matched_table[self._sem_tf.tu_kappa]))[self._good_rows])
            l_g1_out.append((gal_matched_table[self._sem_tf.g1])[self._good_rows])
            l_g2_out.append((gal_matched_table[self._sem_tf.g2])[self._good_rows])
            l_g1_out_err.append((gal_matched_table[self._sem_tf.g1_err])[self._good_rows])
            l_g2_out_err.append((gal_matched_table[self._sem_tf.g2_err])[self._good_rows])
            l_fitclass_zero_rows.append((gal_matched_table[self._sem_tf.fit_class] == 0)[self._good_rows])

        # Check if we have some data, otherwise use empty arrays
        if len(l_g1_in) > 0:
            self._d_g_in = {1: np.concatenate(l_g1_in), 2: np.concatenate(l_g2_in)}
            self._d_g_out = {1: np.concatenate(l_g1_out),
                             2: np.concatenate(l_g2_out)}
            self._d_g_out_err = {1: np.concatenate(l_g1_out_err),
                                 2: np.concatenate(l_g2_out_err)}
            self._fitclass_zero_rows = np.concatenate(l_fitclass_zero_rows)
        else:
            self._d_g_in = {1: np.array([], dtype=float),
                            2: np.array([], dtype=float)}
            self._d_g_out = {1: np.array([], dtype=float),
                             2: np.array([], dtype=float)}
            self._d_g_out_err = {1: np.array([], dtype=float),
                                 2: np.array([], dtype=float)}
            self._fitclass_zero_rows = np.array([], dtype=bool)

        # Init empty dicts for output data
        self._d_linregress_results = {}
        self._d_bias_measurements = {}

    def _calc_component_shear_bias(self,
                                   i: int,
                                   bootstrap_errors: bool,
                                   require_fitclass_zero: bool,
                                   max_g_in: float):
        """ Calculate shear bias for an individual component.
        """

        # Get data limited to the rows where g_in is less than the allowed max
        g = np.sqrt(self.d_g_in[1]**2 + self.d_g_in[2]**2)
        good_g_in_rows = g < max_g_in

        g_in = self.d_g_in[i][good_g_in_rows]
        g_out = self.d_g_out[i][good_g_in_rows]
        g_out_err = self.d_g_out_err[i][good_g_in_rows]

        # Limit to FITCLASS==0 if desired
        if require_fitclass_zero:
            good_fitclass_zero_rows = self._fitclass_zero_rows[good_g_in_rows]
            g_in = g_in[good_fitclass_zero_rows]
            g_out = g_out[good_fitclass_zero_rows]
            g_out_err = g_out_err[good_fitclass_zero_rows]

        # Perform the linear regression, calculate bias, and save it in the bias dict
        if not bootstrap_errors:

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
        self.d_bias_measurements[i] = bias

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Bias measurements for method {self.method.value}:")
        self.d_bias_strings = {}
        for a, d in ("c", C_DIGITS), ("m", M_DIGITS):
            self.d_bias_strings[f"{a}{i}"] = f"{a}{i} = {getattr(bias,a):.{d}f} +/- {getattr(bias,f'{a}_err'):.{d}f} "\
                f"({getattr(bias,f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)"
            logger.info(self.d_bias_strings[f"{a}{i}"])

    def _calc_shear_bias(self):
        """ Plot shear bias for both components.
        """

        bootstrap_errors = self.pipeline_config[ValidationConfigKeys.SBV_BOOTSTRAP_ERRORS]
        require_fitclass_zero = self.pipeline_config[ValidationConfigKeys.SBV_REQUIRE_FITCLASS_ZERO]
        max_g_in = self.pipeline_config[ValidationConfigKeys.SBV_MAX_G_IN]

        for i in (1, 2):

            self._calc_component_shear_bias(i,
                                            bootstrap_errors=bootstrap_errors,
                                            require_fitclass_zero=require_fitclass_zero,
                                            max_g_in=max_g_in)

    # Public methods

    def calc(self) -> None:
        """ Performs data processing, calculating bias measurements and other output data.
        """

        self._load_data()

        self.calc_shear_bias()
