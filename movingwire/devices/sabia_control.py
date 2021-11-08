"""Delta Sabia Undulator control"""

import os as _os
import sys as _sys
import time as _time
import traceback as _traceback
from epics import caget, caput


class UndulatorControl():
    """Delta Sabia Undulator control class."""
    def __init__(self):
        self.init_pvs()

    def init_pvs(self):
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

        self.pv_CID_actual_pos_mon = self.prefix + 'PhyCIDActualPos-Mon'
        self.pv_CIE_actual_pos_mon = self.prefix + 'PhyCIEActualPos-Mon'
        self.pv_CSD_actual_pos_mon = self.prefix + 'PhyCSDActualPos-Mon'
        self.pv_CSE_actual_pos_mon = self.prefix + 'PhyCSEActualPos-Mon'

        self.pv_phy_CID_actual_velo_mon = self.prefix + 'PhyCIDActualVelo-Mon'
        self.pv_phy_CIE_actual_velo_mon = self.prefix + 'PhyCIEActualVelo-Mon'
        self.pv_phy_CSD_actual_velo_mon = self.prefix + 'PhyCSDActualVelo-Mon'
        self.pv_phy_CSE_actual_velo_mon = self.prefix + 'PhyCSEActualVelo-Mon'

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
        self.pv_rel_pos_sp = self.prefix + 'RelPos-SP'
        self.pv_rel_pos_rb = self.prefix + 'RelPos-RB'
        self.pv_velo_sp = self.prefix + 'Velo-SP'
        self.pv_velo_rb = self.prefix + 'Velo-RB'
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

    def reset_motor(self):
        caput(self.pv_rst_cmd, 1)

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
        self.reset_motor()
        self.trig_move()
        self.wait_until_stops()

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
        caput(self.pv_soft_trig_cmd, 1)
        # -> rst
        # -> softtrig
        # -> trigtype

    def wait_until_stops(self):
        pass

    def status(self):
        pass
        # Status:            
        #     -> Enbl 
        #     -> RelPos? (somente relativa? ou abs?) 
        #     -> PhyCIDActualPos 
        #     -> CIDMotionState 
        #     -> CIDPosErr 
        #     -> CIDPosLimSw 
        #     -> CIDNegLimSw 
        #     -> CIDPosKillSw 
        #     -> CIDNegKillSw 
        #     -> CIDEnbl 
        #
        #     -> StateIdx-Mon