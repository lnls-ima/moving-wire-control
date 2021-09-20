# -*- coding: utf-8 -*-

"""Run the moving wire control application."""

from movingwire.gui import movingwireapp


THREAD = False


if THREAD:
    thread = movingwireapp.run_in_thread()
else:
    movingwireapp.run()
