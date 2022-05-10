"""Measurement progress dialog"""

import os as _os
import sys as _sys
import traceback as _traceback
from qtpy.QtCore import Qt as _Qt
from qtpy.QtWidgets import (
    QApplication as _QApplication,
    QDialog as _QDialog,
    QMessageBox as _QMessageBox,
    QVBoxLayout as _QVBoxLayout,
    )

import qtpy.uic as _uic

from movingwire.gui.utils import get_ui_file as _get_ui_file
from imautils.gui.undconfigwidget import UndConfigWidget


class MeasurementDialog(_QDialog):
    """Moving Wire measurement progress dialog."""

    def __init__(self, parent=None):
        """Set up the ui and create connections."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.undctrl = UndConfigWidget()

        self.ui.wdg_und.setLayout(self.undctrl.wdg_und)

        self.connect_signal_slots()

    def connect_signal_slots(self):
        pass
        #self.ui.pbt_cancel.clicked.connect()
        #self.ui.pbt_close.clicked.connect()

    def update_postions(self):
        pass

    def update_progress_bar(self):
        pass