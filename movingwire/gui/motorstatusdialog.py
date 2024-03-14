from qtpy.QtWidgets import (
    QDialog as _QDialog,
    )
from PyQt5 import uic as _uic
from movingwire.devices import ppmac as _ppmac

from movingwire.gui.utils import (
    get_ui_file as _get_ui_file,
    )
import sys as _sys
import traceback as _traceback
import time


class MotorStatus(_QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.change_status()

        self.pbt_reload.clicked.connect(self.change_status)

    def change_status(self):
        motors = [self.lbl_motorXAstatus,
                  self.lbl_motorYAstatus,
                  self.lbl_motorXBstatus,
                  self.lbl_motorYBstatus,
                  ]
        homed = [self.lbl_homedXA,
                 self.lbl_homedYA,
                 self.lbl_homedXB,
                 self.lbl_homedYB,
                 ]
        ampEna = [self.lbl_ampEnableXA,
                  self.lbl_ampEnableYA,
                  self.lbl_ampEnableXB,
                  self.lbl_ampEnableYB,
                  ]

        ampFault = [self.lbl_ampFaultXA,
                    self.lbl_ampFaultYA,
                    self.lbl_ampFaultXB,
                    self.lbl_ampFaultYB,
                    ]

        feFatal = [self.lbl_feFatalXA,
                   self.lbl_feFatalYA,
                   self.lbl_feFatalXB,
                   self.lbl_feFatalXB,
                   ]

        limitstop = [self.lbl_limitStopXA,
                     self.lbl_limitStopYA,
                     self.lbl_limitStopXB,
                     self.lbl_limitStopYB,
                     ]

        pluslimit = [self.lbl_plusLimitXA,
                     self.lbl_plusLimitYA,
                     self.lbl_plusLimitXB,
                     self.lbl_plusLimitYB,
                     ]

        minuslimit = [self.lbl_minusLimitXA,
                      self.lbl_minusLimitYA,
                      self.lbl_minusLimitXB,
                      self.lbl_minusLimitYB,
                      ]

        try:
            self.parent().update_flag = False
            # time.sleep(0.5)
            for i in range(1, 5):

                if _ppmac.query_motor_param(i, 'AmpEna') == '1':
                    motors[i-1].setStyleSheet("background-color: limegreen")
                    ampEna[i-1].setStyleSheet("background-color: limegreen")
                elif _ppmac.query_motor_param(i, 'AmpEna') == '0':
                    motors[i-1].setStyleSheet("background-color: light gray")
                    ampEna[i-1].setStyleSheet("background-color: light gray")

                if _ppmac.query_motor_param(i, 'FeFatal') == '1':
                    feFatal[i-1].setStyleSheet("background-color: red")
                    motors[i-1].setStyleSheet("background-color: orange")
                if _ppmac.query_motor_param(i, 'FeFatal') == '0':
                    feFatal[i-1].setStyleSheet("background-color: light gray")
                    if _ppmac.query_motor_param(i, 'AmpEna') == '1':
                        motors[i-1].setStyleSheet("background-color: limegreen")

                if _ppmac.motor_homed(i):
                    homed[i-1].setStyleSheet("background-color: limegreen")
                elif not _ppmac.motor_homed(i):
                    homed[i-1].setStyleSheet("background-color: light gray")

                if _ppmac.query_motor_param(i, 'AmpFault') == '1':
                    ampFault[i-1].setStyleSheet("background-color: red")
                    motors[i-1].setStyleSheet("background-color: orange")
                elif _ppmac.query_motor_param(i, 'AmpFault') == '0':
                    ampFault[i-1].setStyleSheet("background-color: light gray")
                    if _ppmac.query_motor_param(i, 'AmpEna') == '1':
                        motors[i-1].setStyleSheet("background-color: limegreen")

                if _ppmac.query_motor_param(i, 'LimitStop') == '1':
                    limitstop[i-1].setStyleSheet("background-color: yellow")
                elif _ppmac.query_motor_param(i, 'LimitStop') == '0':
                    limitstop[i-1].setStyleSheet("background-color: light gray")

                if _ppmac.query_motor_param(i, 'PlusLimit') == '1':
                    pluslimit[i-1].setStyleSheet("background-color: red")
                elif _ppmac.query_motor_param(i, 'PlusLimit') == '0':
                    pluslimit[i-1].setStyleSheet("background-color: light gray")

                if _ppmac.query_motor_param(i, 'MinusLimit') == '1':
                    minuslimit[i-1].setStyleSheet("background-color: red")
                elif _ppmac.query_motor_param(i, 'MinusLimit') == '0':
                    minuslimit[i-1].setStyleSheet("background-color: light gray")

            self.parent().update_flag = True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
