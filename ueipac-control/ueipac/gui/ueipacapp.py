# -*- coding: utf-8 -*-

"""Main entry point to the Ueipac Control application."""

import os as _os
import sys as _sys
import threading as _threading
from qtpy.QtWidgets import QApplication as _QApplication

from ueipac.gui import utils as _utils 
from ueipac.gui.ueipacwindow import (
    UeipacWindow as _UeipacWindow)
import ueipac.data as _data
#from ueipac.devices import 


class UeipacApp(_QApplication):
    """Ueipac application."""

    def __init__(self, args):
        """Start application."""
        super().__init__(args)
        self.setStyle(_utils.WINDOW_STYLE)

        self.directory = _utils.BASEPATH
        self.database_name = _utils.DATABASE_NAME
        self.mongo = _utils.MONGO
        self.server = _utils.SERVER
#       self.create_database()

        # positions dict
        self.positions = {}
        self.current_max = 0
        self.current_min = 0

        # create dialogs
#         self.view_probe_dialog = _ViewProbeDialog()

        # devices instances


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
            self.app = UeipacApp([])
            self.window = _UeipacWindow(
                width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
            self.window.show()
            self.window.centralize_window()
            _sys.exit(self.app.exec_())


def run():
    """Run ueipac application."""
    app = None
    if not _QApplication.instance():
        app = UeipacApp([])
        window = _UeipacWindow(
            width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
        window.show()
        window.centralize_window()
        _sys.exit(app.exec_())


def run_in_thread():
    """Run ueipac application in a thread."""
    return GUIThread()
