"""Connection widget for the Moving Wire Control application."""

import os as _os
import sys as _sys
import traceback as _traceback
import serial.tools.list_ports as _list_ports
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtCore import Qt as _Qt
import qtpy.uic as _uic

from imautils.devices import PmacLV_IMS
from imautils.devices import FDI2056
# from imautils.devices import pydrs

from movingwire.gui.utils import get_ui_file as _get_ui_file

from movingwire.devices import (
    ppmac as _ppmac,
    fdi as _fdi,
    ps as _ps,
    volt as _volt,
    mult as _mult,
    )


class ConnectionWidget(_QWidget):
    """Connection widget class for the Moving Wire Control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

#         self.connection_config = _configuration.ConnectionConfig()

        self.connect_signal_slots()
        self.update_serial_ports()
        self.ui.cmb_ps_port.setCurrentText('COM6')

    def init_tab(self):
        pass

    def connect_signal_slots(self):
        """Create signal/slot connections."""
#         pass
        self.ui.pbt_connect.clicked.connect(self.connect)
        self.ui.pbt_disconnect.clicked.connect(self.disconnect)

    def update_serial_ports(self):
            """Update available serial ports."""
            _l = [p[0] for p in _list_ports.comports()]

            if len(_l) == 0:
                return

            _ports = []
            _s = ''
            _k = str
            if 'COM' in _l[0]:
                _s = 'COM'
                _k = int

            for key in _l:
                _ports.append(key.strip(_s))
            _ports.sort(key=_k)
            _ports = [_s + key for key in _ports]

            self.ui.cmb_ps_port.clear()
            self.ui.cmb_ps_port.addItems(_ports)

    def connect(self):
        """Establish connection to the selected instruments."""
        try:
            _ppmac_ip = self.ui.le_ppmac_ip.text()
            _fdi_inst = self.ui.cmb_integrator_inst.currentText()
            _agilent_addr = self.ui.sb_agilent_addr.value()
            _agilent_board = self.ui.sb_agilent_board.value()
            _mult_addr = self.ui.sb_mult_addr.value()

#             if self.ui.chb_integrator_en.isChecked():
#             _fdi.inst = _fdi.rm.open_resource(_fdi_inst.encode())
            if self.ui.chb_ppmac_en.isChecked():
                _ppmac.connect(_ppmac_ip)
                _ppmac.ppmac.timeout = 3
                _ppmac.ppmac_ssh = _ppmac.ssh.invoke_shell(term='vt100')
                _ppmac.ftp = _ppmac.ssh.open_sftp()
            if self.ui.chb_ps_en.isChecked():
                _ps.Connect(self.ui.cmb_ps_port.currentText())
            if self.ui.chb_voltmeter_en.isChecked():
                _volt.connect(address=_agilent_addr, board=_agilent_board)
            if self.ui.chb_multichannel_en.isChecked():
                _mult.connect(_mult_addr)
            _QMessageBox.information(self, 'Information',
                                     'Devices connected.',
                                     _QMessageBox.Ok)

            self.ui.pbt_connect.setEnabled(False)
            self.ui.pbt_disconnect.setEnabled(True)
            for i in range(1, self.parent_window.ui.twg_main.count() - 2):
                self.parent_window.ui.twg_main.setTabEnabled(i, True)

            return True
        except Exception:
            self.ui.pbt_connect.setEnabled(True)
            self.ui.pbt_disconnect.setEnabled(False)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def disconnect(self):
        """Disconnects all instruments."""
        try:
#             _fdi.disconnect()
            if self.ui.chb_ppmac_en.isChecked():
                _ppmac.disconnect()
            if self.ui.chb_ps_en.isChecked():
                _ps.turn_off()
                _ps.Disconnect()
            if self.ui.chb_voltmeter_en.isChecked():
                _volt.disconnect()
            if self.ui.chb_multichannel_en.isChecked():
                _mult.disconnect()

            _QMessageBox.information(self, 'Information',
                                     'Devices disconnected.',
                                     _QMessageBox.Ok)

            self.ui.pbt_connect.setEnabled(True)
            self.ui.pbt_disconnect.setEnabled(False)
            for i in range(1, self.parent_window.ui.twg_main.count() - 2):
                self.parent_window.ui.twg_main.setTabEnabled(i, False)

            return True
        except Exception:
            self.ui.pbt_connect.setEnabled(False)
            self.ui.pbt_disconnect.setEnabled(True)
            _traceback.print_exc(file=_sys.stdout)
            return False
