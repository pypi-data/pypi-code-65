#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import math
from collections import namedtuple

import ROOT
import numpy
from six import string_types
from typing import List, Optional, Union

import wagascianpy.plotting.colors

ROOT.PyConfig.IgnoreCommandLineOptions = True

# compatible with Python 2 *and* 3
try:
    # noinspection PyUnresolvedReferences
    IntTypes = (int, long)  # Python2
except NameError:
    IntTypes = int  # Python3

Range = namedtuple('Range', ['lower_bound', 'upper_bound'])


class Graph(object):
    _num_logscale_bins = 100

    def __init__(self, title, graph_id=None):
        # type: (str, Optional[str]) -> None
        self.title = title
        self.id = graph_id if graph_id is not None else title
        self._xdata = None
        self._ydata = None
        self._color = wagascianpy.plotting.colors.Colors.Black.value
        self._yaxis_color = wagascianpy.plotting.colors.Colors.Black.value
        self._xrange = Range(lower_bound=None, upper_bound=None)
        self._yrange = Range(lower_bound=None, upper_bound=None)
        self._is_empty = True

    @property
    def xdata(self):
        # type: (...) -> Optional[List]
        return self._xdata

    @xdata.setter
    def xdata(self, xdata):
        # type: (List) -> None
        if isinstance(xdata, list):
            self._xdata = numpy.asarray(xdata, dtype=numpy.float64)
        elif isinstance(xdata, numpy.ndarray):
            self._xdata = xdata
        elif xdata is None:
            self._xdata = numpy.array([], dtype=numpy.float64)
        else:
            raise TypeError("Data format not recognized : type(ydata) = {}".format(type(xdata).__name__))
        assert self._xdata.dtype == numpy.float64
        if self._xdata.size == 0:
            self._is_empty = True
        else:
            self._is_empty = False

    @property
    def ydata(self):
        # type: (...) -> Optional[List]
        return self._ydata

    @ydata.setter
    def ydata(self, ydata):
        # type: (List) -> None
        if isinstance(ydata, list):
            self._ydata = numpy.asarray(ydata, dtype=numpy.float64)
        elif isinstance(ydata, numpy.ndarray):
            self._ydata = ydata
        elif ydata is None:
            self._ydata = numpy.array([], dtype=numpy.float64)
        else:
            raise TypeError("Data format not recognized : type(ydata) = {}".format(type(ydata).__name__))
        assert self._ydata.dtype == numpy.float64
        if self._ydata.size == 0:
            self._is_empty = True
        else:
            self._is_empty = False

    @staticmethod
    def _parse_color(color):
        # type: (Union[int, wagascianpy.plotting.colors.Colors, str]) -> int
        if isinstance(color, IntTypes):
            output = color
        elif isinstance(color, wagascianpy.plotting.colors.Colors):
            output = color.value
        elif isinstance(color, string_types):
            output = wagascianpy.plotting.colors.Colors.get_by_detector(color).value
        else:
            raise TypeError("Color type is unknown {}".format(type(color).__name__))
        return output

    @property
    def color(self):
        # type: (...) -> Optional[List]
        return self._color

    @color.setter
    def color(self, color):
        # type: (Union[int, wagascianpy.plotting.colors.Colors, str]) -> None
        self._color = self._parse_color(color)

    @property
    def yaxis_color(self):
        return self._yaxis_color

    @yaxis_color.setter
    def yaxis_color(self, color):
        # type: (Union[int, wagascianpy.plotting.colors.Colors, str]) -> None
        self._yaxis_color = self._parse_color(color)

    @property
    def xrange(self):
        # type: (...) -> Optional[Range]
        return self._xrange

    @xrange.setter
    def xrange(self, xrange):
        # type: (Range) -> None
        if isinstance(xrange, Range):
            self._xrange = xrange
        else:
            raise TypeError("X axis Range type is unknown {}".format(type(xrange).__name__))

    @property
    def yrange(self):
        # type: (...) -> Optional[Range]
        return self._yrange

    @yrange.setter
    def yrange(self, yrange):
        # type: (Range) -> None
        if isinstance(yrange, Range):
            self._yrange = yrange
        else:
            raise TypeError("Y axis Range type is unknown {}".format(type(yrange).__name__))

    def is_empty(self):
        # type: (...) -> bool
        return self._is_empty

    def make_tgraph(self, logscale=False):
        # type: (...) -> ROOT.TGraph
        if self._xdata is None or self._ydata is None:
            raise RuntimeError("Please insert some data in the graph")
        if len(self._xdata) != len(self._ydata):
            raise IndexError("xdata ({}) and ydata ({}) length mismatch".format(len(self._xdata), len(self._ydata)))
        tgraph = ROOT.TGraph(len(self._xdata), self._xdata, self._ydata)
        tgraph.SetNameTitle(self.id, self.title)
        tgraph.SetLineColor(self._color)
        tgraph.SetMarkerColor(self._color)
        x_lower_bound = self._xrange.lower_bound if self._xrange.lower_bound is not None else \
            numpy.amin(self._xdata)
        x_upper_bound = self._xrange.upper_bound if self._xrange.upper_bound is not None else \
            numpy.amax(self._xdata)
        y_lower_bound = self._yrange.lower_bound if self._yrange.lower_bound is not None else \
            numpy.amin(self._ydata)
        y_upper_bound = self._yrange.upper_bound if self._yrange.upper_bound is not None else \
            numpy.amax(self._ydata)
        tgraph.GetXaxis().SetLimits(x_lower_bound, x_upper_bound)
        tgraph.GetHistogram().SetMaximum(y_upper_bound)
        tgraph.GetHistogram().SetMinimum(y_lower_bound)
        tgraph.GetYaxis().SetTitleColor(self.yaxis_color)
        tgraph.GetYaxis().SetLabelColor(self.yaxis_color)
        tgraph.GetYaxis().SetAxisColor(self.yaxis_color)
        return tgraph


class Graph2D(Graph):

    @property
    def ydata(self):
        # type: (...) -> Optional[List]
        return self._ydata

    @ydata.setter
    def ydata(self, ydata):
        # type: (Optional[List[List[float]]]) -> None
        if ydata is None:
            self._ydata = []
            self._is_empty = True
        elif not isinstance(ydata, list):
            self._ydata = []
            self._is_empty = True
            raise TypeError("Data format not recognized : type(ydata) = {}".format(type(ydata).__name__))
        elif len(ydata) == 0:
            self._ydata = []
            self._is_empty = True
        else:
            self._ydata = ydata
            self._is_empty = False

    def _create_logscale_bins(self, min_bin, max_bin):
        # type: (float, float) -> numpy.ndarray
        log_min = math.log10(min_bin)
        log_max = math.log10(max_bin)
        num_bins = self._num_logscale_bins
        dlog = (log_max - log_min) / float(num_bins)
        bins = []
        for i in range(num_bins + 1):
            ibin = log_min + i * dlog
            bins.append(math.pow(10, ibin))
        return numpy.array(bins, dtype=numpy.float64)

    def make_tgraph(self, logscale=False):
        # type: (...) -> ROOT.TH2D
        if self.xdata is None or self.ydata is None:
            raise RuntimeError("Please insert some data in the graph")
        if len(self._xdata) != len(self.ydata):
            raise IndexError("xdata ({}) and ydata ({}) length mismatch".format(len(self.xdata), len(self.ydata)))
        num_history_bins = len(self.xdata)
        min_history_bin = min(self.xdata)
        max_history_bin = max(self.xdata)
        flat_ydata = [item for sublist in self.ydata for item in sublist]
        min_ybin = int(min(flat_ydata))
        max_ybin = int(max(flat_ydata))
        if logscale:
            min_ybin -= int(0.1 * abs(max_ybin - min_ybin))
            min_ybin = max(1., min_ybin)
            max_ybin += int(0.1 * abs(max_ybin - min_ybin))
            th2d = ROOT.TH2D(self.id, self.title,
                             num_history_bins, min_history_bin, max_history_bin,
                             self._num_logscale_bins, self._create_logscale_bins(min_ybin, max_ybin))
        else:
            min_ybin -= int(0.1 * abs(max_ybin - min_ybin))
            max_ybin += int(0.1 * abs(max_ybin - min_ybin))
            num_ybins = abs(max_ybin - min_ybin + 1)
            th2d = ROOT.TH2D(self.id, self.title,
                             num_history_bins, min_history_bin, max_history_bin,
                             num_ybins, min_ybin, max_ybin)
        for counter, i in enumerate(self.xdata):
            for j in self.ydata[counter]:
                th2d.Fill(i, j)
        ROOT.gStyle.SetPalette(ROOT.kRainBow)
        ROOT.gStyle.SetOptStat("MR")
        ROOT.gStyle.SetNumberContours(100)
        th2d.SetMarkerStyle(ROOT.kFullDotMedium)
        th2d.GetXaxis().SetNdivisions(9, 3, 0, ROOT.kTRUE)
        th2d.GetXaxis().SetTimeDisplay(1)
        th2d.GetXaxis().SetTimeFormat("#splitline{%d %b}{%H:%M}%F1970-01-01 00:00:00")
        th2d.GetXaxis().SetLabelOffset(0.03)
        th2d.SetStats(ROOT.kFALSE)
        th2d.GetYaxis().SetTitleColor(self.yaxis_color)
        th2d.GetYaxis().SetLabelColor(self.yaxis_color)
        th2d.GetYaxis().SetAxisColor(self.yaxis_color)
        return th2d
