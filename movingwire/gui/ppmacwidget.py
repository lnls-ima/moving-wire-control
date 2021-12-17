"""PPMAC widget for the Moving Wire Control application."""

import os as _os
import sys as _sys
import numpy as _np
import time as _time
import traceback as _traceback

from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtCore import (
    Qt as _Qt,
    QTimer as _QTimer,
    )
import qtpy.uic as _uic

from movingwire.gui.fiducialdialog import FiducialDialog \
    as _FiducialDialog
from ueipaccontrol.ueipac.gui import ueipacapp \
    as _ueipacapp

from movingwire.gui.utils import (
    get_ui_file as _get_ui_file,
    sleep as _sleep,
    update_db_name_list as _update_db_name_list,
    load_db_from_name as _load_db_from_name,
    )
from movingwire.devices import ppmac as _ppmac
import movingwire.data as _data


class PpmacWidget(_QWidget):
    """PPMAC widget class for the Moving Wire Control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        # self.x_sf = 2e-8  # meters/count
        # self.y_sf = 2e-8  # meters/count

        self.angular_sf = 1e-3  # deg/count

        self.ppmac = _ppmac
        self.cfg = _data.configuration.PpmacConfig()
        self.fiduc_cfg = _data.configuration.FiducializationCfg()

        self.steps_per_turn = 102400  # rotation motor steps/turn
        # self.y_stps_per_cnt = 102.4  # steps/encoder count

        # self.cfg.y_stps_per_cnt = self.y_stps_per_cnt  # steps/encoder count

        self.update_flag = True
        self.timer = _QTimer()
        self.timer.start(1000)

        self.update_cfg_list()
#         self.load_cfg()
        self.update_cfg_from_ui()
        self.connect_signal_slots()

    def init_tab(self):
        name = self.ui.cmb_cfg_name.currentText()
        _load_db_from_name(self.cfg, name)
        self.load_cfg_into_ui()

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
        self.ui.timer.timeout.connect(self.update_position)
        # self.ui.cmb_cfg_name.currentIndexChanged.connect(self.load_cfg)
        self.ui.pbt_move.clicked.connect(self.move)
        self.ui.pbt_move_xy.clicked.connect(self.move_xy)
        self.ui.pbt_home.clicked.connect(self.home)
        self.ui.pbt_home_x.clicked.connect(self.home_x)
        self.ui.pbt_home_y.clicked.connect(self.home_y)
        self.ui.pbt_configure.clicked.connect(self.configure_ppmac)
        self.ui.pbt_save_cfg.clicked.connect(self.save_cfg)
        self.ui.pbt_load_cfg.clicked.connect(self.load_cfg)
        self.ui.pbt_update_cfg.clicked.connect(self.update_cfg_list)
        self.ui.pbt_move_x.clicked.connect(self.move_x_ui)
        self.ui.pbt_move_y.clicked.connect(self.move_y_ui)
        self.ui.pbt_stop_motors.clicked.connect(self.stop_motors)
        self.ui.pbt_fiducialization.clicked.connect(self.fiducial_dialog)
        self.ui.pbt_mount_neg_lim.clicked.connect(self.mount_neg_lim)
        self.ui.pbt_mount_pos_lim.clicked.connect(self.mount_pos_lim)
        self.ui.pbt_clear_faults.clicked.connect(self.clear_faults)
        self.ui.pbt_wire_tension.clicked.connect(self.wire_tension_dialog)

    def enable_moving_buttons(self, state=True):
        self.ui.pbt_move_xy.setEnabled(state)
        self.ui.pbt_home_x.setEnabled(state)
        self.ui.pbt_home_y.setEnabled(state)
        self.ui.pbt_configure.setEnabled(state)
        self.ui.pbt_move_x.setEnabled(state)
        self.ui.pbt_move_y.setEnabled(state)
        self.ui.pbt_fiducialization.setEnabled(state)
        self.ui.pbt_mount_neg_lim.setEnabled(state)
        self.ui.pbt_mount_pos_lim.setEnabled(state)
        self.ui.pbt_clear_faults.setEnabled(state)

    def update_position(self):
        """Updates position displays on ui."""
        try:
            if hasattr(_ppmac, 'ppmac'):
                if all([self.update_flag,
                        not _ppmac.ppmac.closed,
                        self.parent().currentWidget() == self]):
                    self.pos = _ppmac.read_motor_pos([1, 2, 3, 4, 7, 8])
                    self.ui.lcd_pos1.display(
                        self.pos[0]*self.cfg.x_sf - self.cfg.x_offset)
                    self.ui.lcd_pos2.display(
                        self.pos[4]*self.cfg.y_sf - self.cfg.y_offset)
                    self.ui.lcd_pos3.display(
                        self.pos[2]*self.cfg.x_sf - self.cfg.x_offset)
                    self.ui.lcd_pos4.display(
                        self.pos[5]*self.cfg.y_sf - self.cfg.y_offset)
                    # self.ui.lcd_pos5.display(self.pos[4]*self.angular_sf)
                    # self.ui.lcd_pos6.display(self.pos[5]*self.angular_sf)
                    _QApplication.processEvents()
        except Exception:
            # _traceback.print_exc(file=_sys.stdout)
            print('update_position failure in ppmacwidget.')

    def update_cfg_list(self):
        """Updates configuration name list in combobox."""
        try:
            _update_db_name_list(self.cfg, self.ui.cmb_cfg_name)
        except Exception:
            # _traceback.print_exc(file=_sys.stdout)
            print('update_cfg_list failure in ppmacwidget.')

    def update_cfg_from_ui(self):
        """Updates current measurement configuration from ui widgets.

        Returns:
            True if successfull;
            False otherwise."""
        try:
            self.cfg.name = self.ui.cmb_cfg_name.currentText()
            self.cfg.speed = self.ui.dsb_speed.value()
            self.cfg.accel = self.ui.dsb_accel.value()
            self.cfg.jerk = self.ui.dsb_jerk.value()
            self.cfg.rot_sf = self.ui.dsb_rot_sf.value()
            self.cfg.rot_max_err = self.ui.sb_rot_max_err.value()
            self.cfg.steps_per_turn = self.ui.sb_steps_per_turn.value()
            self.cfg.home_offset5 = self.ui.sb_home_offset5.value()
            self.cfg.home_offset6 = self.ui.sb_home_offset6.value()

            self.cfg.pos_x = self.ui.dsb_pos_x.value()
            self.cfg.x_step = self.ui.dsb_x_step.value()
            self.cfg.speed_x = self.ui.dsb_speed_x.value()
            self.cfg.accel_x = self.ui.dsb_accel_x.value()
            self.cfg.jerk_x = self.ui.dsb_jerk_x.value()
            self.cfg.min_x = self.ui.dsb_min_x.value()
            self.cfg.max_x = self.ui.dsb_max_x.value()
            self.cfg.x_sf = self.ui.dsb_x_sf.value()
            self.cfg.x_offset = self.ui.dsb_x_offset.value()
            self.cfg.home_offset1 = self.ui.sb_home_offset1.value()
            self.cfg.home_offset3 = self.ui.sb_home_offset3.value()

            self.cfg.pos_y = self.ui.dsb_pos_y.value()
            self.cfg.y_step = self.ui.dsb_y_step.value()
            self.cfg.speed_y = self.ui.dsb_speed_y.value()
            self.cfg.accel_y = self.ui.dsb_accel_y.value()
            self.cfg.jerk_y = self.ui.dsb_jerk_y.value()
            self.cfg.min_y = self.ui.dsb_min_y.value()
            self.cfg.max_y = self.ui.dsb_max_y.value()
            self.cfg.y_sf = self.ui.dsb_y_sf.value()
            self.cfg.y_stps_per_cnt = self.ui.dsb_y_stps_per_cnt.value()
            self.cfg.y_offset = self.ui.dsb_y_offset.value()
            self.cfg.max_pos_error = self.ui.dsb_max_pos_error.value()
            self.cfg.home_offset2 = self.ui.sb_home_offset2.value()
            self.cfg.home_offset4 = self.ui.sb_home_offset4.value()

            return True
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

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

    def load_cfg(self):
        """Load configuration from database."""
        try:
            name = self.ui.cmb_cfg_name.currentText()
            self.cfg.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            _id = self.cfg.db_search_field('name', name)[0]['id']
            self.cfg.db_read(_id)
            self.load_cfg_into_ui()
            _QMessageBox.information(self, 'Information',
                                     'Configuration Loaded.',
                                     _QMessageBox.Ok)
            return True
        except Exception:
            _QMessageBox.warning(self, 'Information',
                                 'Failed to load this configuration.',
                                 _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def load_fiduc_cfg(self):
        """Loads fiducialization configuration from database."""
        try:
            self.fiduc_cfg.db_update_database(
                    self.database_name,
                    mongo=self.mongo, server=self.server)
            self.fiduc_cfg.db_read(1)
            return True
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def write_fiduc_offsets(self, offset_xa, offset_xb):
        """Writes fiducialization offsets on DeltaTau.

        Args:
            offset_xa (int): Motor Xa offset in encoder counts;
            offset_xb (int): Motor Xb offset in encoder counts.
        Returns:
            True if successful, False othrewise."""
        pass

    def load_cfg_into_ui(self):
        """Loads database configuration into ui widgets."""
        try:
            self.ui.cmb_cfg_name.setCurrentText(self.cfg.name)
            self.ui.dsb_speed.setValue(self.cfg.speed)
            self.ui.dsb_accel.setValue(self.cfg.accel)
            self.ui.dsb_jerk.setValue(self.cfg.jerk)
            self.ui.dsb_rot_sf.setValue(self.cfg.rot_sf)
            self.ui.sb_rot_max_err.setValue(self.cfg.rot_max_err)
            self.ui.sb_steps_per_turn.setValue(self.cfg.steps_per_turn)
            self.ui.sb_home_offset5.setValue(self.cfg.home_offset5)
            self.ui.sb_home_offset6.setValue(self.cfg.home_offset6)

            self.ui.dsb_pos_x.setValue(self.cfg.pos_x)
            self.ui.dsb_x_step.setValue(self.cfg.x_step)
            self.ui.dsb_speed_x.setValue(self.cfg.speed_x)
            self.ui.dsb_accel_x.setValue(self.cfg.accel_x)
            self.ui.dsb_jerk_x.setValue(self.cfg.jerk_x)
            self.ui.dsb_min_x.setValue(self.cfg.min_x)
            self.ui.dsb_max_x.setValue(self.cfg.max_x)
            self.ui.dsb_x_sf.setValue(self.cfg.x_sf)
            self.ui.dsb_x_offset.setValue(self.cfg.x_offset)
            self.ui.sb_home_offset1.setValue(self.cfg.home_offset1)
            self.ui.sb_home_offset3.setValue(self.cfg.home_offset3)

            self.ui.dsb_pos_y.setValue(self.cfg.pos_y)
            self.ui.dsb_y_step.setValue(self.cfg.y_step)
            self.ui.dsb_speed_y.setValue(self.cfg.speed_y)
            self.ui.dsb_accel_y.setValue(self.cfg.accel_y)
            self.ui.dsb_jerk_y.setValue(self.cfg.jerk_y)
            self.ui.dsb_min_y.setValue(self.cfg.min_y)
            self.ui.dsb_max_y.setValue(self.cfg.max_y)
            self.ui.dsb_y_sf.setValue(self.cfg.y_sf)
            self.ui.dsb_y_stps_per_cnt.setValue(self.cfg.y_stps_per_cnt)
            self.ui.dsb_y_offset.setValue(self.cfg.y_offset)
            self.ui.dsb_max_pos_error.setValue(self.cfg.max_pos_error)
            self.ui.sb_home_offset2.setValue(self.cfg.home_offset2)
            self.ui.sb_home_offset4.setValue(self.cfg.home_offset4)
            _QApplication.processEvents()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def configure_ppmac(self):
        """Configures PPMAC motor parameters using ui values."""
        try:
            self.enable_moving_buttons(False)
            self.update_cfg_from_ui()

            _spd = self.cfg.speed * self.steps_per_turn * 10**-3  # [turns/s]
            if self.cfg.accel != 0:
                _ta = -1/self.cfg.accel * 1/self.steps_per_turn * 10**6  # [turns/s^2]
            else:
                _ta = 0
            if self.cfg.jerk != 0:
                _ts = -1/self.cfg.jerk * 1/self.steps_per_turn * 10**9  # [turns/s^3]
            else:
                _ts = 0

            _spd_x = self.cfg.speed_x / self.cfg.x_sf * 10**-3
            if self.cfg.accel_x != 0:
                _ta_x = (-1/self.cfg.accel_x)*self.cfg.x_sf*10**6
            else:
                _ta_x = 0
            if self.cfg.jerk_x != 0:
                _ts_x = (-1/self.cfg.jerk_x)*self.cfg.x_sf*10**9
            else:
                _ts_x = 0

            # self.cfg.y_sf [mm/count]
            # self.cfg.y_stps_per_cnt [steps/count]
            _spd_y = (self.cfg.speed_y/self.cfg.y_sf)*self.cfg.y_stps_per_cnt*10**-3
            if self.cfg.accel_y != 0:
                _ta_y = (-1/self.cfg.accel_y)*self.cfg.y_sf/self.cfg.y_stps_per_cnt*10**6
            else:
                _ta_y = 0
            if self.cfg.jerk_y != 0:
                _ts_y = (-1/self.cfg.jerk_y)*self.cfg.y_sf/self.cfg.y_stps_per_cnt*10**9
            else:
                _ts_y = 0

            self.enable_moving_buttons(True)
            self.update_flag = False
            self.timer.stop()
            _sleep(0.2)
            # Configures rotation motors:
            for i in [5, 6]:
                if i == 5:
                    _home_offset = self.cfg.home_offset5
                else:
                    _home_offset = self.cfg.home_offset6
                msg = ('Motor[{0}].JogSpeed={1};'
                       'Motor[{0}].JogTa={2};'
                       'Motor[{0}].JogTs={3};'
                       'Motor[{0}].HomeOffset={4}'.format(i, _spd, _ta, _ts,
                                                          _home_offset))
#                 with _ppmac.lock_ppmac:
                _ppmac.write(msg)

            # Configures X motors:
            for i in [1, 3]:
                msg = ('Motor[{0}].JogSpeed={1};'
                       'Motor[{0}].JogTa={2};'
                       'Motor[{0}].JogTs={3}'.format(i, _spd_x, _ta_x, _ts_x))
#                 with _ppmac.lock_ppmac:
                _ppmac.write(msg)

            # Configures Y motors:
            for i in [2, 4]:
                msg = ('Motor[{0}].JogSpeed={1};'
                       'Motor[{0}].JogTa={2};'
                       'Motor[{0}].JogTs={3}'.format(i, _spd_y, _ta_y, _ts_y))
#                 with _ppmac.lock_ppmac:
                _ppmac.write(msg)
            _sleep(0.1)
            _ppmac.read()

            # Checks fiducialization parameters
            xa_comp_pos = int(_ppmac.query_motor_param(1, 'CompPos'))
            xb_comp_pos = int(_ppmac.query_motor_param(3, 'CompPos'))
            self.load_fiduc_cfg()
            if any([xa_comp_pos != int(self.fiduc_cfg.offset_xa),
                    xb_comp_pos != int(self.fiduc_cfg.offset_xb)]):
                _QMessageBox.warning(self, 'Warning',
                                     'Fiducialization parameters are wrong;'
                                     ' Please home the X axis.',
                                     _QMessageBox.Ok)
            _QMessageBox.information(self, 'Information',
                                     'PPMAC configured.',
                                     _QMessageBox.Ok)

            # checks homing
            self.check_homed()

            self.update_flag = True
            self.timer.start(1000)
        except Exception:
            # _traceback.print_exc(file=_sys.stdout)
            print('configure_ppmac failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)

    def home(self):
        """Home rotation motors.

        Returns:
            True if successfull;
            False otherwise."""
        try:
            self.update_flag = False
            self.timer.stop()
            _home5 = self.cfg.home_offset5
            _home6 = self.cfg.home_offset6
            _msg = 'Motor[7].HomeOffset={0};Motor[8].HomeOffset={1}'.format(
                _home5, _home6)
#             with _ppmac.lock_ppmac:
            _ppmac.write(_msg)
            _ppmac.write('enable plc HomeA')
            _sleep(0.1)
            _ppmac.read()
            _sleep(3)
            while (all([not _ppmac.motor_homed(5),
                        not _ppmac.motor_homed(6)])):
                _sleep(1)
            self.ppmac.remove_backlash(0)
#             self.ui.chb_homed.setChecked(True)
            self.update_flag = True
            self.timer.start(1000)
            return True
        except Exception:
            self.ui.chb_homed.setChecked(False)
            # _traceback.print_exc(file=_sys.stdout)
            print('home failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)
            return False

    def home_x(self):
        """Home X motors.

        Returns:
            True if successfull;
            False otherwise."""
        try:
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'home the X axis?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

            self.enable_moving_buttons(False)
            # self.ui.chb_homed_x.setCheckable(True)
            self.ui.groupBox_3.setEnabled(False)
            self.ui.pbt_configure.setEnabled(False)
            self.ui.pbt_fiducialization.setEnabled(False)
            self.parent_window.ui.twg_main.setTabEnabled(3, False)
            _QApplication.processEvents()
            self.update_flag = False
            self.timer.stop()
            _sleep(0.5)

            # Clears fiducialization offsets
            _ppmac.set_motor_param(1, 'CompPos', 0)
            _ppmac.set_motor_param(3, 'CompPos', 0)
#             with _ppmac.lock_ppmac:
            _ppmac.write('#1,3j/')
            _ppmac.write('enable plc HomeX')
            _sleep(0.1)
            _ppmac.read()
            _sleep(3)

            _t0 = _time.time()
            while (all([not _ppmac.motor_homed(1),
                        not _ppmac.motor_homed(3)])):
                _sleep(1)
                if _time.time() - _t0 > 10*60:
                    raise RuntimeError('X Homing timeout (10 minutes).')

            _sleep(2)

            # Sets fiducialization parameters again:
            self.load_fiduc_cfg()
            _ppmac.write('#1..3k')
            _ppmac.set_motor_param(1, 'CompPos', self.fiduc_cfg.offset_xa)
            _ppmac.set_motor_param(3, 'CompPos', self.fiduc_cfg.offset_xb)
            _ppmac.write('#1,3j/')

            self.move_x(0)

            self.ui.groupBox_3.setEnabled(True)
            self.ui.chb_homed_x.setChecked(True)
            _QApplication.processEvents()
            # self.ui.chb_homed_x.setCheckable(False)
            self.ui.pbt_configure.setEnabled(True)
            self.ui.pbt_fiducialization.setEnabled(True)
            self.parent_window.ui.twg_main.setTabEnabled(3, True)

            self.enable_moving_buttons(True)
            # move_y enables timer, no need to start it again
            # self.timer.start(1000)
            _QMessageBox.information(self, 'Information',
                                     'X homing complete.',
                                     _QMessageBox.Ok)
            return True
        except Exception:
            self.ui.groupBox_3.setEnabled(True)
            self.ui.chb_homed_x.setChecked(False)
            # self.ui.chb_homed_x.setCheckable(False)
            self.ui.pbt_configure.setEnabled(True)
            self.ui.pbt_fiducialization.setEnabled(True)
            self.parent_window.ui.twg_main.setTabEnabled(3, True)

            # _traceback.print_exc(file=_sys.stdout)
            print('home_x failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)
            _QMessageBox.warning(self, 'Warning',
                                 'X homing failed.',
                                 _QMessageBox.Ok)
            return False

    def home_y(self):
        """Home Y motors.

        Returns:
            True if successfull;
            False otherwise"""
        try:
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'home the Y axis?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

            self.enable_moving_buttons(False)
            # self.ui.chb_homed_y.setCheckable(True)
            self.ui.groupBox_3.setEnabled(False)
            self.ui.pbt_configure.setEnabled(False)
            self.ui.pbt_fiducialization.setEnabled(False)
            self.update_flag = False
            self.timer.stop()
            _sleep(0.5)

            # moves fast closer to the negative limit
            self.move_y(-15)

            # move_y enables timer again
            self.update_flag = False
            self.timer.stop()
            _sleep(0.5)

            _ppmac.write('#2,4j/')
            _ppmac.write('enable plc HomeYopen')
            _sleep(0.1)
            _ppmac.read()
            _sleep(3)

            _t0 = _time.time()
            while (all([not _ppmac.motor_homed(2),
                        not _ppmac.motor_homed(4)])):
                _sleep(1)
                if _time.time() - _t0 > 10*60:
                    raise RuntimeError('Y Homing timeout (10 minutes).')

            _sleep(2)
            self.move_y(0)

            self.ui.chb_homed_y.setChecked(True)
            # self.ui.chb_homed_y.setCheckable(False)
            self.ui.groupBox_3.setEnabled(True)
            self.ui.pbt_configure.setEnabled(True)
            self.ui.pbt_fiducialization.setEnabled(True)
            # move_y enables timer, no need to start it again
            # self.timer.start(1000)

            self.enable_moving_buttons(True)
            _QMessageBox.information(self, 'Information',
                                     'Y homing complete.',
                                     _QMessageBox.Ok)
            return True
        except Exception:
            self.ui.chb_homed_y.setChecked(False)
            # self.ui.chb_homed_y.setCheckable(False)
            self.ui.groupBox_3.setEnabled(True)
            self.ui.pbt_configure.setEnabled(True)
            self.ui.pbt_fiducialization.setEnabled(True)

            # _traceback.print_exc(file=_sys.stdout)
            print('home_y failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)
            _QMessageBox.warning(self, 'Warning',
                                 'Y homing failed.',
                                 _QMessageBox.Ok)
            return False

    def move(self):
        """Move rotation motors."""
        try:
            _steps = [self.ui.sb_steps5.value(), self.ui.sb_steps6.value()]
            if self.ui.rdb_abs.isChecked():
                _mode = '='
            else:
                _mode = '^'
#             with _ppmac.lock_ppmac:
            self.update_flag = False
            self.timer.stop()
            _ppmac.write('#5j' + _mode + str(_steps[0]) +
                         ';#6j' + _mode + str(_steps[1]))
            _sleep(0.1)
            _ppmac.read()
            self.update_flag = True
            self.timer.start(1000)
        except Exception:
            # _traceback.print_exc(file=_sys.stdout)
            print('move failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)

    def move_x(self, position, absolute=True, motor=None):
        """Move X motors and returns only after they stop.

        Args:
            position (float): desired position in [mm];
            absolute (bool): True for absolute positioning;
                             False for relative positioning.
            motor (int): if motor is 1 or 3, moves only the selected motor.
                         Moves both motors otherwise.
        Returns:
            True if successfull;
            False otherwise."""
        try:
            _x_lim = [self.cfg.min_x + self.cfg.x_offset,
                      self.cfg.max_x + self.cfg.x_offset]  # [mm]
            _pos_x = position + self.cfg.x_offset  # [mm] *10**-3/self.cfg.x_sf
            _status = False

            if _x_lim[0] <= _pos_x <= _x_lim[1]:
                _pos_x = int(_pos_x/self.cfg.x_sf)
            else:
                _QMessageBox.warning(self, 'Information',
                                     'X position out of range.',
                                     _QMessageBox.Ok)
                return False

            if absolute:
                _mode = '='
            else:
                _mode = '^'

            self.update_flag = False
            self.timer.stop()
            # _sleep(0.2)

            print('X position: {0}'.format(_pos_x))

            if not (motor in [1, 3]):
                _ppmac.write('#2,4,5,6k')
                _ppmac.write('#1,3j/')
                _msg_x = '#1,3j' + _mode + str(_pos_x)
                _ppmac.write(_msg_x)
                _ppmac.read()
                _sleep(0.2)
                while (not all([self.ppmac.motor_stopped(1),
                                self.ppmac.motor_stopped(3)])):
                    _sleep(0.2)

                if not any([_ppmac.motor_fault(1),
                            _ppmac.motor_fault(3),
                            _ppmac.motor_limits(1),
                            _ppmac.motor_limits(3),
                            _ppmac.motor_fefatal(1),
                            _ppmac.motor_fefatal(3)]):
                    _status = True

            else:
                _ppmac.write('#2,4,5,6k')
                _ppmac.write('#{0}j/'.format(motor))
                _msg_x = '#{0}j'.format(motor) + _mode + str(_pos_x)
                _ppmac.write(_msg_x)
                _ppmac.read()
                _sleep(0.2)
                while not self.ppmac.motor_stopped(motor):
                    _sleep(0.2)

                if not _ppmac.motor_fault(motor):
                    _status = True

            if _status:
                self.update_flag = True
                self.timer.start(1000)
                return True
            else:
                print('X motor faulted or limit switch active.')
                self.update_flag = True
                self.timer.start(1000)
                return False

        except Exception:
            # _traceback.print_exc(file=_sys.stdout)
            print('move_x failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)
            return False

    def move_y(self, position, absolute=True, motor=None):
        """Move Y motors in open loop (verifying encoder positions at motors 7
           and 8) and returns only after they stop.

        Args:
            position (float): desired position in [mm];
            absolute (bool): True for absolute positioning;
                             False for relative positioning.
            motor (int): if motor is 2 or 4, moves only the selected motor.
                         Moves both motors otherwise.
        Returns:
            True if successfull;
            False otherwise."""
        try:
            _y_lim = [self.cfg.min_y + self.cfg.y_offset,
                      self.cfg.max_y + self.cfg.y_offset]  # [mm]
            _pos_y = position + self.cfg.y_offset  # [mm]
            _status = False
            _limit_error = False

            _pos_y = _pos_y/self.cfg.y_sf  # [encoder counts]

            # max_pos_error in encoder counts
            max_pos_error = self.cfg.max_pos_error * 1e-3 / self.cfg.y_sf

            _mode = '^'
            _present_y_pos = _ppmac.read_motor_pos([7, 8])
            if absolute:
                _target_y_pos = _pos_y  # [encoder counts]
                _y_steps = (_pos_y - _present_y_pos)*self.cfg.y_stps_per_cnt
                if not (_y_lim[0] <= _target_y_pos*self.cfg.y_sf <= _y_lim[1]):
                    _limit_error = True
            else:
                _target_y_pos = _present_y_pos + _pos_y  # [encoder counts]
                _y_steps = _np.ones(2) * (_pos_y*self.cfg.y_stps_per_cnt)
                for target in _target_y_pos:
                    if not (_y_lim[0] <= target*self.cfg.y_sf <= _y_lim[1]):
                        _limit_error = True

            if _limit_error:
                    _QMessageBox.warning(self, 'Warning',
                                         'Y position out of range.',
                                         _QMessageBox.Ok)
                    return False

            self.update_flag = False
            self.timer.stop()
            # _sleep(0.4)

            print('Y steps: {0}'.format(_y_steps))

            if not (motor in [2, 4]):
                _ppmac.write('#1,3,5,6k')
                _ppmac.write('#2,4j/')
                _msg_y = '#2j{0}{1};#4j{0}{2}'.format(_mode, int(_y_steps[0]),
                                                      int(_y_steps[1]))
                _ppmac.write(_msg_y)
                _ppmac.read()
                _sleep(0.2)
                while (not all([self.ppmac.motor_stopped(2),
                                self.ppmac.motor_stopped(4)])):
                    _sleep(0.2)

                _present_y_pos = _ppmac.read_motor_pos([7, 8])
                _pos_diff = _target_y_pos - _present_y_pos

                for diff in _pos_diff:
                    if abs(diff) > max_pos_error:  # [encoder counts]
                        raise RuntimeError('Y motor positioning error.')

                if not any([_ppmac.motor_fault(2),
                            _ppmac.motor_fault(4),
                            _ppmac.motor_limits(2),
                            _ppmac.motor_limits(4)]):
                    _status = True

            else:
                if motor == 2:
                    _y_steps = int(_y_steps[0])
                    enc = 7
                    if isinstance(_target_y_pos, _np.ndarray):
                        _target_y_pos = _target_y_pos[0]
                elif motor == 4:
                    _y_steps = int(_y_steps[1])
                    enc = 8
                    if isinstance(_target_y_pos, _np.ndarray):
                        _target_y_pos = _target_y_pos[1]

                _ppmac.write('#1,3,5,6k')
                _ppmac.write('#{0}j/'.format(motor))
                _msg_y = '#{0}j{1}{2}'.format(motor, _mode, _y_steps)
                _ppmac.write(_msg_y)
                _ppmac.read()
                _sleep(0.2)
                while not self.ppmac.motor_stopped(motor):
                    _sleep(0.2)

                _present_y_pos = _ppmac.read_motor_pos([enc])[0]
                _pos_diff = _target_y_pos - _present_y_pos

                if abs(_pos_diff) > max_pos_error:  # [encoder counts]
                    raise RuntimeError('Y motor lost pulses.')

                if not _ppmac.motor_fault(motor):
                    _status = True

            if _status:
                self.update_flag = True
                self.timer.start(1000)
                return True
            else:
                print('Y motor faulted or limit switch active.')
                self.update_flag = True
                self.timer.start(1000)
                return False

        except Exception:
            #_traceback.print_exc(file=_sys.stdout)
            print('move_y failure in ppmacwidget.')
            self.update_flag = True
            self.timer.start(1000)
            return False

    def move_xy(self):
        """Move X and Y motors."""
        try:
            self.enable_moving_buttons(False)
            _pos_x = self.ui.dsb_pos_x.value()
            _pos_y = self.ui.dsb_pos_y.value()

            if self.ui.rdb_abs_xy.isChecked():
                absolute = True
            else:
                absolute = False

            self.move_x(_pos_x, absolute=absolute)
            self.move_y(_pos_y, absolute=absolute)

            self.enable_moving_buttons(True)
            return True
        except Exception:
            #_traceback.print_exc(file=_sys.stdout)
            print('move_xy failure in ppmacwidget.')
            self.enable_moving_buttons(True)
            # self.timer.start(1000)
            return False

    def move_x_ui(self):
        """Move X axis from UI."""
        if not self.check_x_homed():
            _ans = _QMessageBox.question(self, 'Warning', 'The system axes'
                                         ' are not homed. The positions '
                                         'are not referenced and this '
                                         'might also damage the stretched '
                                         'wire. Would you like to '
                                         'continue anyway?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

        self.update_flag = False
        _sleep(0.4)
        self.enable_moving_buttons(False)
        position = self.ui.dsb_pos_x.value()
        if self.ui.rdb_abs_xy.isChecked():
            absolute = True
        else:
            absolute = False
        self.move_x(position, absolute)
        self.enable_moving_buttons(True)

    def move_y_ui(self):
        """Move Y axis from UI."""
        if not self.check_y_homed():
            _ans = _QMessageBox.question(self, 'Warning', 'The system axes'
                                         ' are not homed. The positions '
                                         'are not referenced and this '
                                         'might also damage the stretched '
                                         'wire. Would you like to '
                                         'continue anyway?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

        self.update_flag = False
        _sleep(0.4)
        self.enable_moving_buttons(False)
        position = self.ui.dsb_pos_y.value()
        if self.ui.rdb_abs_xy.isChecked():
            absolute = True
        else:
            absolute = False
        self.move_y(position, absolute)
        self.enable_moving_buttons(True)

    def mount_neg_lim(self):
        """Moves X motors close to negative limit switches."""
        _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                     'move the stages to the negative '
                                     'limit switches? The software position '
                                     'limits will be disconsidered.',
                                     _QMessageBox.Yes |
                                     _QMessageBox.No,
                                     _QMessageBox.No)
        if _ans == _QMessageBox.No:
            return False

        if not self.check_homed():
            _ans = _QMessageBox.question(self, 'Warning', 'The system axes'
                                         ' are not homed. The positions '
                                         'are not referenced and this '
                                         'might also damage the stretched '
                                         'wire. Would you like to '
                                         'continue anyway?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

        self.enable_moving_buttons(False)
        xa_min = -62
        xb_min = -57.5

        _max_x = self.cfg.max_x
        _min_x = self.cfg.min_x
        _max_y = self.cfg.max_y
        _min_y = self.cfg.min_y

        self.cfg.max_x = 99999
        self.cfg.min_x = -99999
        self.cfg.max_y = 99999
        self.cfg.min_y = -99999

        _mnt_neg_flag = False
        if self.move_y(0):
            if self.move_x(xb_min):
                if self.move_x(xa_min, motor=1):
                    _mnt_neg_flag = True

        else:
            if self.move_y(0):
                if self.move_x(xb_min):
                    if self.move_x(xa_min, motor=1):
                        _mnt_neg_flag = True

        self.cfg.max_x = _max_x
        self.cfg.min_x = _min_x
        self.cfg.max_y = _max_y
        self.cfg.min_y = _min_y

        self.enable_moving_buttons(True)
        if _mnt_neg_flag:
            _QMessageBox.information(self, 'Information', 'Mount- routine '
                                     'finished.')
            return True

        else:
            _QMessageBox.warning(self, 'Warning', 'Failed to move stages to '
                                 'negative mounting position. Try lowering '
                                 'speed and acceleration.')
            return False

    def mount_pos_lim(self):
        """Moves X motors close to positive limit switches."""
        _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                     'move the stages to the positive '
                                     'limit switches? The software position '
                                     'limits will be disconsidered.',
                                     _QMessageBox.Yes |
                                     _QMessageBox.No,
                                     _QMessageBox.No)
        if _ans == _QMessageBox.No:
            return False

        if not self.check_homed():
            _ans = _QMessageBox.question(self, 'Warning', 'The system axes'
                                         ' are not homed. The positions '
                                         'are not referenced and this '
                                         'might also damage the stretched '
                                         'wire. Would you like to '
                                         'continue anyway?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

        self.enable_moving_buttons(False)
        xa_max = 39.6
        xb_max = 44.1

        ya_min = -9.7
        yb_min = -6.7

        _max_x = self.cfg.max_x
        _min_x = self.cfg.min_x
        _max_y = self.cfg.max_y
        _min_y = self.cfg.min_y

        self.cfg.max_x = 99999
        self.cfg.min_x = -99999
        self.cfg.max_y = 99999
        self.cfg.min_y = -99999

        # ya_max = 29.8
        # yb_max = 33

        _mnt_pos_flag = False
        if self.move_y(0):
            if self.move_x(xa_max):
                if self.move_x(xb_max, motor=3):
                    if self.move_y(yb_min):
                        if self.move_y(ya_min, motor=2):
                            _mnt_pos_flag = True
        else:
            if self.move_y(0):
                if self.move_x(xa_max):
                    if self.move_x(xb_max, motor=3):
                        if self.move_y(yb_min):
                            if self.move_y(ya_min, motor=2):
                                _mnt_pos_flag = True

        self.cfg.max_x = _max_x
        self.cfg.min_x = _min_x
        self.cfg.max_y = _max_y
        self.cfg.min_y = _min_y

        self.enable_moving_buttons(True)
        if _mnt_pos_flag:
            _QMessageBox.information(self, 'Information', 'Mount+ routine '
                                     'finished.')
            return True

        else:
            _QMessageBox.warning(self, 'Warning', 'Failed to move stages to '
                                 'positive mounting position. Try lowering '
                                 'speed and acceleration.')
            return False

    def clear_faults(self):
        """Clears all motor amplifier faults."""
        try:
            self.update_flag = False
            self.timer.stop()
            _sleep(0.2)
            _ppmac.clear_motor_fault(1)
            _ppmac.clear_motor_fault(2)
            _ppmac.clear_motor_fault(3)
            _ppmac.clear_motor_fault(4)
            _sleep(0.2)
            self.update_flag = True
            self.timer.start(1000)
        except Exception:
            self.update_flag = True
            self.timer.start(1000)
            # _traceback.print_exc(file=_sys.stdout)
            print('claer_faults failure in ppmacwidget.')

    def stop_motors(self):
        """Stops and disables all motors."""
        try:
            self.update_flag = False
            self.timer.stop()
            _sleep(0.2)
            _ppmac.stop_motors()
            _sleep(0.2)
            self.update_flag = True
            self.timer.start(1000)
        except Exception:
            self.update_flag = True
            self.timer.start(1000)
            # _traceback.print_exc(file=_sys.stdout)
            print('stop_motors failure in ppmacwidget.')

    def check_x_homed(self):
        """Checks if X motors were homed.

        Returns:
            True if they were homed, False otherwise."""
        try:
            self.update_flag = False
            self.timer.stop()
            _sleep(0.2)
            if all([_ppmac.motor_homed(1),
                    _ppmac.motor_homed(3)]):
                homed = True
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'X axis motors are not homed. Please '
                                     'run the X homing routine.',
                                     _QMessageBox.Ok)
                homed = False
            _sleep(0.2)
            self.update_flag = True
            self.timer.start(1000)
            return homed
        except Exception:
            self.update_flag = True
            self.timer.start(1000)
            # _traceback.print_exc(file=_sys.stdout)
            raise
            print('check_x_homed failure in ppmacwidget.')
            return False

    def check_y_homed(self):
        """Checks if Y motors were homed.

        Returns:
            True if they were homed, False otherwise."""
        try:
            self.update_flag = False
            self.timer.stop()
            _sleep(0.4)
            if all([_ppmac.motor_homed(2),
                    _ppmac.motor_homed(4)]):
                homed = True
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Y axis motors are not homed. Please '
                                     'run the Y homing routine.',
                                     _QMessageBox.Ok)
                homed = False
            _sleep(0.2)
            self.update_flag = True
            self.timer.start(1000)
            return homed
        except Exception:
            self.update_flag = True
            self.timer.start(1000)
            # _traceback.print_exc(file=_sys.stdout)
            raise
            print('check_y_homed failure in ppmacwidget.')
            return False

    def check_homed(self):
        """Checks if X and Y motors were homed.

        Returns:
            True if they were homed, False otherwise."""
        try:
            if all([self.check_x_homed(),
                    self.check_y_homed()]):
                return True
            else:
                return False
        except Exception:
            # _traceback.print_exc(file=_sys.stdout)
            print('check_homed failure in ppmacwidget.')
            return False

    def fiducial_dialog(self):
        self.update_flag = False
        self.check_homed()
        self.fid_dialog = _FiducialDialog(self.parent_window.motors)
        self.fid_dialog.show()

    def wire_tension_dialog(self):
        self.ueipac_thread = _ueipacapp.run_in_thread()
