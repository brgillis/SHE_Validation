""" @file cti_residual_validation.py

    Created 12 Feb 2018

    Function for performing validation of CTI residuals
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


reg_pix = 1  # Readout register - believed to be y, but might have to fix later

readout_split = 4134.5  # Maximum pixel position for which values are read out downward (in stacked frame)

g1_fail_flag_offset = 1
g2_fail_flag_offset = 4

lower_fail_flag_offset = 1
upper_fail_flag_offset = 2

slope_fail_sigma = 5
intercept_fail_sigma = 5

from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf

d_shear_estimation_method_table_formats = {"KSB": ksbm_tf,
                                           "REGAUSS": regm_tf,
                                           "MomentsML": mmlm_tf,
                                           "LensMC": lmcm_tf}

methods = d_shear_estimation_method_table_formats.keys()
