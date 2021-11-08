# -*- coding: utf-8 -*-

"""Run the ueipac control application."""

from ueipac.gui import ueipacapp


THREAD = True


if THREAD:
    thread = ueipacapp.run_in_thread()
else:
    ueipacapp.run()
