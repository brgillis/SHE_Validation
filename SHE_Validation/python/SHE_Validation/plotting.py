""" @file plotting.py

    Created 9 July 2021

    Common functions to aid with plotting.
"""

__updated__ = "2021-07-09"

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

from copy import deepcopy

from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from scipy.interpolate import interpn

import numpy as np


class ValidationPlotter():

    fig = None
    ax = None
    xlim = None
    ylim = None

    def __init__(self):
        self._ax = None
        self._fig = None
        self._xlim = None
        self._ylim = None

    @property
    def ax(self):
        if self._ax is None:
            self._fig, self._ax = plt.subplots()
        return self._ax

    @ax.setter
    def ax(self, ax):
        self._ax = ax
        self._xlim = None
        self._ylim = None

    @property
    def fig(self):
        if self._fig is None:
            self._fig, self._ax = plt.subplots()
        return self._fig

    @fig.setter
    def fig(self, fig):
        self._fig = fig
        self._xlim = None
        self._ylim = None

    @property
    def xlim(self):
        if self._xlim is None:
            self._xlim = deepcopy(self.ax.get_xlim())
        return self._xlim

    @property
    def ylim(self):
        if self._ylim is None:
            self._ylim = deepcopy(self.ax.get_ylim())
        return self._ylim

    def density_scatter(self, x, y, sort=True, bins=20, colorbar=False, **kwargs):
        """ Scatter plot colored by 2d histogram, taken from https://stackoverflow.com/a/53865762/5099457
            Credit: Guillaume on StackOverflow
        """

        data, x_e, y_e = np.histogram2d(x, y, bins=bins, density=True)
        z = interpn((0.5 * (x_e[1:] + x_e[:-1]), 0.5 * (y_e[1:] + y_e[:-1])), data,
                    np.vstack([x, y]).T, method="splinef2d", bounds_error=False)

        # To be sure to plot all data
        z[np.where(np.isnan(z))] = 0.0

        # Sort the points by density, so that the densest points are plotted last
        if sort:
            idx = z.argsort()
            x, y, z = x[idx], y[idx], z[idx]

        self.ax.scatter(x, y, c=z, **kwargs)

        norm = Normalize(vmin=np.min(z), vmax=np.max(z))
        if colorbar:
            cbar = self.fig.colorbar(cm.ScalarMappable(norm=norm), ax=self.ax)
            cbar.ax.set_ylabel('Density')

    def draw_x_axis(self, color="k", linestyle="solid", **kwargs):
        """ Draws an x-axis on a plot.
        """

        self.ax.plot(self.xlim, [0, 0], label=None, color=color, linestyle=linestyle, **kwargs)

    def draw_y_axis(self, color="k", linestyle="solid", **kwargs):
        """ Draws a y-axis on a plot.
        """

        self.ax.plot([0, 0], self.ylim, label=None, color=color, linestyle=linestyle, **kwargs)

    def draw_axes(self, color="k", linestyle="solid", **kwargs):
        """ Draws an x-axis and y-axis on a plot.
        """

        self.draw_x_axis(color, linestyle, **kwargs)
        self.draw_y_axis(color, linestyle, **kwargs)

    def draw_bestfit_line(self, linregress_results, label=None, color="r", linestyle="solid"):
        """ Draw a line of bestfit on a plot.
        """

        bestfit_x = np.array(self.xlim)
        bestfit_y = linregress_results.slope * bestfit_x + linregress_results.intercept
        self.ax.plot(bestfit_x, bestfit_y, label=label, color=color, linestyle=linestyle)
