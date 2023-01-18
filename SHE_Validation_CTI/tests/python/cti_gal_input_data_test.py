"""
:file: tests/python/cti_gal_input_data_test.py

:date: 14 December 2020
:author: Bryan Gillis

Unit tests of the input_data.py module
"""

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
from copy import deepcopy

import numpy as np
from astropy.table import Table

from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS, ShearEstimationMethods
from SHE_PPT.constants.test_data import LENSMC_MEASUREMENTS_TABLE_FILENAME
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.testing.utility import SheTestCase
from SHE_PPT.utility import is_nan_or_masked
from SHE_Validation_CTI.input_data import (PositionInfo, ShearEstimate, SingleObjectData, get_raw_cti_gal_object_data,
                                           sort_raw_object_data_into_table, )
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF


class TestCtiGalInput(SheTestCase):
    """ Unit tests for loading CTI validation input data.
    """

    def setup_workdir(self):

        self._download_datastack()
        self._download_mdb()

        # Set up some expected values
        self.EX_BG_LEVEL = 45.71

    def test_get_raw_cgo_data(self, local_setup):

        # Read in the mock shear estimates
        lmcm_tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[ShearEstimationMethods.LENSMC]
        lensmc_shear_estimates_table = Table.read(os.path.join(
            self.workdir, "data", LENSMC_MEASUREMENTS_TABLE_FILENAME))
        d_shear_estimates_tables = {ShearEstimationMethods.KSB: None,
                                    ShearEstimationMethods.LENSMC: lensmc_shear_estimates_table,
                                    ShearEstimationMethods.MOMENTSML: None,
                                    ShearEstimationMethods.REGAUSS: None}

        raw_cti_gal_object_data = get_raw_cti_gal_object_data(data_stack=self.data_stack,
                                                              d_shear_estimate_tables=d_shear_estimates_tables)

        # Check the results

        # Check the general attributes of the list
        assert len(raw_cti_gal_object_data) == len(lensmc_shear_estimates_table)

        # Order of IDs isn't guaranteed, so we have to check that we have the right IDs in a roundabout way
        assert raw_cti_gal_object_data[0].id in lensmc_shear_estimates_table[lmcm_tf.ID]
        assert raw_cti_gal_object_data[1].id in lensmc_shear_estimates_table[lmcm_tf.ID]
        assert raw_cti_gal_object_data[0].id != raw_cti_gal_object_data[1].id

        lensmc_shear_estimates_table.add_index(lmcm_tf.ID)

        # Check the info is correct for each object
        for object_data in raw_cti_gal_object_data:

            # Get the corresponding LensMC row for this object
            lmcm_row = lensmc_shear_estimates_table.loc[object_data.id]

            # Check that the world shear info is correct

            lensmc_world_shear_info = object_data.world_shear_info[ShearEstimationMethods.LENSMC]
            assert lensmc_world_shear_info.g1 == lmcm_row[lmcm_tf.g1]
            assert lensmc_world_shear_info.g2 == lmcm_row[lmcm_tf.g2]
            assert lensmc_world_shear_info.weight == lmcm_row[lmcm_tf.weight]

            assert is_nan_or_masked(object_data.world_shear_info[ShearEstimationMethods.KSB].g1)
            assert is_nan_or_masked(object_data.world_shear_info[ShearEstimationMethods.MOMENTSML].g1)
            assert is_nan_or_masked(object_data.world_shear_info[ShearEstimationMethods.REGAUSS].g1)

            # Check the shear info for each exposure
            ministamp_stack = self.data_stack.extract_galaxy_stack(object_data.id, width=1)

            ra = self.data_stack.detections_catalogue.loc[object_data.id][mfc_tf.gal_x_world]
            dec = self.data_stack.detections_catalogue.loc[object_data.id][mfc_tf.gal_y_world]

            num_exposures = len(ministamp_stack.exposures)
            for exp_index in range(num_exposures):
                ministamp = ministamp_stack.exposures[exp_index]
                position_info = object_data.position_info[exp_index]

                x_pix_stamp, y_pix_stamp = ministamp.world2pix(ra, dec)

                assert np.isclose(int(position_info.x_pix), ministamp.offset[0])
                assert np.isclose(int(position_info.y_pix), ministamp.offset[1])
                assert np.isclose(position_info.x_pix, ministamp.offset[0] + x_pix_stamp)
                assert np.isclose(position_info.y_pix, ministamp.offset[1] + y_pix_stamp)

                assert position_info.det_ix == 1
                assert position_info.det_iy == 1
                assert position_info.quadrant == "E"

                lensmc_exposure_shear_info = position_info.exposure_shear_info[ShearEstimationMethods.LENSMC]

                # No rotation here, so all shear values should be the same as the world value
                assert lensmc_exposure_shear_info.g1 == lmcm_row[lmcm_tf.g1]
                assert lensmc_exposure_shear_info.g2 == lmcm_row[lmcm_tf.g2]
                assert lensmc_exposure_shear_info.weight == lmcm_row[lmcm_tf.weight]

                assert is_nan_or_masked(position_info.exposure_shear_info[ShearEstimationMethods.KSB].g1)
                assert is_nan_or_masked(position_info.exposure_shear_info[ShearEstimationMethods.MOMENTSML].g1)
                assert is_nan_or_masked(position_info.exposure_shear_info[ShearEstimationMethods.REGAUSS].g1)

    def test_sort_raw_object_data(self):

        # Set up test data
        l_raw_object_data = []
        num_exposures = 4

        dx_dexp = 100
        dy_dexp = 200
        dg1_dexp = -0.01
        dg2_dexp = 0.02
        dweight_dexp = 1

        id_0 = self.data_stack.detections_catalogue[mfc_tf.ID][0]
        id_1 = self.data_stack.detections_catalogue[mfc_tf.ID][0]

        for object_id, x, y, g1, g2, weight, fvis, fvis_err, fnir, area in ((id_0, 128, 129, 0.1, 0.3, 10,
                                                                             100., 10., 200., 50),
                                                                            (id_1, 2000, 2000, -0.1, 0.2, 11,
                                                                             150., 20., 150., 100)):

            data_stack_copy = deepcopy(self.data_stack)

            detections_row = data_stack_copy.detections_catalogue.loc[object_id]

            # Set up a mock detections row using a dictionary
            detections_row[mfc_tf.FLUX_VIS_APER] = fvis
            detections_row[mfc_tf.FLUXERR_VIS_APER] = fvis_err
            detections_row[mfc_tf.FLUX_NIR_STACK_APER] = fnir
            detections_row[mfc_tf.SEGMENTATION_AREA] = area

            object_data = SingleObjectData(object_id=object_id,
                                           num_exposures=num_exposures, )

            object_data.world_shear_info[ShearEstimationMethods.LENSMC] = ShearEstimate(g1=g1,
                                                                                        g2=g2,
                                                                                        weight=weight)
            object_data.world_shear_info[ShearEstimationMethods.KSB] = ShearEstimate()
            object_data.world_shear_info[ShearEstimationMethods.MOMENTSML] = ShearEstimate()
            object_data.world_shear_info[ShearEstimationMethods.REGAUSS] = ShearEstimate()

            for exp_index in range(num_exposures):
                position_info = PositionInfo()
                position_info.x_pix = x + dx_dexp * exp_index
                position_info.y_pix = y + dy_dexp * exp_index
                position_info.exposure_shear_info[ShearEstimationMethods.LENSMC] = ShearEstimate(
                    g1=g1 + dg1_dexp * exp_index,
                    g2=g2 + dg2_dexp * exp_index,
                    weight=weight + dweight_dexp * exp_index)
                object_data.position_info[exp_index] = position_info

            l_raw_object_data.append(object_data)

        object_data_table_list = sort_raw_object_data_into_table(l_raw_object_data=l_raw_object_data)

        # Check that the tables are as expected
        for exp_index, object_data_table in enumerate(object_data_table_list):

            for object_data, row in zip(l_raw_object_data, object_data_table):

                assert object_data.id == row[CGOD_TF.ID]

                assert np.isclose(object_data.position_info[exp_index].x_pix, row[CGOD_TF.x])
                assert np.isclose(object_data.position_info[exp_index].y_pix, row[CGOD_TF.y])
                assert np.isclose(
                    object_data.position_info[exp_index].exposure_shear_info[ShearEstimationMethods.LENSMC].g1,
                    row[getattr(CGOD_TF, "g1_image_LensMC")])
                assert np.isclose(
                    object_data.position_info[exp_index].exposure_shear_info[ShearEstimationMethods.LENSMC].g2,
                    row[getattr(CGOD_TF, "g2_image_LensMC")])
                assert np.isclose(
                    object_data.position_info[exp_index].exposure_shear_info[ShearEstimationMethods.LENSMC].weight,
                    row[getattr(CGOD_TF, "weight_LensMC")])
