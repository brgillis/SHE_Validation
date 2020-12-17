""" @file results_reporting_test.py

    Created 17 December 2020

    Unit tests of the results_reporting.py module
"""
from collections import namedtuple

__updated__ = "2020-12-17"

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

import pytest

from SHE_PPT import products
from SHE_PPT.logging import getLogger
from SHE_Validation_CTI import constants
from SHE_Validation_CTI.results_reporting import fill_cti_gal_validation_results
from SHE_Validation_CTI.table_formats.regression_results import tf as rr_tf, initialise_regression_results_table
import numpy as np


class TestCase:
    """


    """

    @classmethod
    def setup_class(cls):

        return

    @classmethod
    def teardown_class(cls):

        return

    def test_fill_cti_gal_validation_results(self):
        """ Test of the fill_cti_gal_validation_results function.
        """

        RegResults = namedtuple("RegResults", ["slope", "slope_err",
                                               "intercept", "intercept_err", ])

        exp_results_list = [RegResults(3., 2., 0., 2.),
                            RegResults(-15, 2., 0., 2.),
                            RegResults(3., 2., 44., 5.),
                            RegResults(-15., 2., 44., 5.),
                            RegResults(-15., 0., 44., 0.),
                            RegResults(np.NaN, np.NaN, np.NaN, np.NaN), ]

        num_exposures = len(exp_results_list)
        exp_product_list = [None] * num_exposures

        # Set up mock input data and fill the products for each set of possible results
        exp_results_table = initialise_regression_results_table(product_type="EXP", size=len(exp_results_list))
        for exp_index, exp_results in enumerate(exp_results_list):
            exp_row = exp_results_table[exp_index]
            exp_row[getattr(rr_tf, "slope_LensMC")] = exp_results.slope
            exp_row[getattr(rr_tf, "slope_err_LensMC")] = exp_results.slope_err
            exp_row[getattr(rr_tf, "intercept_LensMC")] = exp_results.intercept
            exp_row[getattr(rr_tf, "intercept_err_LensMC")] = exp_results.intercept_err

            exp_product = products.she_validation_test_results.create_validation_test_results_product(
                num_tests=constants.num_method_cti_gal_test_cases)

            fill_cti_gal_validation_results(test_result_product=exp_product,
                                            regression_results_row=exp_row,
                                            method_data_exists=True)

            exp_product_list[exp_index] = exp_product

        # With the observation, test saying we have no data
        obs_results_table = initialise_regression_results_table(product_type="OBS", size=1)
        obs_row = obs_results_table[0]

        obs_product = products.she_validation_test_results.create_validation_test_results_product(
            num_tests=constants.num_method_cti_gal_test_cases)

        fill_cti_gal_validation_results(test_result_product=obs_product,
                                        regression_results_row=obs_row,
                                        method_data_exists=False)

        # Check that the product validates its binding
        obs_product.validateBinding()

        # Check metadata for the product

        # Check that the product indeed reports no data
        obs_test_result = obs_product.Data.ValidationTestList[0]
        assert obs_test_result.GlobalResult == "PASSED"
        assert obs_test_result.ValidatedRequirements.Requirement[0].Comment == "WARNING: Test not run."
        obs_info = obs_test_result.ValidatedRequirements.Requirement[0].SupplementaryInformation
        assert obs_info.Parameter[0].Key == "REASON"
        assert obs_info.Parameter[0].Description == "Why the test was not run."
        assert obs_info.Parameter[0].StringValue == "No data is available for this test."

        return
