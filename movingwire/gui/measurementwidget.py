"""Measurement widget for the Moving Wire Control application."""

import os as _os
import sys as _sys
import numpy as _np
import time as _time
import traceback as _traceback

from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    QProgressDialog as _QProgressDialog,
    )
from qtpy.QtCore import Qt as _Qt
import qtpy.uic as _uic

import movingwire.data as _data
from movingwire.gui.measurementdialog import MeasurementDialog \
    as _MeasurementDialog
from movingwire.gui.mapdialog import MapDialog \
    as _MapDialog
from movingwire.gui.utils import (
    get_ui_file as _get_ui_file,
    sleep as _sleep,
    update_db_name_list as _update_db_name_list,
    load_db_from_name as _load_db_from_name,
    )
from movingwire.devices import (
    ppmac as _ppmac,
    fdi as _fdi,
    ps as _ps,
    volt as _volt,
    )
from scipy.sparse.linalg._expm_multiply import _trace
# from pywin.framework import startup
# from numpy.distutils.system_info import accelerate_info


class MeasurementWidget(_QWidget):
    """Measurement widget class for the Moving Wire Control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.flag_rm_backlash = True
        self.flag_save = False

        self.volt = _volt

        self.cfg = _data.configuration.MeasurementConfig()
        self.meas_fc = _data.measurement.MeasurementDataFC()
        self.meas_sw = _data.measurement.MeasurementDataSW()
        self.meas_sw2 = _data.measurement.MeasurementDataSW2()

        self.update_cfg_list()
#         self.load_cfg()
        self.connect_signal_slots()

        self.volt_interval = 2

    def init_tab(self):
        self.motors = self.parent_window.motors
        self.analysis = self.parent_window.analysis
        self.ps = self.parent_window.powersupply

        name = self.ui.cmb_cfg_name.currentText()
        _load_db_from_name(self.cfg, name)
        self.load_cfg_into_ui()

#         self.load_cfg()

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
        self.ui.pbt_measure.clicked.connect(self.meas_dialog)
        self.ui.pbt_test.clicked.connect(self.test_steps)
        self.ui.pbt_save_cfg.clicked.connect(self.save_cfg)
        self.ui.pbt_load_cfg.clicked.connect(self.load_cfg)
        self.ui.pbt_update_cfg.clicked.connect(self.update_cfg_list)
        self.ui.rdb_sw.clicked.connect(self.change_mode)
        self.ui.rdb_sw_I2.clicked.connect(self.change_mode)
        self.ui.rdb_fc.clicked.connect(self.change_mode)
        self.ui.pbt_stop_motors.clicked.connect(self.stop_motors)
        self.ui.pbt_map.clicked.connect(self.map_dialog)

    def save_log(self, array, name='', comments=''):
        """Saves log on file."""
        name = (name +
                _time.strftime('_%y_%m_%d_%H_%M', _time.localtime()) + '.dat')
        head = ('Turn1[V.s]\tTurn2[V.s]\tTurn3[V.s]\tTurn4[V.s]\t' +
                'Turn5[V.s]\tTurn6[V.s]\tTurn7[V.s]\tTurn8[V.s]\t' +
                'Turn9[V.s]\tTurn10[V.s]')
        comments = comments + '\n'
        _np.savetxt(name, array, delimiter='\t',
                    comments=comments, header=head)

    def test_steps(self):
        """Tests steps from ui values and prints initial and final positions.
        """
        # Y1/2: CCW/CW M5 (0 a -pi)  M6 (0 a pi)
        # X1/2: CCW/CW M5 (pi/2 a -pi/2) M6 (-pi/2 a pi/2)
        try:
            if not self.ui.rdb_fc.isChecked():
                raise RuntimeError

            _start_pos = int(self.ui.dsb_start_pos.value()*10**3)
            _ppmac.remove_backlash(_start_pos)
#             _ppmac.align_motors(interval=3)
            _sleep(5)
            _frw_steps = [self.ui.sb_frw5.value(), self.ui.sb_frw6.value()]
            _bck_steps = [self.ui.sb_bck5.value(), self.ui.sb_bck6.value()]

#             with _ppmac.lock_ppmac:
            self.motors.timer.stop()
            _ppmac.write('#5j^' + str(_frw_steps[0]) +
                         ';#6j^' + str(_frw_steps[1]))
            _sleep(5)
            pos7f, pos8f = _ppmac.read_motor_pos([7, 8])
#             with _ppmac.lock_ppmac:
            _ppmac.write('#5j^' + str(_bck_steps[0]) +
                         ';#6j^' + str(_bck_steps[1]))
            print(pos7f, pos8f)
            _sleep(5)
            pos7b, pos8b = _ppmac.read_motor_pos([7, 8])
            print(pos7b, pos8b)
            _ppmac.read()
            self.motors.timer.start(1000)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.motors.timer.start(1000)

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
            self.cfg.name = self.ui.cmb_cfg_name.currentText()

            dp5_ida = self.ui.sb_frw5.value()  # -51209
            dp6_ida = self.ui.sb_frw6.value()  # 51170
            dp5_volta = self.ui.sb_bck5.value()  # 51218
            dp6_volta = self.ui.sb_bck6.value()  # -51166
            self.cfg.steps_f = [dp5_ida, dp6_ida]  # steps
            self.cfg.steps_b = [dp5_volta, dp6_volta]  # steps

            self.cfg.direction = (self.ui.rdb_ccw.isChecked() * 'ccw' +
                                  self.ui.rdb_cw.isChecked() * 'cw')

            self.cfg.mode = (self.ui.rdb_sw.isChecked() * 'SW_I1' +
                             self.ui.rdb_sw_I2.isChecked() * 'SW_I2' +
                             self.ui.rdb_fc.isChecked() * 'FC_I1')
            if 'FC' in self.cfg.mode:
                self.cfg.start_pos = self.ui.dsb_start_pos.value()  # [deg]
                self.cfg.end_pos = self.ui.dsb_end_pos.value()  # [deg]
                self.cfg.step = self.ui.dsb_end_pos.value()  # [deg]

            else:
                self.cfg.start_pos = self.ui.dsb_scan_start.value()  # [mm]
                self.cfg.end_pos = self.ui.dsb_scan_end.value()  # [mm]
                self.cfg.step = self.ui.dsb_scan_step.value()  # [mm]
            self.cfg.nmeasurements = self.ui.sb_nmeasurements.value()
            self.cfg.max_init_error = (
                self.motors.ui.sb_rot_max_err.value())

            self.cfg.nplc = self.ui.dsb_nplc.value()
            self.cfg.duration = self.ui.dsb_duration.value()
            self.cfg.gain = self.ui.dsb_gain.value()
            self.cfg.range = self.ui.cmb_range.currentText()

            self.cfg.motion_axis = self.ui.cmb_motion_axis.currentText()

            self.cfg.width = self.ui.dsb_width.value() * 10**-3  # [m]
            self.cfg.length = self.ui.dsb_length.value()  # [m]
            self.cfg.turns = self.ui.sb_turns.value()
            self.cfg.speed = self.motors.ui.dsb_speed.value()  # [turns/s]
            self.cfg.accel = self.motors.ui.dsb_accel.value()  # [turns/s^2]
            self.cfg.jerk = self.motors.ui.dsb_jerk.value()  # [turns/s^3]

            if self.cfg.duration < (self.cfg.acq_init_interval +
                                    self.cfg.acq_final_interval):
                _QMessageBox.warning(self, 'Warining',
                                     'Measurement duration is less than '
                                     'the acquisition intervals sum.',
                                     _QMessageBox.Ok)
                raise ValueError('Measurement duration is less than '
                                 'the acquisition intervals sum.')

            self.cfg.acq_init_interval = (
                self.ui.dsb_acq_init_interval.value())
            self.cfg.acq_final_interval = (
                self.ui.dsb_acq_final_interval.value())

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
            if self.cfg.acq_init_interval is None:
                self.cfg.acq_init_interval = 1
            if self.cfg.acq_final_interval is None:
                self.cfg.acq_final_interval = 1
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

    def load_cfg_into_ui(self):
        """Loads database configuration into ui widgets."""
        try:
            if 'FC' in self.cfg.mode:
                self.ui.dsb_start_pos.setValue(self.cfg.start_pos)  # [deg]
                self.ui.rdb_fc.setChecked(True)
            else:
                self.ui.dsb_scan_start.setValue(self.cfg.start_pos)  # [mm]
                self.ui.dsb_scan_end.setValue(self.cfg.end_pos)  # [mm]
                self.ui.dsb_scan_step.setValue(self.cfg.step)  # [mm]
                if 'I1' in self.cfg.mode:
                    self.ui.rdb_sw.setChecked(True)
                elif 'I2' in self.cfg.mode:
                    self.ui.rdb_sw_I2.setChecked(True)
            self.change_mode()

            self.ui.cmb_cfg_name.setCurrentText(self.cfg.name)

            self.ui.sb_frw5.setValue(self.cfg.steps_f[0])
            self.ui.sb_frw6.setValue(self.cfg.steps_f[1])
            self.ui.sb_bck5.setValue(self.cfg.steps_b[0])
            self.ui.sb_bck6.setValue(self.cfg.steps_b[1])

            if self.cfg.direction == 'ccw':
                self.ui.rdb_ccw.setChecked(True)
            else:
                self.ui.rdb_cw.setChecked(True)
            self.ui.sb_nmeasurements.setValue(self.cfg.nmeasurements)
            self.motors.ui.sb_rot_max_err.setValue(
                self.cfg.max_init_error)

            self.ui.dsb_nplc.setValue(self.cfg.nplc)
            self.ui.dsb_duration.setValue(self.cfg.duration)
            self.ui.dsb_gain.setValue(self.cfg.gain)
            self.ui.dsb_acq_init_interval.setValue(
                self.cfg.acq_init_interval)
            self.ui.dsb_acq_final_interval.setValue(
                self.cfg.acq_final_interval)

            self.ui.cmb_range.setCurrentText(self.cfg.range)

            self.ui.cmb_motion_axis.setCurrentText(self.cfg.motion_axis)

            self.ui.dsb_width.setValue(self.cfg.width * 10**3)  # [mm]
            self.ui.dsb_length.setValue(self.cfg.length)  # [m]
            self.ui.sb_turns.setValue(self.cfg.turns)
            self.motors.ui.dsb_speed.setValue(self.cfg.speed)  # [rev/s]
            self.motors.ui.dsb_accel.setValue(self.cfg.accel)  # [rev/s^2]
            self.motors.ui.dsb_jerk.setValue(self.cfg.jerk)  # [rev/s^3]
            _QApplication.processEvents()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def change_mode(self):
        """Changes measurement mode."""
        if self.ui.rdb_sw.isChecked():
            names = ['X', 'Y']
        elif self.ui.rdb_sw_I2.isChecked():
            names = ['Xa', 'Xb', 'Ya', 'Yb']

        if not self.ui.rdb_fc.isChecked():
            _cmb = self.ui.cmb_motion_axis
            _cmb.clear()
            _cmb.addItems([name for name in names])
            _cmb.setCurrentIndex(0)

    def meas_dialog(self):
        """Creates measurement dialog."""
        self.dialog = _MeasurementDialog()
        self.dialog.show()
        self.dialog.accepted.connect(self.start_measurement)
        self.dialog.rejected.connect(self.cancel_measurement)

        if self.ui.rdb_sw.isChecked():
            _meas = self.meas_sw
        elif self.ui.rdb_sw_I2.isChecked():
            _meas = self.meas_sw2
        else:
            _meas = self.meas_fc

        try:
            _meas.db_update_database(self.database_name, mongo=self.mongo,
                                     server=self.server)
            last_id = _meas.db_get_last_id()
            name = '_'.join(
                _meas.db_get_value('name', last_id).split('_')[:-2])
            self.dialog.ui.le_meas_name.setText(name)

            comments = _meas.db_get_value('comments', last_id)
            self.dialog.ui.le_comments.setText(comments)
#             _update_db_name_list(self.meas, self.dialog.ui.cmb_meas_name)
#             self.meas.db_update_database(database_name=self.database_name,
#                                          mongo=self.mongo, server=self.server)
#             _idn = self.meas.db_get_last_id()
#             if _idn > 0:
#                 _comments = self.meas.db_get_value('comments', _idn)
#                 self.dialog.ui.te_comments.setText(_comments)
            self.update_iamb_list()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_iamb_list(self):
        """Updates Iamb list on measurement dialog."""
        if self.ui.rdb_sw.isChecked():
            _meas = self.meas_sw
        elif self.ui.rdb_sw_I2.isChecked():
            _meas = self.meas_sw2
        else:
            _meas = self.meas_fc

        _meas.db_update_database(
            self.database_name,
            mongo=self.mongo, server=self.server)

        self.dialog.amb_list = _meas.db_search_field('Iamb_id', 0)
        self.dialog.ui.cmb_Iamb.addItems(
            [item['name'] for item in self.dialog.amb_list])
        self.dialog.ui.cmb_Iamb.setCurrentIndex(len(self.dialog.amb_list)-1)

    def cancel_measurement(self):
        """Cancels measurement and destroys measurement dialog."""
        self.dialog.destroy()

    def start_measurement(self):
        """Starts measurement or scan according to configurations. If number
        of measurements > 1, each step in a scan will be repeated before
        changing the setpoint."""

        try:
            self.update_cfg_from_ui()

            if not self.motors.check_homed():
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

            _ppmac.flag_abort = False
            if self.ui.rdb_sw.isChecked():
                _meas = self.meas_sw
                _meas.mode = 'SW_I1'
            elif self.ui.rdb_sw_I2.isChecked():
                _meas = self.meas_sw2
                _meas.mode = 'SW_I2'
            else:
                _meas = self.meas_fc
                _meas.mode = 'FC_I1'
                _measure_integral = self.measure_integral_fc

            if 'SW' in _meas.mode:
                _measure_integral = self.measure_integral_sw
                _meas.motion_axis = self.ui.cmb_motion_axis.currentText()
                _meas.start_pos = self.ui.dsb_scan_start.value()  # [mm]
                _meas.end_pos = self.ui.dsb_scan_end.value()  # [mm]
                _meas.step = self.ui.dsb_scan_step.value()  # [mm]
                _meas.length = self.ui.dsb_length.value()  # [m]

            scan_flag = self.dialog.ui.chb_scan.isChecked()
            repeats = self.dialog.ui.sb_repetitions.value()
            _meas.turns = self.ui.sb_turns.value()
            _meas.nplc = self.ui.dsb_nplc.value()
            _meas.duration = self.ui.dsb_duration.value()
            _meas.nmeasurements = self.ui.sb_nmeasurements.value()
            _meas.gain = self.ui.dsb_gain.value()
            _meas.range = self.ui.cmb_range.currentIndex()
            _meas.acq_init_interval = (
                self.ui.dsb_acq_init_interval.value())
            _meas.acq_final_interval = self.ui.dsb_acq_final_interval.value()

            if not scan_flag:
                # update meas.name and meas.comments
                _meas.comments = self.dialog.ui.le_comments.text()

                # measure
#                 if self.ui.rdb_sw.isChecked():
#                     raise RuntimeError

                for i in range(repeats):
                    if _ppmac.flag_abort:
                        _QMessageBox.information(self, 'Warning',
                                                 'Measurement Aborted.',
                                                 _QMessageBox.Ok)
                        return False
                    name = self.dialog.ui.le_meas_name.text()
                    if _meas.mode == 'fc':
                        name = (name + '_' + self.cfg.direction +
                                _time.strftime('_%y%m%d_%H%M'))
                    else:
                        name = (name + _time.strftime('_%y%m%d_%H%M'))
                    _meas.name = name
                    _meas.date = _time.strftime('%Y-%m-%d')
                    _meas.hour = _time.strftime('%H:%M:%S')
                    if _meas.mode == 'SW_I2':
                        _measure_integral(I2=True)
                    else:
                        _measure_integral()

            if scan_flag:
                param = self.dialog.ui.cmb_scan_param.currentText()
                start = self.dialog.ui.dsb_scan_start.value()
                end = self.dialog.ui.dsb_scan_end.value()
                step = self.dialog.ui.dsb_scan_step.value()
                if step == 0:
                    n_steps = 1
                else:
                    # number of steps
                    n_steps = int(1 + _np.ceil((end-start)/step))

                # get previous parameter
                if 'X' in param:
                    if _meas.mode == 'sw' and _meas.motion_axis == 'X':
                        _QMessageBox.information(self, 'Warning',
                                                 'Motion axis and scan axis '
                                                 'must not be the same.\n'
                                                 'Measurement Aborted.',
                                                 _QMessageBox.Ok)
                        return False
                    previous_param = self.motors.ui.dsb_pos_x.value()
                elif 'Y' in param:
                    if _meas.mode == 'sw' and _meas.motion_axis == 'Y':
                        _QMessageBox.information(self, 'Warning',
                                                 'Motion axis and scan axis '
                                                 'must not be the same.\n'
                                                 'Measurement Aborted.',
                                                 _QMessageBox.Ok)
                        return False
                    previous_param = self.motors.ui.dsb_pos_y.value()
                elif 'Speed' in param:
                    previous_param = self.cfg.speed
                elif 'Acceleration' in param:
                    previous_param = self.cfg.accel
                elif 'Jerk' in param:
                    previous_param = self.cfg.jerk

                for i in range(n_steps):
                    if _ppmac.flag_abort:
                        _QMessageBox.information(self, 'Warning',
                                                 'Measurement Aborted.',
                                                 _QMessageBox.Ok)
                        return False
                    # change setpoint
                    setpoint = start + i * step
                    if i == n_steps - 1:
                        setpoint = end

                    if 'X' in param:
                        p_str = '_X={0:.2f}'.format(setpoint)
                        _x_lim = [self.motors.ui.dsb_min_x.value()*10**3,
                                  self.motors.ui.dsb_max_x.value()*10**3]
                        if _x_lim[0] <= setpoint <= _x_lim[1]:
                            self.motors.ui.dsb_pos_x.setValue(setpoint)
                            self.motors.move_xy()
                            _sleep(10)
                        else:
                            _QMessageBox.information(self, 'Warning',
                                                     'X out of range.',
                                                     _QMessageBox.Ok)
                            raise ValueError
                    elif 'Y' in param:
                        p_str = '_Y={0:.2f}'.format(setpoint)
                        _y_lim = [self.motors.ui.dsb_min_y.value()*10**3,
                                  self.motors.ui.dsb_max_y.value()*10**3]
                        if _y_lim[0] <= setpoint <= _y_lim[1]:
                            self.motors.ui.dsb_pos_y.setValue(setpoint)
                            self.motors.move_xy()
                            _sleep(10)
                        else:
                            _QMessageBox.information(self, 'Warning',
                                                     'Y out of range.',
                                                     _QMessageBox.Ok)
                            raise ValueError
                    elif 'Speed' in param:
                        p_str = '_Spd={0:.2f}'.format(setpoint)
                        self.cfg.speed = setpoint
                    elif 'Acceleration' in param:
                        p_str = '_Acc={0:.2f}'.format(setpoint)
                        self.cfg.accel = setpoint
                    elif 'Jerk' in param:
                        p_str = '_Jrk={0:.2f}'.format(setpoint)
                        self.cfg.jerk = setpoint
                    elif 'Current' in param:
                        p_str = '_I={0:.2f}'.format(setpoint)
                        if self.ps.ps.read_ps_onoff():
                            self.ps.ui.dsb_current_setpoint.setValue(setpoint)
                            _min = self.ps.cfg.min_current
                            _max = self.ps.cfg.max_current
                            if _min <= setpoint <= _max:
                                self.ps.ps.set_slowref(setpoint)
                                _sleep(10)
                            else:
                                _QMessageBox.information(self, 'Warning',
                                                         'Current out of '
                                                         'range.',
                                                         _QMessageBox.Ok)
                                raise ValueError
                        else:
                            _QMessageBox.information(self, 'Warning',
                                                     'Power supply is'
                                                     ' turned off.',
                                                     _QMessageBox.Ok)
                            return False

                    # update meas.name, meas.comments:
                    comments = self.dialog.ui.le_comments.text()
                    comments = comments + ' Scan: ' + p_str.strip('_') + '.'
                    _meas.comments = comments

                    # measure
                    for i in range(repeats):
                        if _ppmac.flag_abort:
                            _QMessageBox.information(self, 'Warning',
                                                     'Measurement Aborted.',
                                                     _QMessageBox.Ok)
                            return False
                        name = self.dialog.ui.le_meas_name.text()
                        name = (name + p_str + _time.strftime('_%y%m%d_%H%M'))
                        _meas.date = _time.strftime('%Y-%m-%d')
                        _meas.hour = _time.strftime('%H:%M:%S')
                        _meas.name = name

                        if _meas.mode == 'SW_I2':
                            _measure_integral(I2=True)
                        else:
                            _measure_integral()

                # set previous parameter
#                 if 'X' in param:
#                     self.motors.ui.dsb_pos_x.setValue(previous_param)
#                 elif 'Y' in param:
#                     self.motors.ui.dsb_pos_y.setValue(previous_param)
                if 'Speed' in param:
                    self.cfg.speed = previous_param
                elif 'Acceleration' in param:
                    self.cfg.accel = previous_param
                elif 'Jerk' in param:
                    self.cfg.jerk = previous_param
                elif 'Current' in param:
                    self.ps.ui.dsb_current_setpoint.setValue(setpoint)
                    self.ps.ps.set_slowref(setpoint)
                    _sleep(5)
                    self.ps.ps.turn_off()

            _QMessageBox.information(self, 'Information',
                                     'Measurement Finished.',
                                     _QMessageBox.Ok)
            return True

        # except UnicodeDecodeError:
        #     print('UnicodeDecodeError in start_measurement (probably from '
        #           'voltmeter).')
        #     # _traceback.print_exc(file=_sys.stdout)
        #     _QMessageBox.warning(self, 'Warning',
        #                          'Measurement Failed.',
        #                          _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Measurement Failed.',
                                 _QMessageBox.Ok)
            return False

    def measure_integral_sw(self, I2=False):
        """Runs stretched wire first field integral measurement."""
        try:
            if not I2:
                _meas = self.meas_sw
            else:
                _meas = self.meas_sw2

            if self.dialog.ui.chb_Iamb.isChecked():
                _meas.Iamb_id = 0
            else:
                try:
                    _id = self.dialog.ui.cmb_Iamb.currentIndex()
                    _meas.Iamb_id = self.dialog.amb_list[_id]['id']
                except AttributeError:
                    _meas.Iamb_id = 0

            motion_axis = _meas.motion_axis
            nmeasurements = _meas.nmeasurements
            nplc = _meas.nplc
            duration = _meas.duration
            # start = _meas.start_pos
            # end = _meas.end_pos
            # step = _meas.step
            start = self.cfg.start_pos
            end = self.cfg.end_pos
            step = self.cfg.step
            acq_init_interval = _meas.acq_init_interval
            npoints = int(_np.ceil(duration/(nplc/60)))

            if end < start:
                _QMessageBox.information(self, 'Warning',
                                         'End position should be greater than '
                                         'start position.\n'
                                         'Measurement Aborted.',
                                         _QMessageBox.Ok)
                return False
            elif start == end:
                n_steps = 1
                _meas.transversal_pos = _np.array([start])
            else:
                if (end - start) < step:
                    _meas.transversal_pos = _np.array([start, end])
                else:
                    # number of steps
                    n_steps = int(1 + _np.ceil((end-start) / step))
                    # warning if n_steps is not an integer?
                    # check if start and end pos are inside limits
                    _meas.transversal_pos = _np.linspace(start, end, n_steps)

            # PPMAC configurations
            ppmac_cfg = self.motors.cfg
            if 'X' in motion_axis:
                speed = ppmac_cfg.speed_x  # [mm/s]
                accel = ppmac_cfg.accel_x  # [mm/s^2]
                jerk = ppmac_cfg.jerk_x  # [mm/s^3]
                _meas.y_pos = self.motors.ui.dsb_pos_y.value()
                _ppmac.enable_motors([2, 4])
                move_axis = self.motors.move_x
                # sf = self.motors.cfg.x_sf
                motion_step = self.motors.cfg.x_step
                if 'a' in motion_axis:
                    moving_motor = 2  # '1'
                    # static_motor = 3  # '3'
                elif 'b' in motion_axis:
                    moving_motor = 4  # '3'
                    # static_motor = 1  # '1'

            elif 'Y' in motion_axis:
                speed = ppmac_cfg.speed_y  # [mm/s]
                accel = ppmac_cfg.accel_y  # [mm/s^2]
                jerk = ppmac_cfg.jerk_y  # [mm/s^3]
                _meas.x_pos = self.motors.ui.dsb_pos_x.value()
                _ppmac.enable_motors([1, 3])
                move_axis = self.motors.move_y
                motion_step = self.motors.cfg.y_step
                # sf = self.motors.cfg.y_sf/self.motors.cfg.y_stps_per_cnt  # [mm/steps]
                if 'a' in motion_axis:
                    moving_motor = 1  # '2'
                    # static_motor = 4  # '4'
                elif 'b' in motion_axis:
                    moving_motor = 3  # '4'
                    # static_motor = 2  # '2'

            #self.motors.configure_ppmac()

            _meas.speed = speed
            _meas.accel = accel
            _meas.jerk = jerk

            _prg_dialog = _QProgressDialog('Measurement', 'Abort', 0,
                                           nmeasurements, self)
            _prg_dialog.setWindowTitle('Measurement Progress')
            _prg_dialog.show()
            _QApplication.processEvents()

            self.motors.timer.stop()

            _sleep(1)

            _volt.configure_volt(nplc=nplc, time=duration, mrange=_meas.range)
            _sleep(0.5)

            _prg_dialog.setValue(0)

            for position in _meas.transversal_pos:
                name = _meas.name.split('_')[:-2]
                _meas.name = '_'.join(name) + _time.strftime('_%y%m%d_%H%M')
                _meas.date = _time.strftime('%Y-%m-%d')
                _meas.hour = _time.strftime('%H:%M:%S')
                _init_pos = position - motion_step/2  # [mm]
                _end_pos = position + motion_step/2  # [mm]
                _meas.start_pos = _init_pos
                _meas.end_pos = _end_pos
                _meas.step = motion_step

                if 'X' in motion_axis:
                    _meas.x_pos = position
                else:
                    _meas.y_pos = position
                data_frw_aux = _np.array([])
                data_bck_aux = _np.array([])

                # go to init pos
                if not I2:
                    move_axis(_init_pos)
                    _sleep(0.5)
                    move_axis(_init_pos)
                else:
                    move_axis(position)
                    _sleep(0.5)
                    move_axis(_init_pos, motor=moving_motor)

                # _volt.read_from_device()
                for i in range(_meas.nmeasurements):
                    for j in range(4):
                        # error = 0
                        if j == 3:
                            _prg_dialog.destroy()
                            _ppmac.flag_abort = True
                            _QMessageBox.warning(self, 'Warning',
                                                 'Measurement aborted after 3 '
                                                 'consecutive moving errors.',
                                                 _QMessageBox.Ok)
                            raise RuntimeError('Measurement aborted after 3 '
                                               'consecutive moving errors.')

                        if _prg_dialog.wasCanceled():
                            _prg_dialog.destroy()
                            _ppmac.flag_abort = True
                            raise RuntimeError('Measurement aborted.')

                        # Forward measurement
                        # error = 1
                        _volt.start_measurement()
    #                     _ppmac.write('Gather.PhaseEnable=2')
                        _t0 = _time.time()
                        _sleep(acq_init_interval)
                        # error = 2
                        # move step
                        if not I2:
                            if not move_axis(_end_pos):
                                move_axis(_init_pos)
                                _sleep(1)
                                move_axis(_init_pos)
                                _sleep(duration + 9)
                                _volt.get_readings_from_memory(5)
                                continue
                        else:
                            if not move_axis(_end_pos, motor=moving_motor):
                                move_axis(_init_pos, motor=moving_motor)
                                _sleep(1)
                                move_axis(_init_pos, motor=moving_motor)
                                _sleep(duration + 9)
                                _volt.get_readings_from_memory(5)
                                continue
                        # _sleep(duration)
    #                     _ppmac.write('Gather.PhaseEnable=0')
    #                     _ppmac.ppmac_ssh.send(
    #                         'gather -p -u /var/ftp/gather/frw{}.dat\r\n'.format(i))

                        if _time.time() - _t0 <= duration:
                            _sleep(0.2)

                        # error = 3
                        _sleep(self.volt_interval)
                        _t = _time.time() - _t0
                        _data_frw = _volt.get_readings_from_memory(5)[::-1]
                        # self.get_volt_data(npoints)
                        # print(_t)

                        if _prg_dialog.wasCanceled():
                            _prg_dialog.destroy()
                            _ppmac.flag_abort = True
                            raise RuntimeError('Measurement aborted.')

                        # comment to minimize  temperature difference
                        # _sleep(3)

                        # Backward measurement
                        _volt.start_measurement()
    #                     _ppmac.write('Gather.PhaseEnable=2')
                        _t0 = _time.time()
                        _sleep(acq_init_interval)
                        # move - step
                        if not I2:
                            if not move_axis(_init_pos):
                                move_axis(_init_pos)
                                _sleep(1)
                                move_axis(_init_pos)
                                _sleep(duration + 9)
                                _volt.get_readings_from_memory(5)
                                self.get_volt_data(npoints)
                                continue
                        else:
                            if not move_axis(_init_pos, motor=moving_motor):
                                move_axis(_init_pos, motor=moving_motor)
                                _sleep(1)
                                move_axis(_init_pos, motor=moving_motor)
                                _sleep(duration + 9)
                                _volt.get_readings_from_memory(5)
                                continue
                        # _sleep(duration)
    #                     _ppmac.write('Gather.PhaseEnable=0')
    #                     _ppmac.ppmac_ssh.send(
    #                         'gather -p -u /var/ftp/gather/bck{}.dat\r\n'.format(i))

                        if _time.time() - _t0 <= duration:
                            _sleep(0.2)

                        _sleep(self.volt_interval)
                        _t = _time.time() - _t0
                        _data_bck = _volt.get_readings_from_memory(5)[::-1]
                        # self.get_volt_data(npoints)
                        # print(_t)

                        break

                    if i == 0:
                        data_bck_aux = _np.append(data_bck_aux, _data_bck)
                        data_frw_aux = _np.append(data_frw_aux, _data_frw)
                    else:
                        data_bck_aux = _np.vstack([data_bck_aux, _data_bck])
                        data_frw_aux = _np.vstack([data_frw_aux, _data_frw])
                    _prg_dialog.setValue(i+1)

                # data[i, j]
                # i: measurement voltage array index
                # j: measurement number index
                _meas.data_frw = data_frw_aux.transpose()
                _meas.data_bck = data_bck_aux.transpose()

                # data analisys
                self.analysis.integral_calculus_sw(_meas, I2)
                self.save_measurement()
                self.analysis.update_meas_list()
                _count = self.analysis.cmb_meas_name.count() - 1
                self.analysis.cmb_meas_name.setCurrentIndex(_count)

            move_axis(position)
            self.motors.timer.start(1000)
            _prg_dialog.destroy()
            return True

        # except UnicodeDecodeError:
        #     print('UnicodeDecodeError in measure_integral_sw (probably from '
        #           'voltmeter).')
        #     print(error)
        #     _prg_dialog.destroy()
        #     _traceback.print_exc(file=_sys.stdout)
        #     _QMessageBox.warning(self, 'Warning',
        #                          'Measurement Failed.',
        #                          _QMessageBox.Ok)
        #     self.motors.timer.start(1000)
        #     return False

        except Exception:
            _prg_dialog.destroy()
            _traceback.print_exc(file=_sys.stdout)
            _QMessageBox.warning(self, 'Warning',
                                 'Measurement Failed.',
                                 _QMessageBox.Ok)
            self.motors.timer.start(1000)
            return False

    def get_volt_data(self, npoints):
        """Gets voltage measurement data from the voltmeter.

        Args:
            npoints (int): number of excpected data points.
        Returns:
            data (np.ndarray): numpy array containg voltage data.
        """
        try:
            _sleep(self.volt_interval)
            data = _volt.get_readings_from_memory(5)
            j = 300
            if data is None:
                data_cnt = 0
            else:
                data_cnt = len(data)
                print(data_cnt, npoints)

            while all([data_cnt < npoints,
                       j > 0]):
                j = j - 1
                _sleep(0.1)
                if data_cnt == 0:
                    data = _volt.get_readings_from_memory(5)
                else:
                    _data = _volt.get_readings_from_memory(5)
                    data = _np.append(
                        data, _volt.get_readings_from_memory(5))

                if data is None:
                    data_cnt = 0
                else:
                    data_cnt = len(data)

            data = data[::-1]
        except Exception:
            raise

        return data

    def measure_integral_fc(self, fdi_mode=False):
        """Runs flip coil first field integral measurement.

        Returns:
            True if successfull;
            False otherwise.
        """
        try:
             # _ppmac.flag_abort = False
             # self.update_cfg_from_ui()
             #
             # self.meas.comments = self.dialog.ui.te_comments.toPlainText()
            if self.dialog.ui.chb_Iamb.isChecked():
                self.meas.Iamb_id = 0
            else:
                _id = self.dialog.ui.cmb_Iamb.currentIndex()
                self.meas.Iamb_id = self.dialog.amb_list[_id]['id']
            self.meas.cfg_id = self.ui.cmb_cfg_name.currentIndex() + 1

            ppmac_cfg = self.motors.cfg
            speed = self.cfg.speed * ppmac_cfg.steps_per_turn * 10**-3  # [turns/s]
            if self.cfg.accel != 0:
                ta = -1/self.cfg.accel * 1/ppmac_cfg.steps_per_turn * 10**6  # [turns/s^2]
            else:
                ta = 0
            if self.cfg.jerk != 0:
                ts = -1/self.cfg.jerk * 1/ppmac_cfg.steps_per_turn * 10**9  # [turns/s^3]
            else:
                ts = 0
            start_pos = int(self.cfg.start_pos*10**3)
#             ta = -0.4  # acceleration time [ms]
#             ts = 0  # jerk time [ms]
#             wait = 2000  # time to wait between moves [ms]
            _dir = 1 if self.cfg.direction == 'ccw' else -1

            name = self.meas.name.split('_')[:-2]
            self.meas.name = '_'.join(name) + _time.strftime('_%y%m%d_%H%M')
            self._meas.date = _time.strftime('%Y-%m-%d')
            self._meas.hour = _time.strftime('%H:%M:%S')

            _prg_dialog = _QProgressDialog('Measurement', 'Abort', 0,
                                           self.cfg.nmeasurements + 1, self)
            _prg_dialog.setWindowTitle('Measurement Progress')
            _prg_dialog.show()
            _QApplication.processEvents()

            data_frw = _np.array([])
            data_bck = _np.array([])
            self.meas.pos7f = _np.zeros((2, self.cfg.nmeasurements))
            self.meas.pos7b = _np.zeros((2, self.cfg.nmeasurements))
            self.meas.pos8f = _np.zeros((2, self.cfg.nmeasurements))
            self.meas.pos8b = _np.zeros((2, self.cfg.nmeasurements))

#             auto_current = self.dialog.ui.chb_auto_current.isChecked()
#             if auto_current:
#                 currents = _np.copy(
#                     self.ps.cfg.current_array)
#                 if len(currents) == 0:
#                     auto_current = False

#             with _ppmac.lock_ppmac:
            self.motors.timer.stop()
            _ppmac.write('#1..4k')
            _sleep(1)
            self.meas.x_pos = (_ppmac.read_motor_pos([1, 3]) *
                               self.motors.x_sf)
            self.meas.y_pos = (_ppmac.read_motor_pos([2, 4]) *
                               self.motors.y_sf)

            msg = ('Motor[{0}].JogSpeed={1};'
                   'Motor[{0}].JogTa={2};'
                   'Motor[{0}].JogTs={3}'.format(5, speed, ta, ts))
            _ppmac.write(msg)
            msg = ('Motor[{0}].JogSpeed={1};'
                   'Motor[{0}].JogTa={2};'
                   'Motor[{0}].JogTs={3}'.format(6, speed, ta, ts))
            _ppmac.write(msg)

            if fdi_mode:
                counts = _fdi.configure_integrator(time=self.cfg.duration,
                                                   interval=50)
                _fdi.send('INP:COUP DC')
            else:
                counts = int(_np.ceil(3/(self.cfg.nplc/60)))
                _volt.configure_volt(nplc=self.cfg.nplc,
                                     time=self.cfg.duration)
            _sleep(0.5)
#             _ppmac.remove_backlash(start_pos)
#             _sleep(10)
#             self.meas.name = (self.dialog.ui.le_meas_name.currentText() +
#                               _time.strftime('_%y%m%d_%H%M'))
            _prg_dialog.setValue(0)
            for i in range(self.cfg.nmeasurements):
                if _prg_dialog.wasCanceled():
                    _prg_dialog.destroy()
                    _ppmac.flag_abort = True
                    return False

                if (self.flag_rm_backlash and
                    any([abs(_ppmac.read_motor_pos([7])[0]) % 360000 > self.cfg.max_init_error,
                         abs(_ppmac.read_motor_pos([8])[0]) % 360000 > self.cfg.max_init_error])):
                    _ppmac.remove_backlash(start_pos)
                if fdi_mode:
                    _fdi.start_measurement()
                else:
                    _volt.start_measurement()
                _sleep(1)

                self.meas.pos7f[0, i], self.meas.pos8f[0, i] = (
                    _ppmac.read_motor_pos([7, 8]))
#                 with _ppmac.lock_ppmac:
                _ppmac.write('#5j^' + str(self.cfg.steps_f[0]) +
                             ';#6j^' + str(self.cfg.steps_f[1]))

                if fdi_mode:
                    while(_fdi.get_data_count() < counts - 1):
                        _sleep(0.1)
                    _data = _fdi.get_data()
                else:
                    _sleep(3)
        #             while(volt.get_data_count() < counts):
        #                 _sleep(0.1)
                    _data = _volt.get_readings_from_memory(5)
                if i == 0:
                    data_frw = _np.append(data_frw, _data)
                else:
                    data_frw = _np.vstack([data_frw, _data])
                self.meas.pos7f[1, i], self.meas.pos8f[1, i] = (
                    _ppmac.read_motor_pos([7, 8]))

                _sleep(5)

                if fdi_mode:
                    _fdi.start_measurement()
                else:
                    _volt.start_measurement()
                _sleep(1)

                self.meas.pos7b[0, i], self.meas.pos8b[0, i] = (
                    _ppmac.read_motor_pos([7, 8]))
#                 with _ppmac.lock_ppmac:
                _ppmac.write('#5j^' + str(self.cfg.steps_b[0]) +
                             ';#6j^' + str(self.cfg.steps_b[1]))
                if fdi_mode:
                    while(_fdi.get_data_count() < counts - 1):
                        _sleep(0.1)
                    _data = _fdi.get_data()
                    _fdi.send('INP:COUP GND')
                else:
                    _sleep(3)
        #             while(volt.get_data_count() < counts):
        #                 time.sleep(0.1)
                    _data = _volt.get_readings_from_memory(5)
                if i == 0:
                    data_bck = _np.append(data_bck, _data)
                else:
                    data_bck = _np.vstack([data_bck, _data])
                self.meas.pos7b[1, i], self.meas.pos8b[1, i] = (
                    _ppmac.read_motor_pos([7, 8]))

                _prg_dialog.setValue(i+1)

            self.meas.data_frw = data_frw.transpose()
            self.meas.data_bck = data_bck.transpose()

            if self.flag_save:
                self.save_log(self.meas.data_frw, 'frw', 'Flip Coil')
                self.save_log(self.meas.data_bck, 'bck', 'Flip Coil')
                self.save_log(self.meas.pos7f, 'pos7f')
                self.save_log(self.meas.pos8f, 'pos8f')
                self.save_log(self.meas.pos7b, 'pos7b')
                self.save_log(self.meas.pos8b, 'pos8b')

            _meas = self.analysis.integral_calculus_fc(
                cfg=self.cfg, meas=self.meas)
            if _meas is not None:
                self.meas_fc = _meas
            else:
                _QMessageBox.warning(self, 'Warning',
                                     'Calculations failed.',
                                     _QMessageBox.Ok)
                return False
            self.save_measurement()
            self.analysis.update_meas_list()
            _count = self.analysis.cmb_meas_name.count() - 1
            self.analysis.cmb_meas_name.setCurrentIndex(_count)
#             self.analysis.plot(plot_from_measurementwidget=True)

            self.motors.timer.start(1000)
            _prg_dialog.destroy()
            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            _QMessageBox.information(self, 'Warning',
                                     'Measurement Failed.',
                                     _QMessageBox.Ok)
            self.motors.timer.start(1000)
            return False

    def save_measurement(self):
        """Saves current measurement into database."""
        try:
            if self.ui.rdb_sw.isChecked():
                _meas = self.meas_sw
            elif self.ui.rdb_sw_I2.isChecked():
                _meas = self.meas_sw2
            else:
                _meas = self.meas_fc

            _meas.db_update_database(
                        self.database_name,
                        mongo=self.mongo, server=self.server)
            _meas.db_save()
            self.analysis.update_meas_list()
            return True
        except Exception:
            _QMessageBox.warning(self, 'Information',
                                 'Failed to save this measurement.',
                                 _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def stop_motors(self):
        """Stops and disables all motors."""
        try:
            self.motors.ppmac.stop_motors()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def map_dialog(self):
        """Creates field map integrals dialog."""
        self.m_dialog = _MapDialog()
        self.m_dialog.show()
        self.m_dialog.accepted.connect(self.integral_map)
        self.m_dialog.rejected.connect(self.cancel_map)

    def cancel_map(self):
        """Cancels integral map and destroys dialog."""
        self.m_dialog.destroy()

    def update_map_meas_variables(self, map_data, map_cfg):
        """Updates integrals map variables.

        Args:
            map_data (IntegralMaps): IntegralMaps data object;
            map_cfg (IntegralMapsCfg): IntegralMapsCfg data object.

        Returns:
            True if successfull, False otherwise."""
        try:
            name = map_cfg.name.split('_')[:-2]
            map_data.name = '_'.join(name) + _time.strftime('_%y%m%d_%H%M')
            map_data.date = _time.strftime('%Y-%m-%d')
            map_data.hour = _time.strftime('%H:%M:%S')
            map_data.comments = map_cfg.comments
            map_data.Ix = map_cfg.Ix
            map_data.Iy = map_cfg.Iy
            map_data.I1 = map_cfg.I1
            map_data.I2 = map_cfg.I2
            map_data.I1x_amb_id = map_cfg.I1x_amb_id
            map_data.I1y_amb_id = map_cfg.I1y_amb_id
            map_data.I2x_amb_id = map_cfg.I1x_amb_id
            map_data.I2y_amb_id = map_cfg.I2y_amb_id
            map_data.x_start_pos = map_cfg.x_start_pos
            map_data.x_end_pos = map_cfg.x_end_pos
            map_data.x_step = map_cfg.x_step
            map_data.x_duration = map_cfg.x_duration
            map_data.y_start_pos = map_cfg.y_start_pos
            map_data.y_end_pos = map_cfg.y_end_pos
            map_data.y_step = map_cfg.y_step
            map_data.y_duration = map_cfg.y_duration
            map_data.repetitions = map_cfg.repetitions
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def integral_map(self):
        """Field integrals map measurement routine."""
        try:
            self.m_dialog.update_cfg_from_ui()
            _cfg = self.m_dialog.cfg
            ppmac_cfg = self.motors.cfg
            _map_data = _data.measurement.IntegralMaps()
            self.update_map_meas_variables(_map_data, _cfg)

            nplc = self.ui.dsb_nplc.value()
            mrange = self.ui.cmb_range.currentIndex()

            _ppmac.flag_abort = False

            if not self.motors.check_homed():
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

            if _cfg.I1:
                self.meas_sw.db_update_database(self.database_name,
                                                mongo=self.mongo,
                                                server=self.server)
                _map_data.I1_start_id = self.meas_sw.db_get_last_id() + 1
                if _cfg.Ix:
                    _meas_I1x = _data.measurement.MeasurementDataSW()
                    _meas_I1x.db_update_database(self.database_name,
                                                 mongo=self.mongo,
                                                 server=self.server)
                    _map_data.I1_start_id = _meas_I1x.db_get_last_id() + 1

                    name = _cfg.name.split('_')[:-2]
                    name = '_'.join(name) + '_I1x'
                    _meas_I1x.name = name + _time.strftime('_%y%m%d_%H%M')
                    _meas_I1x.mode = 'SW_I1'
                    _meas_I1x.comments = _cfg.comments
                    _meas_I1x.step = self.motors.cfg.y_step
                    _meas_I1x.motion_axis = 'Y'
                    _meas_I1x.gain = self.ui.dsb_gain.value()
                    _meas_I1x.turns = self.ui.sb_turns.value()
                    _meas_I1x.length = self.ui.dsb_length.value()
                    _meas_I1x.nplc = nplc
                    _meas_I1x.duration = _cfg.y_duration
                    _meas_I1x.nmeasurements = self.ui.sb_nmeasurements.value()
                    _meas_I1x.speed = ppmac_cfg.speed_y  # [mm/s]
                    _meas_I1x.accel = ppmac_cfg.accel_y  # [mm/s^2]
                    _meas_I1x.jerk = ppmac_cfg.jerk_y  # [mm/s^3]
                    _meas_I1x.Iamb_id = _cfg.I1x_amb_id
                    _meas_I1x.range = mrange
                    _meas_I1x.acq_init_interval = (
                        self.ui.dsb_acq_init_interval.value())
                    _meas_I1x.acq_final_interval = (
                        self.ui.dsb_acq_final_interval.value())

                if _cfg.Iy:
                    _meas_I1y = _data.measurement.MeasurementDataSW()
                    _meas_I1y.db_update_database(self.database_name,
                                                 mongo=self.mongo,
                                                 server=self.server)
                    _map_data.I1_start_id = _meas_I1y.db_get_last_id() + 1

                    name = _cfg.name.split('_')[:-2]
                    name = '_'.join(name) + '_I1y'
                    _meas_I1y.name = name + _time.strftime('_%y%m%d_%H%M')
                    _meas_I1y.mode = 'SW_I1'
                    _meas_I1y.comments = _cfg.comments
                    _meas_I1y.step = self.motors.cfg.x_step
                    _meas_I1y.motion_axis = 'X'
                    _meas_I1y.gain = self.ui.dsb_gain.value()
                    _meas_I1y.turns = self.ui.sb_turns.value()
                    _meas_I1y.length = self.ui.dsb_length.value()
                    _meas_I1y.nplc = nplc
                    _meas_I1y.duration = _cfg.x_duration
                    _meas_I1y.nmeasurements = self.ui.sb_nmeasurements.value()
                    _meas_I1y.speed = ppmac_cfg.speed_x  # [mm/s]
                    _meas_I1y.accel = ppmac_cfg.accel_x  # [mm/s^2]
                    _meas_I1y.jerk = ppmac_cfg.jerk_x  # [mm/s^3]
                    _meas_I1y.Iamb_id = _cfg.I1y_amb_id
                    _meas_I1y.range = mrange
                    _meas_I1y.acq_init_interval = (
                        self.ui.dsb_acq_init_interval.value())
                    _meas_I1y.acq_final_interval = (
                        self.ui.dsb_acq_final_interval.value())

            if _cfg.I2:
                self.meas_sw2.db_update_database(self.database_name,
                                                 mongo=self.mongo,
                                                 server=self.server)
                _map_data.I2_start_id = self.meas_sw2.db_get_last_id() + 1
                if _cfg.Ix:
                    _meas_I2x = _data.measurement.MeasurementDataSW2()

                    name = _cfg.name.split('_')[:-2]
                    name = '_'.join(name) + '_I2x'
                    _meas_I2x.name = name + _time.strftime('_%y%m%d_%H%M')
                    _meas_I2x.mode = 'SW_I2'
                    _meas_I2x.comments = _cfg.comments
                    _meas_I2x.step = self.motors.cfg.y_step
                    _meas_I2x.motion_axis = 'Y'
                    _meas_I2x.gain = self.ui.dsb_gain.value()
                    _meas_I2x.turns = self.ui.sb_turns.value()
                    _meas_I2x.length = self.ui.dsb_length.value()
                    _meas_I2x.nplc = nplc
                    _meas_I2x.duration = _cfg.y_duration
                    _meas_I2x.nmeasurements = self.ui.sb_nmeasurements.value()
                    _meas_I2x.speed = ppmac_cfg.speed_y  # [mm/s]
                    _meas_I2x.accel = ppmac_cfg.accel_y  # [mm/s^2]
                    _meas_I2x.jerk = ppmac_cfg.jerk_y  # [mm/s^3]
                    _meas_I2x.Iamb_id = _cfg.I2x_amb_id
                    _meas_I2x.range = mrange
                    _meas_I2x.acq_init_interval = (
                        self.ui.dsb_acq_init_interval.value())
                    _meas_I2x.acq_final_interval = (
                        self.ui.dsb_acq_final_interval.value())

                if _cfg.Iy:
                    _meas_I2y = _data.measurement.MeasurementDataSW2()

                    name = _cfg.name.split('_')[:-2]
                    name = '_'.join(name) + '_I2y'
                    _meas_I2y.name = name + _time.strftime('_%y%m%d_%H%M')
                    _meas_I2y.mode = 'SW_I2'
                    _meas_I2y.comments = _cfg.comments
                    _meas_I2y.step = self.motors.cfg.x_step
                    _meas_I2y.motion_axis = 'X'
                    _meas_I2y.gain = self.ui.dsb_gain.value()
                    _meas_I2y.turns = self.ui.sb_turns.value()
                    _meas_I2y.length = self.ui.dsb_length.value()
                    _meas_I2y.nplc = nplc
                    _meas_I2y.duration = _cfg.x_duration
                    _meas_I2y.nmeasurements = self.ui.sb_nmeasurements.value()
                    _meas_I2y.speed = ppmac_cfg.speed_x  # [mm/s]
                    _meas_I2y.accel = ppmac_cfg.accel_x  # [mm/s^2]
                    _meas_I2y.jerk = ppmac_cfg.jerk_x  # [mm/s^3]
                    _meas_I2y.Iamb_id = _cfg.I2y_amb_id
                    _meas_I2y.range = mrange
                    _meas_I2y.acq_init_interval = (
                        self.ui.dsb_acq_init_interval.value())
                    _meas_I2y.acq_final_interval = (
                        self.ui.dsb_acq_final_interval.value())

            # define x position array:
            x_motion_step = self.motors.cfg.x_step
            if _cfg.x_end_pos < _cfg.x_start_pos:
                _QMessageBox.information(self, 'Warning',
                                         'X End position should be greater '
                                         'than start position.\n'
                                         'Measurement Aborted.',
                                         _QMessageBox.Ok)
                return False
            elif _cfg.x_start_pos == _cfg.x_end_pos:
                n_steps = 1
                x_pos_array = _np.array([_cfg.x_start_pos])
            else:
                if (_cfg.x_end_pos - _cfg.x_start_pos) < _cfg.x_step:
                    x_pos_array = _np.array([_cfg.x_start_pos, _cfg.x_end_pos])
                else:
                    # number of steps
                    n_steps = int(1 + _np.ceil(
                        (_cfg.x_end_pos - _cfg.x_start_pos) / _cfg.x_step))
                    # warning if n_steps is not an integer?
                    # check if start and end pos are inside limits
                    x_pos_array = _np.linspace(_cfg.x_start_pos,
                                               _cfg.x_end_pos, n_steps)

            # define y position array:
            y_motion_step = self.motors.cfg.y_step
            if _cfg.y_end_pos < _cfg.y_start_pos:
                _QMessageBox.information(self, 'Warning',
                                         'Y End position should be greater '
                                         'than start position.\n'
                                         'Measurement Aborted.',
                                         _QMessageBox.Ok)
                return False
            elif _cfg.y_start_pos == _cfg.y_end_pos:
                n_steps = 1
                y_pos_array = _np.array([_cfg.y_start_pos])
            else:
                if (_cfg.y_end_pos - _cfg.y_start_pos) < _cfg.y_step:
                    y_pos_array = _np.array([_cfg.y_start_pos, _cfg.y_end_pos])
                else:
                    # number of steps
                    n_steps = int(1 + _np.ceil(
                        (_cfg.y_end_pos - _cfg.y_start_pos) / _cfg.y_step))
                    # warning if n_steps is not an integer?
                    # check if start and end pos are inside limits
                    y_pos_array = _np.linspace(_cfg.y_start_pos,
                                               _cfg.y_end_pos, n_steps)

            for y in y_pos_array:
                for x in x_pos_array:
                    if _cfg.Ix:
                        self.motors.move_x(x)
                        y_init_pos = y - y_motion_step/2
                        y_final_pos = y + y_motion_step/2
                        move_axis = self.motors.move_y
                        _volt.configure_volt(nplc, _cfg.y_duration, mrange)
                        if _cfg.I1:
                            _meas_I1x.x_pos = x
                            _meas_I1x.y_pos = y
                            _meas_I1x.start_pos = y_init_pos
                            _meas_I1x.end_pos = y_final_pos
                            _meas_I1x.move_axis = move_axis
                            for _ in range(_cfg.repetitions):
                                if _ppmac.flag_abort:
                                    _QMessageBox.information(self, 'Warning',
                                                             'Measurement '
                                                             'Aborted.',
                                                             _QMessageBox.Ok)
                                    return False
                                self.map_measurement(_meas_I1x)
                                # std limit I1x=20 G.cm
                                if _meas_I1x.I1_std > 20e-6:
                                    print('I1x std_error')
                                    self.map_measurement(_meas_I1x)
                        if _cfg.I2:
                            _meas_I2x.x_pos = x
                            _meas_I2x.y_pos = y
                            _meas_I2x.start_pos = y_init_pos
                            _meas_I2x.end_pos = y_final_pos
                            _meas_I2x.move_axis = move_axis
                            _meas_I2x.moving_motor = 1  # CHECK WHICH ONE IS THE BEST
                            move_axis(y, m_mode=2)
                            move_axis(y, m_mode=3)
                            move_axis(y, m_mode=2)
                            move_axis(y, m_mode=3)
                            for _ in range(_cfg.repetitions):
                                if _ppmac.flag_abort:
                                    _QMessageBox.information(self, 'Warning',
                                                             'Measurement '
                                                             'Aborted.',
                                                             _QMessageBox.Ok)
                                    return False
                                self.map_measurement(_meas_I2x, I2=True)
                                # std limit I2x= 5 kG.cm2
                                if _meas_I2x.I2_std > 5e-5:
                                    print('I2x std_error')
                                    self.map_measurement(_meas_I2x, I2=True)

                    if _cfg.Iy:
                        self.motors.move_y(y)
                        x_init_pos = x - x_motion_step/2
                        x_final_pos = x + x_motion_step/2
                        move_axis = self.motors.move_x
                        _volt.configure_volt(nplc, _cfg.x_duration, mrange)
                        if _cfg.I1:
                            _meas_I1y.x_pos = x
                            _meas_I1y.y_pos = y
                            _meas_I1y.start_pos = x_init_pos
                            _meas_I1y.end_pos = x_final_pos
                            _meas_I1y.move_axis = move_axis
                            for _ in range(_cfg.repetitions):
                                if _ppmac.flag_abort:
                                    _QMessageBox.information(self, 'Warning',
                                                             'Measurement '
                                                             'Aborted.',
                                                             _QMessageBox.Ok)
                                    return False
                                self.map_measurement(_meas_I1y)
                                # std limit I1y=10 G.cm
                                if _meas_I1y.I1_std > 10e-6:
                                    print('I1y std_error')
                                    self.map_measurement(_meas_I1y)
                        if _cfg.I2:
                            _meas_I2y.x_pos = x
                            _meas_I2y.y_pos = y
                            _meas_I2y.start_pos = x_init_pos
                            _meas_I2y.end_pos = x_final_pos
                            _meas_I2y.move_axis = move_axis
                            _meas_I2y.moving_motor = 2  # CHECK WHICH ONE IS THE BEST
                            move_axis(x, m_mode=2)
                            move_axis(x, m_mode=3)
                            for _ in range(_cfg.repetitions):
                                if _ppmac.flag_abort:
                                    _QMessageBox.warning(self, 'Warning',
                                                         'Measurement '
                                                         'Aborted.',
                                                         _QMessageBox.Ok)
                                    return False
                                self.map_measurement(_meas_I2y, I2=True)
                                # std limit I2y=2.5 kG.cm2
                                if _meas_I2y.I2_std > 2.5e-5:
                                    print('I1y std_error')
                                    self.map_measurement(_meas_I2y, I2=True)

            if _cfg.I1:
                self.meas_sw.db_update_database(self.database_name,
                                                mongo=self.mongo,
                                                server=self.server)
                _map_data.I1_end_id = self.meas_sw.db_get_last_id()
            else:
                _map_data.I1_start_id = 0
                _map_data.I1_end_id = 0

            if _cfg.I2:
                self.meas_sw2.db_update_database(self.database_name,
                                                 mongo=self.mongo,
                                                 server=self.server)
                _map_data.I2_end_id = self.meas_sw2.db_get_last_id()
            else:
                _map_data.I2_start_id = 0
                _map_data.I2_end_id = 0

            self.analysis.update_map_arrays(_map_data)

            _map_data.db_update_database(
                        self.database_name,
                        mongo=self.mongo, server=self.server)
            _map_data.db_save()

            _QMessageBox.information(self, 'Information',
                                     'Field integral map finished '
                                     'successfully.',
                                     _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def map_measurement(self, meas, I2=False):
        """Measure field integral in stretched wire mode.

        Args:
            meas (MeasurementDataSw/2): sw 1/2 measurement data object;
            I2 (bool): True for I2 measurement; False for I1 measurement.
        """

        _meas = meas
        name = _meas.name.split('_')[:-2]

        _meas.name = '_'.join(name) + _time.strftime('_%y%m%d_%H%M')
        _meas.date = _time.strftime('%Y-%m-%d')
        _meas.hour = _time.strftime('%H:%M:%S')
        _init_pos = _meas.start_pos  # [mm]
        _end_pos = _meas.end_pos  # [mm]
        nplc = _meas.nplc
        duration = _meas.duration
        acq_init_interval = _meas.acq_init_interval
        nmeasurements = _meas.nmeasurements
        npoints = int(_np.ceil(duration/(nplc/60)))

        move_axis = _meas.move_axis

        data_frw_aux = _np.array([])
        data_bck_aux = _np.array([])

        _prg_dialog = _QProgressDialog('Measurement', 'Abort', 0,
                                       nmeasurements, self)
        _prg_dialog.setWindowTitle('Measurement Progress')
        _prg_dialog.show()
        _QApplication.processEvents()

        # go to init pos
        if not I2:
            move_axis(_init_pos, m_mode=2)
            move_axis(_init_pos, m_mode=3)
            # _sleep(0.5)
            move_axis(_init_pos, m_mode=2)
            move_axis(_init_pos, m_mode=3)
        else:
            moving_motor = _meas.moving_motor
            move_axis(_init_pos, motor=moving_motor, m_mode=2)
            move_axis(_init_pos, motor=moving_motor, m_mode=3)
            move_axis(_init_pos, motor=moving_motor, m_mode=2)
            move_axis(_init_pos, motor=moving_motor, m_mode=3)

        # _volt.read_from_device()
        for i in range(nmeasurements):
            for j in range(4):
                if j == 3:
                    _prg_dialog.destroy()
                    _ppmac.flag_abort = True
                    _QMessageBox.warning(self, 'Warning',
                                         'Measurement aborted after 3 '
                                         'consecutive moving errors.',
                                         _QMessageBox.Ok)
                    raise RuntimeError('Measurement aborted after 3 '
                                       'consecutive moving errors.')

                if _prg_dialog.wasCanceled() or _ppmac.flag_abort:
                    _prg_dialog.destroy()
                    _ppmac.flag_abort = True
                    raise RuntimeError('Measurement aborted.')
                    _QMessageBox.warning(self, 'Warning',
                                         'Measurement aborted.')

                if not I2:
                    move_axis(_end_pos, m_mode=2)
                else:
                    move_axis(_end_pos, motor=moving_motor, m_mode=2)

                # Forward measurement
                _volt.start_measurement()
#                     _ppmac.write('Gather.PhaseEnable=2')
                _t0 = _time.time()
                # _sleep(acq_init_interval)
                _time.sleep(acq_init_interval)
                # move step
                if not I2:
                    if not move_axis(_end_pos, m_mode=3):
                        move_axis(_init_pos, m_mode=2)
                        move_axis(_init_pos, m_mode=3)
                        _sleep(1)
                        move_axis(_init_pos, m_mode=2)
                        move_axis(_init_pos, m_mode=3)
                        _sleep(duration + 9)
                        _volt.get_readings_from_memory(5)
                        continue
                else:
                    if not move_axis(_end_pos, motor=moving_motor, m_mode=3):
                        move_axis(_init_pos, motor=moving_motor, m_mode=2)
                        move_axis(_init_pos, motor=moving_motor, m_mode=3)
                        _sleep(1)
                        move_axis(_init_pos, motor=moving_motor, m_mode=2)
                        move_axis(_init_pos, motor=moving_motor, m_mode=3)
                        _sleep(duration + 9)
                        _volt.get_readings_from_memory(5)
                        continue

                if _time.time() - _t0 <= duration:
                    _sleep(0.2)

                _sleep(self.volt_interval)
                _t = _time.time() - _t0
                _data_frw = _volt.get_readings_from_memory(5)[::-1]
                # print(_t)

                if _prg_dialog.wasCanceled() or _ppmac.flag_abort:
                    _prg_dialog.destroy()
                    _ppmac.flag_abort = True
                    raise RuntimeError('Measurement aborted.')
                    _QMessageBox.warning(self, 'Warning',
                                         'Measurement aborted.')

                # comment to minimize  temperature difference
                # _sleep(3)

                # Backward measurement
                if not I2:
                    move_axis(_init_pos, m_mode=2)
                else:
                    move_axis(_init_pos, motor=moving_motor, m_mode=2)

                _volt.start_measurement()
#                     _ppmac.write('Gather.PhaseEnable=2')
                _t0 = _time.time()
                # _sleep(acq_init_interval)
                _time.sleep(acq_init_interval)
                # move - step
                if not I2:
                    if not move_axis(_init_pos, m_mode=3):
                        move_axis(_init_pos, m_mode=2)
                        move_axis(_init_pos, m_mode=3)
                        _sleep(1)
                        move_axis(_init_pos, m_mode=2)
                        move_axis(_init_pos, m_mode=3)
                        _sleep(duration + 9)
                        _volt.get_readings_from_memory(5)
                        self.get_volt_data(npoints)
                        continue
                else:
                    if not move_axis(_init_pos, motor=moving_motor, m_mode=3):
                        move_axis(_init_pos, motor=moving_motor, m_mode=2)
                        move_axis(_init_pos, motor=moving_motor, m_mode=3)
                        _sleep(1)
                        move_axis(_init_pos, motor=moving_motor, m_mode=2)
                        move_axis(_init_pos, motor=moving_motor, m_mode=3)
                        _sleep(duration + 9)
                        _volt.get_readings_from_memory(5)
                        continue

                if _time.time() - _t0 <= duration:
                    _sleep(0.2)

                _sleep(self.volt_interval)
                _t = _time.time() - _t0
                _data_bck = _volt.get_readings_from_memory(5)[::-1]
                # print(_t)

                break

            if i == 0:
                data_bck_aux = _np.append(data_bck_aux, _data_bck)
                data_frw_aux = _np.append(data_frw_aux, _data_frw)
            else:
                data_bck_aux = _np.vstack([data_bck_aux, _data_bck])
                data_frw_aux = _np.vstack([data_frw_aux, _data_frw])
            _prg_dialog.setValue(i+1)

        # data[i, j]
        # i: measurement voltage array index
        # j: measurement number index
        _meas.data_frw = data_frw_aux.transpose()
        _meas.data_bck = data_bck_aux.transpose()

        # data analisys
        self.analysis.integral_calculus_sw(_meas, I2)
        # self.save_measurement()
        _meas.db_update_database(
                        self.database_name,
                        mongo=self.mongo, server=self.server)
        _meas.db_save()
        self.analysis.update_meas_list()
        _count = self.analysis.cmb_meas_name.count() - 1
        self.analysis.cmb_meas_name.setCurrentIndex(_count)

        # check standard deviation
        # limits I1x=20 G.cm; I1y=10 G.cm; I2x= 5 kG.cm2; I2y=2.5 kG.cm2
