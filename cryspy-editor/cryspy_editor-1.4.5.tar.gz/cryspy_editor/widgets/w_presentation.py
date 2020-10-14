"""Functions to create docks for dock-area."""
from typing import List
import numpy
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import pyqtgraph.dockarea as pg_da

from cryspy import AtomSiteL, Crystal, Cell, SpaceGroup, \
    PdInstrResolution, Diffrn, \
    PdProcL, PdBackgroundL, Pd, PdMeasL, RhoChi, Chi2, RefineLs, \
    Pd2dMeas, Pd2dProc, Pd2d, value_error_to_string, \
    Setup, PhaseL, Range, DiffrnRadiation, Pd2dBackground, \
    Pd2dInstrResolution, DiffrnOrientMatrix, DiffrnReflnL, Phase, \
    AtomElectronConfigurationL, MEM, PdPeakL, Pd2dPeakL

ICON_SIZE = 50

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

pg_pen_black = pg.mkPen("k", width=5)
pg_pen_black_thick = pg.mkPen("k", width=2)


def w_for_presentation(obj, thread: QtCore.QThread) -> tuple:
    """Give tuple of docks for Dockarea."""
    if obj is None:
        return ()

    if isinstance(obj, RhoChi):
        docks = dock_rhochi(obj, thread)
        return docks
    elif isinstance(obj, MEM):
        docks = dock_mem(obj, thread)
        return docks
    elif isinstance(obj, Crystal):
        docks = dock_crystal(obj, thread)
        return docks
    elif isinstance(obj, Pd):
        docks = dock_pd(obj, thread)
        return docks
    elif isinstance(obj, Pd2d):
        docks = dock_pd2d(obj, thread)
        return docks
    elif isinstance(obj, Diffrn):
        docks = dock_diffrn(obj, thread)
        return docks
    return ()


def dock_rhochi(obj: RhoChi, thread: QtCore.QThread):
    """Dock for RhoChi object."""
    crystals = obj.crystals()
    experiments = obj.experiments()
    docks = []
    flag_crystals = len(crystals) != 0
    flag_experiments = len(experiments) != 0
    flag_diffrn = any([isinstance(exp, Diffrn) for exp in experiments])

    for experiment in experiments:
        if isinstance(experiment, Pd):
            docks.extend(list(dock_pd(experiment, thread)))
        elif isinstance(experiment, Pd2d):
            docks.extend(list(dock_pd2d(experiment, thread)))
        elif isinstance(experiment, Diffrn):
            docks.extend(list(dock_diffrn(experiment, thread)))

    if obj.is_defined():
        l_var_name = obj.get_variable_names()
        l_var_name_sigma = [tuple(list(name[:-1]) +
                                  [(f"{name[-1][0]:}_sigma", name[-1][1])])
                            for name in l_var_name]
        l_var_param = [obj.get_variable_by_name(name) for name in l_var_name]
        l_var_sigma = [obj.get_variable_by_name(name)
                       for name in l_var_name_sigma]
        l_var_str = [value_error_to_string(param, sigma)
                     for param, sigma in zip(l_var_param, l_var_sigma)]
        l_var_list = [f"{name[-1][0]:}: {param:}" for name, param in
                      zip(l_var_name, l_var_str)]
        if len(l_var_list) != 0:
            widget_list = QtWidgets.QListWidget()
            widget_list.addItems(l_var_list)
            docks.append(pg_da.Dock("Variables", widget=widget_list,
                                    autoOrientation=False))

    # Action doc
    layout_actions = QtWidgets.QHBoxLayout()
    if (flag_crystals & flag_experiments & obj.is_defined()):
        cb_1 = QtWidgets.QPushButton("Calc. Chi square")
        cb_1.clicked.connect(lambda: run_function(obj.calc_chi_sq,
                                                  (True, ), thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        # cb_1.setMaximumHeight(ICON_SIZE)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#AFD;")

        cb_2 = QtWidgets.QPushButton("Refine")
        cb_2.clicked.connect(lambda: run_function(obj.refine, (False, "BFGS",),
                                                  thread))
        cb_2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        # cb_2.setMaximumHeight(ICON_SIZE)
        cb_2.setMinimumHeight(ICON_SIZE)
        cb_2.setStyleSheet("background-color:#DAF;")
        layout_actions.addWidget(cb_1)
        layout_actions.addWidget(cb_2)
    elif not(flag_crystals & flag_experiments):
        if not flag_crystals:
            cb_1 = QtWidgets.QPushButton("Add crytal")
            # cb_1.setStyleSheet("background-color:red;")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [
                Crystal(data_name="phase")], thread))
            layout_actions.addWidget(cb_1)

        if not flag_experiments:
            cb_2 = QtWidgets.QPushButton("Add diffrn")
            cb_2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_2.setMaximumHeight(ICON_SIZE)
            cb_2.setMinimumHeight(ICON_SIZE)
            cb_2.clicked.connect(lambda: add_items(obj, [
                Diffrn(data_name="mono")], thread))
            cb_3 = QtWidgets.QPushButton("Add pd")
            cb_3.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_3.clicked.connect(lambda: add_items(obj, [
                Pd(data_name="powder1d")], thread))
            cb_3.setMaximumHeight(ICON_SIZE)
            cb_3.setMinimumHeight(ICON_SIZE)
            cb_4 = QtWidgets.QPushButton("Add pd2d")
            cb_4.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_4.setMaximumHeight(ICON_SIZE)
            cb_4.setMinimumHeight(ICON_SIZE)
            cb_4.clicked.connect(lambda: add_items(obj, [
                Pd2d(data_name="powder2d")], thread))
            layout_actions.addWidget(cb_2)
            layout_actions.addWidget(cb_3)
            layout_actions.addWidget(cb_4)
    else:
        qlabel = QtWidgets.QLabel(
            "To run calculations all items should be defined.")
        qlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Expanding)
        layout_actions.addWidget(qlabel)
    if (flag_diffrn & flag_crystals):
        cb_1 = QtWidgets.QPushButton("Estimate F_M")
        # cb_1.setStyleSheet("background-color:red;")
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#FAD;")
        cb_1.clicked.connect(lambda: run_function(
            obj.estimate_f_mag_for_diffrn, (), thread))
        layout_actions.addWidget(cb_1)
    layout_actions.addStretch(1)

    widget_actions = QtWidgets.QWidget()
    widget_actions.setLayout(layout_actions)
    docks.append(pg_da.Dock("Actions RhoChi", widget=widget_actions,
                            autoOrientation=False))

    return tuple(docks)


def dock_mem(obj: MEM, thread: QtCore.QThread):
    """Dock for MEM object."""
    crystals = obj.crystals()
    experiments = obj.experiments()
    docks = []
    flag_crystals = len(crystals) != 0
    flag_experiments = len(experiments) != 0

    for experiment in experiments:
        docks.extend(list(dock_diffrn(experiment, thread)))

    # Action doc
    layout_actions = QtWidgets.QHBoxLayout()
    if (flag_crystals & flag_experiments & obj.is_defined()):
        if flag_crystals:
            crystal = crystals[0]
            if not(crystal.is_attribute("atom_electron_configuration")):
                cb_1 = QtWidgets.QPushButton(
                    "Create AtomElectronConfiguration")
                cb_1.clicked.connect(lambda: crystal.add_items([
                    AtomElectronConfigurationL()]))
                cb_1.clicked.connect(lambda: run_function(pass_func, (),
                                                          thread))
                cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
                cb_1.setMinimumHeight(ICON_SIZE)
                cb_1.setStyleSheet("background-color:#ADF;")
                layout_actions.addWidget(cb_1)

        cb_1 = QtWidgets.QPushButton("Create prior density")
        cb_1.clicked.connect(lambda: run_function(obj.create_prior_density, (),
                                                  thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#DFA;")
        layout_actions.addWidget(cb_1)

        cb_1 = QtWidgets.QPushButton("Calculate FR")
        cb_1.clicked.connect(lambda: run_function(obj.calc_fr, (),
                                                  thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#FAD;")
        layout_actions.addWidget(cb_1)

        cb_1 = QtWidgets.QPushButton("Maximize entropy")
        cb_1.clicked.connect(lambda: run_function(obj.maximize_entropy, (),
                                                  thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#DAF;")
        layout_actions.addWidget(cb_1)

        cb_1 = QtWidgets.QPushButton("Chi refinement")
        cb_1.clicked.connect(lambda: run_function(obj.refine_susceptibility,
                                                  (), thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#AFD;")
        layout_actions.addWidget(cb_1)

        cb_1 = QtWidgets.QPushButton("Run cycle")
        cb_1.clicked.connect(lambda: run_function(obj.make_cycle, (),
                                                  thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#FDA;")
        layout_actions.addWidget(cb_1)

        cb_1 = QtWidgets.QPushButton("Save to '.den' files")
        cb_1.clicked.connect(lambda: run_function(obj.save_to_file_den, (),
                                                  thread))
        cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        cb_1.setMinimumHeight(ICON_SIZE)
        cb_1.setStyleSheet("background-color:#DFD;")
        layout_actions.addWidget(cb_1)
    elif not(flag_crystals & flag_experiments):
        if not flag_crystals:
            cb_1 = QtWidgets.QPushButton("Add crytal")
            # cb_1.setStyleSheet("background-color:red;")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [
                Crystal(data_name="phase")], thread))
            layout_actions.addWidget(cb_1)

        if not flag_experiments:
            cb_2 = QtWidgets.QPushButton("Add diffrn")
            cb_2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_2.setMaximumHeight(ICON_SIZE)
            cb_2.setMinimumHeight(ICON_SIZE)
            cb_2.clicked.connect(lambda: add_items(obj, [
                Diffrn(data_name="mono")], thread))
            layout_actions.addWidget(cb_2)
    else:
        qlabel = QtWidgets.QLabel(
            "To run calculations all items should be defined.")
        qlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Expanding)
        layout_actions.addWidget(qlabel)
    layout_actions.addStretch(1)

    widget_actions = QtWidgets.QWidget()
    widget_actions.setLayout(layout_actions)
    docks.append(pg_da.Dock("Actions MEM", widget=widget_actions,
                            autoOrientation=False))

    return tuple(docks)


def pass_func():
    return


def add_items(obj, l_item, thread: QtCore.QThread):
    obj.add_items(l_item)
    thread.function = pass_func
    thread.arguments = ()
    thread.start()

def run_function(func, args, thread: QtCore.QThread):
    """Run function."""
    thread.function = func
    thread.arguments = args
    thread.start()


def dock_pd(obj: Pd, thread: QtCore.QThread):  # FIXME: dock_peak should be added
    """
    Form dock_pd.

    Based on
    --------
        - dock_proc
        - dock_meas
        - dock_chi2
        - dock_refine_ls
        - dock_peak
    """
    try:
        meas = obj.pd_meas
        f_meas = True
    except AttributeError:
        f_meas = False
    try:
        chi2 = obj.chi2
        f_chi2 = True
    except AttributeError:
        f_chi2 = False
    try:
        refine_ls = obj.refine_ls
        f_refine_ls = True
    except AttributeError:
        f_refine_ls = False
    try:
        proc = obj.pd_proc
        f_proc = True
    except AttributeError:
        f_proc = False
    try:
        phase = obj.phase
        f_phase = True
    except AttributeError:
        f_phase = False

    l_pd_peak = []
    if f_phase:
        for item in phase.items:
            try:
                pd_peak = getattr(obj, f"pd_peak_{item.label.lower():}")
                l_pd_peak.append(pd_peak)
            except AttributeError:
                pass

    docks = []

    try:
        setup = obj.setup
        f_setup = True
    except AttributeError:
        f_setup = False
    try:
        pd_instr_resolution = obj.pd_instr_resolution
        f_pd_instr_resolution = True
    except AttributeError:
        f_pd_instr_resolution = False
    try:
        pd_background = obj.pd_background
        f_pd_background = True
    except AttributeError:
        f_pd_background = False
    try:
        range_ = obj.range
        f_range = True
    except AttributeError:
        f_range = False
    # f_diffrn_radiation = obj.diffrn_radiation is not None

    if not(f_chi2 & f_meas & f_setup & f_pd_instr_resolution & f_phase &
           f_pd_background & f_range):
        layout_actions = QtWidgets.QHBoxLayout()
        if not f_chi2:
            cb_1 = QtWidgets.QPushButton("Add chi2")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Chi2()], thread))
            layout_actions.addWidget(cb_1)
        if not f_meas:
            cb_1 = QtWidgets.QPushButton("Add pd_meas")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [PdMeasL()], thread))
            layout_actions.addWidget(cb_1)
        if not f_setup:
            cb_1 = QtWidgets.QPushButton("Add setup")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Setup()], thread))
            layout_actions.addWidget(cb_1)
        if not f_pd_instr_resolution:
            cb_1 = QtWidgets.QPushButton("Add pd_instr_resolution")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [PdInstrResolution()],
                                                   thread))
            layout_actions.addWidget(cb_1)
        if not f_phase:
            cb_1 = QtWidgets.QPushButton("Add phase")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            vv = PhaseL()
            vv.items = [Phase(label="phase", igsize=0., scale=1.)]
            cb_1.clicked.connect(lambda: add_items(obj, [vv], thread))
            layout_actions.addWidget(cb_1)
        if not f_pd_background:
            cb_1 = QtWidgets.QPushButton("Add pd_background")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [PdBackgroundL()],
                                                   thread))
            layout_actions.addWidget(cb_1)
        if not f_range:
            cb_1 = QtWidgets.QPushButton("Add range")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(
                obj, [Range(ttheta_min=2, ttheta_max=100.)], thread))
            layout_actions.addWidget(cb_1)
        # if not f_diffrn_radiation:
        #     cb_1 = QtWidgets.QPushButton("Add diffrn_radiation")
        #     cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
        #                        QtWidgets.QSizePolicy.Expanding)
        #     cb_1.clicked.connect(lambda: add_items(obj, [DiffrnRadiation()],
        #                          thread))
        #     layout_actions.addWidget(cb_1)
        layout_actions.addStretch(1)
        widget_actions = QtWidgets.QWidget()
        widget_actions.setLayout(layout_actions)
        docks.append(pg_da.Dock("Actions pd", widget=widget_actions,
                                autoOrientation=False))

    if f_proc:
        docks = docks + list(dock_proc(proc, l_pd_peak))
    elif f_meas:
        docks = docks + list(dock_meas(meas))

    if f_chi2:
        docks = docks + list(dock_chi2(chi2))
    if f_refine_ls:
        docks = docks + list(dock_refine_ls(refine_ls))

    return tuple(docks)


def dock_proc(obj: PdProcL, l_pd_peak: List[PdPeakL]):
    """Form dock for PdProc object."""
    np_x_1 = numpy.array(obj.ttheta, dtype=float)
    # np_y_su_1 = numpy.array(obj.intensity_up_sigma, dtype=float)
    # np_y_sd_1 = numpy.array(obj.intensity_down_sigma, dtype=float)
    # np_y_b_1 = numpy.array(obj.intensity_bkg_calc, dtype=float)
    # np_y_u_2 = numpy.array(obj.intensity_up_total, dtype=float)
    # np_y_d_2 = numpy.array(obj.intensity_down_total, dtype=float)
    np_y_s_1 = numpy.array(obj.intensity, dtype=float)
    np_y_ss_1 = numpy.array(obj.intensity_sigma, dtype=float)
    try:
        np_y_u_1 = numpy.array(obj.intensity_up, dtype=float)
        np_y_d_1 = numpy.array(obj.intensity_down, dtype=float)
        np_y_m_1 = np_y_u_1 - np_y_d_1
        flag_polaraized = True
    except AttributeError:
        np_y_m_1 = 0*np_y_s_1
        flag_polaraized = False
    np_y_sm_1 = np_y_ss_1

    np_y_s_2 = numpy.array(obj.intensity_total, dtype=float)
    np_y_m_2 = numpy.array(obj.intensity_diff_total, dtype=float)

    # np_x_2 = numpy.array(peak.ttheta, dtype = float)
    # np_xysm_1 = numpy.vstack((np_x_1, np_y_s_1, np_y_ss_1,
    #                           np_y_s_2)).transpose()
    # np_xb_1 = numpy.vstack((np_x_1, 2*np_y_b_1)).transpose()

    vb_1 = pg.ViewBox()
    vb_1.setMouseMode(vb_1.RectMode)
    widget = pg.PlotWidget(viewBox=vb_1)
    p1 = widget.plotItem
    p2 = add_2nd_axis_to_plot(p1, label_axis_1="Intensity (a.u.)",
                              label_axis_2="Difference")
    err1 = pg.ErrorBarItem(x=np_x_1, y=np_y_s_1, top=np_y_ss_1,
                           bottom=np_y_ss_1, beam=0.5)
    p1.plot(x=np_x_1, y=np_y_s_1, name="exp", title="model",
            symbol='o', pen={'color': 0.8, 'width': 2})
    p1.plot(x=np_x_1, y=np_y_s_2, name="model", title="model",
            pen=pg_pen_black)
    p1.addItem(err1)
    p2.addItem(pg.PlotCurveItem(x=np_x_1, y=np_y_s_1-np_y_s_2,
                                pen=pg_pen_black_thick))

    [x_range_12, y_range_12] = p1.viewRange()
    y_range = y_range_12[1]-y_range_12[0]
    p2.setRange(yRange=(-0.15*y_range, 0.85*y_range))

    yrange_2 = p2.viewRange()[1]
    ysize_2 = 0.05*(yrange_2[1]-yrange_2[0])
    yshift_2 = 0.5*0.5*0.5*ysize_2*len(l_pd_peak)

    if flag_polaraized:

        vb_2 = pg.ViewBox()
        vb_2.setMouseMode(vb_2.RectMode)
        widget_2 = pg.PlotWidget(viewBox=vb_2)
        p3 = widget_2.plotItem
        p4 = add_2nd_axis_to_plot(p3, label_axis_1="Intensity (a.u.)",
                                  label_axis_2="Difference")
        err1 = pg.ErrorBarItem(x=np_x_1, y=np_y_m_1, top=np_y_sm_1,
                               bottom=np_y_ss_1, beam=0.5)
        p3.plot(x=np_x_1, y=np_y_m_1, name="exp", title="model",
                symbol='o', pen={'color': 0.8, 'width': 2})
        p3.plot(x=np_x_1, y=np_y_m_2, name="model", title="model",
                pen=pg_pen_black)
        p3.addItem(err1)
        p4.addItem(pg.PlotCurveItem(x=np_x_1, y=np_y_m_1-np_y_m_2,
                                    pen=pg_pen_black_thick))

        [x_range_34, y_range_34] = p3.viewRange()
        y_range = y_range_34[1]-y_range_34[0]
        p3.setYRange(-0.50*y_range, 0.50*y_range)
        p4.setRange(yRange=(-0.15*y_range, 0.85*y_range))

        yrange_4 = p4.viewRange()[1]
        ysize_4 = 0.05*(yrange_4[1]-yrange_4[0])
        yshift_4 = 0.5*ysize_4*len(l_pd_peak)

    for pd_peak in l_pd_peak:
        numpy_ttheta = numpy.array(pd_peak.ttheta, dtype=float)
        np_zero = 0.*numpy_ttheta
        ind_miller_2 = pg.ErrorBarItem(
            x=numpy_ttheta, y=np_zero+yshift_2, top=np_zero+yshift_2+ysize_2,
            bottom=np_zero-yshift_2+ysize_2, beam=0.0)
        p2.addItem(ind_miller_2)
        yshift_2 -= 0.5*ysize_2
        if flag_polaraized:
            ind_miller_4 = pg.ErrorBarItem(
                x=numpy_ttheta, y=np_zero+yshift_4,
                top=np_zero+yshift_4+ysize_4,
                bottom=np_zero-yshift_4+ysize_4, beam=0.0)
            p4.addItem(ind_miller_4)
            yshift_4 -= 1.0*ysize_4

    if flag_polaraized:
        dock_1 = pg_da.Dock("Sum", widget=widget, autoOrientation=False)
        dock_2 = pg_da.Dock("Difference", widget=widget_2,
                            autoOrientation=False)
        res = (dock_1, dock_2, )
    else:
        dock_1 = pg_da.Dock("Intensity", widget=widget, autoOrientation=False)
        res = (dock_1, )
    return res


def dock_meas(obj: PdMeasL):
    """Form docks for PdMeasL object."""
    np_x_1 = numpy.array(obj.ttheta, dtype=float)
    try:
        np_y_u_1 = numpy.array(obj.intensity_up, dtype=float)
        np_y_su_1 = numpy.array(obj.intensity_up_sigma, dtype=float)
        np_y_d_1 = numpy.array(obj.intensity_down, dtype=float)
        np_y_sd_1 = numpy.array(obj.intensity_down_sigma, dtype=float)
        flag_polaraized = True
    except AttributeError:
        flag_polaraized = False

    if flag_polaraized:
        np_y_s_1 = np_y_u_1 + np_y_d_1
        np_y_ss_1 = numpy.sqrt(numpy.square(np_y_su_1) +
                               numpy.square(np_y_sd_1))
        np_y_m_1 = np_y_u_1 - np_y_d_1
        np_y_sm_1 = np_y_ss_1
    else:
        np_y_s_1 = numpy.array(obj.intensity, dtype=float)
        np_y_ss_1 = numpy.array(obj.intensity_sigma, dtype=float)
        np_y_m_1 = 0*np_y_s_1
        np_y_sm_1 = np_y_ss_1

    vb_1 = pg.ViewBox()
    vb_1.setMouseMode(vb_1.RectMode)
    widget = pg.PlotWidget(viewBox=vb_1)
    p1 = widget.plotItem
    err_s = pg.ErrorBarItem(x=np_x_1, y=np_y_s_1, top=np_y_ss_1,
                            bottom=np_y_ss_1, beam=0.5)
    err_m = pg.ErrorBarItem(x=np_x_1, y=np_y_m_1, top=np_y_sm_1,
                            bottom=np_y_sm_1, beam=0.5)
    p1.plot(x=np_x_1, y=np_y_s_1, name="sum", title="Sum",
            symbol='o', pen={'color': 0.8, 'width': 2})
    p1.addItem(err_s)

    if flag_polaraized:
        p2 = add_2nd_axis_to_plot(p1, label_axis_1="Intensity (a.u.)",
                                  label_axis_2="Intensity (a.u.)")
        p2.addItem(pg.PlotCurveItem(
            x=np_x_1, y=np_y_m_1, name="diff", title="Difference",
            pen=pg_pen_black_thick))
        p2.addItem(pg.ScatterPlotItem(
            x=np_x_1, y=np_y_m_1, symbol='o', pen={'color': 0.8, 'width': 2}))
        p2.addItem(err_m)
        [x_range_12, y_range_12] = p1.viewRange()
        y_range = y_range_12[1]-y_range_12[0]
        p2.setRange(yRange=(-0.25*y_range, 0.75*y_range))

    dock_1 = pg_da.Dock("Sum/Diff.", widget=widget, autoOrientation=False)

    if flag_polaraized:
        vb_2 = pg.ViewBox()
        vb_2.setMouseMode(vb_2.RectMode)
        widget_2 = pg.PlotWidget(viewBox=vb_2)
        p3 = widget_2.plotItem
        p4 = add_2nd_axis_to_plot(p3, label_axis_1="Intensity (a.u.)",
                                  label_axis_2="Intensity (a.u.)")
        err_u = pg.ErrorBarItem(x=np_x_1, y=np_y_u_1, top=np_y_su_1,
                                bottom=np_y_su_1, beam=0.5)
        err_d = pg.ErrorBarItem(x=np_x_1, y=np_y_d_1, top=np_y_sd_1,
                                bottom=np_y_sd_1, beam=0.5)
        p3.plot(x=np_x_1, y=np_y_u_1, name="up", title="Up",
                symbol='o', pen={'color': 0.8, 'width': 2})
        p3.addItem(err_u)
        p4.addItem(pg.PlotCurveItem(x=np_x_1, y=np_y_d_1, name="down",
                                    title="Down", pen=pg_pen_black_thick))
        p4.addItem(pg.ScatterPlotItem(x=np_x_1, y=np_y_d_1,
                                      symbol='o', pen={'color': 0.8, 'width': 2}))
        p4.addItem(err_d)
        dock_2 = pg_da.Dock("Up/Down", widget=widget_2, autoOrientation=False)
        res = (dock_1, dock_2, )
    else:
        res = (dock_1, )
    return res


def dock_chi2(obj: Chi2):
    """Form docks for Chi2 object."""
    docks = []
    layout = QtWidgets.QGridLayout()
    cb_s = QtWidgets.QCheckBox("sum")
    if obj.is_attribute("sum"):
        cb_s.setCheckState(2*int(obj.sum))
    cb_s.stateChanged.connect(lambda x: setattr(obj, "sum", bool(x/2)))
    layout.addWidget(cb_s, 0, 0)

    cb_m = QtWidgets.QCheckBox("diff")
    if obj.is_attribute("diff"):
        cb_m.setCheckState(2*int(obj.diff))
    cb_m.stateChanged.connect(lambda x: setattr(obj, "diff", bool(x/2)))
    layout.addWidget(cb_m, 1, 0)

    cb_u = QtWidgets.QCheckBox("up")
    if obj.is_attribute("up"):
        cb_u.setCheckState(2*int(obj.up))
    cb_u.stateChanged.connect(lambda x: setattr(obj, "up", bool(x/2)))
    layout.addWidget(cb_u, 0, 1)

    cb_d = QtWidgets.QCheckBox("down")
    if obj.is_attribute("down"):
        cb_d.setCheckState(2*int(obj.down))
    cb_d.stateChanged.connect(lambda x: setattr(obj, "down", bool(x/2)))
    layout.addWidget(cb_d, 1, 1)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    dock_1 = pg_da.Dock("Chi2", widget=widget, autoOrientation=False)
    docks.append(dock_1)
    return tuple(docks)


def dock_refine_ls(obj: RefineLs):
    """Form docks for RefineLs object."""
    docks = []
    if ((obj.is_attribute("number_reflns")) &
            (obj.is_attribute("goodness_of_fit_all"))):
        val_1, val_2 = obj.number_reflns, obj.goodness_of_fit_all
        text = f"Points: {val_1:}\nGoF: {val_2:.2f}"
        widget = QtWidgets.QLabel(text)
        docks.append(pg_da.Dock("RefineLs", widget=widget,
                                autoOrientation=False))
    return tuple(docks)


def matrix_widget(win:pg.GraphicsLayoutWidget,
                  data, x_step, y_step, x_point_0, y_point_0):
    win.clear()
    # win.setWindowTitle('pyqtgraph example: Image Analysis')

    # A plot area (ViewBox + axes) for displaying the image
    p1 = win.addPlot(title="")

    # Item for displaying image data
    img = pg.ImageItem()
    p1.addItem(img)

    # # Custom ROI for selecting an image region
    # roi = pg.ROI([-8, 14], [6, 5])
    # roi.addScaleHandle([0.5, 1], [0.5, 0.5])
    # roi.addScaleHandle([0, 0.5], [0.5, 0.5])
    # p1.addItem(roi)
    # roi.setZValue(10)  # make sure ROI is drawn above image

    # Isocurve drawing
    iso = pg.IsocurveItem(level=0.8, pen=pg.mkPen("g", width=2))
    iso.setParentItem(img)
    iso.setZValue(5)

    # Contrast/color control
    hist = pg.HistogramLUTItem()
    hist.setImageItem(img)
    hist.setHistogramRange(data.mean()-3*numpy.std(data), data.mean()+3*numpy.std(data))
    win.addItem(hist)

    # Draggable line for setting isocurve level
    isoLine = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen("g", width=2))
    hist.vb.addItem(isoLine)
    hist.vb.setMouseEnabled(y=True) # makes user interaction a little easier
    isoLine.setValue(0.8)
    isoLine.setZValue(1000) # bring iso line above contrast controls

    # # Another plot area for displaying ROI data
    # win.nextRow()
    # p2 = win.addPlot(colspan=2)
    # p2.setMaximumHeight(250)
    # win.resize(800, 800)
    # win.show()

    # Generate image data
    img.setImage(data)
    hist.setLevels(data.mean()-1*numpy.std(data),
                   data.mean()+1*numpy.std(data))

    # build isocurves from smoothed data
    iso.setData(pg.gaussianFilter(data, (2, 2)))

    # set position and scale of image
    img.scale(x_step, y_step)
    img.translate(x_point_0, y_point_0)

    # zoom to fit imageo
    p1.autoRange()

    # # Callbacks for handling user interaction
    # def updatePlot():
    #     selected = roi.getArrayRegion(data, img)
    #     p2.plot(selected.mean(axis=0), clear=True)

    # roi.sigRegionChanged.connect(updatePlot)
    # updatePlot()

    def updateIsocurve():
        iso.setLevel(isoLine.value())

    isoLine.sigDragged.connect(updateIsocurve)

    def imageHoverEvent(event):
        """Show the position, pixel, and value under the mouse cursor."""
        if event.isExit():
            p1.setTitle("")
            return
        pos = event.pos()
        i, j = pos.y(), pos.x()
        i = int(numpy.clip(i, 0, data.shape[0] - 1))
        j = int(numpy.clip(j, 0, data.shape[1] - 1))
        val = data[i, j]
        ppos = img.mapToParent(pos)
        x, y = ppos.x(), ppos.y()
        p1.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: %g" % (
            x, y, i, j, val))

    # Monkey-patch the image to use our custom hover function.
    # This is generally discouraged (you should subclass ImageItem instead),
    # but it works for a very simple use like this.
    img.hoverEvent = imageHoverEvent
    return

def add_2nd_axis_to_plot(p1:pg.PlotItem, label_axis_1:str="",
                         label_axis_2:str=""):
    p1.setLabels(left=label_axis_1)
    
    ## create a new ViewBox, link the right axis to its coordinate system
    p2 = pg.ViewBox()
    # p2.setMouseMode(p2.RectMode)
    p1.showAxis('right')
    p1.scene().addItem(p2)
    p1.getAxis('right').linkToView(p2)
    p2.setXLink(p1)
    p1.getAxis('right').setLabel(label_axis_2, color='#0000ff')

    ## Handle view resizing
    def updateViews():
        ## view has resized; update auxiliary views to match
        p2.setGeometry(p1.vb.sceneBoundingRect())
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        p2.linkedViewChanged(p1.vb, p2.XAxis)
    updateViews()
    p1.vb.sigResized.connect(updateViews)
    return p2

def dock_pd_instr_resolution(obj:PdInstrResolution):
    tth = numpy.linspace(1, 120, 119)
    docks = []
    if obj.is_defined:
        h_pv, eta, h_g, h_l, a_g, b_g, a_l, b_l = obj.calc_resolution(tth)

        widget = pg.GraphicsLayoutWidget(title="sum/diff")
        p1 = widget.addPlot(x=tth, y=h_g, name="h_g", title="Resolution",
                pen=pg_pen_black)
        p1.plot(x=tth, y=h_l, name="h_l", pen=pg_pen_black)
        docks.append(pg_da.Dock("Instrumental resolution", widget=widget,
                                autoOrientation=False))
    return docks


def dock_cell(obj:Cell):
    docks = []
    s_str = obj.report()
    if s_str is not None:
        widget = QtWidgets.QLabel()
        area = QtWidgets.QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)

        widget.setStyleSheet("background-color:white;")
        #widget.setFont(QtGui.QFont("Courier", 12, QtGui.QFont.Bold))
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Expanding)
        widget.setText(s_str)

        dock_1 = pg_da.Dock("Cell", widget=area, autoOrientation=False)
        docks.append(dock_1)
    return tuple(docks)


def dock_space_group(obj: SpaceGroup):
    """Docks for space_group."""
    docks = []
    s_str = obj.report_space_group()
    if s_str is not None:
        widget = QtWidgets.QLabel()
        area = QtWidgets.QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)

        widget.setStyleSheet("background-color:white;")
        # widget.setFont(QtGui.QFont("Courier", 12, QtGui.QFont.Bold))
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        widget.setText(s_str)

        dock_1 = pg_da.Dock("Space Group", widget=area, autoOrientation=False)
        docks.append(dock_1)
    return tuple(docks)


def dock_crystal(obj: Crystal, thread: QtCore.QThread):
    """Docks for crystal."""
    docks = []
    try:
        cell = obj.cell
    except AttributeError:
        cell = None
    try:
        space_group = obj.space_group
    except AttributeError:
        space_group = None
    try:
        atom_site = obj.atom_site
    except AttributeError:
        atom_site = None

    if not obj.is_defined():
        layout_actions = QtWidgets.QHBoxLayout()
        if cell is None:
            cb_1 = QtWidgets.QPushButton("Add cell")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, 
                                                   [Cell()], thread))
            layout_actions.addWidget(cb_1)
        if space_group is None:
            cb_1 = QtWidgets.QPushButton("Add space group")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, 
                                                   [SpaceGroup(it_number=1)],
                                                   thread))
            layout_actions.addWidget(cb_1)
        if atom_site is None:
            cb_1 = QtWidgets.QPushButton("Add atom site")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, 
                                                    [AtomSiteL()], thread))
            layout_actions.addWidget(cb_1)
        layout_actions.addStretch(1)
        widget_actions = QtWidgets.QWidget()
        widget_actions.setLayout(layout_actions)
        docks.append(pg_da.Dock("Actions crystal", widget=widget_actions,
                                autoOrientation=False))

    if cell is not None:
        docks.extend(list(dock_cell(cell)))
    if space_group is not None:
        docks.extend(list(dock_space_group(space_group)))
    s_str = obj.report_main_axes_of_magnetization_ellipsoids()
    if s_str is not None:
        widget = QtWidgets.QLabel()
        area = QtWidgets.QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)

        widget.setStyleSheet("background-color:white;")
        #widget.setFont(QtGui.QFont("Courier", 12, QtGui.QFont.Bold))
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        widget.setText(s_str)

        dock_1 = pg_da.Dock("Magnetization", widget=area,
                            autoOrientation=False)
        docks.append(dock_1)
    return tuple(docks)


def dock_pd2d(obj:Pd2d, thread: QtCore.QThread):
    f_proc, f_meas, f_bkgr, f_peak = False, False, False, False
    proc, meas, bkgr, peak = None, None, None, None
    try:
        meas = obj.pd2d_meas
        f_meas = True
    except AttributeError:
        f_meas = False
    try:
        bkgr = obj.pd2d_background
        f_bkgr = True
    except AttributeError:
        f_bkgr = False
    try:
        chi2 = obj.chi2
        f_chi2 = True
    except AttributeError:
        f_chi2 = False
    try:
        refine_ls = obj.refine_ls
        f_refine_ls = True
    except AttributeError:
        f_refine_ls = False
    try:
        proc = obj.pd2d_proc
        f_proc = True
    except AttributeError:
        f_proc = False
    l_pd2d_peak = []
    try:
        phase = obj.phase
        f_phase = True
    except AttributeError:
        f_phase = False

    if f_phase:
        for item in phase.items:
            try:
                pd2d_peak = getattr(obj, f"pd2d_peak_{item.label.lower():}")
                l_pd2d_peak.append(pd2d_peak)
            except AttributeError:
                pass

    docks = []
    try:
        setup = obj.setup
        f_setup = True
    except AttributeError:
        f_setup = False
    try:
        pd2d_instr_resolution = obj.pd2d_instr_resolution
        f_pd2d_instr_resolution = True
    except AttributeError:
        f_pd2d_instr_resolution = False
    try:
        phase = obj.phase
        f_phase = True
    except AttributeError:
        f_phase = False
    try:
        pd2d_background = obj.pd2d_background 
        f_pd2d_background = True
    except AttributeError:
        f_pd2d_background = False
    try:
        range_ = obj.range
        f_range = True
    except AttributeError:
        f_range = False
    # f_diffrn_radiation = obj.diffrn_radiation is not None

    if not(f_chi2 & f_meas & f_setup & f_pd2d_instr_resolution & f_phase &
           f_pd2d_background & f_range):
        layout_actions = QtWidgets.QHBoxLayout()
        if not f_chi2:
            cb_1 = QtWidgets.QPushButton("Add chi2")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Chi2()], thread))
            layout_actions.addWidget(cb_1)
        if not f_meas:
            cb_1 = QtWidgets.QPushButton("Add pd2d_meas")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Pd2dMeas()], thread))
            layout_actions.addWidget(cb_1)
        if not f_setup:
            cb_1 = QtWidgets.QPushButton("Add setup")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Setup()], thread))
            layout_actions.addWidget(cb_1)
        if not f_pd2d_instr_resolution:
            cb_1 = QtWidgets.QPushButton("Add \npd2d_instr_resolution")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(
                obj, [Pd2dInstrResolution()], thread))
            layout_actions.addWidget(cb_1)
        if not f_phase:
            cb_1 = QtWidgets.QPushButton("Add phase")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            vv = PhaseL()
            vv.items = [Phase(label="phase", igsize=0., scale=1.)]
            cb_1.clicked.connect(lambda: add_items(obj, [vv], thread))
            layout_actions.addWidget(cb_1)
        if not f_pd2d_background:
            cb_1 = QtWidgets.QPushButton("Add \npd2d_background")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Pd2dBackground()],
                                                   thread))
            layout_actions.addWidget(cb_1)
        if not f_range:
            cb_1 = QtWidgets.QPushButton("Add range")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(
                obj, [Range(ttheta_min=4., ttheta_max=80., phi_min=-10.,
                            phi_max=20.)], thread))
            layout_actions.addWidget(cb_1)
        layout_actions.addStretch(1)
        # if not f_diffrn_radiation:
        #     cb_1 = QtWidgets.QPushButton("Add diffrn_radiation")
        #     cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
        #                        QtWidgets.QSizePolicy.Expanding)
        #     cb_1.clicked.connect(lambda: add_items(obj, [DiffrnRadiation()],
        #                                            thread))
        #     layout_actions.addWidget(cb_1)
        widget_actions = QtWidgets.QWidget()
        widget_actions.setLayout(layout_actions)
        docks.append(pg_da.Dock("Actions pd2d", widget=widget_actions,
                                autoOrientation=False))

    if f_proc:
        docks.extend(list(dock_pd2d_proc(proc, l_pd2d_peak)))
    elif f_meas:
        docks.extend(list(dock_pd2d_meas(meas)))
    if f_chi2:
        docks.extend(list(dock_chi2(chi2)))
    if f_refine_ls:
        docks.extend(list(dock_refine_ls(refine_ls)))
    return tuple(docks)


def dock_pd2d_meas(obj:Pd2dMeas):
    docks = []
    try:
        ttheta = obj.ttheta
        phi = obj.phi
        intensity_up = obj.intensity_up
        intensity_up_sigma = obj.intensity_up_sigma
        intensity_down = obj.intensity_down
        intensity_down_sigma = obj.intensity_down_sigma
    except AttributeError:
        return tuple(docks)
    int_s =  numpy.nan_to_num(intensity_up + intensity_down)
    int_m =  numpy.nan_to_num(intensity_up - intensity_down)
    ttheta_step = ttheta[1]-ttheta[0]
    phi_step = phi[1]-phi[0]
    data = int_m

    x_step = ttheta_step
    y_step = phi_step
    x_point_0 = int(ttheta[0]/ttheta_step)
    y_point_0 = int(phi[0]/phi_step)

    win = pg.GraphicsLayoutWidget()

    win_1d = pg.GraphicsLayoutWidget()

    z_sum_e = intensity_up.transpose()+intensity_down.transpose()
    # z_sum_s_sq = (intensity_up_sigma.transpose())**2+(intensity_down_sigma.transpose())**2
    _z_1_e = numpy.where(numpy.isnan(z_sum_e), 0., z_sum_e).sum(axis=0)
    # _z_1_s = numpy.sqrt(numpy.where(numpy.isnan(z_sum_e), 0., z_sum_s_sq).sum(axis=0))
    _n_1 = numpy.where(numpy.isnan(z_sum_e), 0., 1.).sum(axis=0)
    z_1_sum_e = _z_1_e/_n_1
    # z_1_sum_s = _z_1_s/_n_1

    z_diff_e = intensity_up.transpose()-intensity_down.transpose()
    _z_1_e = numpy.where(numpy.isnan(z_diff_e), 0., z_diff_e).sum(axis=0)
    _n_1 = numpy.where(numpy.isnan(z_diff_e), 0., 1.).sum(axis=0)
    z_1_diff_e = _z_1_e/_n_1
    # z_1_diff_s = _z_1_s/_n_1

    p1 = win_1d.addPlot()

    vb_p2 = add_2nd_axis_to_plot(p1, label_axis_1="Intensity (a.u.)",
                                  label_axis_2="Intensity (a.u.)")

    p1.plot(ttheta, z_1_sum_e, symbol='o', pen={'color': 0.8, 'width': 2})
    p2 = pg.ScatterPlotItem(ttheta, z_1_diff_e, symbol='o',
                                pen={'color': 0.2, 'width': 2})
    p3 = pg.PlotCurveItem(x=ttheta, y=z_1_diff_e, pen=pg_pen_black_thick)
    vb_p2.addItem(p2)
    vb_p2.addItem(p3)

    [x_range_12, y_range_12] = p1.viewRange()
    y_range = y_range_12[1]-y_range_12[0]
    vb_p2.setRange(yRange=(-0.25*y_range, 0.75*y_range))

    cb_s = QtWidgets.QPushButton("2D sum")
    cb_s.clicked.connect(lambda: matrix_widget(win, int_s, x_step, y_step,
                                               x_point_0, y_point_0))

    cb_m = QtWidgets.QPushButton("2D diff")
    cb_m.clicked.connect(lambda: matrix_widget(win, int_m, x_step, y_step,
                                               x_point_0, y_point_0))

    matrix_widget(win, int_m, x_step, y_step, x_point_0, y_point_0)

    layout = QtWidgets.QGridLayout()
    layout.addWidget(cb_s, 0, 0)
    layout.addWidget(cb_m, 0, 1)
    layout.addWidget(win, 1, 0, 1, 2)
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    #win = matrix_widget(data, x_step, y_step, x_point_0, y_point_0)

    #docks.append(pg_da.Dock("2D measurements: sum", widget=imv_s))

    docks.append(pg_da.Dock("Projection of sum and difference", widget=win_1d,
                            autoOrientation=False))
    docks.append(pg_da.Dock("Plot", widget=widget, autoOrientation=False))
    return tuple(docks)


def dock_pd2d_proc(obj:Pd2dProc, l_pd2d_peak: List[Pd2dPeakL]):
    """Docks for pd2d_proc object."""
    docks = []
    try:
        ttheta = obj.ttheta
        phi = obj.phi
        intensity_up = obj.intensity_up
        intensity_up_sigma = obj.intensity_up_sigma
        intensity_down = obj.intensity_down
        intensity_down_sigma = obj.intensity_down_sigma
        intensity_up_total = obj.intensity_up_total
        intensity_down_total = obj.intensity_down_total
    except AttributeError:
        return tuple(docks)

    z_sum = intensity_up_total+intensity_down_total
    z_sum_e = intensity_up+intensity_down
    z_sum_s_sq = (intensity_up_sigma)**2+(intensity_down_sigma)**2
    _z_1_e = numpy.where(numpy.isnan(z_sum_e), 0., z_sum_e).sum(axis=1)
    _z_1 = numpy.where(numpy.isnan(z_sum_e), 0., z_sum).sum(axis=1)
    _z_1_s = numpy.sqrt(numpy.where(numpy.isnan(z_sum_e), 0., z_sum_s_sq).sum(
        axis=1))
    _n_1 = numpy.where(numpy.isnan(z_sum_e), 0., 1.).sum(axis=1)
    z_1_sum = _z_1/_n_1
    z_1_sum_e = _z_1_e/_n_1
    z_1_sum_s = _z_1_s/_n_1

    z_diff = intensity_up_total-intensity_down_total
    z_diff_e = intensity_up-intensity_down
    _z_1_e = numpy.where(numpy.isnan(z_diff_e), 0., z_diff_e).sum(axis=1)
    _z_1 = numpy.where(numpy.isnan(z_diff_e), 0., z_diff).sum(axis=1)
    _n_1 = numpy.where(numpy.isnan(z_diff_e), 0., 1.).sum(axis=1)
    z_1_diff = _z_1/_n_1
    z_1_diff_e = _z_1_e/_n_1
    z_1_diff_s = _z_1_s/_n_1

    z_sum_e_0 = numpy.nan_to_num(z_sum_e)
    z_diff_e_0 = numpy.nan_to_num(z_diff_e)

    ttheta_step = ttheta[1]-ttheta[0]
    phi_step = phi[1]-phi[0]
    x_step = ttheta_step
    y_step = phi_step
    x_point_0 = int(ttheta[0]/ttheta_step)
    y_point_0 = int(phi[0]/phi_step)

    win = pg.GraphicsLayoutWidget()

    err_s = pg.ErrorBarItem(x=ttheta, y=z_1_sum_e, top=z_1_sum_s,
                            bottom=z_1_sum_s, beam=0.5)
    err_m = pg.ErrorBarItem(x=ttheta, y=z_1_diff_e, top=z_1_diff_s,
                            bottom=z_1_diff_s, beam=0.5)

    win_1d_s = pg.GraphicsLayoutWidget()
    p1 = win_1d_s.addPlot()
    vb_p2 = add_2nd_axis_to_plot(p1, label_axis_1="Intensity (a.u.)",
                                 label_axis_2="Intensity (a.u.)")
    p1.plot(ttheta, z_1_sum_e, symbol='o', pen={'color': 0.8, 'width': 2})
    p1.plot(ttheta, z_1_sum, pen=pg_pen_black)
    p1.addItem(err_s)
    p2 = pg.PlotCurveItem(ttheta, z_1_sum_e-z_1_sum, pen=pg_pen_black_thick)
    vb_p2.addItem(p2)

    win_1d_m = pg.GraphicsLayoutWidget()
    p3 = win_1d_m.addPlot()
    vb_p4 = add_2nd_axis_to_plot(p3, label_axis_1="Intensity (a.u.)",
                                 label_axis_2="Intensity (a.u.)")
    p3.plot(ttheta, z_1_diff_e, symbol='o', pen={'color': 0.8, 'width': 2})
    p3.plot(ttheta, z_1_diff, pen=pg_pen_black)
    p3.addItem(err_m)
    p4 = pg.PlotCurveItem(ttheta, z_1_diff_e-z_1_diff, pen=pg_pen_black_thick)
    vb_p4.addItem(p4)

    [x_range_12, y_range_12] = p1.viewRange()
    y_range = y_range_12[1]-y_range_12[0]
    vb_p2.setRange(yRange=(-0.15*y_range, 0.85*y_range))
    [x_range_34, y_range_34] = p3.viewRange()
    y_range = y_range_34[1]-y_range_34[0]
    p3.setYRange(-0.50*y_range, 0.50*y_range)
    vb_p4.setRange(yRange=(-0.15*y_range, 0.85*y_range))

    yrange_2 = vb_p2.viewRange()[1]
    ysize_2 = 0.05*(yrange_2[1]-yrange_2[0])
    yshift_2 = 0.5*0.5*0.5*ysize_2*len(l_pd2d_peak)
    yrange_4 = vb_p4.viewRange()[1]
    ysize_4 = 0.05*(yrange_4[1]-yrange_4[0])
    yshift_4 = 0.5*ysize_4*len(l_pd2d_peak)
    for pd2d_peak in l_pd2d_peak:
        numpy_ttheta = numpy.array(pd2d_peak.ttheta, dtype=float)
        np_zero = 0.*numpy_ttheta
        ind_miller_2 = pg.ErrorBarItem(
            x=numpy_ttheta, y=np_zero+yshift_2, top=np_zero+yshift_2+ysize_2,
            bottom=np_zero-yshift_2+ysize_2, beam=0.0)
        ind_miller_4 = pg.ErrorBarItem(
            x=numpy_ttheta, y=np_zero+yshift_4, top=np_zero+yshift_4+ysize_4,
            bottom=np_zero-yshift_4+ysize_4, beam=0.0)
        vb_p2.addItem(ind_miller_2)
        vb_p4.addItem(ind_miller_4)
        yshift_2 -= 0.5*ysize_2
        yshift_4 -= 1.0*ysize_4

    cb_s = QtWidgets.QPushButton("2D sum model")
    cb_s.clicked.connect(lambda: matrix_widget(
        win, z_sum, x_step, y_step, x_point_0, y_point_0))

    cb_s_e = QtWidgets.QPushButton("2D sum exp")
    cb_s_e.clicked.connect(lambda: matrix_widget(
        win, z_sum_e_0, x_step, y_step, x_point_0, y_point_0))

    cb_m = QtWidgets.QPushButton("2D diff model")
    cb_m.clicked.connect(lambda: matrix_widget(
        win, z_diff, x_step, y_step, x_point_0, y_point_0))

    cb_m_e = QtWidgets.QPushButton("2D diff exp")
    cb_m_e.clicked.connect(lambda: matrix_widget(
        win, z_diff_e_0, x_step, y_step, x_point_0, y_point_0))

    matrix_widget(win, z_diff, x_step, y_step, x_point_0, y_point_0)

    layout = QtWidgets.QGridLayout()
    layout.addWidget(cb_s, 0, 0)
    layout.addWidget(cb_s_e, 0, 1)
    layout.addWidget(cb_m, 0, 2)
    layout.addWidget(cb_m_e, 0, 3)
    layout.addWidget(win, 1, 0, 1, 4)
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    # win = matrix_widget(data, x_step, y_step, x_point_0, y_point_0)

    # docks.append(pg_da.Dock("2D measurements: sum", widget=imv_s))

    docks.append(pg_da.Dock("Projection of sum", widget=win_1d_s,
                            autoOrientation=False))
    docks.append(pg_da.Dock("Projection of difference", widget=win_1d_m,
                            autoOrientation=False))
    docks.append(pg_da.Dock("Plot", widget=widget, autoOrientation=False))
    return tuple(docks)


def dock_diffrn(obj: Diffrn, thread: QtCore.QThread):
    """Docks for Diffrn objects."""
    docks = []

    f_setup = obj.is_attribute("setup")
    f_diffrn_radiation = obj.is_attribute("diffrn_radiation")
    f_diffrn_orient_matrix = obj.is_attribute("diffrn_orient_matrix")
    f_diffrn_refln = obj.is_attribute("diffrn_refln")
    f_phase = obj.is_attribute("phase")
    if not(f_setup & f_diffrn_radiation & f_diffrn_orient_matrix &
           f_diffrn_refln & f_phase):
        layout_actions = QtWidgets.QHBoxLayout()
        if not f_setup:
            cb_1 = QtWidgets.QPushButton("Add setup")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Setup()], thread))
            layout_actions.addWidget(cb_1)
        if not f_diffrn_radiation:
            cb_1 = QtWidgets.QPushButton("Add diffrn_radiation")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [DiffrnRadiation()],
                                                   thread))
            layout_actions.addWidget(cb_1)
        if not f_diffrn_orient_matrix:
            cb_1 = QtWidgets.QPushButton("Add diffrn_orient_matrix")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(
                obj, [DiffrnOrientMatrix(ub_11=1., ub_12=0., ub_13=0.,
                                         ub_21=0., ub_22=1., ub_23=0.,
                                         ub_31=0., ub_32=0., ub_33=1.,)],
                thread))
            layout_actions.addWidget(cb_1)
        if not f_diffrn_refln:
            cb_1 = QtWidgets.QPushButton("Add diffrn_refln")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [DiffrnReflnL()],
                                                   thread))
            layout_actions.addWidget(cb_1)
        if not f_phase:
            cb_1 = QtWidgets.QPushButton("Add phase")
            cb_1.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
            cb_1.setMaximumHeight(ICON_SIZE)
            cb_1.setMinimumHeight(ICON_SIZE)
            cb_1.clicked.connect(lambda: add_items(obj, [Phase(label="phase")],
                                                   thread))
            layout_actions.addWidget(cb_1)
        layout_actions.addStretch(1)
        widget_actions = QtWidgets.QWidget()
        widget_actions.setLayout(layout_actions)
        docks.append(pg_da.Dock("Actions diffrn", widget=widget_actions,
                                autoOrientation=False))

    if f_diffrn_refln:
        diffrn_refln = obj.diffrn_refln
        x = numpy.array(diffrn_refln.fr_calc, dtype=float)
        y = numpy.array(diffrn_refln.fr, dtype=float)
        err = numpy.array(diffrn_refln.fr_sigma, dtype=float)

        if not(numpy.all(numpy.isnan(x))):
            vb_1 = pg.ViewBox()
            vb_1.setMouseMode(vb_1.RectMode)
            widget = pg.PlotWidget(viewBox=vb_1)
            p1 = widget.plotItem
            err_s = pg.ErrorBarItem(x=x, y=y, top=err,
                                    bottom=err, beam=0.01)
            # err_m = pg.ErrorBarItem(x=np_x_1, y=np_y_m_1, top=np_y_sm_1,
            #                 bottom=np_y_sm_1, beam=0.5)
            p1.scatterPlot(x=x, y=y, name="fr", title="Flip ratio",
                           symbol='o', pen={'color': 0.8, 'width': 2})
            p1.plot(x=y, y=y)
            p1.addItem(err_s)
            docks.append(pg_da.Dock("Diffrn", widget=widget,
                                    autoOrientation=False))

            s1 = diffrn_refln.report_agreement_factor_exp()
            diffrn_orient_matrix = obj.diffrn_orient_matrix
            s2 = ""
            if f_diffrn_orient_matrix:
                s2 = diffrn_refln.report_chi_sq_exp(diffrn_orient_matrix.cell)
            area = QtWidgets.QScrollArea()
            area.setWidgetResizable(True)
            widget = QtWidgets.QLabel()
            widget.setText(s1+2*"\n"+s2)
            area.setWidget(widget)
            docks.append(pg_da.Dock("Difrn Refln", widget=area,
                                    autoOrientation=False))

    if f_diffrn_orient_matrix:
        diffrn_orient_matrix = obj.diffrn_orient_matrix
        widget = QtWidgets.QLabel()
        widget.setText(str(diffrn_orient_matrix.u))
        docks.append(pg_da.Dock("Diffrn Orient Matrix", widget=widget,
                                autoOrientation=False))

    try:
        refine_ls = obj.is_attribute("refine_ls")
        docks.extend(list(dock_refine_ls(refine_ls)))
    except AttributeError:
        pass
    return tuple(docks)
