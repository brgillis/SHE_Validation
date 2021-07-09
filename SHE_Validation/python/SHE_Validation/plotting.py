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


def density_scatter(x, y, fig=None, ax=None, sort=True, bins=20, colorbar=False, **kwargs):
    """ Scatter plot colored by 2d histogram, taken from https://stackoverflow.com/a/53865762/5099457
        Credit: Guillaume on StackOverflow
    """
    if ax is None or fig is None:
        fig, ax = plt.subplots()
    data, x_e, y_e = np.histogram2d(x, y, bins=bins, density=True)
    z = interpn((0.5 * (x_e[1:] + x_e[:-1]), 0.5 * (y_e[1:] + y_e[:-1])), data,
                np.vstack([x, y]).T, method="splinef2d", bounds_error=False)

    # To be sure to plot all data
    z[np.where(np.isnan(z))] = 0.0

    # Sort the points by density, so that the densest points are plotted last
    if sort:
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]

    ax.scatter(x, y, c=z, **kwargs)

    norm = Normalize(vmin=np.min(z), vmax=np.max(z))
    if colorbar:
        cbar = fig.colorbar(cm.ScalarMappable(norm=norm), ax=ax)
        cbar.ax.set_ylabel('Density')

    return fig, ax


def draw_x_axis(ax, color, linestyle, **kwargs):
    """ Draws an x-axis on a plot.
    """

    xlim = deepcopy(ax.get_xlim())
    ax.plot(xlim, [0, 0], label=None, color=color, linestyle=linestyle, **kwargs)

    return xlim


def draw_y_axis(ax, color, linestyle, **kwargs):
    """ Draws a y-axis on a plot.
    """

    ylim = deepcopy(ax.get_ylim())
    ax.plot([0, 0], ylim, label=None, color=color, linestyle=linestyle, **kwargs)

    return ylim


def draw_axes(ax, color="k", linestyle="solid", **kwargs):
    """ Draws an x-axis and y-axis on a plot.
    """

    xlim = draw_x_axis(ax, color, linestyle, **kwargs)
    ylim = draw_y_axis(ax, color, linestyle, **kwargs)

    return xlim, ylim


def draw_bestfit_line(ax, linregress_results, xlim=None, label=None, color="r", linestyle="solid"):
    """ Draw a line of bestfit on a plot.
    """

    if xlim is None:
        xlim = ax.get_xlim()

    bestfit_x = np.array(xlim)
    bestfit_y = linregress_results.slope * bestfit_x + linregress_results.intercept
    ax.plot(bestfit_x, bestfit_y, label=label, color=color, linestyle=linestyle)

    return xlim
