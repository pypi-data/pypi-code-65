#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import abc
import ctypes
import os
from datetime import datetime

import ROOT
import numpy
from typing import List, Union, Optional

import wagascianpy.analysis.spill
import wagascianpy.database.wagascidb
import wagascianpy.plotting.colors
import wagascianpy.plotting.colors as colors
import wagascianpy.plotting.detector
import wagascianpy.plotting.graph
import wagascianpy.plotting.harvest
import wagascianpy.plotting.marker
import wagascianpy.plotting.topology
import wagascianpy.utils.utils

ROOT.PyConfig.IgnoreCommandLineOptions = True

# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

# compatible with Python 2 *and* 3
try:
    # noinspection PyUnresolvedReferences
    IntTypes = (int, long)  # Python2
except NameError:
    IntTypes = int  # Python3


class Plotter(ABC):

    def __init__(self,
                 output_file_path="./plot.pdf",
                 save_tfile=False,
                 enabled_markers=wagascianpy.plotting.marker.MarkerTuple(run=False, maintenance=False, trouble=False)):
        # type: (str, bool, wagascianpy.plotting.marker.MarkerTuple) -> None
        ROOT.PyConfig.IgnoreCommandLineOptions = True
        ROOT.gROOT.IsBatch()
        self._canvas = ROOT.TCanvas("canvas", "canvas", 1280, 720)
        self._title = ""
        self._graphs = []
        self._markers = []
        self._multi_graph = None
        self._1d_draw_options = "AL"
        self._2d_draw_options = "ZCOLPCOL"
        self._output_file_path = output_file_path
        self._enabled_markers = enabled_markers
        self._save_tfile = save_tfile
        self._plot_legend_flag = False
        self._xdata_is_datetime = True
        self._logscale = False

    def template_plotter(self):
        # type: (...) -> None
        self._graphs = self.setup_graphs()
        self.set_title()
        for graph in self._graphs:
            self.gather_data(graph)
        self.change_graph_titles(self._graphs)
        self.build_multigraph()
        self.change_yaxis_title(self._multi_graph)
        self.add_run_markers()
        self.add_maintenance_day_markers()
        self.add_trouble_markers()
        self.plot()
        if self._save_tfile:
            self.save()
        self._canvas.Close()

    @property
    def plot_legend_flag(self):
        # type: (...) -> bool
        return self._plot_legend_flag

    @plot_legend_flag.setter
    def plot_legend_flag(self, plot_legend_flag):
        # type: (bool) -> None
        if not isinstance(plot_legend_flag, bool):
            raise TypeError("Plot legend flag must be a boolean")
        self._plot_legend_flag = plot_legend_flag

    @property
    def draw_options_1d(self):
        # type: (...) -> str
        return self._1d_draw_options

    @draw_options_1d.setter
    def draw_options_1d(self, draw_options):
        # type: (str) -> None
        self._1d_draw_options = draw_options

    @property
    def draw_options_2d(self):
        # type: (...) -> str
        return self._2d_draw_options

    @draw_options_2d.setter
    def draw_options_2d(self, draw_options):
        # type: (str) -> None
        self._2d_draw_options = draw_options

    @property
    def xdata_is_datetime(self):
        # type: (...) -> bool
        return self._xdata_is_datetime

    @xdata_is_datetime.setter
    def xdata_is_datetime(self, xdata_is_datetime):
        # type: (bool) -> None
        assert isinstance(xdata_is_datetime, bool), "xdata_is_datetime only accept a boolean value"
        self._xdata_is_datetime = xdata_is_datetime

    @property
    def logscale(self):
        # type: (...) -> bool
        return self._logscale

    @logscale.setter
    def logscale(self, logscale):
        # type: (bool) -> None
        self._logscale = logscale

    @abc.abstractmethod
    def set_title(self):
        pass

    @abc.abstractmethod
    def setup_graphs(self):
        pass

    @abc.abstractmethod
    def gather_data(self, graph):
        pass

    def build_multigraph(self):
        # type: (...) -> None
        self._multi_graph = ROOT.TMultiGraph()
        self._multi_graph.SetName("multi_graph")
        ROOT.TGaxis.SetMaxDigits(3)
        for graph in self._graphs:
            if not graph.is_empty() and not isinstance(graph, wagascianpy.plotting.graph.Graph2D):
                self._multi_graph.Add(graph.make_tgraph())
                if graph.yaxis_color != wagascianpy.plotting.colors.Colors.Black.value:
                    self._multi_graph.GetYaxis().SetTitleColor(graph.yaxis_color)
                    self._multi_graph.GetYaxis().SetLabelColor(graph.yaxis_color)
                    self._multi_graph.GetYaxis().SetAxisColor(graph.yaxis_color)
        self._multi_graph.SetTitle(self._title)
        if self._xdata_is_datetime:
            self._multi_graph.GetXaxis().SetNdivisions(9, 3, 0, ROOT.kTRUE)
            self._multi_graph.GetXaxis().SetTimeDisplay(1)
            self._multi_graph.GetXaxis().SetTimeFormat("#splitline{%d %b}{%H:%M}%F1970-01-01 00:00:00")
            self._multi_graph.GetXaxis().SetLabelOffset(0.03)

    def add_maintenance_day_markers(self):
        # type: (...) -> None
        if self._enabled_markers.maintenance and hasattr(self, "_start") and hasattr(self, "_stop"):
            if hasattr(self, "_wagasci_database"):
                database = self._wagasci_database
            else:
                database = None
            self.make_maintenance_day_markers(start=self._start, stop=self._stop, wagasci_database=database)

    def add_run_markers(self):
        # type: (...) -> None
        if self._enabled_markers.run and hasattr(self, "_start") and hasattr(self, "_stop"):
            if hasattr(self, "_wagasci_database"):
                database = self._wagasci_database
            else:
                database = None
            self.make_run_markers(start=self._start, stop=self._stop, wagasci_database=database)

    def add_trouble_markers(self):
        # type: (...) -> None
        if self._enabled_markers.trouble and hasattr(self, "_start") and hasattr(self, "_stop"):
            if hasattr(self, "_wagasci_database"):
                database = self._wagasci_database
            else:
                database = None
            self.make_trouble_markers(start=self._start, stop=self._stop, wagasci_database=database)

    def change_graph_titles(self, graphs):
        # type: (List[wagascianpy.plotting.graph.Graph]) -> None
        pass

    def change_yaxis_title(self, multigraph):
        # type: (ROOT.TMultiGraph) -> None
        pass

    def make_run_markers(self, wagasci_database, start, stop=None):
        # type: (str, Union[int, datetime], Optional[Union[int, datetime]]) -> None
        with wagascianpy.database.wagascidb.WagasciDataBase(db_location=wagasci_database, repo_location="") as db:
            if isinstance(start, IntTypes):
                if not stop:
                    stop = db.get_last_run_number(only_good=False)
                records = db.get_run_interval(run_number_start=start, run_number_stop=stop, only_good=False)
            else:
                if not stop:
                    stop = datetime.now()
                records = db.get_time_interval(datetime_start=start, datetime_stop=stop, only_good=False,
                                               include_overlapping=False)
        counter = 0
        markers = []
        for record in records:
            marker = wagascianpy.plotting.marker.DoubleMarker(left_position=record["start_time"],
                                                              right_position=record["stop_time"],
                                                              left_text="WAGASCI run %s" % record["run_number"],
                                                              right_text="",
                                                              line_color=colors.Colors.Blue)
            if counter % 2 == 0:
                marker.fill_color = colors.Colors.Azure.value
            else:
                marker.fill_color = colors.Colors.Orange.value
            marker.transparency = 0.1
            markers.append(marker)
            counter += 1
        self._markers += markers

    def make_maintenance_day_markers(self, wagasci_database, start, stop=None):
        # type: (str, Union[int, datetime], Optional[Union[int, datetime]]) -> None
        markers = wagascianpy.plotting.marker.MaintenanceDays(
            start=start, stop=stop, wagasci_database=wagasci_database
        ).get_markers(include_overlapping=False)
        self._markers += markers

    def make_trouble_markers(self, wagasci_database, start, stop=None):
        # type: (str, Union[int, datetime], Optional[Union[int, datetime]]) -> None
        markers = wagascianpy.plotting.marker.TroubleEvents(
            start=start, stop=stop, wagasci_database=wagasci_database
        ).get_markers(include_overlapping=False)
        self._markers += markers

    def _has_both_graph1d_and_graph2d(self):
        # type: (...) -> bool
        has_graph1d = self._how_many_graph1d() > 0
        has_graph2d = self._how_many_graph2d() > 0
        return has_graph2d and has_graph1d

    def _how_many_graph1d(self):
        # type: (...) -> int
        return sum(map(lambda g: not isinstance(g, wagascianpy.plotting.graph.Graph2D) and not g.is_empty(),
                       self._graphs))

    def _how_many_graph2d(self):
        # type: (...) -> int
        return sum(map(lambda g: isinstance(g, wagascianpy.plotting.graph.Graph2D) and not g.is_empty(),
                       self._graphs))

    def plot(self):
        # type: (...) -> None

        # PREPARE CANVAS
        ROOT.gStyle.Reset("Modern")
        ROOT.gStyle.SetTitleFontSize(0.035)
        pad1 = ROOT.TPad("pad1", "", 0, 0, 1, 1)
        pad2 = ROOT.TPad("pad2", "", 0, 0, 1, 1)
        self._canvas.cd()
        if self._has_both_graph1d_and_graph2d():
            self._canvas.SetFillColor(0)
            self._canvas.SetBorderMode(0)
            pad1.SetGrid()
            pad2.SetFillStyle(4000)
            pad2.SetFrameFillStyle(0)
            pad1.Draw()
            pad1.cd()

        # PLOT 2D HISTOGRAMS
        for graph in self._graphs:
            if isinstance(graph, wagascianpy.plotting.graph.Graph2D) and not graph.is_empty():
                tgraph = graph.make_tgraph(self.logscale)
                tgraph.SetTitle(self._title)
                tgraph.Draw(self.draw_options_2d)
                tgraph.GetYaxis().SetTitleOffset(0.75)
                if self.logscale:
                    self._canvas.SetLogy()
                    pad1.SetLogy()

        # PLOT 1D GRAPHS
        ROOT.gPad.Update()
        xmin = ctypes.c_double(0)
        ymin = ctypes.c_double(0)
        xmax = ctypes.c_double(0)
        ymax = ctypes.c_double(0)
        if self._has_both_graph1d_and_graph2d():
            pad1.GetRangeAxis(xmin, ymin, xmax, ymax)
            ymin = self._multi_graph.GetYaxis().GetXmin()
            ymax = self._multi_graph.GetYaxis().GetXmax()
            pad2.RangeAxis(xmin.value, ymin, xmax.value, ymax)
            pad2.Draw()
            pad2.cd()
        if self._how_many_graph1d() > 0:
            self._multi_graph.Draw(self.draw_options_1d)

        # PLOT MARKERS
        ROOT.gPad.Update()
        tobjects = []
        for marker in self._markers:
            tobjects += marker.make_tobjects()
        for tobj in tobjects:
            tobj.Draw()
        if self._plot_legend_flag:
            tlegend = ROOT.TLegend(0.13, 0.7, 0.4, 0.89)
            tlegend.SetFillColorAlpha(ROOT.kWhite, 1.)
            for graph in [graph for graph in self._graphs if not graph.is_empty()]:
                opt = "f"
                if "l" in self.draw_options_1d.lower():
                    opt += "l"
                if "p" in self.draw_options_1d.lower():
                    opt += "p"
                tlegend.AddEntry(graph.id, graph.title, opt)
            tlegend.Draw()

        # PRINT TO FILE
        ROOT.gPad.Update()
        self._canvas.Print(self._output_file_path)

    def save(self):
        # type: (...) -> None
        output_path = os.path.splitext(self._output_file_path)[0] + ".root"
        output_tfile = ROOT.TFile(output_path, "RECREATE")
        output_tfile.cd()
        self._canvas.Write()
        self._multi_graph.Write()
        output_tfile.Write()
        output_tfile.Close()


class BsdPlotter(Plotter, ABC):

    def __init__(self, bsd_database, bsd_repository, start,
                 stop=None, wagasci_database=None, t2krun=10,
                 *args, **kwargs):
        super(BsdPlotter, self).__init__(*args, **kwargs)
        self._bsd_database = bsd_database
        self._bsd_repository = bsd_repository
        self._wagasci_database = wagasci_database
        self._t2krun = t2krun
        self._start = start
        self._stop = stop
        self._patron = wagascianpy.plotting.harvest.Patron(start=start, stop=stop, wagasci_database=wagasci_database)
        self._bsd_harvester_class = None

    @abc.abstractmethod
    def set_title(self):
        pass

    @abc.abstractmethod
    def setup_graphs(self):
        pass

    def gather_data(self, graph):
        assert self._bsd_harvester_class is not None, \
            "Derived class must set the _bsd_harvester_class attribute"
        if graph.id != "BSD":
            raise ValueError("Wrong graph with title {} and ID {}".format(graph.title, graph.id))
        self._patron.harvester = self._bsd_harvester_class(
            database=self._bsd_database, repository=self._bsd_repository, t2krun=self._t2krun)
        graph.xdata, graph.ydata = self._patron.gather_data()


class BsdPotPlotter(BsdPlotter):

    def __init__(self, *args, **kwargs):
        super(BsdPotPlotter, self).__init__(*args, **kwargs)
        self._bsd_harvester_class = wagascianpy.plotting.harvest.BsdPotHarvester

    def set_title(self):
        self._title = "Delivered POT during run {};;POT".format(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = True
        graph = wagascianpy.plotting.graph.Graph("Delivered POT", "BSD")
        graph.color = wagascianpy.plotting.colors.Colors.Red.value
        return [graph]


class BsdSpillPlotter(BsdPlotter):

    def __init__(self, *args, **kwargs):
        super(BsdSpillPlotter, self).__init__(*args, **kwargs)
        self._bsd_harvester_class = wagascianpy.plotting.harvest.BsdSpillHarvester

    def set_title(self):
        self._title = "BSD spill history during run {};;spill number".format(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = True
        graph = wagascianpy.plotting.graph.Graph("BSD spill history", "BSD")
        graph.color = wagascianpy.plotting.colors.Colors.Red.value
        return [graph]


class WagasciPlotter(Plotter, ABC):

    def __init__(self,
                 bsd_database,  # type: str
                 bsd_repository,  # type: str
                 wagasci_database,  # type: str
                 wagasci_repository,  # type: str
                 start,  # type: Union[str, int]
                 stop=None,  # type: Optional[Union[str, int]]
                 topology=None,  # type: Optional[str]
                 t2krun=10,  # type: int
                 only_good=False,  # type: bool
                 *args, **kwargs):
        super(WagasciPlotter, self).__init__(*args, **kwargs)
        self._bsd_database = bsd_database
        self._bsd_repository = bsd_repository
        self._wagasci_database = wagasci_database
        self._wagasci_repository = wagasci_repository
        self._t2krun = t2krun
        self._start = start
        self._stop = stop
        self._patron = wagascianpy.plotting.harvest.Patron(start=start, stop=stop, wagasci_database=wagasci_database)
        self._wagasci_harvester_class = None
        self._bsd_harvester_class = None
        self._topology = topology if topology is not None else wagascianpy.plotting.topology.Topology()
        self._only_good = only_good

    @abc.abstractmethod
    def set_title(self):
        pass

    @abc.abstractmethod
    def setup_graphs(self):
        graphs = []
        for enabled_detector in self._topology.get_enabled():
            graph = wagascianpy.plotting.graph.Graph(enabled_detector.name)
            graph.color = enabled_detector.name
            graphs.append(graph)
        return graphs

    def gather_data(self, graph):
        if graph.id == "BSD":
            assert self._bsd_harvester_class is not None, \
                "Derived class must set the _bsd_harvester_class attribute"
            if not self._patron.is_harvester_ready() or \
                    not isinstance(self._patron.harvester, self._bsd_harvester_class):
                self._patron.harvester = self._bsd_harvester_class(
                    database=self._bsd_database,
                    repository=self._bsd_repository,
                    t2krun=self._t2krun)
            graph.xdata, graph.ydata = self._patron.gather_data()
        else:
            for enabled_detector in self._topology.get_enabled():
                if graph.id == str(enabled_detector.name):
                    assert self._wagasci_harvester_class is not None, \
                        "Derived class must set the _wagasci_harvester_class attribute"
                    if not self._patron.is_harvester_ready() or \
                            not isinstance(self._patron.harvester, self._wagasci_harvester_class):
                        self._patron.harvester = self._wagasci_harvester_class(
                            database=self._wagasci_database,
                            repository=self._wagasci_repository,
                            t2krun=self._t2krun,
                            topology=self._topology)
                    graph.xdata, graph.ydata = self._patron.gather_data(enabled_detector.name, self._only_good)


class WagasciPotPlotter(WagasciPlotter):

    def __init__(self, *args, **kwargs):
        super(WagasciPotPlotter, self).__init__(*args, **kwargs)
        self._wagasci_harvester_class = wagascianpy.plotting.harvest.WagasciPotHarvester
        self._bsd_harvester_class = wagascianpy.plotting.harvest.BsdPotHarvester

    def set_title(self):
        self._title = "#splitline{Accumulated POT for each subdetector during run %s}" \
                      "{after spill matching but before data quality};;POT" % str(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = True
        self.xdata_is_datetime = True
        graphs = super(WagasciPotPlotter, self).setup_graphs()
        bsd_graph = wagascianpy.plotting.graph.Graph("Delivered POT", "BSD")
        bsd_graph.color = wagascianpy.plotting.colors.Colors.Red.value
        graphs.append(bsd_graph)
        return graphs

    def change_graph_titles(self, graphs):
        bsd_graph = next((bsd_graph for bsd_graph in graphs if bsd_graph.id == "BSD"), None)
        if bsd_graph is None:
            return
        if bsd_graph.ydata.size == 0:
            bsd_pot = 0
        else:
            bsd_pot = numpy.amax(bsd_graph.ydata)
        bsd_graph.title += " = {:.2e} POT".format(bsd_pot)
        for igraph in [graph for graph in graphs if graph.id != "BSD"]:
            if igraph.ydata.size == 0:
                max_pot = 0
            else:
                max_pot = numpy.amax(igraph.ydata)
            percent = 100 * float(max_pot) / float(bsd_pot) if bsd_pot != 0 else 0
            igraph.title += " {:.1f}%".format(percent)


class WagasciSpillHistoryPlotter(WagasciPlotter):

    def __init__(self, *args, **kwargs):
        super(WagasciSpillHistoryPlotter, self).__init__(*args, **kwargs)
        self._wagasci_harvester_class = wagascianpy.plotting.harvest.WagasciSpillHistoryHarvester

    def set_title(self):
        self._title = "#splitline{WAGASCI spill history during run %s}" \
                      "{before bit flip fixing};;spill number" % str(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = True
        self.draw_options_1d = "AP"
        graphs = super(WagasciSpillHistoryPlotter, self).setup_graphs()
        for graph in graphs:
            graph.yrange = wagascianpy.plotting.graph.Range(
                lower_bound=wagascianpy.analysis.spill.WAGASCI_MINIMUM_SPILL,
                upper_bound=wagascianpy.analysis.spill.WAGASCI_MAXIMUM_SPILL)

        return graphs


class WagasciFixedSpillPlotter(WagasciPlotter):

    def __init__(self, *args, **kwargs):
        super(WagasciFixedSpillPlotter, self).__init__(*args, **kwargs)
        self._wagasci_harvester_class = wagascianpy.plotting.harvest.WagasciFixedSpillHarvester

    def set_title(self):
        self._title = "#splitline{WAGASCI fixed spill history during run %s}" \
                      "{after bit flip fixing but before data quality};;spill number" % str(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = True
        self.draw_options_1d = "AP"
        return super(WagasciFixedSpillPlotter, self).setup_graphs()


class WagasciSpillNumberPlotter(WagasciPlotter):

    def __init__(self, *args, **kwargs):
        super(WagasciSpillNumberPlotter, self).__init__(*args, **kwargs)
        self._wagasci_harvester_class = wagascianpy.plotting.harvest.WagasciSpillNumberHarvester

    def set_title(self):
        self._title = "#splitline{WAGASCI spill number during run %s}" \
                      "{before bit flip fixing and BSD spill matching};event number (increasing in time);spill number" \
                      % str(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = False
        self.draw_options_1d = "AP"
        graphs = super(WagasciSpillNumberPlotter, self).setup_graphs()
        for graph in graphs:
            graph.yrange = wagascianpy.plotting.graph.Range(
                lower_bound=wagascianpy.analysis.spill.WAGASCI_MINIMUM_SPILL,
                upper_bound=wagascianpy.analysis.spill.WAGASCI_MAXIMUM_SPILL)

        return graphs


class TemperaturePlotter(WagasciPlotter):

    def __init__(self, *args, **kwargs):
        super(TemperaturePlotter, self).__init__(*args, **kwargs)
        self._wagasci_harvester_class = wagascianpy.plotting.harvest.TemperatureHarvester

    def set_title(self):
        self._title = "WAGASCI temperature history during run %s};;Temperature (C°)" % str(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = True
        self.xdata_is_datetime = True
        return super(TemperaturePlotter, self).setup_graphs()


class HumidityPlotter(WagasciPlotter):

    def __init__(self, *args, **kwargs):
        super(HumidityPlotter, self).__init__(*args, **kwargs)
        self._wagasci_harvester_class = wagascianpy.plotting.harvest.HumidityHarvester

    def set_title(self):
        self._title = "WAGASCI humidity history during run %s};;Humidity (%%)" % str(self._t2krun)

    def setup_graphs(self):
        self.plot_legend_flag = True
        self.xdata_is_datetime = True
        return super(HumidityPlotter, self).setup_graphs()


class DataQualityPlotter(Plotter, ABC):

    def __init__(self, data_quality_location, data_quality_filename, topology=None,
                 *args, **kwargs):
        super(DataQualityPlotter, self).__init__(*args, **kwargs)
        self._data_quality_location = data_quality_location
        self._data_quality_filename = data_quality_filename
        self._patron = wagascianpy.plotting.harvest.Patron()
        self._data_quality_harvester_class = None
        self._temperature_harvester_class = None
        self._topology = topology if topology is not None else wagascianpy.plotting.topology.Topology(
            iterate_by_dif=True)

    @abc.abstractmethod
    def set_title(self):
        pass

    @abc.abstractmethod
    def setup_graphs(self):
        graphs = [wagascianpy.plotting.graph.Graph2D("history")]
        if self._topology.how_many_enabled() == 1:
            for enabled_detector in self._topology.get_enabled():
                graph = wagascianpy.plotting.graph.Graph(enabled_detector.name)
                graph.color = wagascianpy.plotting.colors.Colors.Red
                graph.yaxis_color = wagascianpy.plotting.colors.Colors.Red
                graphs.append(graph)
        return graphs

    def change_yaxis_title(self, multigraph):
        # type: (ROOT.TMultiGraph) -> None
        multigraph.GetYaxis().SetTitle("Temperature (Celsius Degrees)")

    def gather_data(self, graph):
        if not self._topology.iterate_by_dif:
            raise RuntimeError("You must iterate through the active detectors by DIF")
        if isinstance(graph, wagascianpy.plotting.graph.Graph2D):
            assert self._data_quality_harvester_class is not None, \
                "Derived class must set the _data_quality_harvester_class attribute"
            self._patron.harvester = self._data_quality_harvester_class(
                database=None,
                repository=self._data_quality_location,
                t2krun=None,
                topology=self._topology,
                filename=self._data_quality_filename)
            graph.xdata, graph.ydata = self._patron.gather_data()
        else:
            assert self._temperature_harvester_class is not None, \
                "Derived class must set the _temperature_harvester_class attribute"
            for enabled_detector in self._topology.get_enabled():
                if graph.id == str(enabled_detector.name):
                    if not self._patron.is_harvester_ready() or \
                            not isinstance(self._patron.harvester, self._temperature_harvester_class):
                        self._patron.harvester = self._temperature_harvester_class(
                            database=None,
                            repository=self._data_quality_location,
                            t2krun=None,
                            topology=self._topology,
                            filename=self._data_quality_filename)
                    graph.xdata, graph.ydata = self._patron.gather_data(detector_name=enabled_detector.name)


class GainHistoryPlotter(DataQualityPlotter):

    def __init__(self, *args, **kwargs):
        super(GainHistoryPlotter, self).__init__(*args, **kwargs)
        self._data_quality_harvester_class = wagascianpy.plotting.harvest.GainHarvester
        self._temperature_harvester_class = wagascianpy.plotting.harvest.DataQualityTemperatureHarvester

    def set_title(self):
        self._title = "Gain history"
        if self._topology.how_many_enabled() == 1:
            self._title += " for %s" % self._topology.get_enabled()[0].name
        self._title += ";;Gain (ADC counts)"

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = True
        self.draw_options_2d = "COL"
        if self._topology.how_many_enabled() == 1:
            self.draw_options_2d += "Y+"
        else:
            self.draw_options_2d += "Z"
        self.draw_options_1d = "AL"
        return super(GainHistoryPlotter, self).setup_graphs()


class DarkNoiseHistoryPlotter(DataQualityPlotter):

    def __init__(self, *args, **kwargs):
        super(DarkNoiseHistoryPlotter, self).__init__(*args, **kwargs)
        self._data_quality_harvester_class = wagascianpy.plotting.harvest.DarkNoiseHarvester
        self._temperature_harvester_class = wagascianpy.plotting.harvest.DataQualityTemperatureHarvester

    def set_title(self):
        self._title = "Dark noise history"
        if self._topology.how_many_enabled() == 1:
            self._title += " for %s" % self._topology.get_enabled()[0].name
        self._title += ";;Dark noise (Hz)"

    def setup_graphs(self):
        self.plot_legend_flag = False
        self.xdata_is_datetime = True
        self.draw_options_2d = "COL"
        if self._topology.how_many_enabled() == 1:
            self.draw_options_2d += "Y+"
        else:
            self.draw_options_2d += "Z"
        self.draw_options_1d = "AL"
        self.logscale = True

        return super(DarkNoiseHistoryPlotter, self).setup_graphs()
