"""Main window for the Moving Wire Control application"""

import sys as _sys
import traceback as _traceback
from qtpy.QtWidgets import (
    QFileDialog as _QFileDialog,
    QMainWindow as _QMainWindow,
    QApplication as _QApplication,
    QDesktopWidget as _QDesktopWidget,
    )
from qtpy.QtCore import QTimer as _QTimer
import qtpy.uic as _uic

from movingwire.gui import utils as _utils

from movingwire.gui.analysiswidget import AnalysisWidget \
    as _AnalysisWidget
from movingwire.gui.connectionwidget import ConnectionWidget \
    as _ConnectionWidget
from movingwire.gui.powersupplywidget import PowerSupplyWidget \
    as _PowerSupplyWidget
from movingwire.gui.measurementwidget import MeasurementWidget \
    as _MeasurementWidget
from movingwire.gui.ppmacwidget import PpmacWidget \
    as _PpmacWidget
from movingwire.gui.databasewidget import DatabaseWidget \
    as _DatabaseWidget


class MovingWireWindow(_QMainWindow):
    """Main Window class for the Moving Wire Control application."""

    _update_positions_interval = _utils.UPDATE_POSITIONS_INTERVAL

    def __init__(
            self, parent=None, width=_utils.WINDOW_WIDTH,
            height=_utils.WINDOW_HEIGHT):
        """Set up the ui and add main tabs."""
        super().__init__(parent)

        # setup the ui
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)
        self.resize(width, height)

        # clear the current tabs
        self.ui.twg_main.clear()

        # define tab names and corresponding widgets
        self.tab_names = [
            'connection',
            'motors',
            'power supply',
            'measurement',
            'analysis',
            'database',
            ]

        self.tab_widgets = [
            _ConnectionWidget(),
            _PpmacWidget(),
            _PowerSupplyWidget(),
            _MeasurementWidget(),
            _AnalysisWidget(),
            _DatabaseWidget(),
            ]

        # connect signals and slots
#         self.connect_signal_slots()

        # add widgets to main tab
        self.ui.twg_main.clear()
        for i in range(len(self.tab_names)):
            tab_name = self.tab_names[i]
            tab = self.tab_widgets[i]
            setattr(self, tab_name.replace(' ', ''), tab)
            self.ui.twg_main.addTab(tab, tab_name.capitalize())
            setattr(tab, 'parent_window', self)

        for tab in self.tab_widgets:
            tab.init_tab()

        for i in range(1, self.ui.twg_main.count() - 2):
            self.ui.twg_main.setTabEnabled(i, False)

    def centralize_window(self):
        """Centralize window."""
        window_center = _QDesktopWidget().availableGeometry().center()
        self.move(
            window_center.x() - self.geometry().width()/2,
            window_center.y() - self.geometry().height()/2)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        pass
