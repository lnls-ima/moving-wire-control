"""Measurement progress dialog"""

import os as _os
import sys as _sys
import time as _time
import traceback as _traceback
from qtpy.QtCore import Qt as _Qt
from qtpy.QtWidgets import (
    QApplication as _QApplication,
    QDialog as _QDialog,
    QMessageBox as _QMessageBox,
    )

import qtpy.uic as _uic

import movingwire.data as _data
from movingwire.gui.utils import (
    get_ui_file as _get_ui_file,
    sleep as _sleep,
    update_db_name_list as _update_db_name_list,
    pandas_load_db_measurements as _pandas_load_db_measurements,
    )


class MapDialog(_QDialog):
    """Moving Wire integral maps dialog."""

    def __init__(self, parent=None):
        """Set up the ui and create connections."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.cfg = _data.configuration.IntegralMapsCfg()
        self.cfg_aux = _data.configuration.IntegralMapsCfg()

        self.meas_sw = _data.measurement.MeasurementDataSW()
        self.meas_sw2 = _data.measurement.MeasurementDataSW2()

        self.connect_signal_slots()

        self.update_cfg_list()

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

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.cmb_cfg_name.currentIndexChanged.connect(self.load_cfg)
        self.ui.pbt_load_cfg.clicked.connect(self.load_cfg)
        self.ui.pbt_update_cfg.clicked.connect(self.update_cfg_list)
        self.ui.pbt_save_cfg.clicked.connect(self.save_cfg)

    def load_cfg(self):
        """Load configuration from database."""
        try:
            name = self.ui.cmb_cfg_name.currentText()
            self.cfg.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            _id = self.cfg.db_search_field('name', name)[0]['id']
            self.cfg.db_read(_id)
            self.update_iamb_list()
            self.load_cfg_into_ui()
            # _QMessageBox.information(self, 'Information',
            #                          'Configuration Loaded.',
            #                          _QMessageBox.Ok)
            return True
        except Exception:
            _QMessageBox.warning(self, 'Warning',
                                 'Failed to load this configuration.',
                                 _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def get_Iamb_name(self, table, idx):
        """Get Iamb name from database.

        Args:
            table (MeasurementDataSW1/2): measurement data class;
            idx (int): Iamb measurement index.

        Returns:
            Iamb name (str) if successful; None otherwise."""
        try:
            table.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            table.db_read(idx)
            return table.name
        except Exception:
            _QMessageBox.warning(self, 'Warning',
                                 'Failed to load Iamb name.',
                                 _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return None

    def get_Iamb_id(self, table, name):
        """Get Iamb name from database.

        Args:
            table (MeasurementDataSW1/2): measurement data class;
            name (str): Iamb measurement name.

        Returns:
            Iamb id (int) if successful; None otherwise."""
        try:
            table.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            ans = table.db_search_field('name', name)
            return ans[0]['id']
        except Exception:
            _QMessageBox.warning(self, 'Information',
                                 'Failed to load Iamb name.',
                                 _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return None

    def load_cfg_into_ui(self):
        """Loads database configuration into ui widgets."""
        try:
            name = self.cfg.name.split('_')[:-2]
            self.ui.le_map_name.setText('_'.join(name))
            self.ui.le_comments.setText(self.cfg.comments)

            if self.cfg.Ix:
                self.ui.chb_Ix.setChecked(True)
            else:
                self.ui.chb_Ix.setChecked(False)
            if self.cfg.Iy:
                self.ui.chb_Iy.setChecked(True)
            else:
                self.ui.chb_Iy.setChecked(False)
            if self.cfg.I1:
                self.ui.chb_I1.setChecked(True)
            else:
                self.ui.chb_I1.setChecked(False)
            if self.cfg.I2:
                self.ui.chb_I2.setChecked(True)
            else:
                self.ui.chb_I2.setChecked(False)

            if self.cfg.I1x_amb_id == 0:
                self.ui.chb_Iamb.setChecked(True)
            else:
                self.ui.chb_Iamb.setChecked(True)
                _I1x_name = self.get_Iamb_name(self.meas_sw,
                                               self.cfg.I1x_amb_id)
                _I1y_name = self.get_Iamb_name(self.meas_sw,
                                               self.cfg.I1y_amb_id)
                _I2x_name = self.get_Iamb_name(self.meas_sw2,
                                               self.cfg.I2x_amb_id)
                _I2y_name = self.get_Iamb_name(self.meas_sw2,
                                               self.cfg.I2y_amb_id)
                self.ui.cmb_I1x_amb.setCurrentText(_I1x_name)
                self.ui.cmb_I1y_amb.setCurrentText(_I1y_name)
                self.ui.cmb_I2x_amb.setCurrentText(_I2x_name)
                self.ui.cmb_I2y_amb.setCurrentText(_I2y_name)

            self.ui.dsb_x_start_pos.setValue(self.cfg.x_start_pos)
            self.ui.dsb_x_end_pos.setValue(self.cfg.x_end_pos)
            self.ui.dsb_x_step.setValue(self.cfg.x_step)
            self.ui.dsb_x_duration.setValue(self.cfg.x_duration)

            self.ui.dsb_y_start_pos.setValue(self.cfg.y_start_pos)
            self.ui.dsb_y_end_pos.setValue(self.cfg.y_end_pos)
            self.ui.dsb_y_step.setValue(self.cfg.y_step)
            self.ui.dsb_y_duration.setValue(self.cfg.y_duration)

            self.ui.sb_repetitions.setValue(self.cfg.repetitions)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def save_cfg(self):
        """Saves current ui configuration into database."""
        try:
            self.update_cfg_from_ui()
            self.cfg.db_update_database(
                        self.database_name,
                        mongo=self.mongo, server=self.server)
            self.cfg.db_save()
            self.update_cfg_list()
            _QMessageBox.information(self, 'Information',
                                     'Configuration Saved.',
                                     _QMessageBox.Ok)
            return True
        except Exception:
            _QMessageBox.warning(self, 'Information',
                                 'Failed to save this configuration.',
                                 _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def update_cfg_list(self):
        """Updates configuration name list in combobox."""
        try:
            _update_db_name_list(self.cfg, self.ui.cmb_cfg_name)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_cfg_from_ui(self):
        """Updates current measurement configuration from ui widgets.

        Returns:
            True if successfull;
            False otherwise."""
        try:
            self.cfg.name = (self.ui.le_map_name.text() +
                             _time.strftime('_%y%m%d_%H%M'))
            self.cfg.comments = self.ui.le_comments.text()

            self.cfg.Ix = 1*self.ui.chb_Ix.isChecked()
            self.cfg.Iy = 1*self.ui.chb_Iy.isChecked()
            self.cfg.I1 = 1*self.ui.chb_I1.isChecked()
            self.cfg.I2 = 1*self.ui.chb_I2.isChecked()

            if self.ui.chb_Iamb.isChecked():
                self.cfg.I1x_amb_id = 0
                self.cfg.I1y_amb_id = 0
                self.cfg.I2x_amb_id = 0
                self.cfg.I2y_amb_id = 0

            else:
                _I1x_amb_name = self.ui.cmb_I1x_amb.currentText()
                _I1y_amb_name = self.ui.cmb_I1y_amb.currentText()
                _I2x_amb_name = self.ui.cmb_I2x_amb.currentText()
                _I2y_amb_name = self.ui.cmb_I2y_amb.currentText()
                self.cfg.I1x_amb_id = self.get_Iamb_id(self.meas_sw,
                                                       _I1x_amb_name)
                self.cfg.I1y_amb_id = self.get_Iamb_id(self.meas_sw,
                                                       _I1y_amb_name)
                self.cfg.I2x_amb_id = self.get_Iamb_id(self.meas_sw2,
                                                       _I2x_amb_name)
                self.cfg.I2y_amb_id = self.get_Iamb_id(self.meas_sw2,
                                                       _I2y_amb_name)

            self.cfg.x_start_pos = self.ui.dsb_x_start_pos.value()
            self.cfg.x_end_pos = self.ui.dsb_x_end_pos.value()
            self.cfg.x_step = self.ui.dsb_x_step.value()
            self.cfg.x_duration = self.ui.dsb_x_duration.value()

            self.cfg.y_start_pos = self.ui.dsb_y_start_pos.value()
            self.cfg.y_end_pos = self.ui.dsb_y_end_pos.value()
            self.cfg.y_step = self.ui.dsb_y_step.value()
            self.cfg.y_duration = self.ui.dsb_y_duration.value()

            self.cfg.repetitions = self.ui.sb_repetitions.value()

            return True
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def update_iamb_list(self):
        """Updates Iamb list on integrals map dialog."""
        _meas_I1, _meas_I2 = _pandas_load_db_measurements()

        _I1x_amb = _meas_I1.loc[(_meas_I1['Iamb_id'] == 0) &
                                (_meas_I1['motion_axis'] == 'Y')]
        _I1y_amb = _meas_I1.loc[(_meas_I1['Iamb_id'] == 0) &
                                (_meas_I1['motion_axis'] == 'X')]

        _I2x_amb = _meas_I2.loc[(_meas_I2['Iamb_id'] == 0) &
                                ((_meas_I2['motion_axis'] == 'Ya') |
                                 (_meas_I2['motion_axis'] == 'Yb'))]
        _I2y_amb = _meas_I2.loc[(_meas_I2['Iamb_id'] == 0) &
                                ((_meas_I2['motion_axis'] == 'Xa') |
                                 (_meas_I2['motion_axis'] == 'Xb'))]

        self.ui.cmb_I1x_amb.addItems(
            [item for item in _I1x_amb['name'].values])
        self.ui.cmb_I1x_amb.setCurrentIndex(len(_I1x_amb['name']) - 1)

        self.ui.cmb_I1y_amb.addItems(
            [item for item in _I1y_amb['name'].values])
        self.ui.cmb_I1y_amb.setCurrentIndex(len(_I1y_amb['name']) - 1)

        self.ui.cmb_I2x_amb.addItems(
            [item for item in _I2x_amb['name'].values])
        self.ui.cmb_I2x_amb.setCurrentIndex(len(_I2x_amb['name']) - 1)

        self.ui.cmb_I2y_amb.addItems(
            [item for item in _I2y_amb['name'].values])
        self.ui.cmb_I2y_amb.setCurrentIndex(len(_I2y_amb['name']) - 1)
