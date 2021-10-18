"""UEIPAC widget for the ueipac Control application. (Determination of wire mechanic tension)"""

import os as _os
import sys as _sys
import time as _time
import traceback as _traceback
import paramiko as _paramiko
import numpy as np
import matplotlib.pyplot as plt 
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq


from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    QVBoxLayout as _QVBoxLayout,
    )
from qtpy.QtCore import Qt as _Qt
import qtpy.uic as _uic

import ueipac.data as _data
from ueipac.gui.utils import (
    get_ui_file as _get_ui_file,
    sleep as _sleep,
    update_db_name_list as _update_db_name_list,
    )

import matplotlib
from _ast import Try
from prompt_toolkit.key_binding.bindings.named_commands import self_insert
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as _FigureCanvas)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as _NavigationToolbar)
from matplotlib.figure import Figure


class MplCanvas(_FigureCanvas):

    def __init__(self, parent=None, width=5, height=6, dpi=100):
        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class UEIPACWidget(_QWidget):
    """UEIPAC widget class for the Ueipac Control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.set_pyplot()
        self.connect_signal_slots()
        


    def init_tab(self):
        #self.load_measurement()
        pass
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

        self.ui.pbt_start.clicked.connect(self.start_meas)
        self.ui.pbt_connect.clicked.connect(self.connect_ueipac)
        self.ui.pbt_disconnect.clicked.connect(self.disconnect_ueipac)
        self.ui.pbt_config.clicked.connect(self.config_ueipac)
        self.ui.cmb_plot.currentIndexChanged.connect(self.plot)
        self.ui.cmb_mode.currentIndexChanged.connect(self.change_mode)
        
        
    def change_mode(self):
        
        if self.ui.cmb_mode.currentText() == 'Compensating Acquisition Mode':
            self.ui.pbt_start.clicked.disconnect()
            self.ui.pbt_start.clicked.connect(self.start_meas_mode2_1)  
        if self.ui.cmb_mode.currentText() == 'Normal Acquisition Mode':
            self.ui.pbt_start.clicked.disconnect()
            self.ui.pbt_start.clicked.connect(self.start_meas)
    
    def sleep(self, time):
        """Halts the program while processing UI events."""
        """Args:"""
        """time (float): time to halt the program in seconds."""
        try:
            _dt = 0.02
            _tf = _time.time() + time
            while _time.time() < _tf:
                _QApplication.processEvents()
                _time.sleep(_dt)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)   

    def connect_ueipac(self):
        """Connect to the controller.
        Returns:
            True if operation completed successfully;
            False otherwise."""

        try: 
            self.user = 'root'
            self.password = 'root'
            ip = '10.0.28.246'
            port = 22
            self.ssh = _paramiko.SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(_paramiko.AutoAddPolicy())
            self.ssh.connect(ip, port, self.user, self.password, timeout=3)
            self.sftp = self.ssh.open_sftp()
            self.sleep(0.3)
            self.ppmac = self.ssh.invoke_shell(term='vt100')
            self.sleep(0.3)
            self.ppmac.send('ls\r\n')
            self.ppmac.recv(1024)
            self.sleep(0.4)
            return _QMessageBox.information(self, "Information",
                                             "Connection was successful",
                                              _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
        
    def start_meas(self):
        """Download a file from the controller via sftp.
        Returns:
            True if operation completed successfully;
            False otherwise."""
        try:
            self.ppmac.send('cd /tmp \n')
            self.ppmac.send('./SampleVMap207_v3 \n')
            self.sleep(self.ui.dsb_time.value())
            self.ppmac.send('\x03 \n')
            self.sleep(0.4)
            remotepath = '/tmp/Gustavo.csv'
            localpath = self.ui.le_outputname.text()
            self.sftp = self.ssh.open_sftp()
            self.get = self.sftp.get(remotepath, localpath)
            self.sleep(0.3)
            
            """Load Voltage file.
        Returns:
            True if operation completed successfully;
            False otherwise."""
            self.peaks = []
            self.L = self.ui.dsb_length.value()
            self.density = self.ui.dsb_density.value()
            self.diameter = self.ui.dsb_diameter.value()
            self.LDensity = (self.density*np.pi*(self.diameter)**2)/4
            fname = r"{}".format(localpath)
            self.iline = 0 
            self.fline= int(10*self.ui.dsb_numsample.value() - 1)
            self.icol=1
            self.fcol= int(self.ui.dsb_numchannels.value())
            frequency = int(self.ui.dsb_frequency.value())
            i=0
            self.voltage = np.zeros((self.fline-self.iline+1)*(self.fcol-self.icol+1), dtype = float)
            self.voltage = np.reshape(self.voltage, newshape=(self.fline-self.iline+1, self.fcol-self.icol+1))
            for i in range (0,self.fcol-self.icol+1):
                self.voltage[:,i] = np.loadtxt(fname, dtype=float, unpack=True, skiprows=self.iline,
                                              usecols=(self.icol+i))
            
            self.x = np.shape(self.voltage)[0]
            self.y = np.shape(self.voltage)[1]
            _fmax = np.zeros(self.y, dtype = float)
            _tension = np.zeros(self.y, dtype = float)
            self.t = np.linspace(0,self.x/frequency,self.x)
            self.voltage = self.voltage[np.where(self.voltage != 0.000000)[0][0]:self.x,0:self.y]
            self.x = np.shape(self.voltage)[0]
            self.t = self.t[0:self.x]
            self.voltage_fft = np.zeros(self.x*self.y,dtype=complex)
            self.voltage_fft = np.reshape(self.voltage_fft, newshape=(self.x,self.y))
            self.voltage_abs = np.zeros(self.x*self.y,dtype=float)
            self.voltage_abs = np.reshape(self.voltage_abs, newshape=(self.x,self.y))
            for i in range (0,self.y):
                self.voltage_fft[:,i] = fft(self.voltage[:,i])
                self.voltage_abs[:,i] = np.abs(self.voltage_fft[:,i])
                self.f = fftfreq(self.x,self.t[1]-self.t[0])  
                _fmax[i] = self.f[np.where(self.voltage_abs == np.max(self.voltage_abs[2:self.x//2,i]))[0][0]]
                _tension[i] = self.LDensity*(_fmax[i]*2*self.L)**2 
                self.peaks, _ = find_peaks(self.voltage_abs[:self.x//2,i], height = 2)
            _resultT = '{:.2f}'.format(_tension[0])  
            _resultF = '{:.2f}'.format(_fmax[0])    
            self.ui.le_mech_tension.setText(_resultT)
            self.ui.le_frequency.setText(_resultF)
            
            self.plot()   
            _QApplication.processEvents()        
                      
             
            return _QMessageBox.information(self, "Information",
                                             "Measurement Finished",
                                              _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
        
    def closest(self, num, arr):
        curr = arr[0]
        for index in range (len (arr)):
            if abs (num - arr[index]) <= abs (num - curr):
                curr = arr[index]
        if abs(curr - num) <= 0.5: 
            return curr      
        else:
            return False
        
    def start_meas_mode2_1(self):
        """Download a file from the controller via sftp.
        Returns:
            True if operation completed successfully;
            False otherwise."""
        try:
            self.ppmac.send('cd /tmp \n')
            self.ppmac.send('./SampleVMap207_v3 \n')
            self.sleep(self.ui.dsb_time.value())
            self.ppmac.send('\x03 \n')
            self.sleep(0.4)
            remotepath = '/tmp/Gustavo.csv'
            localpath = self.ui.le_outputname.text()
            self.sftp = self.ssh.open_sftp()
            self.get = self.sftp.get(remotepath, localpath)
            self.sleep(0.3)
            
            """Load Voltage file.
        Returns:
            True if operation completed successfully;
            False otherwise."""
            self.peaks = []
            self.peaks_2 = []
            self.L = self.ui.dsb_length.value()
            self.density = self.ui.dsb_density.value()
            self.diameter = self.ui.dsb_diameter.value()
            self.LDensity = (self.density*np.pi*(self.diameter)**2)/4
            self.fname = r"{}".format(localpath)
            self.iline = 0 
            self.fline= int(10*self.ui.dsb_numsample.value() - 1)
            self.icol=1
            self.fcol= int(self.ui.dsb_numchannels.value())
            self.frequency = int(self.ui.dsb_frequency.value())
            i=0
            self.voltage = np.zeros((self.fline-self.iline+1)*(self.fcol-self.icol+1), dtype = float)
            self.voltage = np.reshape(self.voltage, newshape=(self.fline-self.iline+1, self.fcol-self.icol+1))
            for i in range (0,self.fcol-self.icol+1):
                self.voltage[:,i] = np.loadtxt(self.fname, dtype=float, unpack=True, skiprows=self.iline,
                                              usecols=(self.icol+i))
            
            self.x = np.shape(self.voltage)[0]
            self.y = np.shape(self.voltage)[1]
          
            self.t = np.linspace(0,self.x/self.frequency,self.x)
            self.voltage = self.voltage[np.where(self.voltage != 0.000000)[0][0]:self.x,0:self.y]
            self.x = np.shape(self.voltage)[0]
            self.t = self.t[0:self.x]
            self.voltage_fft = np.zeros(self.x*self.y,dtype=complex)
            self.voltage_fft = np.reshape(self.voltage_fft, newshape=(self.x,self.y))
            self.voltage_abs = np.zeros(self.x*self.y,dtype=float)
            self.voltage_abs = np.reshape(self.voltage_abs, newshape=(self.x,self.y))
            for i in range (0,self.y):
                self.voltage_fft[:,i] = fft(self.voltage[:,i])
                self.voltage_abs[:,i] = np.abs(self.voltage_fft[:,i])
                self.f = fftfreq(self.x,self.t[1]-self.t[0])  
                self.peaks, _ = find_peaks(self.voltage_abs[:self.x//2,i], height = 2)
             
            _QMessageBox.information(self, "Information",
                                            "Click to continue the measurement",
                                            _QMessageBox.Ok)
            
            #_QMessageBox.buttonClicked.connect(self.start_meas_mode2_2)
            self.start_meas_mode2_2()
            
            #_QMessageBox.exec_()
            self.plot()   
            _QApplication.processEvents()
            
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
            
    def start_meas_mode2_2(self):  
        try:        
            self.ppmac.send('cd /tmp \n')
            self.ppmac.send('./SampleVMap207_v3 \n')
            self.sleep(self.ui.dsb_time.value())
            self.ppmac.send('\x03 \n')
            self.sleep(0.4)
            remotepath = '/tmp/Gustavo.csv'
            localpath = self.ui.le_outputname.text()
            self.sftp = self.ssh.open_sftp()
            self.get = self.sftp.get(remotepath, localpath)
            self.sleep(0.3)
            i=0
            self.voltage2 = np.zeros((self.fline-self.iline+1)*(self.fcol-self.icol+1), dtype = float)
            self.voltage2 = np.reshape(self.voltage2, newshape=(self.fline-self.iline+1, self.fcol-self.icol+1))
            
            _fmax = np.zeros(self.y, dtype = float)
            _tension = np.zeros(self.y, dtype = float)
            for i in range (0,self.fcol-self.icol+1):
                self.voltage2[:,i] = np.loadtxt(self.fname, dtype=float, unpack=True, skiprows=self.iline,
                                              usecols=(self.icol+i))
            self.x2 = np.shape(self.voltage2)[0]
            self.y2 = np.shape(self.voltage2)[1]
            self.t2 = np.linspace(0,self.x2/self.frequency,self.x2)
            self.voltage2 = self.voltage2[np.where(self.voltage2 != 0.000000)[0][0]:self.x2,0:self.y2]
            self.x2 = np.shape(self.voltage2)[0]
            self.t2 = self.t2[0:self.x2]
            self.voltage_fft2 = np.zeros(self.x2*self.y2,dtype=complex)
            self.voltage_fft2 = np.reshape(self.voltage_fft2, newshape=(self.x2,self.y2))
            self.voltage_abs2 = np.zeros(self.x2*self.y2,dtype=float)
            self.voltage_abs2 = np.reshape(self.voltage_abs2, newshape=(self.x2,self.y2))
            for i in range (0,self.y2):
                self.voltage_fft2[:,i] = fft(self.voltage2[:,i])
                self.voltage_abs2[:,i] = np.abs(self.voltage_fft2[:,i])
                self.f2 = fftfreq(self.x2,self.t2[1]-self.t2[0])  
            self.fpeaks = np.zeros(np.shape(self.peaks)[0]) 
            self.index = np.zeros(np.shape(self.peaks)[0],dtype = int) 
            
            for i in range (0,np.shape(self.peaks)[0]):
                self.fpeaks[i] = self.closest(self.f[self.peaks[i]], self.f2[0:self.x2//2])
                self.index[i] = np.where(self.f2 == self.fpeaks[i])[0]
            self.voltage_abs2[self.index] = 0
            for i in range (0,np.shape(self.peaks)[0]):
                self.voltage_abs2[np.where(np.logical_and(self.f2 >= self.f2[self.index[i]] - 1, self.f2 <= self.f2[self.index[i]] + 1))] = 0
            for i in range (0,self.y2):
                _fmax[i] = self.f[np.where(self.voltage_abs2 == np.max(self.voltage_abs2[2:self.x//2,i]))[0][0]]
                _tension[i] = self.LDensity*(_fmax[i]*2*self.L)**2 
                self.peaks_2, _ = find_peaks(self.voltage_abs2[:self.x//2,i], height = 2)         
            _resultT = '{:.2f}'.format(_tension[0])  
            _resultF = '{:.2f}'.format(_fmax[0])    
            self.ui.le_mech_tension.setText(_resultT)
            self.ui.le_frequency.setText(_resultF)
            
       
           
             
            return _QMessageBox.information(self, "Information",
                                             "Measurement Finished",
                                              _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def disconnect_ueipac(self):
        """Disconnect the controller.
        Returns:
            True if operation completed successfully;
            False otherwise."""

        try:
            
            self.ppmac.close()
            self.ssh.close()
            self.sftp.close()
            return _QMessageBox.information(self, "Information",
                                             "Desconnection was successful",
                                              _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
    
    def config_ueipac(self):
        """Write input parameters UEIPAC controller.
        Returns:
            True if operation completed successfully;
            False otherwise."""
        
        try:
            self.n = []
            Channel0 = None 
            Channel1 = None 
            Channel2 = None 
            Channel3 = None
            Channel4 = None 
            Channel5 = None 
            Channel6 = None
            Channel7 = None
            Channel8 = None 
            Channel9 = None
            Channel10 = None 
            Channel11 = None
            Channel12 = None 
            Channel13 = None 
            Channel14 = None 
            Channel15 = None
            self.device = '0'
            self.numChannels = int(self.ui.dsb_numchannels.value())
            self.frequency = self.ui.dsb_frequency.value()
            self.trigger = '0'
            self.numSamplePerChannels = int(self.ui.dsb_numsample.value())
            self.regenerate = '0'
            self.gain = int(self.ui.cmb_gain.currentIndex())
            filepath = __file__
            filepath = filepath.replace('ueipacwidget.py','')
            file = open(filepath + "input.txt", 'w')
            if self.ui.cb_channel0.isChecked():
                Channel0 = '0'
                self.n = np.append(self.n,"0")
            if self.ui.cb_channel1.isChecked():
                Channel1 = '1'   
                self.n = np.append(self.n,"1")
            if self.ui.cb_channel2.isChecked():
                Channel2 = '2'    
                self.n = np.append(self.n,"2")
            if self.ui.cb_channel3.isChecked():
                Channel3 = '3'
                self.n = np.append(self.n,"3")
            if self.ui.cb_channel4.isChecked():
                Channel4 = '4' 
                self.n = np.append(self.n,"4")
            if self.ui.cb_channel5.isChecked():
                Channel5 = '5' 
                self.n = np.append(self.n,"5")
            if self.ui.cb_channel6.isChecked():
                Channel6 = '6' 
                self.n = np.append(self.n,"6")
            if self.ui.cb_channel7.isChecked():
                Channel7 = '7' 
                self.n = np.append(self.n,"7")
            if self.ui.cb_channel8.isChecked():
                Channel8 = '8' 
                self.n = np.append(self.n,"8")
            if self.ui.cb_channel9.isChecked():
                Channel9 = '9'
                self.n = np.append(self.n,"9")  
            if self.ui.cb_channel10.isChecked():
                Channel10 = '10' 
                self.n = np.append(self.n,"10")
            if self.ui.cb_channel11.isChecked():
                Channel11 = '11' 
                self.n = np.append(self.n,"11")
            if self.ui.cb_channel12.isChecked():
                Channel12 = '12' 
                self.n = np.append(self.n,"12")
            if self.ui.cb_channel13.isChecked():
                Channel13 = '13'  
                self.n = np.append(self.n,"13") 
            if self.ui.cb_channel14.isChecked():
                Channel14 = '14' 
                self.n = np.append(self.n,"14")
            if self.ui.cb_channel15.isChecked():
                Channel15 = '15'       
                self.n = np.append(self.n,"15")
            params = ["{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\
                      \n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}"
                      .format(self.device, self.numChannels, self.frequency, self.trigger,
                              self.numSamplePerChannels, self.regenerate, self.gain, Channel0,\
                              Channel1, Channel2, Channel3, Channel4, Channel5,\
                              Channel6, Channel7, Channel8, Channel9, Channel10,\
                              Channel11, Channel12, Channel13, Channel14, Channel15)]
            file.writelines(params)
            file.close() #to change file access modes
            
            """Upload a file from the computer to controller via sftp.
        Returns:
            True if operation completed successfully;
            False otherwise."""
            self.remotepath = "/tmp/input.txt"
            self.localpath = filepath + "input.txt"
            self.sftp = self.ssh.open_sftp()
            self.put = self.sftp.put(self.localpath, self.remotepath)
            return _QMessageBox.information(self, "Information",
                                             "Configuration was successful",
                                              _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

        


    def set_pyplot(self):
        """Configures plot widget"""
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        _toolbar = _NavigationToolbar(self.canvas, self)

        _layout = _QVBoxLayout()
        _layout.addWidget(self.canvas)
        _layout.addWidget(_toolbar)

        self.wg_plot.setLayout(_layout)


    def plot(self):
        """Plots measurement data.

        Args:
            plot_from_measurementwidget (bool): flag indicating wether to get
            measruement data and configurations from measurement widget (if
            True) or analysis widget (if False, default)."""
        try:
            print("entrou")
            self.canvas.axes.cla()
            #self.canvas.tight_layout()
            self.canvas.axes.grid(True)
            
            if self.ui.cmb_mode.currentIndex() == 1:
                print("fft1")
                if self.ui.cmb_plot.currentIndex() == 0:
                    print("voltage")
                    for i in range(self.y2):
                        self.canvas.axes.plot(self.f2[10:self.x2//2], self.voltage_abs2[10:self.x2//2, i], label = "Channel {}" .format(self.n))
                        self.canvas.axes.plot(self.f2[self.peaks_2], self.voltage_abs2[self.peaks_2], "x" ,label = "Channel {}" .format(self.n))
                    self.canvas.axes.set_xlabel('Frequency [Hz]')
                    self.canvas.axes.set_ylabel('Intensity [u.a.]')
                    self.canvas.draw()

                elif self.ui.cmb_plot.currentIndex() == 1:
                    for i in range(self.y2):
                        self.canvas.axes.plot(self.t2, self.voltage2[:, i], label = "Channel {}" .format(self.n))
                    self.canvas.axes.set_xlabel('Time [s]')
                    self.canvas.axes.set_ylabel('Voltage [V]')
                    self.canvas.draw()
                    
            elif self.ui.cmb_mode.currentIndex() == 0:
                if self.ui.cmb_plot.currentIndex() == 0:
                    for i in range(self.y):
                        self.canvas.axes.plot(self.f[10:self.x//2], self.voltage_abs[10:self.x//2, i], label = "Channel {}" .format(self.n))
                        self.canvas.axes.plot(self.f[self.peaks], self.voltage_abs[self.peaks], "x" ,label = "Channel {}" .format(self.n))
                    self.canvas.axes.set_xlabel('Frequency [Hz]')
                    self.canvas.axes.set_ylabel('Intensity [u.a.]')
                    self.canvas.draw()

                elif self.ui.cmb_plot.currentIndex() == 1:
                    for i in range(self.y):
                        self.canvas.axes.plot(self.t, self.voltage[:, i], label = "Channel {}" .format(self.n))
                    self.canvas.axes.set_xlabel('Time [s]')
                    self.canvas.axes.set_ylabel('Voltage [V]')
                    self.canvas.draw()
            # e 
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            


