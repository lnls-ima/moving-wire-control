# -*- coding: utf-8 -*-

"""Main entry point to the Moving Wire Control application."""

import os as _os
import sys as _sys
import threading as _threading
from qtpy.QtWidgets import QApplication as _QApplication

from movingwire.gui import utils as _utils
from movingwire.gui.movingwirewindow import (
    MovingWireWindow as _MovingWireWindow)
import movingwire.data as _data
from movingwire.devices import (
    ppmac as _ppmac,
    fdi as _fdi,
    ps as _ps,
    volt as _volt,
    )


class MovingWireApp(_QApplication):
    """Moving Wire application."""

    def __init__(self, args):
        """Start application."""
        super().__init__(args)
        self.setStyle(_utils.WINDOW_STYLE)

        self.directory = _utils.BASEPATH
        self.database_name = _utils.DATABASE_NAME
        self.mongo = _utils.MONGO
        self.server = _utils.SERVER
        self.create_database()

        # positions dict
        self.positions = {}
        self.current_max = 0
        self.current_min = 0

        # create dialogs
#         self.view_probe_dialog = _ViewProbeDialog()

        # devices instances
        self.ppmac = _ppmac
        self.fdi = _fdi
        self.volt = _volt
        self.ps = _ps

    def create_database(self):
        """Create database and tables."""
#         _ConnectionConfig = _data.configuration.ConnectionConfig(
#             database_name=self.database_name,
#             mongo=self.mongo, server=self.server)
#         _IntegratorConfig = (
#             _data.configuration.IntegratorConfig(
#                 database_name=self.database_name,
#                 mongo=self.mongo, server=self.server))
#         _CyclingCurve = _data.configuration.CyclingCurve(
#             database_name=self.database_name,
#             mongo=self.mongo, server=self.server)
        _PowerSupplyConfig = _data.configuration.PowerSupplyConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _PpmacConfig = _data.configuration.PpmacConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _MeasurementConfig = _data.configuration.MeasurementConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _MeasurementDataFC = _data.measurement.MeasurementDataFC(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _MeasurementDataSW = _data.measurement.MeasurementDataSW(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _MeasurementDataSW2 = _data.measurement.MeasurementDataSW2(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)

        status = []
#         status.append(_ConnectionConfig.db_create_collection())
#         status.append(_CyclingCurve.db_create_collection())
#         status.append(_IntegratorConfig.db_create_collection())
        status.append(_PowerSupplyConfig.db_create_collection())
        status.append(_PpmacConfig.db_create_collection())
        status.append(_MeasurementConfig.db_create_collection())
        status.append(_MeasurementDataFC.db_create_collection())
        status.append(_MeasurementDataSW.db_create_collection())
        status.append(_MeasurementDataSW2.db_create_collection())

        if not all(status):
            raise Exception("Failed to create database.")


class GUIThread(_threading.Thread):
    """GUI Thread."""

    def __init__(self):
        """Start thread."""
        _threading.Thread.__init__(self)
        self.app = None
        self.window = None
        self.daemon = True
        self.start()

    def run(self):
        """Thread target function."""
        self.app = None
        if not _QApplication.instance():
            self.app = MovingWireApp([])
            self.window = _MovingWireWindow(
                width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
            self.window.show()
            self.window.centralize_window()
            _sys.exit(self.app.exec_())


def run():
    """Run movingwire application."""
    app = None
    if not _QApplication.instance():
        app = MovingWireApp([])
        window = _MovingWireWindow(
            width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
        window.show()
        window.centralize_window()
        _sys.exit(app.exec_())


def run_in_thread():
    """Run movingwire application in a thread."""
    return GUIThread()
