""" @file mock_data.py

    Created 15 October 2021.

    Utilities to generate mock data for validation tests.
"""

__updated__ = "2021-10-05"

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

from typing import Dict, List, Optional

import numpy as np

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS,
                                                        D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.detector import VIS_DETECTOR_PIXELS_X, VIS_DETECTOR_PIXELS_Y
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.mer_final_catalog import (MerFinalCatalogFormat, filter_list, filter_list_ext,
                                                     mer_final_catalog_format, )
from SHE_PPT.table_formats.she_measurements import SheMeasurementsFormat
from SHE_PPT.table_formats.she_star_catalog import SHE_STAR_CAT_TF, SheStarCatalogFormat
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat, she_tu_matched_table_format
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_NAN_TEST_POINTS, NUM_ZERO_WEIGHT_TEST_POINTS
from SHE_PPT.utility import default_init_if_none, default_value_if_none
from SHE_Validation.constants.default_config import (DEFAULT_BIN_LIMITS)
from SHE_Validation.constants.test_info import BinParameters

logger = getLogger(__name__)

# MFC info
MFC_SEED = 57632

# Input shear info
INPUT_G_MIN = -0.7
INPUT_G_MAX = 0.7

# Estimated shear info
EST_SEED = 6413
EST_G_ERR = 0.025
EXTRA_EST_G_ERR = 0.005
EXTRA_EST_G_ERR_ERR = 0.005

D_D_L_D_INPUT_BIAS: Dict[ShearEstimationMethods, Dict[BinParameters, List[Dict[str, float]]]] = {
    ShearEstimationMethods.LENSMC: {BinParameters.TOT: [{"m1"    : 0.05,
                                                         "m1_err": 0.015,
                                                         "c1"    : -0.2,
                                                         "c1_err": 0.05,
                                                         "m2"    : -0.1,
                                                         "m2_err": 0.04,
                                                         "c2"    : 0.01,
                                                         "c2_err": 0.003, }]},
    ShearEstimationMethods.KSB   : {BinParameters.SNR: [{"m1"    : 0.2,
                                                         "m1_err": 0.003,
                                                         "c1"    : -0.3,
                                                         "c1_err": 0.03,
                                                         "m2"    : 0.1,
                                                         "m2_err": 0.21,
                                                         "c2"    : -0.4,
                                                         "c2_err": 0.43, },
                                                        {"m1"    : -0.3,
                                                         "m1_err": 0.031,
                                                         "c1"    : -0.5,
                                                         "c1_err": 0.05,
                                                         "m2"    : 0.35,
                                                         "m2_err": 0.15,
                                                         "c2"    : 0.,
                                                         "c2_err": 0.1,
                                                         }]}}


class MockMFCDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock MER Final Catalog data.
    """

    # Overring base class default values
    tf: MerFinalCatalogFormat = mer_final_catalog_format
    seed: int = MFC_SEED

    FLUX_MIN: float = 100
    FLUX_MAX: float = 10000

    F_FLUX_ERR_MIN: float = 0.01
    F_FLUX_ERR_MAX: float = 0.50

    BG_MIN: float = 20
    BG_MAX: float = 60

    SIZE_MIN: float = 20
    SIZE_MAX: float = 330

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        # Deterministic data
        self.data[self.tf.ID] = self._indices
        self.data[self.tf.seg_ID] = self._indices
        self.data[self.tf.vis_det] = np.ones(self.num_test_points)

        # Randomly-generated data
        self.data[self.tf.gal_x_world] = self._rng.uniform(0., 360., self.num_test_points)
        self.data[self.tf.gal_y_world] = self._rng.uniform(-180., 180., self.num_test_points)

        for f in filter_list_ext + filter_list + ["NIR_STACK"]:
            flux = self._rng.uniform(self.FLUX_MIN, self.FLUX_MAX, self.num_test_points)
            self.data["FLUX_%s_APER" % f] = flux
            self.data["FLUXERR_%s_APER" % f] = flux * self._rng.uniform(self.F_FLUX_ERR_MIN,
                                                                        self.F_FLUX_ERR_MAX,
                                                                        self.num_test_points)

        self.data[self.tf.SEGMENTATION_AREA] = self._rng.uniform(self.SIZE_MIN, self.SIZE_MAX, self.num_test_points)
        self.data[self.tf.bg] = self._rng.uniform(self.BG_MIN, self.BG_MAX, self.num_test_points)


class MockTUGalaxyDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock galaxy catalog data.
    """

    # Overring base class default values
    tf: SheTUMatchedFormat = she_tu_matched_table_format
    seed: int = 3513

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        self.data[self.tf.ID] = self._indices

        # Fill in input data
        self.data[self.tf.tu_gamma1] = -np.linspace(INPUT_G_MIN, INPUT_G_MAX, self.num_test_points)
        self.data[self.tf.tu_gamma2] = np.linspace(INPUT_G_MAX, INPUT_G_MIN, self.num_test_points)
        self.data[self.tf.tu_kappa] = np.zeros_like(self.data[self.tf.tu_gamma1])

        # Fill in data for bin parameter info, with different bins for each parameter

        i: int
        bin_parameter: BinParameters
        for i, bin_parameter in enumerate(BinParameters):
            if bin_parameter == BinParameters.TOT:
                continue
            factor = 2 ** i
            self.data[bin_parameter.name] = np.where(self._indices % factor < factor / 2, self._ones, self._zeros)


class MockShearEstimateDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock shear estimates data.
    """

    # Overring base class default values
    tf: SheMeasurementsFormat
    seed: int = 75275

    # New attributes for this subclass
    mock_tu_galaxy_data_generator: MockTUGalaxyDataGenerator
    method: ShearEstimationMethods
    num_nan_test_points: int = NUM_NAN_TEST_POINTS
    num_zero_weight_test_points: int = NUM_ZERO_WEIGHT_TEST_POINTS
    num_good_test_points: int

    # Attributes used while generating data
    _tu_data: Optional[Dict[str, np.ndarray]] = None
    _tu_tf: Optional[SheTUMatchedFormat] = None

    def __init__(self,
                 method: ShearEstimationMethods,
                 mock_tu_galaxy_data_generator: Optional[MockTUGalaxyDataGenerator] = None,
                 num_nan_test_points: Optional[int] = NUM_NAN_TEST_POINTS,
                 num_zero_weight_test_points: Optional[int] = NUM_ZERO_WEIGHT_TEST_POINTS,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]

        # Init the data generator
        self.mock_tu_galaxy_data_generator = default_init_if_none(mock_tu_galaxy_data_generator,
                                                                  type = MockTUGalaxyDataGenerator)

        # Init and check the numbers of test points
        self.num_test_points = self.mock_tu_galaxy_data_generator.num_test_points
        self.num_nan_test_points = default_value_if_none(num_nan_test_points, self.num_nan_test_points)
        self.num_zero_weight_test_points = default_value_if_none(num_zero_weight_test_points, self.num_nan_test_points)
        self.num_good_test_points = self.num_test_points - self.num_nan_test_points - self.num_zero_weight_test_points
        assert self.num_test_points >= self.num_good_test_points > 0

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        self.data[self.tf.ID] = self._indices

        # Get the TU data generator and table format
        self._tu_data = self.mock_tu_galaxy_data_generator.get_data()
        self._tu_tf = self.mock_tu_galaxy_data_generator.tf

        self.data[self.tf.ID] = self._indices

        # Generate random noise for output data
        l_extra_g_err = EXTRA_EST_G_ERR + EXTRA_EST_G_ERR_ERR * self._rng.standard_normal(self.num_test_points)
        l_g_err = np.sqrt(EST_G_ERR ** 2 + l_extra_g_err ** 2)
        l_g1_deviates = l_g_err * self._rng.standard_normal(self.num_test_points)
        l_g2_deviates = l_g_err * self._rng.standard_normal(self.num_test_points)

        # Save the error in the table
        self.data[self.tf.g1_err] = l_g_err
        self.data[self.tf.g2_err] = l_g_err
        self.data[self.tf.weight] = 0.5 * l_g_err ** -2

        # Fill in rows with mock output data - this bit depends on which method we're using
        d_l_d_method_input_bias = D_D_L_D_INPUT_BIAS[self.method]
        if self.method == ShearEstimationMethods.LENSMC:
            d_bias_0m2 = d_l_d_method_input_bias[BinParameters.TOT][0]
            d_bias_1m2 = d_l_d_method_input_bias[BinParameters.TOT][0]
        else:
            d_bias_0m2 = d_l_d_method_input_bias[BinParameters.SNR][0]
            d_bias_1m2 = d_l_d_method_input_bias[BinParameters.SNR][1]

        g1_0m2 = d_bias_0m2["c1"] + (1 + d_bias_0m2["m1"]) * -self._tu_data[self._tu_tf.tu_gamma1] + l_g1_deviates
        g1_1m2 = d_bias_1m2["c1"] + (1 + d_bias_1m2["m1"]) * -self._tu_data[self._tu_tf.tu_gamma1] + l_g1_deviates

        g2_0m2 = d_bias_0m2["c2"] + (1 + d_bias_0m2["m2"]) * self._tu_data[self._tu_tf.tu_gamma2] + l_g2_deviates
        g2_1m2 = d_bias_1m2["c2"] + (1 + d_bias_1m2["m2"]) * self._tu_data[self._tu_tf.tu_gamma2] + l_g2_deviates

        # Add to table, flipping g1 due to SIM's format
        self.data[self.tf.g1] = np.where(self._indices % 2 < 1, g1_0m2, g1_1m2)
        self.data[self.tf.g2] = np.where(self._indices % 2 < 1, g2_0m2, g2_1m2)

        # Flag the last bit of data as bad or zero weight
        self.data[self.tf.g1][-self.num_nan_test_points - self.num_zero_weight_test_points:
                              -self.num_zero_weight_test_points] = np.NaN
        self.data[self.tf.g1_err][-self.num_nan_test_points - self.num_zero_weight_test_points:] = np.NaN
        self.data[self.tf.g2][-self.num_nan_test_points - self.num_zero_weight_test_points:
                              -self.num_zero_weight_test_points] = np.NaN
        self.data[self.tf.g2_err][-self.num_nan_test_points - self.num_zero_weight_test_points:] = np.NaN

        self.data[self.tf.g1_err][-self.num_zero_weight_test_points:] = np.inf
        self.data[self.tf.g2_err][-self.num_zero_weight_test_points:] = np.inf
        self.data[self.tf.weight][-self.num_zero_weight_test_points:] = 0

        # Set the fit flags
        self.data[self.tf.fit_flags] = np.where(self._indices < self.num_good_test_points, 0,
                                                np.where(self._indices < self.num_good_test_points +
                                                         self.num_nan_test_points,
                                                         1,
                                                         0))


class MockTUMatchedDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock TU Matched tables.
    """

    # Overring base class default values
    tf: SheTUMatchedFormat
    seed: int = 75275

    # New attributes for this subclass
    mock_tu_galaxy_data_generator: MockTUGalaxyDataGenerator
    mock_shear_estimate_data_generator: MockShearEstimateDataGenerator
    method: ShearEstimationMethods

    # Attributes used while generating data
    _tu_data: Optional[Dict[str, np.ndarray]] = None
    _se_data: Optional[Dict[str, np.ndarray]] = None

    def __init__(self,
                 method: ShearEstimationMethods,
                 mock_tu_galaxy_data_generator: Optional[MockTUGalaxyDataGenerator] = None,
                 num_nan_test_points: Optional[int] = NUM_NAN_TEST_POINTS,
                 num_zero_weight_test_points: Optional[int] = NUM_ZERO_WEIGHT_TEST_POINTS,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]

        # Init the data generators
        self.mock_tu_galaxy_data_generator = default_init_if_none(mock_tu_galaxy_data_generator,
                                                                  type = MockTUGalaxyDataGenerator)
        self.mock_shear_estimate_data_generator = MockShearEstimateDataGenerator(method = method,
                                                                                 mock_tu_galaxy_data_generator =
                                                                                 self.mock_tu_galaxy_data_generator,
                                                                                 num_nan_test_points =
                                                                                 num_nan_test_points,
                                                                                 num_zero_weight_test_points =
                                                                                 num_zero_weight_test_points)

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate data by combining the dicts from the two generators.
        """
        self._tu_data = self.mock_tu_galaxy_data_generator.get_data()
        self._se_data = self.mock_shear_estimate_data_generator.get_data()

        self.data = {**self.data, **self._tu_data, **self._se_data}


# Constants describing how to generate mock star data

STAR_CAT_SEED = 152314
STAR_CAT_POS_ERR_PIX = 0.2
STAR_CAT_PIXEL_SCALE = 0.1 / 3600
STAR_CAT_FLUX_MIN = 10
STAR_CAT_FLUX_MAX = 100
STAR_CAT_FLUX_ERR = 5
STAR_CAT_SIGMA_E = 0.2
STAR_CAT_E_ERR = 0.01
STAR_CAT_RES_CHISQ_MEAN = 1000
STAR_CAT_RES_CHISQ_ERR = 30
STAR_CAT_RES_CHISQ_DOF = 1000


class MockStarCatDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock star catalog data.
    """

    # Overring base class default values
    tf: SheStarCatalogFormat = SHE_STAR_CAT_TF
    seed: int = 3513

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate mock star data.
        """

        self.data[self.tf.id] = self._indices

        # Fill in catalog data

        # Detector position - random detector for each mock star
        self.data[self.tf.det_x] = self._rng.integers(low = 1, high = 6, size = self.num_test_points)
        self.data[self.tf.det_y] = self._rng.integers(low = 1, high = 6, size = self.num_test_points)

        # Position on detector - random uniform position
        self.data[self.tf.x] = self._rng.uniform(low = 0, high = VIS_DETECTOR_PIXELS_X, size = self.num_test_points)
        self.data[self.tf.y] = self._rng.uniform(low = 0, high = VIS_DETECTOR_PIXELS_Y, size = self.num_test_points)

        # Position on error - same for all
        self.data[self.tf.x_err] = STAR_CAT_POS_ERR_PIX * self._ones
        self.data[self.tf.y_err] = STAR_CAT_POS_ERR_PIX * self._ones

        # Sky position - use pixel-scale only WCS here for simplicity
        self.data[self.tf.ra] = -self.data[self.tf.x] * STAR_CAT_PIXEL_SCALE
        self.data[self.tf.dec] = self.data[self.tf.y] * STAR_CAT_PIXEL_SCALE
        self.data[self.tf.ra_err] = self.data[self.tf.x_err] * STAR_CAT_PIXEL_SCALE
        self.data[self.tf.dec_err] = self.data[self.tf.y_err] * STAR_CAT_PIXEL_SCALE

        # Uniform distribution for flux, fixed value for flux error
        self.data[self.tf.flux] = self._rng.uniform(low = STAR_CAT_FLUX_MIN, high = STAR_CAT_FLUX_MAX,
                                                    size = self.num_test_points)
        self.data[self.tf.flux_err] = STAR_CAT_FLUX_ERR * self._ones

        # Gaussian distributions for e1 and e2, fixed values for errors
        self.data[self.tf.e1] = self._rng.uniform(loc = 0, scale = STAR_CAT_SIGMA_E, size = self.num_test_points)
        self.data[self.tf.e2] = self._rng.uniform(loc = 0, scale = STAR_CAT_SIGMA_E, size = self.num_test_points)
        self.data[self.tf.e1_err] = STAR_CAT_E_ERR * self._ones
        self.data[self.tf.e2_err] = STAR_CAT_E_ERR * self._ones

        # All even-indexed used for fit
        self.data[self.tf.used_for_fit] = np.where(self._indices % 2 == 0, self._ones.astype(bool),
                                                   self._zeros.astype(bool))

        # Gaussian dist of chi-squared, fixed value for DOF
        self.data[self.tf.res_chisq] = self._rng.uniform(loc = STAR_CAT_RES_CHISQ_MEAN, scale = STAR_CAT_RES_CHISQ_ERR,
                                                         size = self.num_test_points)
        self.data[self.tf.dof] = STAR_CAT_RES_CHISQ_DOF * self._ones


def make_mock_bin_limits() -> Dict[BinParameters, np.ndarray]:
    """ Generate a mock dictionary of bin limits for testing.
    """

    d_l_bin_limits: Dict[BinParameters, np.ndarray] = {}
    for bin_parameter in BinParameters:
        if bin_parameter == BinParameters.SNR:
            d_l_bin_limits[bin_parameter] = np.array([-0.5, 0.5, 1.5])
        else:
            d_l_bin_limits[bin_parameter] = np.array(DEFAULT_BIN_LIMITS)

    return d_l_bin_limits
