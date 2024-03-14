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
    QProgressDialog as _QProgressDialog
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
from movingwire.gui.motorstatusdialog import MotorStatus as _MotorStatus

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
        self.pos = _np.zeros(6)

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
        self.ui.pbt_configure.clicked.connect(self.configuration_button)
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
        self.ui.pbt_status.clicked.connect(self.status_button)

    def status_button(self):
        self.statuswindow = _MotorStatus(self.parent_window.motors)
        try:
            self.statuswindow.show()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

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
        self.ui.pbt_status.setEnabled(state)

    def configuration_button(self):
        self.configure_ppmac()
        _QMessageBox.information(self, 'Information',
                                 'PPMAC configured.',
                                 _QMessageBox.Ok)

    def update_position(self):
        """Updates position displays on ui."""
        try:
            if hasattr(_ppmac, 'ppmac'):
                if all([  # self.update_flag,
                        not _ppmac.ppmac.closed,
                        self.parent().currentWidget() == self]):
                    if self.update_flag:
                        self.pos = _ppmac.read_motor_pos([1, 2, 3, 4])
                    self.ui.lcd_pos1.display(
                        self.pos[1]*self.cfg.x_sf - self.cfg.x_offset)
                    self.ui.lcd_pos2.display(
                        self.pos[0]*self.cfg.y_sf - self.cfg.y_offset)
                    self.ui.lcd_pos3.display(
                        self.pos[3]*self.cfg.x_sf - self.cfg.x_offset)
                    self.ui.lcd_pos4.display(
                        self.pos[2]*self.cfg.y_sf - self.cfg.y_offset)

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

            _spd_y = self.cfg.speed_y / self.cfg.y_sf * 10**-3
            if self.cfg.accel_y != 0:
                _ta_y = (-1/self.cfg.accel_y)*self.cfg.y_sf*10**6
            else:
                _ta_y = 0
            if self.cfg.jerk_y != 0:
                _ts_y = (-1/self.cfg.jerk_y)*self.cfg.y_sf*10**9
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
            for i in [2, 4]:
                msg = ('Motor[{0}].JogSpeed={1};'
                       'Motor[{0}].JogTa={2};'
                       'Motor[{0}].JogTs={3}'.format(i, _spd_x, _ta_x, _ts_x))
#                 with _ppmac.lock_ppmac:
                _ppmac.write(msg)

            # Configures Y motors:
            for i in [1, 3]:
                msg = ('Motor[{0}].JogSpeed={1};'
                       'Motor[{0}].JogTa={2};'
                       'Motor[{0}].JogTs={3}'.format(i, _spd_y, _ta_y, _ts_y))
#                 with _ppmac.lock_ppmac:
                _ppmac.write(msg)
            _sleep(0.1)
            _ppmac.read()

            # Checks fiducialization parameters
            # xa_comp_pos = int(_ppmac.query_motor_param(2, 'CompPos'))
            # xb_comp_pos = int(_ppmac.query_motor_param(4, 'CompPos'))
            # self.load_fiduc_cfg()
            # if any([xa_comp_pos != int(self.fiduc_cfg.offset_xa),
            #         xb_comp_pos != int(self.fiduc_cfg.offset_xb)]):
            #     _QMessageBox.warning(self, 'Warning',
            #                          'Fiducialization parameters are wrong;'
            #                          ' Please home the X axis.',
            #                          _QMessageBox.Ok)
            '''_QMessageBox.information(self, 'Information',
                                     'PPMAC configured.',
                                     _QMessageBox.Ok)'''

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
            # Progress Dialog during the homing process
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'home the X axis?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

            # Set the hioming jog speed at 2mm/s
            _ppmac.set_motor_param(2, 'JogSpeed', 100)
            _ppmac.set_motor_param(4, 'JogSpeed', 50)

            xnofsteps = 4
            xactualstep = 0
            _prg_dialog = _QProgressDialog('Homing process in progress...', 'Abort', 0,
                                           xnofsteps, self)
            _prg_dialog.setWindowTitle('Homing X axis')
            _prg_dialog.show()
            _QApplication.processEvents()
            while _prg_dialog.wasCanceled() == False:

                self.enable_moving_buttons(False)
                # self.ui.chb_homed_x.setCheckable(True)
                self.ui.groupBox_3.setEnabled(False)
                self.ui.pbt_configure.setEnabled(False)
                self.ui.pbt_fiducialization.setEnabled(False)
                self.parent_window.ui.twg_main.setTabEnabled(3, False)
                _QApplication.processEvents()
                # self.update_flag = False
                self.timer.stop()
                _sleep(0.5)

                xactualstep += 1
                _prg_dialog.setValue(xactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                # Clears fiducialization offsets
                _ppmac.set_motor_param(2, 'CompPos', 0)
                _ppmac.set_motor_param(4, 'CompPos', 0)
    #             with _ppmac.lock_ppmac:
                _ppmac.write('#2,4j/')
                _ppmac.write('enable plc HomeX')
                _sleep(0.1)
                _ppmac.read()
                _sleep(3)

                xactualstep += 1
                _prg_dialog.setValue(xactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                _t0 = _time.time()
                while (all([not _ppmac.motor_homed(2),
                            not _ppmac.motor_homed(4)])):
                    _sleep(1)
                    if _time.time() - _t0 > 10*60:
                        raise RuntimeError('X Homing timeout (10 minutes).')
                    self.update_position()
                    _QApplication.processEvents()
                    if _prg_dialog.wasCanceled() == True:
                        self.stop_motors()
                        raise RuntimeError('Homing Aborted')

                _sleep(2)

                xactualstep += 1
                _prg_dialog.setValue(xactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                # Sets fiducialization parameters again:
                self.load_fiduc_cfg()
                _ppmac.write('#2,4k')
                _ppmac.set_motor_param(2, 'CompPos', self.fiduc_cfg.offset_xa)
                _ppmac.set_motor_param(4, 'CompPos', self.fiduc_cfg.offset_xb)
                _ppmac.write('#2,4j/')

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

                xactualstep += 1
                _prg_dialog.setValue(xactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                _QMessageBox.information(self, 'Information',
                                         'X homing complete.',
                                         _QMessageBox.Ok)
                return True
                break

        except Exception:
            self.ui.groupBox_3.setEnabled(True)
            self.ui.chb_homed_x.setChecked(False)
            # self.ui.chb_homed_x.setCheckable(False)
            self.ui.pbt_configure.setEnabled(True)
            self.ui.pbt_fiducialization.setEnabled(True)
            self.parent_window.ui.twg_main.setTabEnabled(3, True)
            self.enable_moving_buttons(True)

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
            False otherwise."""
        try:
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'home the Y axis?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

            # Set the homing jog speed at 2mm/s
            _ppmac.set_motor_param(1, 'JogSpeed', 100)
            _ppmac.set_motor_param(3, 'JogSpeed', 100)

            ynofsteps = 4
            yactualstep = 0
            _prg_dialog = _QProgressDialog('Homing process in progress...',
                                           'Abort', 0, ynofsteps, self)
            _prg_dialog.setWindowTitle('Homing Y axis')
            _prg_dialog.show()
            _QApplication.processEvents()

            while _prg_dialog.wasCanceled() == False:

                self.enable_moving_buttons(False)
                # self.ui.chb_homed_x.setCheckable(True)
                self.ui.groupBox_3.setEnabled(False)
                self.ui.pbt_configure.setEnabled(False)
                self.ui.pbt_fiducialization.setEnabled(False)
                self.parent_window.ui.twg_main.setTabEnabled(3, False)
                _QApplication.processEvents()
                # self.update_flag = False
                self.timer.stop()
                _sleep(0.5)

                yactualstep += 1
                _prg_dialog.setValue(yactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

    #             with _ppmac.lock_ppmac:
                _ppmac.write('#1,3j/')
                _ppmac.write('enable plc HomeY')
                _sleep(0.1)
                _ppmac.read()
                _sleep(3)

                yactualstep += 1
                _prg_dialog.setValue(yactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                _t0 = _time.time()
                while (all([not _ppmac.motor_homed(1),
                            not _ppmac.motor_homed(3)])):
                    _sleep(1)
                    if _time.time() - _t0 > 10*60:
                        raise RuntimeError('Y Homing timeout (10 minutes).')
                    self.update_position()
                    _QApplication.processEvents()
                    if _prg_dialog.wasCanceled() == True:
                        self.stop_motors()
                        raise RuntimeError('Homing Aborted')

                _sleep(2)

                yactualstep += 1
                _prg_dialog.setValue(yactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                self.move_y(0)

                self.ui.groupBox_3.setEnabled(True)
                self.ui.chb_homed_y.setChecked(True)
                _QApplication.processEvents()
                # self.ui.chb_homed_x.setCheckable(False)
                self.ui.pbt_configure.setEnabled(True)
                self.ui.pbt_fiducialization.setEnabled(True)
                self.parent_window.ui.twg_main.setTabEnabled(3, True)

                self.enable_moving_buttons(True)
                # move_y enables timer, no need to start it again
                # self.timer.start(1000)

                yactualstep += 1
                _prg_dialog.setValue(yactualstep)
                _QApplication.processEvents()
                if _prg_dialog.wasCanceled() == True:
                    self.stop_motors()
                    raise RuntimeError('Homing Aborted')

                _QMessageBox.information(self, 'Information',
                                         'Y homing complete.',
                                         _QMessageBox.Ok)
                return True
                break
        except Exception:
            self.ui.groupBox_3.setEnabled(True)
            self.ui.chb_homed_y.setChecked(False)
            # self.ui.chb_homed_x.setCheckable(False)
            self.ui.pbt_configure.setEnabled(True)
            self.ui.pbt_fiducialization.setEnabled(True)
            self.parent_window.ui.twg_main.setTabEnabled(3, True)
            self.enable_moving_buttons(True)

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

    def move_x(self, position, absolute=True, motor=None, m_mode=1):
        """Move X motors and returns only after they stop.

        Args:
            position (float): desired position in [mm];
            absolute (bool): True for absolute positioning;
                             False for relative positioning.
            motor (int): if motor is 2 or 4, moves only the selected motor.
                         Moves both motors otherwise.
            m_mode (int): 1=Normal; 2=configure move; 3=trig move.
        Returns:
            True if successfull;
            False otherwise."""
        try:
            _x_lim = [self.cfg.min_x + self.cfg.x_offset,
                      self.cfg.max_x + self.cfg.x_offset]  # [mm]
            if absolute:
                _mode = '='
                _pos_x = position + self.cfg.x_offset  # [mm] *10**-3/self.cfg.x_sf
            else:
                _mode = '^'
                _pos_x = position
            _status = False

            if _x_lim[0] <= _pos_x <= _x_lim[1]:
                _pos_x = int(_pos_x/self.cfg.x_sf)
            else:
                _QMessageBox.warning(self, 'Information',
                                     'X position out of range.',
                                     _QMessageBox.Ok)
                return False

            self.update_flag = False
            self.timer.stop()
            # _sleep(0.2)

            # print('X position: {0}'.format(_pos_x))

            if not (motor in [2, 4]):
                if m_mode == 1:
                    # Normal operating mode
                    _ppmac.write('#1,3,5,6k')
                    _ppmac.write('#2,4j/')
                    _msg_x = '#2,4j' + _mode + str(_pos_x)
                    _ppmac.write(_msg_x)
                    _ppmac.read()
                elif m_mode == 2:
                    # Only configures the motor
                    _ppmac.set_motor_param(2, 'ProgJogPos', _pos_x)
                    _ppmac.set_motor_param(4, 'ProgJogPos', _pos_x)
                    _rb_sp_m2 = int(_ppmac.query_motor_param(2, 'ProgJogPos'))
                    _rb_sp_m4 = int(_ppmac.query_motor_param(4, 'ProgJogPos'))
                    if not all([(_pos_x - 0.1 < _rb_sp_m2 < _pos_x + 0.1),
                                (_pos_x - 0.1 < _rb_sp_m4 < _pos_x + 0.1)]):
                        raise ValueError(
                            'move_x tried to set {0},'.format(_pos_x),
                            ' {1} steps but {2}, {3} were set.'.format(_pos_x,
                                                       _rb_sp_m2, _rb_sp_m4))
                    return True
                elif m_mode == 3:
                    # reads initial position [mm]
                    _initial_pos_m2, _initial_pos_m4 = \
                        _ppmac.read_motor_pos([2, 4])*self.cfg.x_sf

                    # Triggers movement with previously configured steps
                    _ppmac.write('#1,3,5,6k')
                    _ppmac.write('#2,4j/')
                    _msg_x = '#2,4j{0}*'.format(_mode)
                    _ppmac.write(_msg_x)
                    _ppmac.read()

                    # reads setpoints [mm]
                    _sp_pos_m2 = self.cfg.x_sf*int(
                        _ppmac.query_motor_param(2, 'ProgJogPos'))
                    _sp_pos_m4 = self.cfg.x_sf*int(
                        _ppmac.query_motor_param(4, 'ProgJogPos'))

                    # finds movement direction
                    if absolute:
                        _dir_m2 = _np.sign(_sp_pos_m2 - _initial_pos_m2)
                        _dir_m4 = _np.sign(_sp_pos_m4 - _initial_pos_m4)
                    else:
                        _dir_m2 = _np.sign(_sp_pos_m2)
                        _dir_m4 = _np.sign(_sp_pos_m4)

                    # find movement limits
                    # (adds 1mm to the setpoint in the moving direction)
                    if absolute:
                        _limit_m2 = _sp_pos_m2 + _dir_m2*1
                        _limit_m4 = _sp_pos_m4 + _dir_m4*1
                    else:
                        _limit_m2 = _initial_pos_m2 + _sp_pos_m2 + _dir_m2*1
                        _limit_m4 = _initial_pos_m4 + _sp_pos_m4 + _dir_m4*1

                    # finds maximum position difference from start point
                    _delta_m2 = abs(_limit_m2 - _initial_pos_m2)
                    _delta_m4 = abs(_limit_m4 - _initial_pos_m4)

                _sleep(0.2)

                while (not all([self.ppmac.motor_stopped(2),
                                self.ppmac.motor_stopped(4)])):
                    self.pos = _ppmac.read_motor_pos([1, 2, 3, 4, 7, 8])
                    self.update_position()
                    if m_mode == 3:
                        # checks if the stages are not out of bounds:
                        _pos_m2 = self.pos[1]*self.cfg.x_sf
                        _pos_m4 = self.pos[3]*self.cfg.x_sf

                        # if not all([(_x_lim[0] <= _pos_m2 <= _x_lim[1]),
                        #             (_x_lim[0] <= _pos_m4 <= _x_lim[1])]):
                        if not all([(abs(_pos_m2 - _initial_pos_m2) > _delta_m2),
                                    (abs(_pos_m4 - _initial_pos_m4) > _delta_m4),
                                    (_x_lim[0] <= _pos_m2 <= _x_lim[1]),
                                    (_x_lim[0] <= _pos_m4 <= _x_lim[1])]):
                            _ppmac.stop_motors()
                            _ppmac.flag_abort = False
                            _rb_sp_m2 = int(
                                _ppmac.query_motor_param(2, 'ProgJogPos'))
                            _rb_sp_m4 = int(
                                _ppmac.query_motor_param(4, 'ProgJogPos'))
                            print(_pos_m2, _pos_m4)
                            print(_pos_x, _rb_sp_m2, _rb_sp_m4)
                            raise RuntimeError('move_x: positions out of '
                                               'limits. Motors stopped.')
                    _sleep(0.1)

                if not any([_ppmac.motor_fault(2),
                            _ppmac.motor_fault(4),
                            _ppmac.motor_limits(2),
                            _ppmac.motor_limits(4),
                            _ppmac.motor_fefatal(2),
                            _ppmac.motor_fefatal(4)]):
                    _status = True

            else:
                # _ppmac.write('#1,3,5,6k')
                # _ppmac.write('#{0}j/'.format(motor))
                # _msg_x = '#{0}j'.format(motor) + _mode + str(_pos_x)
                # _ppmac.write(_msg_x)
                # _ppmac.read()
                if m_mode == 1:
                    # Normal operating mode
                    _ppmac.write('#1,3,5,6k')
                    _ppmac.write('#{0}j/'.format(motor))
                    _msg_x = '#{0}j'.format(motor) + _mode + str(_pos_x)
                    _ppmac.write(_msg_x)
                    _ppmac.read()
                elif m_mode == 2:
                    # Only configures the motor
                    _ppmac.set_motor_param(2, 'ProgJogPos', _pos_x)
                    _ppmac.set_motor_param(4, 'ProgJogPos', _pos_x)
                    _rb_sp_m2 = int(_ppmac.query_motor_param(2, 'ProgJogPos'))
                    _rb_sp_m4 = int(_ppmac.query_motor_param(4, 'ProgJogPos'))
                    if not all([(_pos_x - 0.1 < _rb_sp_m2 < _pos_x + 0.1),
                                (_pos_x - 0.1 < _rb_sp_m4 < _pos_x + 0.1)]):
                        raise ValueError(
                            'move_y tried to set {0},'.format(_pos_x),
                            ' {1} steps but {2}, {3} were set.'.format(_pos_x,
                                                       _rb_sp_m2, _rb_sp_m4))
                    return True
                elif m_mode == 3:
                    # Triggers movement with previously configured steps
                    _ppmac.write('#1,3,5,6k')
                    _ppmac.write('#2,4j/')
                    _msg_x = '#{0}j{1}*'.format(motor, _mode)
                    _ppmac.write(_msg_x)
                    _ppmac.read()

                _sleep(0.2)
                while not self.ppmac.motor_stopped(motor):
                    self.update_flag = True
                    self.update_position()
                    _sleep(0.5)

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

    def move_y(self, position, absolute=True, motor=None, m_mode=1):
        """Move Y motors and returns only after they stop.

        Args:
            position (float): desired position in [mm];
            absolute (bool): True for absolute positioning;
                             False for relative positioning.
            motor (int): if motor is 1 or 3, moves only the selected motor.
                         Moves both motors otherwise.
            m_mode (int): 1=Normal; 2=configure move; 3=trig move.
        Returns:
            True if successfull;
            False otherwise."""
        try:
            _y_lim = [self.cfg.min_y + self.cfg.y_offset,
                      self.cfg.max_y + self.cfg.y_offset]  # [mm]
            if absolute:
                _mode = '='
                _pos_y = position + self.cfg.y_offset  # [mm] *10**-3/self.cfg.y_sf
            else:
                _mode = '^'
                _pos_y = position
            _status = False

            if _y_lim[0] <= _pos_y <= _y_lim[1]:
                _pos_y = int(_pos_y/self.cfg.y_sf)
            else:
                _QMessageBox.warning(self, 'Information',
                                     'Y position out of range.',
                                     _QMessageBox.Ok)
                return False

            self.update_flag = False
            self.timer.stop()
            # _sleep(0.2)

            # print('Y position: {0}'.format(_pos_y))

            if not (motor in [1, 3]):
                if m_mode == 1:
                    # Normal operating mode
                    _ppmac.write('#2,4,5,6k')
                    _ppmac.write('#1,3j/')
                    _msg_y = '#1,3j' + _mode + str(_pos_y)
                    _ppmac.write(_msg_y)
                    _ppmac.read()
                elif m_mode == 2:
                    # Only configures the motor
                    _ppmac.set_motor_param(1, 'ProgJogPos', _pos_y)
                    _ppmac.set_motor_param(3, 'ProgJogPos', _pos_y)
                    _rb_sp_m1 = int(_ppmac.query_motor_param(1, 'ProgJogPos'))
                    _rb_sp_m3 = int(_ppmac.query_motor_param(3, 'ProgJogPos'))
                    if not all([(_pos_y - 0.1 < _rb_sp_m1 < _pos_y + 0.1),
                                (_pos_y - 0.1 < _rb_sp_m3 < _pos_y + 0.1)]):
                        raise ValueError(
                            'move_y tried to set {0},'.format(_pos_y),
                            ' {1} steps but {2}, {3} were set.'.format(_pos_y,
                                                       _rb_sp_m1, _rb_sp_m3))
                    return True
                elif m_mode == 3:
                    # reads initial position [mm]
                    _initial_pos_m1, _initial_pos_m3 = \
                        _ppmac.read_motor_pos([1, 3])*self.cfg.x_sf

                    # Triggers movement with previously configured steps
                    _ppmac.write('#2,4,5,6k')
                    _ppmac.write('#1,3j/')
                    _msg_y = '#1,3j{0}*'.format(_mode)
                    _ppmac.write(_msg_y)
                    _ppmac.read()

                    # reads setpoints [mm]
                    _sp_pos_m1 = self.cfg.x_sf*int(
                        _ppmac.query_motor_param(1, 'ProgJogPos'))
                    _sp_pos_m3 = self.cfg.x_sf*int(
                        _ppmac.query_motor_param(3, 'ProgJogPos'))

                    # finds movement direction
                    if absolute:
                        _dir_m1 = _np.sign(_sp_pos_m1 - _initial_pos_m1)
                        _dir_m3 = _np.sign(_sp_pos_m3 - _initial_pos_m3)
                    else:
                        _dir_m1 = _np.sign(_sp_pos_m1)
                        _dir_m3 = _np.sign(_sp_pos_m3)

                    # find movement limits
                    # (adds 1mm to the setpoint in the moving direction)
                    if absolute:
                        _limit_m1 = _sp_pos_m1 + _dir_m1*1
                        _limit_m3 = _sp_pos_m3 + _dir_m3*1
                    else:
                        _limit_m1 = _initial_pos_m1 + _sp_pos_m1 + _dir_m1*1
                        _limit_m3 = _initial_pos_m3 + _sp_pos_m3 + _dir_m3*1

                    # finds maximum position difference from start point
                    _delta_m1 = abs(_limit_m1 - _initial_pos_m1)
                    _delta_m3 = abs(_limit_m3 - _initial_pos_m3)

                _sleep(0.2)
                while (not all([self.ppmac.motor_stopped(1),
                                self.ppmac.motor_stopped(3)])):
                    self.pos = _ppmac.read_motor_pos([1, 2, 3, 4])
                    self.update_position()
                    if m_mode == 3:
                        # checks if the stages are not out of bounds:
                        _pos_m1 = self.pos[0]*self.cfg.y_sf
                        _pos_m3 = self.pos[2]*self.cfg.y_sf

                        # if not all([(_y_lim[0] <= _pos_m1 <= _y_lim[1]),
                        #             (_y_lim[0] <= _pos_m3 <= _y_lim[1])]):
                        if not all([(abs(_pos_m1 - _initial_pos_m1) > _delta_m1),
                                    (abs(_pos_m3 - _initial_pos_m3) > _delta_m3),
                                    (_y_lim[0] <= _pos_m1 <= _y_lim[1]),
                                    (_y_lim[0] <= _pos_m3 <= _y_lim[1])]):
                            _ppmac.stop_motors()
                            _ppmac.flag_abort = False
                            _rb_sp_m1 = int(
                                _ppmac.query_motor_param(1, 'ProgJogPos'))
                            _rb_sp_m3 = int(
                                _ppmac.query_motor_param(3, 'ProgJogPos'))
                            print(_pos_m1, _pos_m3)
                            print(_pos_y, _rb_sp_m1, _rb_sp_m3)
                            raise RuntimeError('move_y: positions out of '
                                               'limits. Motors stopped.')
                    _sleep(0.1)

                if not any([_ppmac.motor_fault(1),
                            _ppmac.motor_fault(3),
                            _ppmac.motor_limits(1),
                            _ppmac.motor_limits(3),
                            _ppmac.motor_fefatal(1),
                            _ppmac.motor_fefatal(3)]):
                    _status = True

            else:
                # _ppmac.write('#2,4,5,6k')
                # _ppmac.write('#{0}j/'.format(motor))
                # _msg_y = '#{0}j'.format(motor) + _mode + str(_pos_y)
                # _ppmac.write(_msg_y)
                # _ppmac.read()
                if m_mode == 1:
                    # Normal operating mode
                    _ppmac.write('#2,4,5,6k')
                    _ppmac.write('#{0}j/'.format(motor))
                    _msg_y = '#{0}j'.format(motor) + _mode + str(_pos_y)
                    _ppmac.write(_msg_y)
                    _ppmac.read()
                elif m_mode == 2:
                    # Only configures the motor
                    _ppmac.set_motor_param(1, 'ProgJogPos', _pos_y)
                    _ppmac.set_motor_param(3, 'ProgJogPos', _pos_y)
                    _rb_sp_m1 = int(_ppmac.query_motor_param(1, 'ProgJogPos'))
                    _rb_sp_m3 = int(_ppmac.query_motor_param(3, 'ProgJogPos'))
                    if not all([(_pos_y - 0.1 < _rb_sp_m1 < _pos_y + 0.1),
                                (_pos_y - 0.1 < _rb_sp_m3 < _pos_y + 0.1)]):
                        raise ValueError(
                            'move_y tried to set {0},'.format(_pos_y),
                            ' {1} steps but {2}, {3} were set.'.format(_pos_y,
                                                       _rb_sp_m1, _rb_sp_m3))
                    return True
                elif m_mode == 3:
                    # Triggers movement with previously configured steps
                    _ppmac.write('#2,4,5,6k')
                    _ppmac.write('#1,3j/')
                    _msg_y = '#{0}j{1}*'.format(motor, _mode)
                    _ppmac.write(_msg_y)
                    _ppmac.read()

                _sleep(0.2)
                while not self.ppmac.motor_stopped(motor):
                    self.update_flag = True
                    self.update_position()
                    _sleep(0.5)

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
            # _traceback.print_exc(file=_sys.stdout)
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

        self.configure_ppmac()

        self.update_flag = False
        _sleep(0.5)
        self.enable_moving_buttons(False)
        position = self.ui.dsb_pos_x.value()
        if self.ui.rdb_abs_xy.isChecked():
            absolute = True
        else:
            absolute = False

        # Check if a single motor is selected
        if self.ui.cmb_x_selection.currentText() == "Xa":
            self.move_x(position, absolute, motor=2)
        elif self.ui.cmb_x_selection.currentText() == "Xb":
            self.move_x(position, absolute, motor=4)
        elif self.ui.cmb_x_selection.currentText() == "X":
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

        self.enable_moving_buttons(False)
        position = self.ui.dsb_pos_y.value()
        if self.ui.rdb_abs_xy.isChecked():
            absolute = True
        else:
            absolute = False

        self.configure_ppmac()

        self.update_flag = False
        _sleep(0.5)
        #Check if a single motor is selected
        if self.ui.cmb_y_selection.currentText() == "Ya":
            self.move_y(position, absolute, motor=1)
        elif self.ui.cmb_y_selection.currentText() == "Yb":
            self.move_y(position, absolute, motor=3)
        elif self.ui.cmb_y_selection.currentText() == "Y":
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
                if self.move_x(xa_min, motor=2):
                    _mnt_neg_flag = True

        else:
            if self.move_y(0):
                if self.move_x(xb_min):
                    if self.move_x(xa_min, motor=2):
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
                if self.move_x(xb_max, motor=4):
                    if self.move_y(yb_min):
                        if self.move_y(ya_min, motor=1):
                            _mnt_pos_flag = True
        else:
            if self.move_y(0):
                if self.move_x(xa_max):
                    if self.move_x(xb_max, motor=4):
                        if self.move_y(yb_min):
                            if self.move_y(ya_min, motor=1):
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
            _sleep(0.6)
            if all([_ppmac.motor_homed(2),
                    _ppmac.motor_homed(4)]):
                homed = True
            else:
                # _QMessageBox.warning(self, 'Warning',
                #                      'X axis motors are not homed. Please '
                #                      'run the X homing routine.',
                #                      _QMessageBox.Ok)
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
            _sleep(0.6)
            if all([_ppmac.motor_homed(1),
                    _ppmac.motor_homed(3)]):
                homed = True
            else:
                # _QMessageBox.warning(self, 'Warning',
                #                      'Y axis motors are not homed. Please '
                #                      'run the Y homing routine.',
                #                      _QMessageBox.Ok)
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
                _QMessageBox.warning(self, 'Warning',
                                     'Motors are not homed. Please '
                                     'run the homing routine.',
                                     _QMessageBox.Ok)
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
