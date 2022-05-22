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
from typing import Iterable, List, Optional, Tuple, Union

import numpy as np
from matplotlib import cm, pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.figure import Axes, Figure
from scipy.interpolate import interpn

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.logging import getLogger
from SHE_PPT.math import LinregressResults
from SHE_PPT.utility import is_nan_or_masked
from .file_io import SheValFileNamer

logger = getLogger(__name__)


class ValidationPlotter(abc.ABC):
    """Abstract base class for plotters for various types of plots made in the SHE_Validation project.

    This class can be used in the following manner:

    1. Create a subclass of it to make a particular style of plot.
    2. Concretely implement the abstract __init__ and _draw_plot methods
    3. Override and/or inherit other methods of this which are called from the template method plot(), to alter aspects
       of how the plot is constructed. See the structure of this method to see which methods are called and in which
       order (and keep in mind that attribute calls are generally to getters, which have their own methods which can
       be overriden/inherited).

       At time of implementation, the relevant methods which you might wish to override are:

        _get_legend_loc()*
            Set the location of the plot's legend (default None = no legend)
        _get_plot_title()*
            Set the plot title (default no title)
        _get_x_label()*
            Set the plot's x-axis label (default no label)
        _get_y_label()*
            Set the plot's y-axis label (default no label)
        _get_l_summary_text()*
            Set the lines of summary text to display on the plot (default no text)
        _get_msg_plot_saved()*
            Set the message to log when the plot is saved (default prints the qualified file name and says it's been
            saved)
        _calc_plotting_data()
            Calculate any member variables needed for plotting (this can alternatively be done within __init__ if
            it's not necessary that this be done each time plot() is called)
        _subplots_adjust()
            Set the margins of the plot

        *For any of the _get_*()methods, if the value you wish to set is fixed and not dependent on any attributes, you
        can alternatively set the corresponding member variable directly, e.g. _x_label = "X"

        (Check the implementation of the plot() method to be sure, in case this documentation has gone out of date.)
    """

    # Class constants
    TITLE_FONTSIZE = 12
    AXISLABEL_FONTSIZE = 12

    SUM_TXT_HALIGN = 'left'
    SUM_TXT_VALIGN = 'top'
    SUM_TXT_X_ORIGIN = 0.02
    SUM_TXT_Y_ORIGIN = 0.98
    SUM_TXT_Y_STEP = -0.05
    SUM_TEXT_FONTSIZE = 12

    MSG_INSUFFICIENT_DATA_TOT = ("Insufficient valid data to plot for %s test case, but making "
                                 "plot anyway for testing purposes.")
    MSG_INSUFFICIENT_DATA = ("Insufficient valid valid data to plot for %s test case, bin "
                             "%s, so skipping plot.")

    # Fixed attributes which can be overridden by child classes
    plot_format: str = "png"

    # Attributes set directly at init
    file_namer: Optional[SheValFileNamer] = None
    bin_limits: Optional[np.ndarray] = None

    # Intermediate values used while plotting
    _fig: Optional[Figure] = None
    _ax: Optional[Axes] = None
    _xlim: Optional[Tuple[float, float]] = None
    _ylim: Optional[Tuple[float, float]] = None
    _legend_loc: Optional[str] = None
    _plot_title: Optional[str] = None
    _x_label: Optional[str] = None
    _y_label: Optional[str] = None
    _l_summary_text: Optional[Union[str, List[str]]] = None
    _msg_plot_saved: Optional[str] = None

    # Output values from plotting
    plot_filename: Optional[str] = None
    qualified_plot_filename: Optional[str] = None

    @abc.abstractmethod
    def __init__(self,
                 file_namer: Optional[SheValFileNamer] = None,
                 bin_limits: Optional[np.ndarray] = None):

        if file_namer is not None:
            self.file_namer = file_namer

        if bin_limits is not None:
            self.bin_limits = bin_limits

    # Attribute getters and setters

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

    @xlim.setter
    def xlim(self, xlim: Tuple[float, float]) -> None:
        self.ax.set_xlim(xlim[0], xlim[1])
        self._xlim = xlim

    @property
    def ylim(self) -> Tuple[float, float]:
        if self._ylim is None:
            self._ylim = deepcopy(self.ax.get_ylim())
        return self._ylim

    @ylim.setter
    def ylim(self, ylim: Tuple[float, float]) -> None:
        self.ax.set_ylim(ylim[0], ylim[1])
        self._ylim = ylim

    @property
    def x_label(self) -> str:
        if self._x_label is None:
            self._x_label = self._get_x_label()
        return self._x_label

    @x_label.setter
    def x_label(self, x_label: str) -> None:
        self._x_label = x_label

    @property
    def y_label(self) -> str:
        if self._y_label is None:
            self._y_label = self._get_y_label()
        return self._y_label

    @y_label.setter
    def y_label(self, y_label: str) -> None:
        self._y_label = y_label

    @property
    def plot_title(self) -> str:
        if self._plot_title is None:
            self._plot_title = self._get_plot_title()
        return self._plot_title

    @plot_title.setter
    def plot_title(self, plot_title: str) -> None:
        self._plot_title = plot_title

    @property
    def legend_loc(self) -> str:
        if self._legend_loc is None:
            self._legend_loc = self._get_legend_loc()
        return self._legend_loc

    @legend_loc.setter
    def legend_loc(self, legend_loc: str) -> None:
        self._legend_loc = legend_loc

    @property
    def l_summary_text(self) -> Union[str, List[str]]:
        if self._l_summary_text is None:
            self._l_summary_text = self._get_l_summary_text()
        return self._l_summary_text

    @l_summary_text.setter
    def l_summary_text(self, l_summary_text: Union[str, List[str]]) -> None:
        self._l_summary_text = l_summary_text

    @property
    def msg_plot_saved(self) -> str:
        if self._msg_plot_saved is None:
            self._msg_plot_saved = self._get_msg_plot_saved()
        return self._msg_plot_saved

    @msg_plot_saved.setter
    def msg_plot_saved(self, msg_plot_saved: str) -> None:
        self._msg_plot_saved = msg_plot_saved

    # Public methods

    def plot(self,
             show: bool = False) -> None:
        """ Makes and saves the plot(s).
        """

        cancel_plotting = self._calc_plotting_data()
        if cancel_plotting:
            # We've received a signal to cancel plotting without raising an error, so return here
            return

        # Set up the figure
        self._subplots_adjust()

        # Draw the figure
        self._draw_plot()

        # Add the legend to the figure
        self._draw_legend()

        # Set the plot title and labels
        self._set_title()
        self._set_xy_labels()

        # Write the text on the plot
        self._write_summary_text()

        # Display the plot if requested
        if show:
            plt.show()

        # Save the plot (which generates a filename) and log it
        self._save_plot()

        logger.info(self.msg_plot_saved)

        plt.close()

    # Protected methods intended to be overridden as needed by child classes

    @staticmethod
    def _get_legend_loc() -> Optional[str]:
        """ Overridable method to get location of the legend (None = don't display legend)
        """
        return None

    @staticmethod
    def _get_plot_title() -> str:
        """ Overridable method to get the plot title
        """
        return ""

    @staticmethod
    def _get_x_label() -> str:
        """ Overridable method to get the label for the X axis.
        """
        return ""

    @staticmethod
    def _get_y_label() -> str:
        """ Overridable method to get the label for the Y axis.
        """
        return ""

    @staticmethod
    def _get_l_summary_text() -> List[str]:
        """ Overridable method to get the summary text to be printed on the plot
        """
        return []

    def _get_msg_plot_saved(self) -> str:
        """ Overridable method to get the method to print to log that a plot has been saved
        """
        return f"Saved plot to {self.qualified_plot_filename}"

    def _calc_plotting_data(self) -> None:
        """ Overridable method to get all the data we want to plot
        """
        pass

    def _subplots_adjust(self) -> None:
        """ Set up the figure with a single subplot in a standard format.
        """
        self.fig.subplots_adjust(wspace = 0, hspace = 0, bottom = 0.1, right = 0.95, top = 0.95, left = 0.12)

    @abc.abstractmethod
    def _draw_plot(self) -> None:
        """ Abstract method for drawing the plot
        """
        pass

    # Protected methods for use as needed by child classes

    def _get_bin_info_str(self):
        """ Get a string for the bin info, which can be added to the plot title.
        """

        bin_info_str = f" - {self.bin_parameter.value}"
        if self.bin_parameter != BinParameters.TOT:
            bin_info_str += f" {self.bin_limits}"

        return bin_info_str

    def _density_scatter(self,
                         l_x: np.ndarray,
                         l_y: np.ndarray,
                         sort: bool = True,
                         bins: int = 20,
                         colorbar: bool = False,
                         **kwargs) -> None:
        """ Scatter plot colored by 2d histogram, taken from https://stackoverflow.com/a/53865762/5099457
            Credit: Guillaume on StackOverflow
        """

        if not len(l_x) == len(l_y):
            raise ValueError(f"Input arrays must be the same length: len(l_x)={len(l_x)}, len(l_y)={len(l_y)}")

        # Prune any NaN values from l_x and l_y
        nan_values = np.logical_or(is_nan_or_masked(l_x), is_nan_or_masked(l_y))

        l_x = l_x[~nan_values]
        l_y = l_y[~nan_values]

        data, l_xe, l_ye = np.histogram2d(l_x, l_y, bins = bins, density = True)
        l_z: np.ndarray = interpn((0.5 * (l_xe[1:] + l_xe[:-1]), 0.5 * (l_ye[1:] + l_ye[:-1])), data,
                                  np.vstack([l_x, l_y]).T, method = "splinef2d", bounds_error = False)

        # To be sure to plot all data
        l_z[np.where(is_nan_or_masked(l_z))] = 0.0

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

    def _draw_x_axis(self, color: str = "k", linestyle: str = "solid", **kwargs) -> None:
        """ Draws an x-axis on a plot.
        """

        self.ax.plot(self.xlim, [0, 0], label = None, color = color, linestyle = linestyle, **kwargs)

    def _draw_y_axis(self, color: str = "k", linestyle: str = "solid", **kwargs) -> None:
        """ Draws a y-axis on a plot.
        """

        self.ax.plot([0, 0], self.ylim, label = None, color = color, linestyle = linestyle, **kwargs)

    def _draw_axes(self, color: str = "k", linestyle: str = "solid", **kwargs) -> None:
        """ Draws an x-axis and y-axis on a plot.
        """

        self._draw_x_axis(color, linestyle, **kwargs)
        self._draw_y_axis(color, linestyle, **kwargs)

    def _draw_bestfit_line(self,
                           linregress_results: LinregressResults,
                           label: Optional[str] = None,
                           color: str = "r",
                           linestyle: str = "solid") -> None:
        """ Draw a line of bestfit on a plot.
        """

        bestfit_x: Iterable[float] = np.array(self.xlim)
        bestfit_y: Iterable[float] = linregress_results.slope * bestfit_x + linregress_results.intercept
        self.ax.plot(bestfit_x, bestfit_y, label = label, color = color, linestyle = linestyle)

    def _reset_axes(self):
        """ Resets the axes to saved xlim/ylim from when they were first accessed.
        """

        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)

    def _clear_plots(self) -> None:
        """ Closes the plots and resets self.ax and self.fig.
        """

        plt.close()
        self.ax = None
        self.fig = None

    # Protected classes normally expected to be left alone, but which can be overridden if needed

    def _save_plot(self) -> str:

        # Get the filename to save to
        self.plot_filename = self.file_namer.filename
        self.qualified_plot_filename = self.file_namer.qualified_filename

        # Save the figure and close it
        plt.savefig(self.qualified_plot_filename, format = self.plot_format,
                    bbox_inches = "tight", pad_inches = 0.05)
        logger.info(self.msg_plot_saved)

        return self.plot_filename

    def _write_summary_text(self) -> None:
        """ Writes summary text on the plot. If self.l_summary_text a list of strings, each will be written on a
            separate line. If it's just a string, it will be written on a single line
        """

        # If just one string, write it directly and return
        if isinstance(self.l_summary_text, str):
            self._write_summary_text_line(self.l_summary_text)

        # Write each string on a separate line
        for line_num, s in enumerate(self.l_summary_text):
            self._write_summary_text_line(s, line_num = line_num)

    def _write_summary_text_line(self,
                                 s: str,
                                 line_num: int = 0) -> None:
        """ Writes a single line of summary text on the plot.
        """

        self.ax.text(s = s,
                     x = self.SUM_TXT_X_ORIGIN,
                     y = self.SUM_TXT_Y_ORIGIN + line_num * self.SUM_TXT_Y_STEP,
                     horizontalalignment = self.SUM_TXT_HALIGN,
                     verticalalignment = self.SUM_TXT_VALIGN,
                     transform = self.ax.transAxes,
                     fontsize = self.SUM_TEXT_FONTSIZE)

    def _set_xy_labels(self) -> None:
        self.ax.set_xlabel(self.x_label, fontsize = self.AXISLABEL_FONTSIZE)
        self.ax.set_ylabel(self.y_label, fontsize = self.AXISLABEL_FONTSIZE)

    def _set_title(self) -> None:
        plt.title(self.plot_title, fontsize = self.TITLE_FONTSIZE)

    def _draw_legend(self) -> None:
        if self.legend_loc is not None:
            plt.legend(loc = self.legend_loc)
