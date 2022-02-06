""" @file plotting.py

    Created 9 July 2021

    Common functions to aid with plotting.
"""

__updated__ = "2021-08-30"

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
from copy import deepcopy
from typing import Iterable, Optional, Tuple

import numpy as np
from matplotlib import cm, pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.figure import Axes, Figure
from scipy.interpolate import interpn

from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import LinregressResults
from .file_io import SheValFileNamer

logger = getLogger(__name__)


class ValidationPlotter(abc.ABC):
    """TODO: Add a docstring for this class."""

    # Fixed attributes which can be overridden by child classes
    plot_format: str = "png"

    # Attributes set directly at init
    file_namer: Optional[SheValFileNamer] = None

    # Intermediate values used while plotting
    _fig: Optional[Figure] = None
    _ax: Optional[Axes] = None
    _xlim: Optional[Tuple[float, float]] = None
    _ylim: Optional[Tuple[float, float]] = None

    # Output values from plotting
    plot_filename: Optional[str] = None
    qualified_plot_filename: Optional[str] = None

    @abc.abstractmethod
    def __init__(self,
                 file_namer: Optional[SheValFileNamer] = None):

        if file_namer is not None:
            self.file_namer = file_namer

    @property
    def method(self) -> Optional[ShearEstimationMethods]:
        if self.file_namer is None:
            return None
        return self.file_namer.method

    @property
    def bin_parameter(self) -> Optional[ShearEstimationMethods]:
        if self.file_namer is None:
            return None
        return self.file_namer.bin_parameter

    @property
    def bin_index(self) -> Optional[ShearEstimationMethods]:
        if self.file_namer is None:
            return None
        return self.file_namer.bin_index

    @property
    def ax(self) -> Axes:
        if self._ax is None:
            self._fig, self._ax = plt.subplots()
        return self._ax

    @ax.setter
    def ax(self, ax: Axes):
        self._ax = ax
        self._xlim = None
        self._ylim = None

    @property
    def fig(self) -> Figure:
        if self._fig is None:
            self._fig, self._ax = plt.subplots()
        return self._fig

    @fig.setter
    def fig(self, fig: Figure):
        self._fig = fig
        self._xlim = None
        self._ylim = None

    @property
    def xlim(self) -> Tuple[float, float]:
        if self._xlim is None:
            self._xlim = deepcopy(self.ax.get_xlim())
        return self._xlim

    @property
    def ylim(self) -> Tuple[float, float]:
        if self._ylim is None:
            self._ylim = deepcopy(self.ax.get_ylim())
        return self._ylim

    # Public methods

    def _save_plot(self) -> str:

        # Get the filename to save to
        self.plot_filename = self.file_namer.filename
        self.qualified_plot_filename = self.file_namer.qualified_filename

        # Save the figure and close it
        plt.savefig(self.qualified_plot_filename, format = self.plot_format,
                    bbox_inches = "tight", pad_inches = 0.05)
        logger.info(f"Saved {self.file_namer.type_name} plot {self.file_namer.instance_id} to "
                    f"{self.qualified_plot_filename}")

        return self.plot_filename

    def density_scatter(self,
                        l_x: np.ndarray,
                        l_y: np.ndarray,
                        sort: bool = True,
                        bins: int = 20,
                        colorbar: bool = False,
                        **kwargs):
        """ Scatter plot colored by 2d histogram, taken from https://stackoverflow.com/a/53865762/5099457
            Credit: Guillaume on StackOverflow
        """

        if not len(l_x) == len(l_y):
            raise ValueError(f"Input arrays must be the same length: len(l_x)={len(l_x)}, len(l_y)={len(l_y)}")

        # Prune any NaN values from l_x and l_y
        nan_values = np.logical_or(np.isnan(l_x), np.isnan(l_y))

        l_x = l_x[~nan_values]
        l_y = l_y[~nan_values]

        data, l_xe, l_ye = np.histogram2d(l_x, l_y, bins = bins, density = True)
        l_z: np.ndarray = interpn((0.5 * (l_xe[1:] + l_xe[:-1]), 0.5 * (l_ye[1:] + l_ye[:-1])), data,
                                  np.vstack([l_x, l_y]).T, method = "splinef2d", bounds_error = False)

        # To be sure to plot all data
        l_z[np.where(np.isnan(l_z))] = 0.0

        # Sort the points by density, so that the densest points are plotted last
        if sort:
            idx: np.ndarray = l_z.argsort()
            l_x, l_y, l_z = l_x[idx], l_y[idx], l_z[idx]

        self.ax.scatter(l_x, l_y, c = l_z, **kwargs)

        if colorbar:
            if len(l_z) == 0:
                norm = Normalize(vmin = 0, vmax = 1)
            else:
                norm = Normalize(vmin = np.min(l_z), vmax = np.max(l_z))
            cbar = self.fig.colorbar(cm.ScalarMappable(norm = norm), ax = self.ax)
            cbar.ax.set_ylabel('Density')

    def draw_x_axis(self, color: str = "k", linestyle: str = "solid", **kwargs):
        """ Draws an x-axis on a plot.
        """

        self.ax.plot(self.xlim, [0, 0], label = None, color = color, linestyle = linestyle, **kwargs)

    def draw_y_axis(self, color: str = "k", linestyle: str = "solid", **kwargs):
        """ Draws a y-axis on a plot.
        """

        self.ax.plot([0, 0], self.ylim, label = None, color = color, linestyle = linestyle, **kwargs)

    def draw_axes(self, color: str = "k", linestyle: str = "solid", **kwargs):
        """ Draws an x-axis and y-axis on a plot.
        """

        self.draw_x_axis(color, linestyle, **kwargs)
        self.draw_y_axis(color, linestyle, **kwargs)

    def draw_bestfit_line(self,
                          linregress_results: LinregressResults,
                          label: Optional[str] = None,
                          color: str = "r",
                          linestyle: str = "solid"):
        """ Draw a line of bestfit on a plot.
        """

        bestfit_x: Iterable[float] = np.array(self.xlim)
        bestfit_y: Iterable[float] = linregress_results.slope * bestfit_x + linregress_results.intercept
        self.ax.plot(bestfit_x, bestfit_y, label = label, color = color, linestyle = linestyle)

    def reset_axes(self):
        """ Resets the axes to saved xlim/ylim from when they were first accessed.
        """

        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)

    def clear_plots(self):
        """ Closes the plots and resets self.ax and self.fig.
        """

        plt.close()
        self.ax = None
        self.fig = None

    @abc.abstractmethod
    def plot(self, *args, **kwargs):
        """ Makes and saves the plot(s).
        """
        pass
