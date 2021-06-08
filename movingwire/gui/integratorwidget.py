"""Integrator widget for the Moving Wire Control application."""

import os as _os
import sys as _sys
import traceback as _traceback

from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtCore import Qt as _Qt
import qtpy.uic as _uic

from movingwire.gui.utils import get_ui_file as _get_ui_file


class IntegratorWidget(_QWidget):
    """Integrator widget class for the Moving Wire Control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.connect_signal_slots()

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        pass
