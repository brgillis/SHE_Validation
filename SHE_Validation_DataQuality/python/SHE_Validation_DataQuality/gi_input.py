"""
:file: python/SHE_Validation_DataQuality/gi_input.py

:date: 01/24/23
:author: Bryan Gillis

Code for reading in input data for GalInfo validation test
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
from dataclasses import dataclass
from typing import Optional, Tuple

from astropy.table import Table

from SHE_PPT.file_io import read_xml_product
from SHE_PPT.table_formats.mer_final_catalog import mer_final_catalog_format
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import is_any_type_of_none
from SHE_Validation_DataQuality.dp_input import DataProcInput, read_data_proc_input
from ST_DataModelBindings.dpd.mer.raw.finalcatalog_stub import dpdMerFinalCatalog

ERR_MER_CAT_NONE = "No MER Final Catalog table found in data product."
ERR_MER_CAT_FORMAT = "MER Final Catalog table for is not in expected format."


@dataclass
class GalInfoInput(DataProcInput):
    """Dataclass containing read-in input data for the GalInfo validation test. Since the input for this test is a 
    strict superset of the input for the DataProc validation test, we inherit from it to avoid code duplication. 
    Attributes listed here are only those unique to this child class.

    Attributes
    ----------
    p_mer_cat: dpdMerFinalCatalog or None
        The MER Final Catalog data product, if successfully read in, otherwise None
    err_p_mer_cat: str or None
        The text of any exceptions raised when attempting to read in the MER Final Catalog data product, or else None
    mer_cat: Table or None
        The MER Final Catalog table, if successfully read in, otherwise None
    err_mer_cat: Table or None
        The text of any exceptions raised when attempting to read in the MER Final Catalog table, or else None
    """

    p_mer_cat: Optional[dpdMerFinalCatalog]
    err_p_mer_cat: Optional[str]

    mer_cat: Optional[Table]
    err_mer_cat: Optional[str]


def read_gal_info_input(p_she_cat_filename, p_she_chains_filename, p_mer_cat_filename, workdir):
    """Read in the products and filenames that the GalInfo test checks for.

    Parameters
    ----------
    p_she_cat_filename : str
        Workdir-relative filename of the Shear Measurements catalog data product
    p_she_chains_filename : str or None
        Workdir-relative filename of the Chains catalog data product
    p_mer_cat_filename : str or None
        Workdir-relative filename of the Chains catalog data product
    workdir : str
        Fully-qualified path to the workdir

    Returns
    -------
    GalInfoInput
        The read-in products and catalogs, structured as attributes of a dataclass
    """

    # For the products shared with the DataProc input, we reuse its reading method here to read those in to avoid
    # code duplication
    dp_input = read_data_proc_input(p_she_cat_filename=p_she_cat_filename,
                                    p_she_chains_filename=p_she_chains_filename,
                                    workdir=workdir)

    # Read in the MER Final Catalog product and table
    try:

        p_mer_cat, mer_cat, err_mer_cat = _read_p_mer_cat(p_mer_cat_filename, workdir)
        err_p_mer_cat = None

    except Exception as e:

        p_mer_cat = None
        err_p_mer_cat = str(e)
        mer_cat = None
        err_mer_cat = None

    return GalInfoInput(**dp_input.__dict__,
                        p_mer_cat=p_mer_cat,
                        err_p_mer_cat=err_p_mer_cat,
                        mer_cat=mer_cat,
                        err_mer_cat=err_mer_cat)


def _read_p_mer_cat(p_mer_cat_filename: str, workdir: str) -> Tuple[dpdMerFinalCatalog,
                                                                    Optional[Table],
                                                                    Optional[str]]:
    """Private function to read in the MER Final Catalog data product and associated catalogs.
    """

    p_mer_cat: dpdMerFinalCatalog = read_xml_product(p_mer_cat_filename,
                                                     workdir=workdir,
                                                     product_type=dpdMerFinalCatalog)

    # Read in each catalog to a dict, and keep track of any error messages in an error dict

    mer_cat_filename = p_mer_cat.get_data_filename()

    mer_cat: Optional[Table]
    err_mer_cat: Optional[str]

    # Check for if table isn't provided, and use custom error message instead
    if is_any_type_of_none(mer_cat_filename):

        mer_cat = None
        err_mer_cat = ERR_MER_CAT_NONE

    else:
        try:

            chains = Table.read(os.path.join(workdir, mer_cat_filename))

            if not is_in_format(chains, mer_final_catalog_format):
                raise ValueError(ERR_MER_CAT_FORMAT)

            mer_cat = chains
            err_mer_cat = None

        except Exception as e:

            mer_cat = None
            err_mer_cat = str(e)

    return p_mer_cat, mer_cat, err_mer_cat
