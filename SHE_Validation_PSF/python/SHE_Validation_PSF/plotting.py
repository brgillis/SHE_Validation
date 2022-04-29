""" @file plotting.py

    Created 28 April 2022

    Classes and functions to perform plotting for PSF validation tests.
"""

__updated__ = "2022-04-28"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
import abc
from typing import Sequence

import numpy as np
from astropy.table import Table

from SHE_PPT.utility import coerce_to_list, is_inf_nan_or_masked
from SHE_Validation.binning.bin_constraints import get_table_of_ids
from SHE_Validation.plotting import ValidationPlotter
from SHE_Validation_PSF.data_processing import ESC_TF
from SHE_Validation_PSF.file_io import PsfResSPPlotFileNamer


class PsfResSPPlotter(ValidationPlotter, abc.ABC):
    """Abstract plotting class for plots generated by the PSF Residual (Star Positions) validation test.
    """

    # Fixed attributes which can be overridden by child classes
    plot_format: str = "png"

    def __init__(self,
                 star_cat: Table,
                 file_namer: PsfResSPPlotFileNamer,
                 bin_limits: Sequence[float],
                 l_ids_in_bin: Sequence[int], ):
        super().__init__(file_namer = file_namer)

        # Set attrs directly
        self.star_cat = star_cat
        self.bin_limits = bin_limits
        self.l_ids_in_bin = l_ids_in_bin

        # Determine attrs from kwargs

        self.t_good = get_table_of_ids(t = self.star_cat,
                                       l_ids = self.l_ids_in_bin, )


class PsfResSPHistPlotter(PsfResSPPlotter):

    def plot(self):
        """ Plot histograms of p values
        """

        # Get the data we want to plot
        l_p: Sequence[float] = np.array(coerce_to_list(self.t_good[ESC_TF.p]))
        l_logp: Sequence[float] = np.log10(l_p)

        # Remove any bad values from the data
        l_logp = np.array([x for x in l_logp if not is_inf_nan_or_masked(x)])

        # TODO: Start editing from here

        if self.g1_err_colname is not None:
            l_g1_err: Sequence[float] = np.array(coerce_to_list(self.g1_err_colname))
        else:
            l_g1_err: Sequence[float] = np.array(coerce_to_list(1 / np.sqrt(self.t_good[self.weight_colname])))

        if self.method_name is None:
            opt_method_str: str = ""
            plot_title: str = f"CTI-PSF Validation - {self.bin_parameter.value}"
        else:
            opt_method_str = f"method {self.method_name}, "
            plot_title: str = f"{self.method_name} CTI-Gal Validation - {self.bin_parameter.value}"

        # Append note of exposure or observation
        exp_index = self.file_namer.exp_index
        if exp_index is None:
            plot_title += "- Full Observation"
        else:
            plot_title += f"- Exposure {exp_index}"

        # Check if there's any valid data for this bin
        if len(l_rr_dist) <= 1:
            # We'll always make the tot plot for testing purposes, but log a warning if no data
            if self.bin_parameter == BinParameters.TOT:
                logger.warning(f"Insufficient valid data to plot for {opt_method_str}and test case "
                               f"{self.bin_parameter.value}, but making plot anyway for testing purposes.")
            else:
                logger.debug(f"Insufficient valid valid data to plot for {opt_method_str}test case "
                             f"{self.bin_parameter.value}, bin {self.bin_limits}, so skipping plot.")
                return

        # Perform the linear regression, calculate bias, and save it in the bias dict
        linregress_results: LinregressResults = linregress_with_errors(x = l_rr_dist,
                                                                       y = l_g1,
                                                                       y_err = l_g1_err)

        # Log the bias measurements, and save these strings for the plot
        logger.info(f"Linear regression for {opt_method_str}test case {self.bin_parameter.value}, "
                    f"bin {self.bin_limits}:")
        d_linregress_strings: Dict[str, str] = {}
        for a, d in ("slope", SLOPE_DIGITS), ("intercept", INTERCEPT_DIGITS):
            d_linregress_strings[f"{a}"] = (f"{a} = {getattr(linregress_results, a):.{d}f} +/- "
                                            f"{getattr(linregress_results, f'{a}_err'):.{d}f} "
                                            f"({getattr(linregress_results, f'{a}_sigma'):.{SIGMA_DIGITS}f}$\\sigma$)")
            logger.info(d_linregress_strings[f"{a}"])

        # Make a plot of the data and bestfit line

        # Set up the figure, with a density scatter as a base

        self.fig.subplots_adjust(wspace = 0, hspace = 0, bottom = 0.1, right = 0.95, top = 0.95, left = 0.12)

        self.density_scatter(l_rr_dist, l_g1, sort = True, bins = 200, colorbar = False, s = 4)

        if self.bin_parameter != BinParameters.TOT:
            plot_title += f" {self.bin_limits}"
        plt.title(plot_title, fontsize = TITLE_FONTSIZE)

        self.ax.set_xlabel(f"Readout Register Distance (pix)", fontsize = AXISLABEL_FONTSIZE)
        self.ax.set_ylabel(f"e1 (detector coordinates)", fontsize = AXISLABEL_FONTSIZE)

        # Draw the x axis
        self.draw_x_axis()

        # Draw the line of best-fit
        self.draw_bestfit_line(linregress_results)

        # Reset the axes
        self.reset_axes()

        # Write the bias
        self.ax.text(0.02, 0.98, d_linregress_strings[f"slope"], horizontalalignment = 'left',
                     verticalalignment = 'top',
                     transform = self.ax.transAxes, fontsize = TEXT_SIZE)
        self.ax.text(0.02, 0.93, d_linregress_strings[f"intercept"], horizontalalignment = 'left',
                     verticalalignment = 'top',
                     transform = self.ax.transAxes, fontsize = TEXT_SIZE)

        # Save the plot (which generates a filename) and log it
        super()._save_plot()
        logger.info(f"Saved {self.method_name} CTI plot to {self.qualified_plot_filename}")

        plt.close()
