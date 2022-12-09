""" @file mock_pipeline_config.py

    Created 8 October 2021.

    Utilities to generate, write, read, and cleanup mock pipeline configs for unit tests.
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

import os
from typing import Any, Dict, Optional

import numpy as np

from SHE_PPT.constants.config import ConfigKeys
from SHE_PPT.logging import getLogger
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory
from .constants import DEFAULT_GLOBAL_FAIL_SIGMA, DEFAULT_LOCAL_FAIL_SIGMA, DEFAULT_MOCK_BIN_LIMITS
from ..constants.default_config import DEFAULT_AUTO_BIN_LIMITS, D_VALIDATION_CONFIG_DEFAULTS, ValidationConfigKeys
from ..constants.test_info import BinParameters, D_BIN_PARAMETER_META

logger = getLogger(__name__)


class MockValPipelineConfigFactory(MockPipelineConfigFactory):
    """TODO: Add docstring for this class."""

    # Attributes to override from parent class
    _config_keys = ValidationConfigKeys
    _config_defaults = D_VALIDATION_CONFIG_DEFAULTS

    # Input values with defaults
    _test_bin_parameter: BinParameters = BinParameters.SNR
    _mock_bin_limits: np.ndarray = np.array(DEFAULT_MOCK_BIN_LIMITS)
    _local_fail_sigma: float = DEFAULT_LOCAL_FAIL_SIGMA
    _global_fail_sigma: float = DEFAULT_GLOBAL_FAIL_SIGMA

    # Generated values
    _d_l_bin_limits: Optional[Dict[BinParameters, np.ndarray]] = None

    # Getters and setters for input properties

    @property
    def test_bin_parameter(self) -> BinParameters:
        return self.test_bin_parameter

    @test_bin_parameter.setter
    def test_bin_parameter(self, value) -> None:
        self._test_bin_parameter = value
        self._decache()

    @property
    def mock_bin_limits(self) -> np.ndarray:
        return self.mock_bin_limits

    @mock_bin_limits.setter
    def mock_bin_limits(self, value) -> None:
        self._mock_bin_limits = value
        self._decache()

    @property
    def local_fail_sigma(self) -> float:
        return self.local_fail_sigma

    @local_fail_sigma.setter
    def local_fail_sigma(self, value) -> None:
        self._local_fail_sigma = value
        self._decache()

    @property
    def global_fail_sigma(self) -> float:
        return self.global_fail_sigma

    @global_fail_sigma.setter
    def global_fail_sigma(self, value) -> None:
        self._global_fail_sigma = value
        self._decache()

    @property
    def d_l_bin_limits(self) -> Dict[BinParameters, np.ndarray]:
        if self._d_l_bin_limits is None:
            self._d_l_bin_limits = self._make_d_l_bin_limits()
        return self._d_l_bin_limits

    # Private and protected methods

    def _decache(self):
        super()._decache()
        self._d_l_bin_limits = None

    def _make_d_l_bin_limits(self) -> Dict[BinParameters, np.ndarray]:
        d_l_bin_limits: Dict[BinParameters, np.ndarray] = {}
        for bin_parameter in BinParameters:
            if bin_parameter == self._test_bin_parameter:
                d_l_bin_limits[bin_parameter] = np.array(self._mock_bin_limits)
            else:
                d_l_bin_limits[bin_parameter] = DEFAULT_AUTO_BIN_LIMITS

        return d_l_bin_limits

    def _make_pipeline_config(self, ) -> Dict[ConfigKeys, Any]:
        """ Create and return a mock pipeline config dict.
        """

        config_dict = super()._make_pipeline_config()

        config_dict[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA] = self._local_fail_sigma
        config_dict[ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA] = self._global_fail_sigma

        # Set modified bin limits in the dict
        for bin_parameter in BinParameters:
            config_key = D_BIN_PARAMETER_META[bin_parameter].config_key
            if bin_parameter == BinParameters.TOT or bin_parameter == BinParameters.EPOCH:
                continue
            else:
                config_dict[config_key] = self.d_l_bin_limits[bin_parameter]

        return config_dict

    # Public methods

    def cleanup(self):
        super().cleanup()
        os.remove(os.path.join(self.file_namer.qualified_filename))
