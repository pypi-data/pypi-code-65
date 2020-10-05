""""""
#------------------------------------------------------------------------------
# Description    : Pulsar QCM QCoDeS interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
#------------------------------------------------------------------------------


#-- include -------------------------------------------------------------------

from ieee488_2.transport       import ip_transport, pulsar_dummy_transport
from pulsar_qcm.pulsar_qcm_ifc import pulsar_qcm_ifc
from qcodes                    import validators as vals
from qcodes                    import Instrument
from jsonschema                import validate
import json

#-- class ---------------------------------------------------------------------

class pulsar_qcm_qcodes(pulsar_qcm_ifc, Instrument):
    """
    The Pulsar QCM QCoDeS interface.
    """

    #--------------------------------------------------------------------------
    def __init__(self, name, transport_inst, debug=0):
        """
        Constructor
        """

        #Initialize parent classes.
        super(pulsar_qcm_qcodes, self).__init__(transport_inst, debug)
        Instrument.__init__(self, name)

        #Set device parameters
        self._num_sequencers = 2

        #Set JSON schema to validate JSON file with
        self._wave_and_prog_json_schema = {"title":       "Sequencer waveforms and program container",
                                           "description": "Contains both all waveforms and program required for a sequence.",
                                           "type":        "object",
                                           "required":    ["program", "waveforms"],
                                           "properties": {
                                               "program": {
                                                   "description": "Sequencer assembly program in string format.",
                                                   "type":        "string"
                                               },
                                               "waveforms": {
                                                   "description": "Waveform dictionary containing one or multiple AWG waveform(s).",
                                                   "type":        "object",
                                                   "properties": {
                                                       "awg": {
                                                            "description": "Waveform dictionary containing one or multiple AWG waveform(s).",
                                                            "type":        "object"
                                                       },
                                                   }
                                               }
                                           }}
        self._wave_json_schema = {"title":       "Waveform container",
                                  "description": "Waveform dictionary a single waveform.",
                                  "type":        "object",
                                  "required":    ["data"],
                                  "properties": {
                                      "data":  {
                                          "description": "List of waveform samples.",
                                          "type":        "array"
                                      },
                                      "index": {
                                          "description": "Optional waveform index number.",
                                          "type":        "number"
                                      }
                                  }}

        #Add QCoDeS parameters
        self.add_parameter(
            "reference_source",
            label      = "Reference source",
            docstring  = "Sets/gets reference source (True = internal 10 MHz, False = External 10 MHz)",
            unit       = '',
            vals       = vals.Bool(),
            get_parser = bool,
            set_cmd    = self._set_reference_source,
            get_cmd    = self._get_reference_source
        )

        for seq_idx in range(0, self._num_sequencers):
            #--Sequencer settings----------------------------------------------
            self.add_parameter(
                "sequencer{}_sync_en".format(seq_idx),
                label      = "Sequencer {} synchronization enable which enables party-line synchronization".format(seq_idx),
                docstring  = "Sets/gets sequencer {} synchronization enable which enables party-line synchronization".format(seq_idx),
                unit       = '',
                vals       = vals.Bool(),
                get_parser = bool,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "sync_en"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "sync_en")
            )

            self.add_parameter(
                "sequencer{}_nco_freq".format(seq_idx),
                label      = "Sequencer {} NCO frequency".format(seq_idx),
                docstring  = "Sets/gets sequencer {} NCO frequency in Hz with a resolution of 0.25 Hz".format(seq_idx),
                unit       = 'Hz',
                vals       = vals.Numbers(-300e6, 300e6),
                get_parser = float,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "freq_hz"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "freq_hz")
            )

            self.add_parameter(
                "sequencer{}_nco_phase".format(seq_idx),
                label      = "Sequencer {} NCO phase".format(seq_idx),
                docstring  = "Sets/gets sequencer {} NCO phase in degrees with a resolution of 3.6e-7 degrees".format(seq_idx),
                unit       = 'Degrees',
                vals       = vals.Numbers(0, 360),
                get_parser = float,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "phase_degree"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "phase_degree")
            )

            self.add_parameter(
                "sequencer{}_marker_ovr_en".format(seq_idx),
                label      = "Sequencer {} marker override enable".format(seq_idx),
                docstring  = "Sets/gets sequencer {} marker override enable".format(seq_idx),
                unit       = '',
                vals       = vals.Bool(),
                get_parser = bool,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "mrk_ovr_en"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "mrk_ovr_en")
            )

            self.add_parameter(
                "sequencer{}_marker_ovr_value".format(seq_idx),
                label      = "Sequencer {} marker override value".format(seq_idx),
                docstring  = "Sets/gets sequencer {} marker override value".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(0, 15),
                get_parser = bool,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "mrk_ovr_val"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "mrk_ovr_val")
            )

            self.add_parameter(
                "sequencer{}_waveforms_and_program".format(seq_idx),
                label     = "Sequencer {} AWG and acquistion waveforms and ASM program".format(seq_idx),
                docstring = "Sets sequencer {} AWG and acquistion waveforms and ASM program. Valid input is a string representing the JSON filename.".format(seq_idx),
                set_cmd   = pulsar_qcm._gen_set_func_par(self._set_sequencer_waveforms_and_program, seq_idx),
                vals      = vals.Strings()
            )



            #--AWG settings----------------------------------------------------
            self.add_parameter(
                "sequencer{}_cont_mode_en_awg_path0".format(seq_idx),
                label      = "Sequencer {} continous waveform mode enable for AWG path 0".format(seq_idx),
                docstring  = "Sets/gets sequencer {} continous waveform mode enable for AWG path 0".format(seq_idx),
                unit       = '',
                vals       = vals.Bool(),
                get_parser = bool,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "cont_mode_en_awg_path_0"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "cont_mode_en_awg_path_0")
            )

            self.add_parameter(
                "sequencer{}_cont_mode_en_awg_path1".format(seq_idx),
                label      = "Sequencer {} continous waveform mode enable for AWG path 1".format(seq_idx),
                docstring  = "Sets/gets sequencer {} continous waveform mode enable for AWG path 1".format(seq_idx),
                unit       = '',
                vals       = vals.Bool(),
                get_parser = bool,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "cont_mode_en_awg_path_1"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "cont_mode_en_awg_path_1")
            )

            self.add_parameter(
                "sequencer{}_cont_mode_waveform_idx_awg_path0".format(seq_idx),
                label      = "Sequencer {} continous waveform mode waveform index for AWG path 0".format(seq_idx),
                docstring  = "Sets/gets sequencer {} continous waveform mode waveform index or AWG path 0".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(0, 2**10-1),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "cont_mode_waveform_idx_awg_path_0"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "cont_mode_waveform_idx_awg_path_0")
            )

            self.add_parameter(
                "sequencer{}_cont_mode_waveform_idx_awg_path1".format(seq_idx),
                label      = "Sequencer {} continous waveform mode waveform index for AWG path 1".format(seq_idx),
                docstring  = "Sets/gets sequencer {} continous waveform mode waveform index or AWG path 1".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(0, 2**10-1),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "cont_mode_waveform_idx_awg_path_1"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "cont_mode_waveform_idx_awg_path_1")
            )

            self.add_parameter(
                "sequencer{}_upsample_rate_awg_path0".format(seq_idx),
                label      = "Sequencer {} upsample rate for AWG path 0".format(seq_idx),
                docstring  = "Sets/gets sequencer {} upsample rate for AWG path 0".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(0, 2**16-1),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "upsample_rate_awg_path_0"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "upsample_rate_awg_path_0")
            )

            self.add_parameter(
                "sequencer{}_upsample_rate_awg_path1".format(seq_idx),
                label      = "Sequencer {} upsample rate for AWG path 1".format(seq_idx),
                docstring  = "Sets/gets sequencer {} upsample rate for AWG path 1".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(0, 2**16-1),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "upsample_rate_awg_path_1"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "upsample_rate_awg_path_1")
            )

            self.add_parameter(
                "sequencer{}_gain_awg_path0".format(seq_idx),
                label      = "Sequencer {} gain for AWG path 0".format(seq_idx),
                docstring  = "Sets/gets sequencer {} gain for AWG path 0".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(-1.0, 1.0),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "gain_awg_path_0_float"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "gain_awg_path_0_float")
            )

            self.add_parameter(
                "sequencer{}_gain_awg_path1".format(seq_idx),
                label      = "Sequencer {} gain for AWG path 1".format(seq_idx),
                docstring  = "Sets/gets sequencer {} gain for AWG path 1".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(-1.0, 1.0),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "gain_awg_path_1_float"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "gain_awg_path_1_float")
            )

            self.add_parameter(
                "sequencer{}_offset_awg_path0".format(seq_idx),
                label      = "Sequencer {} offset for AWG path 0".format(seq_idx),
                docstring  = "Sets/gets sequencer {} offset for AWG path 0".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(-1.0, 1.0),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "offset_awg_path_0_float"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "offset_awg_path_0_float")
            )

            self.add_parameter(
                "sequencer{}_offset_awg_path1".format(seq_idx),
                label      = "Sequencer {} offset for AWG path 1".format(seq_idx),
                docstring  = "Sets/gets sequencer {} offset for AWG path 1".format(seq_idx),
                unit       = '',
                vals       = vals.Numbers(-1.0, 1.0),
                get_parser = int,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "offset_awg_path_1_float"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "offset_awg_path_1_float")
            )

            self.add_parameter(
                "sequencer{}_mod_en_awg".format(seq_idx),
                label      = "Sequencer {} modulation enable for AWG".format(seq_idx),
                docstring  = "Sets/gets sequencer {} modulation enable for AWG".format(seq_idx),
                unit       = '',
                vals       = vals.Bool(),
                get_parser = bool,
                set_cmd    = pulsar_qcm._gen_set_func_par(self._set_sequencer_config_val, seq_idx, "mod_en_awg"),
                get_cmd    = pulsar_qcm._gen_get_func_par(self._get_sequencer_config_val, seq_idx, "mod_en_awg")
            )

    #--------------------------------------------------------------------------
    def _set_sequencer_config_val(self, sequencer, param, val):
        """
        Set sequencer configuration helper
        """

        try:
            self._set_sequencer_config(sequencer, {param: val})
        except:
            raise

    #--------------------------------------------------------------------------
    def _get_sequencer_config_val(self, sequencer, param):
        """
        Get sequencer configuration helper
        """

        try:
            return self._get_sequencer_config(sequencer)[param]
        except:
            raise

    #--------------------------------------------------------------------------
    def _set_sequencer_waveforms_and_program(self, sequencer, file_name):
        """
        Set sequencer waveforms and program
        """

        try:
            with open(file_name, 'r') as file:
                wave_and_prog_dict = json.load(file)
                validate(wave_and_prog_dict, self._wave_and_prog_json_schema)
                if "awg" in wave_and_prog_dict["waveforms"]:
                    for name in wave_and_prog_dict["waveforms"]["awg"]:
                        validate(wave_and_prog_dict["waveforms"]["awg"][name], self._wave_json_schema)
                self._delete_waveforms(sequencer)
                self._add_waveforms(sequencer, wave_and_prog_dict["waveforms"])
                self._set_sequencer_program(sequencer, wave_and_prog_dict["program"])
        except:
            raise

    #--------------------------------------------------------------------------
    @staticmethod
    def _gen_set_func_par(func, *args):
        """
        Generate set function with fixed parameters
        """

        def set_func(val):
            return func(*args, val)
        return set_func

    #--------------------------------------------------------------------------
    @staticmethod
    def _gen_get_func_par(func, *args):
        """
        Generate get function with fixed parameters
        """

        def get_func():
            return func(*args)
        return get_func

#-- class ---------------------------------------------------------------------

class pulsar_qcm(pulsar_qcm_qcodes):

    #--------------------------------------------------------------------------
    def __init__(self, name, host, port=5025, debug=0):
        """
        Constructor
        """

        #Create transport layer (socket interface)
        transport_inst = ip_transport(host=host, port=port)

        #Initialize parent classes.
        super(pulsar_qcm, self).__init__(name, transport_inst, debug)

#-- class ---------------------------------------------------------------------

class pulsar_qcm_dummy(pulsar_qcm_qcodes):

    #--------------------------------------------------------------------------
    def __init__(self, name, debug=1):
        """
        Constructor
        """

        #Create transport layer (socket interface)
        transport_inst = pulsar_dummy_transport(pulsar_qcm_ifc._get_sequencer_cfg_format())

        #Initialize parent classes.
        super(pulsar_qcm_dummy, self).__init__(name, transport_inst, debug)