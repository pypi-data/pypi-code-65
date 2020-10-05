""""""
#------------------------------------------------------------------------------
# Description    : Pulsar QCM native interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
#------------------------------------------------------------------------------


#-- include -------------------------------------------------------------------

import sys
import os
import numpy
import struct

#Add SCPI support
from ieee488_2.transport            import transport
from pulsar_qcm.pulsar_qcm_scpi_ifc import pulsar_qcm_scpi_ifc

#-- class ---------------------------------------------------------------------

class pulsar_qcm_ifc(pulsar_qcm_scpi_ifc):

    #--------------------------------------------------------------------------
    def __init__(self, transport_inst, debug = 0):
        """
        Constructor
        """

        #Build information
        self._build = {"version": "0.1.1",
                       "date":    "05/10/2020-11:41:10",
                       "hash":    "0x3E64CB99",
                       "dirty":   False}

        #Initialize parent class.
        super(pulsar_qcm_ifc, self).__init__(transport_inst, debug)

    #--------------------------------------------------------------------------
    def _get_scpi_commands(self):
        """
        Get SCPI commands.
        """

        try:
            #Format command string
            cmds          = super()._get_scpi_commands()
            cmd_elem_list = cmds.split(';')[:-1]
            cmd_list      = numpy.reshape(cmd_elem_list, (int(len(cmd_elem_list) / 9), 9))
            cmd_dict      = {cmd[0]: {"scpi_in_type":    cmd[1].split(',') if cmd[1] != "None" and cmd[1] != "" else [],
                                      "scpi_out_type":   cmd[2].split(',') if cmd[2] != "None" and cmd[2] != "" else [],
                                      "python_func":     cmd[3],
                                      "python_in_type":  cmd[4].split(',') if cmd[4] != "None" and cmd[4] != "" else [],
                                      "python_in_var":   cmd[5].split(',') if cmd[5] != "None" and cmd[5] != "" else [],
                                      "python_out_type": cmd[6].split(',') if cmd[6] != "None" and cmd[6] != "" else [],
                                      "comment":         cmd[8]} for cmd in cmd_list}

            return cmd_dict
        except:
            raise

    #--------------------------------------------------------------------------
    def get_idn(self):
        """
        Get device identity and build information.
        """

        try:
            #Format IDN string
            idn            = super()._get_idn()
            idn_elem_list  = idn.split(',')
            idn_build_list = idn_elem_list[-1].split(' ')
            idn_dict       = {"manufacturer":  idn_elem_list[0],
                              "device":        idn_elem_list[1],
                              "serial_number": idn_elem_list[2],
                              "build":         {"firmware":    {"version": idn_build_list[0].split("=")[-1],
                                                                "date":    idn_build_list[1].split("=")[-1],
                                                                "hash":    idn_build_list[2].split("=")[-1],
                                                                "dirty":   True if int(idn_build_list[3].split("=")[-1]) else False},
                                                "kernel_mod":  {"version": idn_build_list[4].split("=")[-1],
                                                                "date":    idn_build_list[5].split("=")[-1],
                                                                "hash":    idn_build_list[6].split("=")[-1],
                                                                "dirty":   True if int(idn_build_list[7].split("=")[-1]) else False},
                                                "application": {"version": idn_build_list[8].split("=")[-1],
                                                                "date":    idn_build_list[9].split("=")[-1],
                                                                "hash":    idn_build_list[10].split("=")[-1],
                                                                "dirty":   True if int(idn_build_list[11].split("=")[-1]) else False},
                                                "driver":      self._build}}

            return idn_dict
        except:
            raise



    #--------------------------------------------------------------------------
    def get_system_status(self):
        """
        Get general system status.
        """

        try:
            #Format status string
            status           = self._get_system_status()
            status_elem_list = status.split(';')
            status_flag_list = status_elem_list[-1].split(',')[:-1] if status_elem_list[-1] != '' else []
            status_dict      = {"status": status_elem_list[0],
                                "flags":  status_flag_list}
            return status_dict
        except:
            raise

    #--------------------------------------------------------------------------
    def _set_sequencer_program(self, sequencer, program):
        """
        Program sequencer.
        """

        try:
            super()._set_sequencer_program(sequencer, program)
        except:
            print(self.get_assembler_log())
            raise

    @staticmethod
    #--------------------------------------------------------------------------
    def _get_sequencer_cfg_format():
        """
        Get sequencer configuration format
        """

        seq_proc_cfg_format  = '?I'
        awg_cfg_format       = '??IIIIIIIIIII?III??I'
        awg_float_cfg_format = 'ffffff'

        return seq_proc_cfg_format + awg_cfg_format + awg_float_cfg_format

    #--------------------------------------------------------------------------
    def _set_sequencer_config(self, sequencer, cfg_dict):
        """
        Set sequencer configuration.
        """

        try:
            #Get current configuration and merge dictionaries
            cfg_dict = {**self._get_sequencer_config(sequencer), **cfg_dict}

            #Set new configuration
            cfg = [#Sequence processor
                   cfg_dict["sync_en"],                           #Sequence processor synchronization enable
                   0,                                             #Sequence processor program counter start (unused)

                   #AWG
                   cfg_dict["cont_mode_en_awg_path_0"],           #Continuous mode enable for AWG path 0
                   cfg_dict["cont_mode_en_awg_path_1"],           #Continuous mode enable for AWG path 1
                   cfg_dict["cont_mode_waveform_idx_awg_path_0"], #continuous mode waveform index for AWG path 0
                   cfg_dict["cont_mode_waveform_idx_awg_path_1"], #Continuous mode waveform index for AWG path 1
                   cfg_dict["upsample_rate_awg_path_0"],          #Upsample rate for AWG path 0
                   cfg_dict["upsample_rate_awg_path_1"],          #Upsample rate for AWG path 1
                   0,                                             #Gain for AWG path 0         (unused)
                   0,                                             #Gain for AWG path 1         (unused)
                   0,                                             #Offset for AWG path 0       (unused)
                   0,                                             #Offset for AWG path 1       (unused)
                   0,                                             #Phase increment; ultra-fine (unused)
                   0,                                             #Phase increment; fine       (unused)
                   0,                                             #Phase increment; coarse     (unused)
                   0,                                             #Phase increment; sign       (unused)
                   0,                                             #Phase; ultra-fine           (unused)
                   0,                                             #Phase; fine                 (unused)
                   0,                                             #Phase; coarse               (unused)
                   cfg_dict["mod_en_awg"],                        #Modulation enable for AWG paths 0 and 1
                   cfg_dict["mrk_ovr_en"],                        #Marker override enable
                   cfg_dict["mrk_ovr_val"],                       #Marker override value

                   #AWG floating point values to be converted
                   cfg_dict["freq_hz"],                           #Frequency in Hz
                   cfg_dict["phase_degree"],                      #Phase in degrees
                   cfg_dict["gain_awg_path_0_float"],             #Gain for AWG path 0 as float
                   cfg_dict["gain_awg_path_1_float"],             #Gain for AWG path 1 as float
                   cfg_dict["offset_awg_path_0_float"],           #Offset for AWG path 0 as float
                   cfg_dict["offset_awg_path_1_float"]]           #Offset for AWG path 1 as float

            super()._set_sequencer_config(sequencer, struct.pack(pulsar_qcm_ifc._get_sequencer_cfg_format(), *cfg))
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_sequencer_config(self, sequencer):
        """
        Get sequencer configuration.
        """
        try:
            cfg      = struct.unpack(pulsar_qcm_ifc._get_sequencer_cfg_format(), super()._get_sequencer_config(sequencer))
            cfg_dict = {#Sequence processor
                        "sync_en":                           cfg[0],

                        #AWG
                        "cont_mode_en_awg_path_0":           cfg[2],
                        "cont_mode_en_awg_path_1":           cfg[3],
                        "cont_mode_waveform_idx_awg_path_0": cfg[4],
                        "cont_mode_waveform_idx_awg_path_1": cfg[5],
                        "upsample_rate_awg_path_0":          cfg[6],
                        "upsample_rate_awg_path_1":          cfg[7],
                        "mod_en_awg":                        cfg[19],
                        "mrk_ovr_en":                        cfg[20],
                        "mrk_ovr_val":                       cfg[21],

                        #AWG floating point values
                        "freq_hz":                           cfg[22],
                        "phase_degree":                      cfg[23],
                        "gain_awg_path_0_float":             cfg[24],
                        "gain_awg_path_1_float":             cfg[25],
                        "offset_awg_path_0_float":           cfg[26],
                        "offset_awg_path_1_float":           cfg[27]}
            return cfg_dict
        except:
            raise



    #--------------------------------------------------------------------------
    def arm_sequencer(self, sequencer=None):
        """
        Arm sequencer.
        """

        try:
            if sequencer is not None:
                self._arm_sequencer(sequencer)
            else:
                try:
                    #Arm all sequencers (SCPI call)
                    self._write('SEQuencer:ARM')
                except Exception as err:
                    self._check_error_queue(err)
                finally:
                    self._check_error_queue()
        except:
            raise

    #--------------------------------------------------------------------------
    def start_sequencer(self, sequencer=None):
        """
        Start sequencer.
        """

        try:
            if sequencer is not None:
                self._start_sequencer(sequencer)
            else:
                try:
                    #Start all sequencers (SCPI call)
                    self._write('SEQuencer:START')
                except Exception as err:
                    self._check_error_queue(err)
                finally:
                    self._check_error_queue()
        except:
            raise

    #--------------------------------------------------------------------------
    def stop_sequencer(self, sequencer=None):
        """
        Stop sequencer.
        """

        try:
            if sequencer is not None:
                self._stop_sequencer(sequencer)
            else:
                try:
                    #Stop all sequencers (SCPI call)
                    self._write('SEQuencer:STOP')
                except Exception as err:
                    self._check_error_queue(err)
                finally:
                    self._check_error_queue()
        except:
            raise

    #--------------------------------------------------------------------------
    def get_sequencer_state(self, sequencer):
        """
        Get sequencer state.
        """

        try:
            #Format status string
            status           = self._get_sequencer_state(sequencer)
            status_elem_list = status.split(';')
            status_flag_list = status_elem_list[-1].split(',')[:-1] if status_elem_list[-1] != '' else []
            status_dict      = {"status": status_elem_list[0],
                                "flags":  status_flag_list}
            return status_dict
        except:
            raise



    #--------------------------------------------------------------------------
    def _add_awg_waveform(self, sequencer, name, waveform, index=None):
        """
        Add AWG waveform to sequencer.
        """

        try:
            super()._add_awg_waveform(sequencer, 0, name, len(waveform), False)
            self._set_awg_waveform_data(sequencer, name, waveform)
            if index is not None:
                self._set_awg_waveform_index(sequencer, name, index)
        except:
            raise

    #--------------------------------------------------------------------------
    def _delete_awg_waveform(self, sequencer, name):
        """
        Delete AWG waveform from sequencer.
        """

        try:
            super()._delete_awg_waveform(sequencer, 0, name)
        except:
            raise

    #--------------------------------------------------------------------------
    def _set_awg_waveform_data(self, sequencer, name, waveform):
        """
        Set AWG waveform data in sequencer
        """

        try:
            super()._set_awg_waveform_data(sequencer, 0, name, waveform)
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_awg_waveform_data(self, sequencer, name, start=0, size=2**31):
        """
        Get AWG waveform data from sequencer.
        """

        try:
            return super()._get_awg_waveform_data(sequencer, 0, name, start, size)
        except:
            raise

    #--------------------------------------------------------------------------
    def _set_awg_waveform_index(self, sequencer, name, index):
        """
        Set AWG waveform index in sequencer.
        """

        try:
            super()._set_awg_waveform_index(sequencer, 0, name, index)
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_awg_waveform_index(self, sequencer, name):
        """
        Get AWG waveform index from sequencer.
        """

        try:
            return super()._get_awg_waveform_index(sequencer, 0, name)
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_awg_waveform_length(self, sequencer, name):
        """
        Get AWG waveform length from sequencer.
        """

        try:
            return super()._get_awg_waveform_length(sequencer, 0, name)
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_awg_waveform_name(self, sequencer, index):
        """
        Get AWG waveform name form sequencer.
        """

        try:
            return super()._get_awg_waveform_name(sequencer, 0, index)
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_awg_waveform_names(self, sequencer):
        """
        Return all AWG waveforms names
        """

        try:
            names     = super()._get_awg_waveforms(sequencer, 0)
            name_list = names.split(';')[:-1] if names != '' else []
            return name_list
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_num_awg_waveforms(self, sequencer):
        """
        Get number of AWG waveforms in sequencer.
        """

        try:
            return super()._get_num_awg_waveforms(sequencer, 0)
        except:
            raise



    #--------------------------------------------------------------------------
    def _add_waveforms(self, sequencer, waveform_dict):
        """
        Add all waveforms in dictionary to sequencer.
        """

        try:
            if "awg" in waveform_dict:
                for name in waveform_dict["awg"]:
                    if "data" in waveform_dict["awg"][name]:
                        if "index" in waveform_dict["awg"][name]:
                            self._add_awg_waveform(sequencer, name, waveform_dict["awg"][name]["data"], waveform_dict["awg"][name]["index"])
                        else:
                            self._add_awg_waveform(sequencer, name, waveform_dict["awg"][name]["data"])
                    else:
                        raise Exception("Missing data key for {} in AWG waveform dictionary".format(name))
        except:
            raise

    #--------------------------------------------------------------------------
    def _delete_waveforms(self, sequencer):
        """
        Delete all waveforms from sequencer.
        """

        try:
            self._delete_awg_waveform(sequencer, "all")
        except:
            raise

    #--------------------------------------------------------------------------
    def get_waveforms(self, sequencer):
        """
        Return all waveforms in a dictionary
        """

        try:
            waveform_dict = {"awg": {}}

            name_list = self._get_awg_waveform_names(sequencer)
            for name in name_list:
                waveform_dict["awg"][name] = {}
                waveform_dict["awg"][name]["data"]  = self._get_awg_waveform_data(sequencer, name)
                waveform_dict["awg"][name]["index"] = self._get_awg_waveform_index(sequencer, name)

            return waveform_dict
        except:
            raise