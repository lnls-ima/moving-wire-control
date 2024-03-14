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

from movingwire.gui.utils import (
    get_ui_file as _get_ui_file,
    sleep as _sleep,
    )

from movingwire.devices import (
    ppmac as _ppmac,
    volt as _volt,
    )

import movingwire.data as _data

from future.backports.test.pystone import FALSE


class FiducialDialog(_QDialog):
    """Moving Wire fiducial dialog.

    Info: cylindrical device radius: 12.5 mm;
        hole C in the fiducialization device 
        (C hole center at 47.5mm from device support center) """

    def __init__(self, motors, parent=None):
        """Set up the ui and create connections."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.motors = motors
        self.motors.update_flag = False

        self.connect_signal_slots()

        self.last_motor = 0
        self.offset_Xa = 0
        self.offset_Xb = 0
        self.offset_Xa_changed = True
        self.offset_Xb_changed = True
        self.abort_flag = False

        self.configure_ohm()
        _sleep(1)
        self.update_position()

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
        self.ui.pbt_move_Xa.clicked.connect(self.move_Xa)
        self.ui.pbt_move_Xb.clicked.connect(self.move_Xb)
        self.ui.pbt_move_Ya.clicked.connect(self.move_Ya)
        self.ui.pbt_move_Yb.clicked.connect(self.move_Yb)
        self.ui.pbt_update.clicked.connect(self.update_status)
        self.ui.pbt_abort.clicked.connect(self.abort_fiducialization)
        self.ui.pbt_configure_ohm.clicked.connect(self.configure_ohm)
        self.ui.pbt_reset.clicked.connect(self.reset_fiducialization)
        self.ui.pbt_write.clicked.connect(self.manual_write)
        self.ui.pbt_fiducialization.clicked.connect(self.fiducialization)

    def update_position(self):
        """Updates position displays on UI."""
        try:
            self.motors.update_flag = False
            if hasattr(_ppmac, 'ppmac'):
                if not _ppmac.ppmac.closed:
                    self.pos = _ppmac.read_motor_pos([1, 2, 3, 4, 7, 8])
                    self.ui.lcd_pos1.display(self.pos[1]*self.motors.cfg.x_sf -
                                             self.motors.cfg.x_offset)
                    self.ui.lcd_pos2.display(self.pos[0]*self.motors.cfg.y_sf -
                                             self.motors.cfg.y_offset)
                    self.ui.lcd_pos3.display(self.pos[3]*self.motors.cfg.x_sf -
                                             self.motors.cfg.x_offset)
                    self.ui.lcd_pos4.display(self.pos[2]*self.motors.cfg.y_sf -
                                             self.motors.cfg.y_offset)
                    # self.ui.lcd_pos1.display(self.pos[0]*self.motors.cfg.x_sf -
                    #                          self.motors.cfg.x_offset)
                    # self.ui.lcd_pos2.display(self.pos[4]*self.motors.cfg.y_sf -
                    #                          self.motors.cfg.y_offset)
                    # self.ui.lcd_pos3.display(self.pos[2]*self.motors.cfg.x_sf -
                    #                          self.motors.cfg.x_offset)
                    # self.ui.lcd_pos4.display(self.pos[5]*self.motors.cfg.y_sf -
                    #                          self.motors.cfg.y_offset)
                    _QApplication.processEvents()

            # if self.read_short_circuit():
            #     self.ui.lbl_status.setText('Closed')
            # else:
            #     self.ui.lbl_status.setText('Open')
            # self.motors.update_flag = True
        except Exception:
            # self.motors.update_flag = True
            _traceback.print_exc(file=_sys.stdout)

    def update_status(self):
        """Updates position and device circuit status on UI."""
        self.update_position()
        self.read_short_circuit()

    def configure_ohm(self):
        """Configures multimeter to read resistance (full scale: 1 kOhm)."""
        _volt.configure_ohm()

    def move_Xa(self):
        """Moves Xa motor independent from Xb. Position can be absolute or
        relative."""
        try:
            if self.ui.rdb_absolute.isChecked():
                absolute = True
            else:
                absolute = False

            motor = 2
            position = self.ui.dsb_Xa_pos.value()

            self.motors.move_x(position, absolute, motor)
            _sleep(0.3)
            self.update_position()
            self.read_short_circuit()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def move_Xb(self):
        """Moves Xb motor independent from Xa. Position can be absolute or
        relative."""
        try:
            if self.ui.rdb_absolute.isChecked():
                absolute = True
            else:
                absolute = False

            motor = 4
            position = self.ui.dsb_Xb_pos.value()

            self.motors.move_x(position, absolute, motor)
            _sleep(0.3)
            self.update_position()
            self.read_short_circuit()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def move_Ya(self):
        """Moves Ya motor independent from Yb. Position can be absolute or
        relative."""
        try:
            if self.ui.rdb_absolute.isChecked():
                absolute = True
            else:
                absolute = False

            motor = 1
            position = self.ui.dsb_Ya_pos.value()

            self.motors.move_y(position, absolute, motor)
            _sleep(0.3)
            self.update_position()
            self.read_short_circuit()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def move_Yb(self):
        """Moves Yb motor independent from Ya. Position can be absolute or
        relative."""
        try:
            if self.ui.rdb_absolute.isChecked():
                absolute = True
            else:
                absolute = False

            motor = 3
            position = self.ui.dsb_Yb_pos.value()

            self.motors.move_y(position, absolute, motor)
            _sleep(0.3)
            self.update_position()
            self.read_short_circuit()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def reset_fiducialization(self):
        """Resets fiducialization process to start a new one."""
        try:
            _ans = _QMessageBox.question(self, 'Attention', 'Do you want to '
                                         'reset the fiducialization process?',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

            self.last_motor = 0
            self.offset_Xa = 0
            self.offset_Xb = 0
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def fiducialization(self):
        """Run the fiducialization routine."""
        try:
            self.motors.update_flag = False
            step = self.ui.dsb_fiduc_step.value()

            if self.ui.cmb_x_motor_dir.currentIndex() == 1:
                direction = -1
            else:
                direction = 1

            step = direction*step

            if self.ui.cmb_x_motor.currentIndex() == 0:
                motor = 2
                move_motor = motor
                if self.last_motor != 0:
                    if self.offset_Xa != 0:
                        self.motors.move_x(self.offset_Xa*self.motors.cfg.x_sf,
                                           True, 2)
                    if self.offset_Xb != 0:
                        self.motors.move_x(self.offset_Xb*self.motors.cfg.x_sf,
                                           True, 4)
                else:
                    if self.offset_Xa != 0:
                        if self.offset_Xb == 0:
                            _init_motor = None
                        else:
                            _init_motor = 2
                        self.motors.move_x(
                            self.offset_Xa*self.motors.cfg.x_sf,
                            True, _init_motor)
                    if self.offset_Xb != 0:
                        if self.offset_Xa == 0:
                            _init_motor = None
                        else:
                            _init_motor = 4
                        self.motors.move_x(
                            self.offset_Xb*self.motors.cfg.x_sf,
                            True, _init_motor)
            else:
                motor = 4
                move_motor = motor
                if self.last_motor != 0:
                    if self.offset_Xa != 0:
                        self.motors.move_x(self.offset_Xa*self.motors.cfg.x_sf,
                                           True, 2)
                    if self.offset_Xb != 0:
                        self.motors.move_x(self.offset_Xb*self.motors.cfg.x_sf,
                                           True, 4)
                else:
                    if self.offset_Xa != 0:
                        if self.offset_Xb == 0:
                            _init_motor = None
                        else:
                            _init_motor = 2
                        self.motors.move_x(
                            self.offset_Xa*self.motors.cfg.x_sf,
                            True, _init_motor)
                    if self.offset_Xb != 0:
                        if self.offset_Xa == 0:
                            _init_motor = None
                        else:
                            _init_motor = 4
                        self.motors.move_x(
                            self.offset_Xb*self.motors.cfg.x_sf,
                            True, _init_motor)

            if self.last_motor == 0:
                # Moves both motors at first iteration
                move_motor = None

            if self.read_short_circuit():
                # If short circuited, retreat until circuit opens
                while all([self.read_short_circuit(),
                           not self.abort_flag]):
                    self.motors.move_x(-5*step, False, move_motor)
                    _sleep(0.1)
                    self.update_position()
                if self.abort_flag:
                    self.abort()
                    return False

            if not self.read_short_circuit():
                # If not short circuited, advances until circuit closes
                while all([not self.read_short_circuit(),
                           not self.abort_flag]):
                    self.motors.move_x(step, False, move_motor)
                    _sleep(0.05)
                    self.update_position()
                if self.abort_flag:
                    self.abort()
                    return False
                pos_closed = _ppmac.read_motor_pos([motor])[0]
                _sleep(0.5)

                # Retreats until circuit opens again
                n_back_steps = 0
                while all([self.read_short_circuit(),
                           not self.abort_flag]):
                    self.motors.move_x(-1*step, False, move_motor)
                    _sleep(0.05)
                    n_back_steps += 1
                    self.update_position()
                if self.abort_flag:
                    self.abort()
                    return False
                pos_open = _ppmac.read_motor_pos([motor])[0]
                _sleep(0.5)

                # Advances to check if the circuit closes at the same position
                while not self.read_short_circuit():
                    self.motors.move_x(step, False, move_motor)
                    _sleep(0.05)
                    self.update_position()
                if self.abort_flag:
                    self.abort()
                    return False
                pos_closed_2 = _ppmac.read_motor_pos([motor])[0]

                if self.last_motor == 0:
                    self.offset_Xa = pos_open
                    self.offset_Xb = pos_open

                print(pos_closed*2e-5, pos_closed_2*2e-5, pos_open*2e-5)

            # if offset difference is greater than 2 steps, updates its value
            if motor == 2:
                if (abs(self.offset_Xa - pos_closed_2) >
                        round(abs(2 * step) / self.motors.cfg.x_sf, 0)):
                    self.offset_Xa = pos_open
                    self.offset_Xa_changed = True
                    if self.last_motor == 0:
                        # Updates both offsets at first iteration
                        self.offset_Xb = pos_open
                        self.offset_Xb_changed = True
                else:
                    self.offset_Xa_changed = False
            else:
                if (abs(self.offset_Xb - pos_closed_2) >
                        round(abs(2 * step) / self.motors.cfg.x_sf, 0)):
                    self.offset_Xb = pos_open
                    self.offset_Xb_changed = True
                    if self.last_motor == 0:
                        # Updates both offsets at first iteration
                        self.offset_Xa = pos_open
                        self.offset_Xa_changed = True
                else:
                    self.offset_Xb_changed = False

            xa_comp_pos = int(_ppmac.query_motor_param(2, 'CompPos'))
            xb_comp_pos = int(_ppmac.query_motor_param(4, 'CompPos'))
            offset_xa = int(self.offset_Xa - xa_comp_pos)
            offset_xb = int(self.offset_Xb - xb_comp_pos)
            self.ui.spb_offset_Xa.setValue(offset_xa)
            self.ui.spb_offset_Xb.setValue(offset_xb)
            _QApplication.processEvents()

            # Retreats 2mm to replace the device
            self.motors.move_x(direction*-2, False)

            self.last_motor = motor

            if n_back_steps > 1:
                _msg = (str(n_back_steps) + ' steps were necessary to '
                        'open the circuit after it was closed. '
                        'Consider reducing the step size.')
                _QMessageBox.information(self, 'Information', _msg,
                                         _QMessageBox.Ok)

            # Checks if both offsets haven't changed to end routine
            if all([not self.offset_Xa_changed,
                    not self.offset_Xb_changed]):
                _ans = _QMessageBox.question(self, 'Attention',
                                             'Fiducialization finished.'
                                             ' Would you like to write the '
                                             'new offsets to the controller '
                                             'and close the fiducialization '
                                             'window?',
                                             _QMessageBox.Yes |
                                             _QMessageBox.No,
                                             _QMessageBox.Yes)
                if _ans == _QMessageBox.No:
                    return False
                self.write_offsets(offset_xa, offset_xb)
                _volt.configure_volt(2, 1, 10)  # configures voltmeter
                self.motors.update_flag = True
                self.destroy()

            _QMessageBox.information(self, 'Information',
                                     'Iteration finished. Please position the '
                                     'device at the other side of the '
                                     'undulator.',
                                     _QMessageBox.Ok)

        except Exception:
            # self.motors.update_flag = True
            _traceback.print_exc(file=_sys.stdout)

    def write_offsets(self, offset_xa, offset_xb):
        """Writes fiducialization offsets on DeltaTau. Note that it discounts
        the device position from the UI offsets.

        Args:
            offset_xa (int): Motor Xa offset in encoder count units;
            offset_xb (int): Motor Xb offset in encoder count units.
        Returns:
            True if successful, False otherwise."""
        try:
            device_pos = round(
                self.ui.dsb_dev_pos.value()/self.motors.cfg.x_sf, 0)
            # device_pos_a = round(
            #     self.ui.dsb_dev_pos_a.value()/self.motors.cfg.x_sf, 0)
            # device_pos_b = round(
            #     self.ui.dsb_dev_pos_b.value()/self.motors.cfg.x_sf, 0)
            wire_radius = 0.05/self.motors.cfg.x_sf  # from mm to enc counts
            offset_xa = -1 * int(offset_xa - (device_pos - wire_radius))
            offset_xb = -1 * int(offset_xb - (device_pos - wire_radius))
            offset_xa = -1 * int(offset_xa - (device_pos_a - wire_radius))
            offset_xb = -1 * int(offset_xb - (device_pos_b - wire_radius))
            _ppmac.write('#2,4k')
            _ppmac.set_motor_param(2, 'CompPos', offset_xa)
            _ppmac.set_motor_param(4, 'CompPos', offset_xb)
            self.save_offsets(offset_xa, offset_xb)
            return True
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def manual_write(self):
        """Writes fiducialization offsets from UI, without considering the
        values from the automated process."""
        try:
            _ans = _QMessageBox.question(self, 'Attention',
                                         'Are you sure you want to write'
                                         ' the offsets from the UI?\n'
                                         'The fiducialization dialog will '
                                         'close afterwards.',
                                         _QMessageBox.Yes |
                                         _QMessageBox.No,
                                         _QMessageBox.No)
            if _ans == _QMessageBox.No:
                return False

            offset_xa = int(self.ui.spb_offset_Xa.value())
            offset_xb = int(self.ui.spb_offset_Xb.value())
            self.write_offsets(offset_xa, offset_xb)
            _volt.configure_volt(2, 1, 10)  # configures voltmeter
            self.motors.update_flag = True
            self.destroy()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def save_offsets(self, offset_xa, offset_xb):
        """Saves fiducialization offsets on database.

        Args:
            offset_xa (int): Motor Xa offset in encoder count units;
            offset_xb (int): Motor Xb offset in encoder count units.
        Returns:
            True if successful, False otherwise."""
        try:
            self.motors.load_fiduc_cfg()
            self.motors.fiduc_cfg.date = _time.strftime('%Y-%m-%d')
            self.motors.fiduc_cfg.hour = _time.strftime('%H:%M:%S')
            self.motors.fiduc_cfg.offset_xa = offset_xa
            self.motors.fiduc_cfg.offset_xb = offset_xb
            self.motors.fiduc_cfg.db_update(1)
            return True
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def read_short_circuit(self):
        """Checks if the fiducialization device is short-circuited.

        Returns:
            True if shot-circuited, False otherwise."""
        try:
            _volt.start_measurement()
            _sleep(0.1)
            _r = _volt.get_readings_from_memory(5)
            if _r[0] < 1000:
                self.ui.lbl_status.setText('Closed')
                return True
            else:
                self.ui.lbl_status.setText('Open')
                return False
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def abort(self):
        self.abort_flag = False
        _QMessageBox.warning(self, 'Warning', 'Iteration aborted',
                             _QMessageBox.Ok)

    def abort_fiducialization(self):
        self.abort_flag = True
