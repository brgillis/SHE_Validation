"""
:file: python/SHE_Validation_DataQuality/dp_input.py

:date: 01/18/23
:author: Bryan Gillis

Code for reading in input data for DataProc validation test
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
from typing import Dict, Optional, Tuple

from astropy.table import Table

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.shear_estimation_methods import D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.table_formats.she_lensmc_chains import lensmc_chains_table_format
from SHE_PPT.table_utility import is_in_format
from ST_DataModelBindings.dpd.she.reconciledlensmcchains_stub import dpdSheReconciledLensMcChains
from ST_DataModelBindings.dpd.she.reconciledmeasurements_stub import dpdSheReconciledMeasurements

ERR_MEASUREMENTS_NONE = "No Shear Estimates table for method %s found in data product."
ERR_MEASUREMENTS_FORMAT = "Shear Estimates table for method %s is not in expected format %s."

ERR_CHAINS_NONE = "No Chains table found in data product."
ERR_CHAINS_FORMAT = "Chains table for is not in expected format."


@dataclass
class DataProcInput:
    """Dataclass containing read-in input data for the DataProc validation test.

    Attributes
    ----------
    p_rec_cat: dpdSheReconciledMeasurements or None
        The Reconciled Shear Measurements data product, if successfully read in, otherwise None
    err_p_rec_cat: str or None
        The text of any exceptions raised when attempting to read in the Reconciled Shear Measurements data product,
        or else None
    d_rec_cat: Dict[ShearEstimationMethod, Table or None] or None
        A dictionary of the Reconciled Shear Measurements catalogs for each shear estimation method, if successfully
        read in, otherwise None
    d_err_rec_cat: Dict[ShearEstimationMethod, str or None] or None
        The text of any exceptions raised when attempting to read each Reconciled Shear Measurements catalog, or else
        None
    p_rec_chains: dpdSheReconciledLensMcChains or None
        The Reconciled Chains data product, if successfully read in, otherwise None
    err_p_rec_chains: str or None
        The text of any exceptions raised when attempting to read in the Reconciled Chains data product, or else None
    rec_chains: Table or None
        The Reconciled Chains catalog, if successfully read in, otherwise None
    err_rec_chains: Table or None
        The text of any exceptions raised when attempting to read in the Reconciled Chains catalog, or else None
    """

    p_rec_cat: dpdSheReconciledMeasurements
    err_p_rec_cat: Optional[str]

    d_rec_cat: Optional[Dict[ShearEstimationMethods, Optional[Table]]]
    d_err_rec_cat: Optional[Dict[ShearEstimationMethods, Optional[str]]]

    p_rec_chains: Optional[dpdSheReconciledLensMcChains]
    err_p_rec_chains: Optional[str]

    rec_chains: Optional[Table]
    err_rec_chains: Optional[str]


def read_data_proc_input(p_rec_cat_filename, p_rec_chains_filename, workdir):
    """Read in the products and filenames that the DataProc test checks for.

    Parameters
    ----------
    p_rec_cat_filename : str
        Workdir-relative filename of the Reconciled Shear Measurements catalog data product
    p_rec_chains_filename : str or None
        Workdir-relative filename of the Reconciled Chains catalog data product
    workdir : str
        Fully-qualified path to the workdir

    Returns
    -------
    DataProcInput
        The read-in products and catalogs, structured as attributes of a dataclass
    """

    # Since the purpose of this test is to check for presence and suitability of products and tables, we wrap the
    # reading-in of each one in a try block so that we can report if any issue arises rather than crashing

    try:

        p_rec_cat, d_rec_cat, d_err_rec_cat = _read_p_rec_cat(p_rec_cat_filename, workdir)
        err_p_rec_cat = None

    except Exception as e:

        p_rec_cat = None
        err_p_rec_cat = str(e)
        d_rec_cat = None
        d_err_rec_cat = None

    # The Reconciled Chains product is optional, so we don't consider it an error if it's not present
    if p_rec_chains_filename is None:

        p_rec_chains = None
        err_p_rec_chains = None
        rec_chains = None
        err_rec_chains = None

    else:

        try:

            p_rec_chains, rec_chains, err_rec_chains = _read_p_rec_chains(p_rec_chains_filename, workdir)
            err_p_rec_chains = None

        except Exception as e:

            p_rec_chains = None
            err_p_rec_chains = str(e)
            rec_chains = None
            err_rec_chains = None

    return DataProcInput(p_rec_cat=p_rec_cat,
                         err_p_rec_cat=err_p_rec_cat,
                         d_rec_cat=d_rec_cat,
                         d_err_rec_cat=d_err_rec_cat,
                         p_rec_chains=p_rec_chains,
                         err_p_rec_chains=err_p_rec_chains,
                         rec_chains=rec_chains,
                         err_rec_chains=err_rec_chains)


def _read_p_rec_cat(p_rec_cat_filename: str, workdir: str) -> Tuple[dpdSheReconciledMeasurements,
                                                                    Dict[ShearEstimationMethods, Optional[Table]],
                                                                    Dict[ShearEstimationMethods, Optional[str]]]:
    """Private function to read in the Reconciled Shear Measurements catalog data product and associated catalogs.
    """

    p_rec_cat: dpdSheReconciledMeasurements = read_xml_product(p_rec_cat_filename,
                                                               workdir=workdir,
                                                               product_type=dpdSheReconciledMeasurements)

    # Read in each catalog to a dict, and keep track of any error messages in an error dict

    d_rec_cat: Dict[ShearEstimationMethods, Optional[Table]] = {}
    d_err_rec_cat: Dict[ShearEstimationMethods, Optional[str]] = {}

    for method, tf in D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS.items():

        method_cat_filename = p_rec_cat.get_method_filename(method)

        # Check for if table isn't provided, and use custom error message instead
        if method_cat_filename is None:
            d_rec_cat[method] = None
            d_err_rec_cat[method] = ERR_MEASUREMENTS_NONE % method.value
            continue

        try:

            method_cat = Table.read(os.path.join(workdir, method_cat_filename))

            if not is_in_format(method_cat, tf):
                raise ValueError(ERR_MEASUREMENTS_FORMAT % method.value, tf)

            d_rec_cat[method] = method_cat
            d_err_rec_cat[method] = None

        except Exception as e:

            d_rec_cat[method] = None
            d_err_rec_cat[method] = str(e)

    return p_rec_cat, d_rec_cat, d_err_rec_cat


def _read_p_rec_chains(p_rec_chains_filename: str, workdir: str) -> Tuple[dpdSheReconciledLensMcChains,
                                                                          Optional[Table],
                                                                          Optional[str]]:
    """Private function to read in the Reconciled Chains catalog data product and associated catalogs.
    """

    p_rec_chains: dpdSheReconciledLensMcChains = read_xml_product(p_rec_chains_filename,
                                                                  workdir=workdir,
                                                                  product_type=dpdSheReconciledLensMcChains)

    # Read in each catalog to a dict, and keep track of any error messages in an error dict

    chains_filename = p_rec_chains.get_data_filename()

    rec_chains: Optional[Table]
    err_rec_chains: Optional[str]

    # Check for if table isn't provided, and use custom error message instead
    if chains_filename is None:

        rec_chains = None
        err_rec_chains = ERR_CHAINS_NONE

    else:
        try:

            chains = Table.read(os.path.join(workdir, chains_filename))

            if not is_in_format(chains, lensmc_chains_table_format):
                raise ValueError(ERR_CHAINS_FORMAT)

            rec_chains = chains
            err_rec_chains = None

        except Exception as e:

            rec_chains = None
            err_rec_chains = str(e)

    return p_rec_chains, rec_chains, err_rec_chains
