"""Delta Sabia Undulator control"""

import os as _os
import sys as _sys
import numpy as _np
import time as _time
import traceback as _traceback
from epics import caget, caput

import collections as _collections
import imautils.db.database as _database

from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QApplication as _QApplication,
    QTableWidgetItem as _QTableWidgetItem,
    QMessageBox as _QMessageBox,
    )


class UndulatorPosCfg(_database.DatabaseAndFileDocument):
    """Read, write and store undulator position configuration."""

    database_name = 'UndulatorPosCfg'
    label = 'UndulatorPosCfg'
    collection_name = 'undulator_pos_cfg'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True, 'unique': True}),
        ('positions', {'field': 'positions', 'dtype': str, 'not_null': True}),
    ])

    def __init__(
            self, database_name=database_name, mongo=False, server=None):
        """Initialize object.

        Args:
            filename (str): connection configuration filepath.
            database_name (str): database file path (sqlite) or name (mongo).
            idn (int): id in database table (sqlite) / collection (mongo).
            mongo (bool): flag indicating mongoDB (True) or sqlite (False).
            server (str): MongoDB server.

        """
        super().__init__(
            database_name=database_name, mongo=mongo, server=server)
        self.database_name = database_name + '.db'

    def update_db_name_list(self, cmb):
        """Updates a db name list on a combobox.

        Args:
            Db (DatabaseAndFileDocument): database instance;
            cmb (QComboBox): QComboBox instance.
        """
        try:
            self.db_update_database(
                database_name=self.database_name,
                mongo=_QApplication.instance().mongo,
                server=_QApplication.instance().server)
            names = self.db_get_values('name')

            current_text = cmb.currentText()
            cmb.clear()
            cmb.addItems([name for name in names])
            if len(current_text) == 0:
                cmb.setCurrentIndex(cmb.count()-1)
            else:
                cmb.setCurrentText(current_text)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def create_database(self):
        """Create database and tables."""
        # print(_os.path.dirname(_os.path.abspath(__file__)))
        status = self.db_create_collection()
        if not status:
            raise Exception("Failed to create database.")


class UndulatorControl():
    """Delta Sabia Undulator control class."""
    def __init__(self, virtual=False):
        self.init_pvs(virtual)
        self.cfg = UndulatorPosCfg()

    def init_pvs(self, virtual=False):
        self.prefix = 'delta:mod01:'

        # Status PVs
        self.pv_coup_sts = self.prefix + 'Coup-Sts'
        self.pv_trig_type_sts = self.prefix + 'TrigType-Sts'
        self.pv_ref_type_sts = self.prefix + 'RefType-Sts'
        self.pv_mirror_sts = self.prefix + 'Mirror-Sts'

        # Monitor PVs
        self.pv_ext_trig_mon = self.prefix + 'ExtTrig-Mon'
        self.pv_soft_trig_mon = self.prefix + 'SoftTrig-Mon'
        self.pv_motion_state_mon = self.prefix + 'MotionState-Mon'
        self.pv_CID_motion_state_mon = self.prefix + 'CIDMotionState-Mon'
        self.pv_CIE_motion_state_mon = self.prefix + 'CIEMotionState-Mon'
        self.pv_CSD_motion_state_mon = self.prefix + 'CSDMotionState-Mon'
        self.pv_CSE_motion_state_mon = self.prefix + 'CSEMotionState-Mon'
        self.pv_enbl_mon = self.prefix + 'Enbl-Mon'
        self.pv_state_idx_mon = self.prefix + 'StateIdx-Mon'

        self.pv_CID_actual_pos_mon = self.prefix + 'CIDPhyPos-Mon'
        self.pv_CIE_actual_pos_mon = self.prefix + 'CIEPhyPos-Mon'
        self.pv_CSD_actual_pos_mon = self.prefix + 'CSDPhyPos-Mon'
        self.pv_CSE_actual_pos_mon = self.prefix + 'CSEPhyPos-Mon'

        self.pv_CID_actual_velo_mon = self.prefix + 'CIDPhyVelo-Mon'
        self.pv_CIE_actual_velo_mon = self.prefix + 'CIEPhyVelo-Mon'
        self.pv_CSD_actual_velo_mon = self.prefix + 'CSDPhyVelo-Mon'
        self.pv_CSE_actual_velo_mon = self.prefix + 'CSEPhyVelo-Mon'

        if virtual:
            self.pv_CID_actual_pos_mon = self.prefix + 'CIDVirtPos-Mon'
            self.pv_CIE_actual_pos_mon = self.prefix + 'CIEVirtPos-Mon'
            self.pv_CSD_actual_pos_mon = self.prefix + 'CSDVirtPos-Mon'
            self.pv_CSE_actual_pos_mon = self.prefix + 'CSEVirtPos-Mon'

            self.pv_CID_actual_velo_mon = self.prefix + 'CIDVirtVelo-Mon'
            self.pv_CIE_actual_velo_mon = self.prefix + 'CIEVirtVelo-Mon'
            self.pv_CSD_actual_velo_mon = self.prefix + 'CSDVirtVelo-Mon'
            self.pv_CSE_actual_velo_mon = self.prefix + 'CSEVirtVelo-Mon'

        self.pv_CID_pos_err_mon = self.prefix + 'CIDPosErr-Mon'
        self.pv_CIE_pos_err_mon = self.prefix + 'CIEPosErr-Mon'
        self.pv_CSD_pos_err_mon = self.prefix + 'CSDPosErr-Mon'
        self.pv_CSE_pos_err_mon = self.prefix + 'CSEPosErr-Mon'

        self.pv_CID_pos_lim_mon = self.prefix + 'CIDPosLimSw-Mon'
        self.pv_CIE_pos_lim_mon = self.prefix + 'CIEPosLimSw-Mon'
        self.pv_CSD_pos_lim_mon = self.prefix + 'CSDPosLimSw-Mon'
        self.pv_CSE_pos_lim_mon = self.prefix + 'CSEPosLimSw-Mon'
        self.pv_CID_neg_lim_mon = self.prefix + 'CIDNegLimSw-Mon'
        self.pv_CIE_neg_lim_mon = self.prefix + 'CIENegLimSw-Mon'
        self.pv_CSD_neg_lim_mon = self.prefix + 'CSDNegLimSw-Mon'
        self.pv_CSE_neg_lim_mon = self.prefix + 'CSENegLimSw-Mon'

        self.pv_CID_pos_kill_mon = self.prefix + 'CIDPosKillSw-Mon'
        self.pv_CIE_pos_kill_mon = self.prefix + 'CIEPosKillSw-Mon'
        self.pv_CSD_pos_kill_mon = self.prefix + 'CSDPosKillSw-Mon'
        self.pv_CSE_pos_kill_mon = self.prefix + 'CSEPosKillSw-Mon'
        self.pv_CID_neg_kill_mon = self.prefix + 'CIDNegKillSw-Mon'
        self.pv_CIE_neg_kill_mon = self.prefix + 'CIENegKillSw-Mon'
        self.pv_CSD_neg_kill_mon = self.prefix + 'CSDNegKillSw-Mon'
        self.pv_CSE_neg_kill_mon = self.prefix + 'CSENegKillSw-Mon'

        self.pv_CID_enbl_mon = self.prefix + 'CIDEnbl-Mon'
        self.pv_CIE_enbl_mon = self.prefix + 'CIEEnbl-Mon'
        self.pv_CSD_enbl_mon = self.prefix + 'CSDEnbl-Mon'
        self.pv_CSE_enbl_mon = self.prefix + 'CSEEnbl-Mon'

        # Selection PVs
        self.pv_coup_sel = self.prefix + 'Coup-Sel'
        self.pv_trig_type_sel = self.prefix + 'TrigType-Sel'
        self.pv_ref_type_sel = self.prefix + 'RefType-Sel'
        self.pv_mirror_sel = self.prefix + 'Mirror-Sel'

        # Configuration PVs
        self.pv_rel_pos_sp = self.prefix + 'RelPos-SP'  # [mm]
        self.pv_rel_pos_rb = self.prefix + 'RelPos-RB'  # [mm]
        self.pv_velo_sp = self.prefix + 'Velo-SP'  # [mm/s]
        self.pv_velo_rb = self.prefix + 'Velo-RB'  # [mm/s]
        self.pv_mov_time_sp = self.prefix + 'MovTime-SP'
        self.pv_mov_time_rb = self.prefix + 'MovTime-RB'
        self.pv_acc_sp = self.prefix + 'Acc-SP'
        self.pv_acc_rb = self.prefix + 'Acc-RB'
        self.pv_decel_sp = self.prefix + 'Decel-SP'
        self.pv_decel_rb = self.prefix + 'Decel-RB'

        # Command PVs
        self.pv_soft_trig_cmd = self.prefix + 'SoftTrig-Cmd'
        self.pv_stop_cmd = self.prefix + 'Stop-Cmd'
        self.pv_rst_cmd = self.prefix + 'Rst-Cmd'

        # Machine state index dict
        self.state_idx_dict = {1: 'Undefined',
                               2: 'Clearing',
                               4: 'Stopped',
                               8: 'Starting',
                               16: 'Idle',
                               32: 'Suspended',
                               64: 'Execute',
                               128: 'Stopping',
                               256: 'Aborting',
                               512: 'Aborted',
                               1024: 'Holding',
                               2048: 'Held',
                               4096: 'Unholding',
                               8192: 'Suspending',
                               16384: 'Unsuspending',
                               32768: 'Resetting',
                               65536: 'Completing',
                               131072: 'Complete',
                               }

    def reset_motor(self):
        caput(self.pv_rst_cmd, 1)

    def stop(self):
        caput(self.pv_stop_cmd, 1)

    def home_motors(self):
        """Sends all cassettes to position 0 mm."""
        current_pos = self.read_encoder()

        # Home CSD
        self.configure_move(coup=6, rel_pos=-1*current_pos[0])
        self.move_until_stops()

        # Home CSE
        self.configure_move(coup=7, rel_pos=-1*current_pos[1])
        self.move_until_stops()

        # Home CIE
        self.configure_move(coup=8, rel_pos=-1*current_pos[2])
        self.move_until_stops()

        # Home CID
        self.configure_move(coup=9, rel_pos=-1*current_pos[3])
        self.move_until_stops()

    def move_until_stops(self):
        """Trigs movements and waits all motors to stop."""
        self.stop()
        _time.sleep(0.5)
        self.reset_motor()
        _time.sleep(0.5)
        # checks distance errors
        error, vel = self.check_distance_error()

        # triggers movement
        self.trig_move()
        _time.sleep(0.3)
        self.wait_until_stops()

        if error:
            caput(self.pv_velo_sp, vel)
            self.stop()

    def move_all(self, pos=0):
        """Moves all cassettes to a relative position.

        Args:
            phase (float): phase relative position change in [mm]."""
        self.configure_move(coup=1, rel_pos=pos)
        self.move_until_stops()

    def move_phase(self, phase=0, mirror=0):
        """Moves cassettes in phase mode to a relative position.

        Args:
            phase (float): phase relative position change in [mm];
            mirror (int): 0 moves CSE, CID;
                          1 moves CSD, CIE."""
        self.configure_move(coup=2, mirror=mirror, rel_pos=phase)
        self.move_until_stops()

    def move_counterphase(self, counterphase=0, mirror=0):
        """Moves cassettes in counterphase mode to a relative position.

        Args:
            counterphase (float): counterphase relative position
                                  change in [mm]."""
        self.configure_move(coup=3, mirror=mirror, rel_pos=counterphase)
        self.move_until_stops()

    def move_gv(self, gv=0, mirror=0):
        """Moves cassettes in gv mode to a relative position.

        Args:
            gv (float): gv relative position change in [mm]."""
        self.configure_move(coup=4, mirror=mirror, rel_pos=gv)
        self.move_until_stops()

    def move_gh(self, gh=0, mirror=0):
        """Moves cassettes in gh mode to a relative position.

        Args:
            gh (float): gh relative position change in [mm]."""
        self.configure_move(coup=5, mirror=mirror, rel_pos=gh)
        self.move_until_stops()

    def move_csd(self, pos=0):
        """Moves CSD in to a relative position.

        Args:
            pos (float): CSD relative position change in [mm]."""
        self.configure_move(coup=6, rel_pos=pos)
        self.move_until_stops()

    def move_cse(self, pos=0):
        """Moves CSE in to a relative position.

        Args:
            pos (float): CSE relative position change in [mm]."""
        self.configure_move(coup=7, rel_pos=pos)
        self.move_until_stops()

    def move_cie(self, pos=0):
        """Moves CIE in to a relative position.

        Args:
            pos (float): CIE relative position change in [mm]."""
        self.configure_move(coup=8, rel_pos=pos)
        self.move_until_stops()

    def move_cid(self, pos=0):
        """Moves CSD in to a relative position.

        Args:
            pos (float): CSD relative position change in [mm]."""
        self.configure_move(coup=9, rel_pos=pos)
        self.move_until_stops()

    def go_to_phase_abs(self, phase=0, counterphase=0, gv=0, gh=0):
        """Sends all cassettes to zero, then positions them at the chose phase.

            Args:
                phase (float): phase absolute position in [mm];
                counterphase (float): counterphase absolute position in [mm];
                gv (float): gv absolute position in [mm];
                gh (float): gh absolute position in [mm]."""

        self.home_motors()
        if phase != 0:
            self.move_phase(phase)
        if counterphase != 0:
            self.move_counterphase(counterphase)
        if gv != 0:
            self.move_gv(gv)
        if gh != 0:
            self.move_gh(gh)

        # check status

    def read_encoder(self):
        """Read encoder positions.
        Returns:
                positions (list): list containing CSD, CSE, CIE and CID
                                  positions respectively."""
        pos_CSD = caget(self.pv_CSD_actual_pos_mon)
        pos_CSE = caget(self.pv_CSE_actual_pos_mon)
        pos_CIE = caget(self.pv_CIE_actual_pos_mon)
        pos_CID = caget(self.pv_CID_actual_pos_mon)

        return [pos_CSD, pos_CSE, pos_CIE, pos_CID]

    def configure_move(self, coup=0, mirror=0, trig_type=0,
                       rel_pos=0, velo=2, acc=1000, decel=1000):
        """Configures the undulator movements."""
        # -> Coup
        #     0 - Uncouple
        #     1 - All
        #     2 - Phase
        #     3 - Counterphase
        #     4 - GV
        #     5 - GH
        #     6 - CSD
        #     7 - CSE
        #     8 - CIE
        #     9 - CID

        # -> TrigType 0
        #     1 sw
        #     2 hw
        # -> RefType 0 - não implementado

        # Write values
        caput(self.pv_coup_sel, coup)
        caput(self.pv_mirror_sel, mirror)
        caput(self.pv_trig_type_sel, trig_type)
        caput(self.pv_rel_pos_sp, rel_pos)
        caput(self.pv_velo_sp, velo)
        caput(self.pv_acc_sp, acc)
        caput(self.pv_decel_sp, decel)

        # Read and check values
        if all([caget(self.pv_coup_sts) - coup == 0,
                caget(self.pv_mirror_sts) - mirror == 0,
                caget(self.pv_trig_type_sel) - trig_type == 0,
                caget(self.pv_rel_pos_rb) - rel_pos == 0,
                caget(self.pv_velo_rb) - velo == 0,
                caget(self.pv_acc_rb) - acc == 0,
                caget(self.pv_decel_rb) - decel == 0]):
            return True

        else:
            return False

    def trig_move(self):
        """Triggers the configured undulator movement."""
        caput(self.pv_soft_trig_cmd, 1)
        # -> rst
        # -> softtrig
        # -> trigtype

    def wait_until_stops(self):
        """Holds until the undulator stops moving."""
        while(self.query_moving()):
            _time.sleep(0.5)
        print(self.read_encoder())

    def check_distance_error(self):
        """Checks the relative distance the cassettes must travel in order
        to correct a firmware bug which causes errors if it takes less than 1s
        to move.
            Args:
                distance (float): relative distance in mm.
            Returns:
                Error (bool): True if the distance will cause error and the
                    velocity was set to be lower, False otherwise;
                vel (float): original velocity (used in order to set the
                    original velocity after a movement with distance error)."""
        distance = caget(self.pv_rel_pos_rb)
        vel = caget(self.pv_velo_rb)  # mm/s
        travel_time = abs(distance/vel)
        if travel_time < 1:
            # sets speed to take 2s to complete the movement
            vel_slower = distance/2
            caput(self.pv_velo_sp, vel_slower)
            return True, vel

        return False, vel

    def query_moving(self):
        """Returns True if any cassette is moving, False otherwise."""
        # return any([caget(self.pv_CSD_motion_state_mon) == 1,
        #             caget(self.pv_CSE_motion_state_mon) == 1,
        #             caget(self.pv_CIE_motion_state_mon) == 1,
        #             caget(self.pv_CID_motion_state_mon) == 1])
        state = self.state_idx_dict[caget(self.pv_state_idx_mon)]
        moving_states = ['Starting', 'Stopping', 'Aborting', 'Completing']

        return state in moving_states

    def check_connection(self):
        """Checks if the undulator is connected.

        Returns:
            Status (bool): True if connected, False otherwise."""
        try:
            state = caget(self.pv_state_idx_mon)
            if state is None:
                return False
            return True
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def get_status(self):
        """Returns a dict with the undulator status."""
        """Returns dictionary containing undulator status."""
        status_dict = {
            'state_idx': caget(self.pv_state_idx_mon),
            'enable_mon': caget(self.pv_enbl_mon),
            'CSD_enable': caget(self.pv_CSD_enbl_mon),
            'CSE_enable': caget(self.pv_CSE_enbl_mon),
            'CIE_enable': caget(self.pv_CIE_enbl_mon),
            'CID_enable': caget(self.pv_CID_enbl_mon),
            'CID_motion_state': caget(self.pv_CID_motion_state_mon),
            'CIE_motion_state': caget(self.pv_CIE_motion_state_mon),
            'CSE_motion_state': caget(self.pv_CSE_motion_state_mon),
            'CSD_motion_state': caget(self.pv_CSD_motion_state_mon),
            'CSD_pos_err': caget(self.pv_CSD_pos_err_mon),
            'CSE_pos_err': caget(self.pv_CSE_pos_err_mon),
            'CIE_pos_err': caget(self.pv_CIE_pos_err_mon),
            'CID_pos_err': caget(self.pv_CID_pos_err_mon),
            'CSD_pos_lim': caget(self.pv_CSD_pos_lim_mon),
            'CSE_pos_lim': caget(self.pv_CSE_pos_lim_mon),
            'CIE_pos_lim': caget(self.pv_CIE_pos_lim_mon),
            'CID_pos_lim': caget(self.pv_CID_pos_lim_mon),
            'CSD_neg_lim': caget(self.pv_CSD_neg_lim_mon),
            'CSE_neg_lim': caget(self.pv_CSE_neg_lim_mon),
            'CIE_neg_lim': caget(self.pv_CIE_neg_lim_mon),
            'CID_neg_lim': caget(self.pv_CID_neg_lim_mon),
            'CSD_pos_kill': caget(self.pv_CSD_pos_kill_mon),
            'CSE_pos_kill': caget(self.pv_CSE_pos_kill_mon),
            'CIE_pos_kill': caget(self.pv_CIE_pos_kill_mon),
            'CID_pos_kill': caget(self.pv_CID_pos_kill_mon),
            'CSD_neg_kill': caget(self.pv_CSD_neg_kill_mon),
            'CSE_neg_kill': caget(self.pv_CSE_neg_kill_mon),
            'CIE_neg_kill': caget(self.pv_CIE_neg_kill_mon),
            'CID_neg_kill': caget(self.pv_CID_neg_kill_mon),
            }

        return status_dict
        # Status:
        #     -> RelPos? (somente relativa? ou abs?)


class Utils():
    """Undulator control utils."""
    def __init__(self):
        pass

    def save_cfg(self, cfg):
        """Saves current ui configuration into database."""
        try:
            cfg.db_update_database(
                        cfg.database_name,
                        mongo=cfg.mongo, server=cfg.server)
            cfg.db_save()
            # _QMessageBox.information(self, 'Information',
            #                          'Configuration Saved.',
            #                          _QMessageBox.Ok)
            return True
        except Exception:
            # _QMessageBox.warning(self, 'Information',
            #                      'Failed to save this configuration.',
            #                      _QMessageBox.Ok)
            # _traceback.print_exc(file=_sys.stdout)
            raise
            return False

    def load_cfg(self, cfg, name):
        """Load configuration from database."""
        try:
            cfg.db_update_database(
                cfg.database_name,
                mongo=cfg.mongo, server=cfg.server)
            _id = cfg.db_search_field('name', name)[0]['id']
            cfg.db_read(_id)
            # _QMessageBox.information(self, 'Information',
            #                          'Configuration Loaded.',
            #                          _QMessageBox.Ok)
            return True
        except Exception:
            # _QMessageBox.warning(self, 'Information',
            #                      'Failed to load this configuration.',
            #                      _QMessageBox.Ok)
            # _traceback.print_exc(file=_sys.stdout)
            raise
            return False

    def table_to_str(self, tw):
        """Returns tableWidget position configurations in a string."""
        try:
            _tw = tw
            _ncells = _tw.rowCount()
            _pos_str = ''
            if _ncells > 0:
                for i in range(_ncells):
                    _tw.setCurrentCell(i, 0)
                    if _tw.currentItem() is not None:
                        _pos_str += str(_tw.currentItem().text()) + ':'
                    _tw.setCurrentCell(i, 1)
                    if _tw.currentItem() is not None:
                        _pos_str += str(_tw.currentItem().text()) + '\n'
                return _pos_str
            else:
                return ''
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            # _QMessageBox.warning(self, 'Warning',
            #                      'Could not convert table to string.\n'
            #                      'Check if all inputs are numbers.',
            #                      _QMessageBox.Ok)

    def str_to_table(self, cfg, tw):
        """Inserts position configuration values into tableWidget."""
        try:
            _tw = tw
            _ncells = _tw.rowCount()
            _string = cfg.positions
            _pos_list = _string.split('\n')[:-1]
            if _ncells > 0:
                self.clear_table(_tw)
            for i in range(len(_pos_list)):
                _idx, _str = _pos_list[i].split(':')
                _tw.insertRow(i)
                _item0 = _QTableWidgetItem()
                _item1 = _QTableWidgetItem()
                _tw.setItem(i, 0, _item0)
                _item0.setText(_idx)
                _tw.setItem(i, 1, _item1)
                _item1.setText(_str)
                _QApplication.processEvents()
                _time.sleep(0.01)
            return True
        except Exception:
            raise
            # _traceback.print_exc(file=_sys.stdout)
            # _QMessageBox.warning(self, 'Warning',
            #                      'Could not insert array values into table.',
            #                      _QMessageBox.Ok)
            return False

    def get_pos_cfg_dict(self, cfg):
        """Returns a dict containg all the position configurations.
            Args:
                cfg (UndulatorPosCfg): undulator position configuration data.
            Returns:
                pos_cfg_dict (dict): dictionary containing all the position
                    configurations. The dict key is the configurarition index
                    and the item contains a list of positions, being
                    pos_cfg_dic[key] = [Phase, CounterPhase, GV, GH]."""
        _pos_cfg_dict = {}
        _pos_cfg_str = cfg.positions
        _pos_list = _pos_cfg_str.split('\n')[:-1]
        for i in range(len(_pos_list)):
            _key, _str = _pos_list[i].split(':')
            _pos = []
            for _p in _str.split(';'):
                _pos.append(float(_p.split('=')[1]))
            _pos_cfg_dict[_key] = _pos

        return _pos_cfg_dict

    def clear_table(self, tw):
        """Clears tableWidget."""
        try:
            _tw = tw
            _tw.clearContents()
            _ncells = _tw.rowCount()
            while _ncells >= 0:
                _tw.removeRow(_ncells)
                _ncells = _ncells - 1
                _QApplication.processEvents()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def warp_measurements(self, und, cfg, measurement_func):  # , meas_cfg):
        try:
            # _name = meas_cfg.name
            # _comments = meas_cfg.comments
            _pos_cfg_dict = self.get_pos_cfg_dict(cfg)
            for key in _pos_cfg_dict.keys():
                pos = _pos_cfg_dict[key]
                und.go_to_phase_abs(pos[0], pos[1], pos[2], pos[3])
                measurement_func()
        except Exception:
            raise
