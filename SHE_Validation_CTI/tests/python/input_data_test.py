""" @file input_data_test.py

    Created 14 December 2020

    Unit tests of the input_data.py module
"""
from copy import deepcopy

__updated__ = "2021-03-03"

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
import time

from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.constants.test_data import (SYNC_CONF, TEST_FILES_DATA_STACK, TEST_DATA_LOCATION,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         LENSMC_MEASUREMENTS_TABLE_FILENAME)
from SHE_PPT.file_io import read_xml_product, find_file, read_listfile
from SHE_PPT.logging import getLogger
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from astropy.table import Table
import pytest

from ElementsServices.DataSync import DataSync
from SHE_Validation_CTI import constants
from SHE_Validation_CTI.input_data import (SingleObjectData, PositionInfo, ShearInfo,
                                           get_raw_cti_gal_object_data, sort_raw_object_data_into_table)
from SHE_Validation_CTI.table_formats.cti_gal_object_data import TF as CGOD_TF
from SHE_Validation_CTI.validate_cti_gal import run_validate_cti_gal_from_args
import numpy as np


class TestCase:
    """


    """

    @classmethod
    def setup_class(cls):

        # Download the data stack files from WebDAV
        sync_datastack = DataSync(SYNC_CONF, TEST_FILES_DATA_STACK)
        sync_datastack.download()
        qualified_vis_calibrated_frames_filename = sync_datastack.absolutePath(
            os.path.join(TEST_DATA_LOCATION, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME))
        assert os.path.isfile(
            qualified_vis_calibrated_frames_filename), f"Cannot find file: {qualified_vis_calibrated_frames_filename}"

        # Get the workdir based on where the data images listfile is
        cls.workdir = os.path.split(qualified_vis_calibrated_frames_filename)[0]
        cls.logdir = os.path.join(cls.workdir, "logs")

        # Read in the test data
        cls.data_stack = SHEFrameStack.read(exposure_listfile_filename=VIS_CALIBRATED_FRAME_LISTFILE_FILENAME,
                                            detections_listfile_filename=MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                            workdir=cls.workdir,
                                            clean_detections=False,
                                            memmap=True,
                                            mode='denywrite')

        # Set up some expected values
        cls.ex_bg_level = 45.71

        return

    @classmethod
    def teardown_class(cls):

        return

    def test_get_raw_cti_gal_object_data(self):

        # Read in the mock shear estimates
        lmcm_tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS["LensMC"]
        lensmc_shear_estimates_table = Table.read(os.path.join(
            self.workdir, "data", LENSMC_MEASUREMENTS_TABLE_FILENAME))
        d_shear_estimates_tables = {"KSB": None,
                                    "LensMC": lensmc_shear_estimates_table,
                                    "MomentsML": None,
                                    "REGAUSS": None}

        raw_cti_gal_object_data = get_raw_cti_gal_object_data(data_stack=self.data_stack,
                                                              shear_estimate_tables=d_shear_estimates_tables)

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

            lensmc_world_shear_info = object_data.world_shear_info["LensMC"]
            assert lensmc_world_shear_info.g1 == lmcm_row[lmcm_tf.g1]
            assert lensmc_world_shear_info.g2 == lmcm_row[lmcm_tf.g2]
            assert lensmc_world_shear_info.weight == lmcm_row[lmcm_tf.weight]

            assert np.isnan(object_data.world_shear_info["KSB"].g1)
            assert np.isnan(object_data.world_shear_info["MomentsML"].g1)
            assert np.isnan(object_data.world_shear_info["REGAUSS"].g1)

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

                lensmc_exposure_shear_info = position_info.exposure_shear_info["LensMC"]

                # No rotation here, so all shear values should be the same as the world value
                assert lensmc_exposure_shear_info.g1 == lmcm_row[lmcm_tf.g1]
                assert lensmc_exposure_shear_info.g2 == lmcm_row[lmcm_tf.g2]
                assert lensmc_exposure_shear_info.weight == lmcm_row[lmcm_tf.weight]

                assert np.isnan(position_info.exposure_shear_info["KSB"].g1)
                assert np.isnan(position_info.exposure_shear_info["MomentsML"].g1)
                assert np.isnan(position_info.exposure_shear_info["REGAUSS"].g1)

    def test_sort_raw_object_data_into_table(self):

        # Set up test data
        raw_object_data_list = []
        num_exposures = 4

        dx_dexp = 100
        dy_dexp = 200
        dg1_dexp = -0.01
        dg2_dexp = 0.02
        dweight_dexp = 1

        ID_0 = self.data_stack.detections_catalogue[mfc_tf.ID][0]
        ID_1 = self.data_stack.detections_catalogue[mfc_tf.ID][0]

        for ID, x, y, g1, g2, weight, fvis, fvis_err, fnir, area in ((ID_0, 128, 129, 0.1, 0.3, 10,
                                                                      100., 10., 200., 50),
                                                                     (ID_1, 2000, 2000, -0.1, 0.2, 11,
                                                                      150., 20., 150., 100)):

            data_stack_copy = deepcopy(self.data_stack)

            detections_row = data_stack_copy.detections_catalogue.loc[ID]

            # Set up a mock detections row using a dictionary
            detections_row[mfc_tf.FLUX_VIS_APER] = fvis
            detections_row[mfc_tf.FLUXERR_VIS_APER] = fvis_err
            detections_row[mfc_tf.FLUX_NIR_STACK_APER] = fnir
            detections_row[mfc_tf.SEGMENTATION_AREA] = area

            object_data = SingleObjectData(ID=ID,
                                           num_exposures=num_exposures,
                                           data_stack=data_stack_copy)

            # Check that SNR, Colour, and Size are as expected
            assert np.isclose(object_data.snr, fvis / fvis_err)
            assert np.isclose(object_data.colour, 2.5 * np.log10(fvis / fnir))
            assert np.isclose(object_data.size, area)

            for bg_level in object_data.background_level:
                assert np.isclose(bg_level, self.ex_bg_level)
            assert np.isclose(object_data.mean_background_level, self.ex_bg_level)

            object_data.world_shear_info["LensMC"] = ShearInfo(g1=g1,
                                                               g2=g2,
                                                               weight=weight)
            object_data.world_shear_info["KSB"] = ShearInfo()
            object_data.world_shear_info["MomentsML"] = ShearInfo()
            object_data.world_shear_info["REGAUSS"] = ShearInfo()

            for exp_index in range(num_exposures):
                position_info = PositionInfo()
                position_info.x_pix = x + dx_dexp * exp_index
                position_info.y_pix = y + dy_dexp * exp_index
                position_info.exposure_shear_info["LensMC"] = ShearInfo(g1=g1 + dg1_dexp * exp_index,
                                                                        g2=g2 + dg2_dexp * exp_index,
                                                                        weight=weight + dweight_dexp * exp_index)
                object_data.position_info[exp_index] = position_info

            raw_object_data_list.append(object_data)

        object_data_table_list = sort_raw_object_data_into_table(raw_object_data_list=raw_object_data_list)

        # Check that the tables are as expected
        for exp_index, object_data_table in enumerate(object_data_table_list):

            for object_data, row in zip(raw_object_data_list, object_data_table):

                assert object_data.id == row[CGOD_TF.ID]

                assert np.isclose(object_data.snr, row[CGOD_TF.snr])
                assert np.isclose(object_data.colour, row[CGOD_TF.colour])
                assert np.isclose(object_data.size, row[CGOD_TF.size])

                assert np.isclose(object_data.position_info[exp_index].x_pix, row[CGOD_TF.x])
                assert np.isclose(object_data.position_info[exp_index].y_pix, row[CGOD_TF.y])
                assert np.isclose(object_data.position_info[exp_index].exposure_shear_info["LensMC"].g1,
                                  row[getattr(CGOD_TF, "g1_image_LensMC")])
                assert np.isclose(object_data.position_info[exp_index].exposure_shear_info["LensMC"].g2,
                                  row[getattr(CGOD_TF, "g2_image_LensMC")])
                assert np.isclose(object_data.position_info[exp_index].exposure_shear_info["LensMC"].weight,
                                  row[getattr(CGOD_TF, "weight_LensMC")])

        return
