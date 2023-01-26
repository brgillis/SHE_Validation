""" @file calc_common_val_data.py

    Created 28 Oct 2021

    Code to implement calculation of data common to multiple validation executables
"""

__updated__ = "2021-08-18"

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

from typing import Any, Dict, Optional, Set

from astropy.table import Table

from SHE_PPT import file_io
from SHE_PPT.argument_parser import CA_MER_CAT, CA_SHE_MEAS, CA_VIS_CAL_FRAME, CA_WORKDIR
from SHE_PPT.file_io import read_d_method_tables
from SHE_PPT.logging import getLogger
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_Validation.argument_parser import CA_SHE_EXT_CAT
from SHE_Validation.binning.bin_data import (add_binning_data, )
from SHE_Validation.file_io import SheValFileNamer
from SHE_Validation.utility import get_object_id_list_from_se_tables

logger = getLogger(__name__)


def calc_common_val_data_from_args(d_args: Dict[str, Any]):
    """ Main function for performing True Universe matching
    """

    workdir = d_args[CA_WORKDIR]

    # Read in the shear estimates data product, and get the filenames of the tables for each method from it
    d_shear_tables, _ = read_d_method_tables(d_args[CA_SHE_MEAS],
                                             workdir=workdir,
                                             log_info=True)

    # Read in the data stack
    s_object_ids: Set[int] = get_object_id_list_from_se_tables(d_shear_tables)
    data_stack: Optional[SHEFrameStack] = SHEFrameStack.read(exposure_listfile_filename=d_args[CA_VIS_CAL_FRAME],
                                                             detections_listfile_filename=d_args[CA_MER_CAT],
                                                             object_id_list=s_object_ids,
                                                             workdir=workdir)

    # We'll modify the detections stack attribute within the data stack to create the extended table
    extended_catalog: Table = data_stack.detections_catalogue

    # Add bin data columns to the table
    add_binning_data(extended_catalog, data_stack=data_stack)

    # Write out to a fits file
    extended_catalog_namer = SheValFileNamer(type_name="P-EX-MFC",
                                             workdir=workdir)
    extended_catalog.write(extended_catalog_namer.qualified_filename)

    # Create output data product
    extended_catalog_product = create_dpd_mer_final_catalog(extended_catalog_namer.filename)

    # Write the data product
    file_io.write_xml_product(extended_catalog_product,
                              d_args[CA_SHE_EXT_CAT],
                              workdir=workdir,
                              log_info=True)
