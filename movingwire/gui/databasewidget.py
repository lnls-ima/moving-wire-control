"""Database tables widgets."""

import os as _os
import sys as _sys
import time as _time
import numpy as _np
import pandas as _pd
import sqlite3 as _sqlite3
import traceback as _traceback
import qtpy.uic as _uic
from qtpy.QtCore import Qt as _Qt
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QApplication as _QApplication,
    QLabel as _QLabel,
    QTableWidget as _QTableWidget,
    QTableWidgetItem as _QTableWidgetItem,
    QMessageBox as _QMessageBox,
    QVBoxLayout as _QVBoxLayout,
    QHBoxLayout as _QHBoxLayout,
    QSpinBox as _QSpinBox,
    QFileDialog as _QFileDialog,
    QInputDialog as _QInputDialog,
    QAbstractItemView as _QAbstractItemView,
    )

from imautils.gui import databasewidgets as _databasewidgets
from movingwire.gui.utils import get_ui_file as _get_ui_file
import movingwire.data as _data
from stretchedwire.gui.databasewidget import _PowerSupplyConfig


_PpmacConfig = _data.configuration.PpmacConfig
_PowerSupplyConfig = _data.configuration.PowerSupplyConfig
_MeasurementConfig = _data.configuration.MeasurementConfig
_MeasurementDataFC = _data.measurement.MeasurementDataFC
_MeasurementDataSW = _data.measurement.MeasurementDataSW
_MeasurementDataSW2 = _data.measurement.MeasurementDataSW2


class DatabaseWidget(_QWidget):
    """Database widget class for the control application."""

    _PpmacConfig_table_name = _PpmacConfig.collection_name
    _PowerSupplyConfig_table_name = _PowerSupplyConfig.collection_name
    _MeasurementConfig_table_name = _MeasurementConfig.collection_name
    _MeasurementDataFC_table_name = _MeasurementDataFC.collection_name
    _MeasurementDataSW_table_name = _MeasurementDataSW.collection_name
    _MeasurementDataSW2_table_name = _MeasurementDataSW2.collection_name

    _hidden_columns = []

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self._table_object_dict = {
            self._PpmacConfig_table_name: _PpmacConfig,
            self._PowerSupplyConfig_table_name: _PowerSupplyConfig,
            self._MeasurementConfig_table_name: _MeasurementConfig,
            self._MeasurementDataFC_table_name: _MeasurementDataFC,
            self._MeasurementDataSW_table_name: _MeasurementDataSW,
            self._MeasurementDataSW2_table_name: _MeasurementDataSW2,
            }

        self._table_page_dict = {}
        for key in self._table_object_dict.keys():
            self._table_page_dict[key] = None
#        self._table_page_dict[
#            self._measurement_table_name] = self.ui.pg_movingwire_measurement

        self.short_version_hidden_tables = []

        self.twg_database = _databasewidgets.DatabaseTabWidget(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        self.ui.lyt_database.addWidget(self.twg_database)

        self.connect_signal_slots()
#         self.disable_invalid_buttons()

    @property
    def database_name(self):
        """Database name."""
        return _QApplication.instance().database_name

    @property
    def mongo(self):
        """MongoDB database."""
        return _QApplication.instance().mongo

    @property
    def server(self):
        """Server for MongoDB database."""
        return _QApplication.instance().server

    @property
    def directory(self):
        """Return the default directory."""
        return _QApplication.instance().directory

    def init_tab(self):
        self.update_database_tables()

    def clear(self):
        """Clear."""
        try:
            self.twg_database.delete_widgets()
            self.twg_database.clear()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
#         self.ui.pbt_save.clicked.connect(self.save_files)
#         self.ui.pbt_read.clicked.connect(self.read_files)
#         self.ui.pbt_delete.clicked.connect(
#             self.twg_database.delete_database_documents)

        self.ui.pbt_update.clicked.connect(self.update_database_tables)
        self.ui.pbt_clear.clicked.connect(self.clear)
#         self.ui.twg_database.currentChanged.connect(
#             self.disable_invalid_buttons)

#     def disable_invalid_buttons(self):
#         """Disable invalid buttons."""
#         try:
#             current_table_name = self.twg_database.get_current_table_name()
#             if current_table_name is not None:
#                 self.ui.stw_buttons.setEnabled(True)
# 
#                 for table_name, page in self._table_page_dict.items():
#                     if page is not None:
#                         page.setEnabled(False)
#                         _idx = self.ui.stw_buttons.indexOf(page)
#                     else:
#                         self.ui.stw_buttons.setCurrentIndex(0)
# 
#                 current_page = self._table_page_dict[current_table_name]
#                 if current_page is not None:
#                     current_page.setEnabled(True)
#                     _idx = self.ui.stw_buttons.indexOf(current_page)
#                     self.ui.stw_buttons.setCurrentWidget(current_page)
#             else:
#                 self.ui.stw_buttons.setCurrentIndex(0)
#                 self.ui.stw_buttons.setEnabled(False)
# 
#         except Exception:
#             _traceback.print_exc(file=_sys.stdout)

    def load_database(self):
        """Load database."""
        try:
            self.twg_database.database_name = self.database_name
            self.twg_database.mongo = self.mongo
            self.twg_database.server = self.server
            self.twg_database.hidden_tables = []
#             if self.ui.chb_short_version.isChecked():
#                 hidden_tables = self.short_version_hidden_tables
#                 self.twg_database.hidden_tables = hidden_tables
#             else:
#                 self.twg_database.hidden_tables = []
            self.twg_database.load_database()
#             self.disable_invalid_buttons()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_database_tables(self):
        """Update database tables."""
        if not self.isVisible():
            return

        try:
            self.twg_database.database_name = self.database_name
            self.twg_database.mongo = self.mongo
            self.twg_database.server = self.server
            self.twg_database.hidden_tables = []
#             if self.ui.chb_short_version.isChecked():
#                 hidden_tables = self.short_version_hidden_tables
#                 self.twg_database.hidden_tables = hidden_tables
#             else:
#                 self.twg_database.hidden_tables = []
            self.twg_database.update_database_tables()
#             self.disable_invalid_buttons()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
