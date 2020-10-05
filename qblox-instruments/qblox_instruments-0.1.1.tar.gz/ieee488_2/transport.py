""""""
#------------------------------------------------------------------------------
# Description    : Transport layer (abstract, IP, file, dummy)
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
#------------------------------------------------------------------------------


#-- include -------------------------------------------------------------------

import socket
import re
import os
import sys
import struct
import subprocess

#-- class ----------------------------------------------------------------------

class transport:
    """
    Abstract base class for data transport to instruments
    """

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        pass

    def write(self, cmd_str: str) -> None:
        pass

    def write_binary(self, data: bytes) -> None:
        pass

    def read_binary(self, size: int) -> bytes:
        pass

    def readline(self) -> str:
        pass

#-- class ---------------------------------------------------------------------

class ip_transport(transport):
    """
    IP socket transport
    """

    def __init__(self,
                 host:         str,
                 port:         int = 5025,
                 timeout           = 10.0,
                 snd_buf_size: int = 512 * 1024) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)                                           #Setup timeout (before connect)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, snd_buf_size) #Enlarge buffer
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)         #Send immediately
        self._socket.connect((host, port))

    def close(self) -> None:
        self._socket.close()

    def write(self, cmd_str: str) -> None:
        out_str = cmd_str + '\n'
        self.write_binary(out_str.encode('ascii'))

    def write_binary(self, data: bytes) -> None:
        exp_len = len(data)
        act_len = 0
        while True:
            act_len += self._socket.send(data[act_len:exp_len])
            if act_len == exp_len:
                break

    def read_binary(self, size: int) -> bytes:
        data = self._socket.recv(size)
        act_len = len(data)
        exp_len = size
        while act_len != exp_len:
            data += self._socket.recv(exp_len - act_len)
            act_len = len(data)
        return data

    def readline(self) -> str:
        return self._socket.makefile().readline()

#-- class ---------------------------------------------------------------------

class pulsar_dummy_transport(transport):
    """
    Dummy transport
    """

    def __init__(self, cfg_format) -> None:
        self._cmd_hist         = []
        self._data_out         = 0
        self._bin_out          = None
        self._system_error     = []
        self._asm_status       = False
        self._asm_log          = ''
        self._cfg              = {}
        self._cfg_bin_size     = struct.calcsize(cfg_format)
        self._awg_waveforms    = {}
        self._acq_waveforms    = {}
        self._acq_acquisitions = {}
        self._cmds             = {"*CMDS?":                                          self._get_cmds,
                                  "*IDN?":                                           self._get_idn,
                                  "*RST":                                            self._reset,
                                  "SYSTem:ERRor:NEXT?":                              self._get_system_error,
                                  "SYSTem:ERRor:COUNt?":                             self._get_system_error_cnt,
                                  "STATus:ASSEMbler:SUCCess?":                       self._get_assembler_status,
                                  "STATus:ASSEMbler:LOG?":                           self._get_assembler_log,
                                  "SEQuencer#:PROGram":                              self._set_sequencer_program,
                                  "SEQuencer#:CONFiguration":                        self._set_sequencer_config,
                                  "SEQuencer#:CONFiguration?":                       self._get_sequencer_config,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:NEW":              self._add_awg_waveform,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:DELete":           self._del_awg_waveform,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:DATA":             self._set_awg_waveform_data,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:DATA?":            self._get_awg_waveform_data,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:INDex":            self._set_awg_waveform_index,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:INDex?":           self._get_awg_waveform_index,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:LENGth?":          self._get_awg_waveform_length,
                                  "SEQuencer#:AWG#:WLISt:WAVeform:NAME?":            self._get_awg_waveform_name,
                                  "SEQuencer#:AWG#:WLISt:SIZE?":                     self._get_num_awg_waveforms,
                                  "SEQuencer#:AWG#:WLISt?":                          self._get_acq_waveforms,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:NEW":              self._add_acq_waveform,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:DELete":           self._del_acq_waveform,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:DATA":             self._set_acq_waveform_data,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:DATA?":            self._get_acq_waveform_data,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:INDex":            self._set_acq_waveform_index,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:INDex?":           self._get_acq_waveform_index,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:LENGth?":          self._get_acq_waveform_length,
                                  "SEQuencer#:ACQ#:WLISt:WAVeform:NAME?":            self._get_acq_waveform_name,
                                  "SEQuencer#:ACQ#:WLISt:SIZE?":                     self._get_num_acq_waveforms,
                                  "SEQuencer#:ACQ#:WLISt?":                          self._get_acq_waveforms,
                                  "SEQuencer#:ACQ#:PATH#:ALISt:ACQuisition:NEW":     self._add_acq_acquisition,
                                  "SEQuencer#:ACQ#:PATH#:ALISt:ACQuisition:DELete":  self._del_acq_acquisition,
                                  "SEQuencer#:ACQ#:PATH#:ALISt:ACQuisition:DATA":    self._set_acq_acquisition_data,
                                  "SEQuencer#:ACQ#:PATH#:ALISt:ACQuisition:DATA?":   self._get_acq_acquisition_data,
                                  "SEQuencer#:ACQ#:PATH#:ALISt:ACQuisition:LENGth?": self._get_acq_acquisition_length,
                                  "SEQuencer#:ACQ#:PATH#:ALISt:SIZE?":               self._get_num_acq_acquisitions,
                                  "SEQuencer#:ACQ#:PATH#:ALISt?":                    self._get_acq_acquisitions}

    def close(self) -> None:
        self.__init__('')

    def write(self, cmd_str: str) -> None:
        self._cmd = cmd_str
        self._handle_cmd(cmd_str)

    def write_binary(self, data: bytes) -> None:
        cmd_parts = data.split('#'.encode())
        cmd_str   = cmd_parts[0].decode()
        bin_in    = '#'.encode() + '#'.encode().join(cmd_parts[1:])
        self._handle_cmd(cmd_str, bin_in)

    def read_binary(self, size: int) -> bytes:
        bin = self._bin_out[:size]
        self._bin_out = self._bin_out[size:]
        return bin

    def readline(self) -> str:
        return self._data_out if type(self._data_out) == str else str(self._data_out)

    def _handle_cmd(self, cmd_str: str, bin_in: bytes = 0) -> None:
        cmd_parts  = cmd_str.split(' ')
        cmd_params = re.findall("[0-9]+", cmd_parts[0])
        cmd_args   = [arg.strip('"') for arg in (cmd_parts[1].split(',') if len(cmd_parts) > 1 else [])]
        cmd_str    = re.sub("[0-9]+", '#', cmd_parts[0])
        self._cmd_hist.append(cmd_str)

        if cmd_str in self._cmds:
            self._cmds[cmd_str](cmd_params, cmd_args, bin_in)
        else:
            self._data_out = 0
            self._bin_out  = self._encode_bin('0'.encode())

    def _encode_bin(self, data: bytes) -> None:
        header_b = str(len(data)).encode()
        header_a = ('#' + str(len(header_b))).encode()
        end      = '\r\n'.encode()
        return header_a + header_b + data + end

    def _decode_bin(self, data: bytes) -> bytes:
        header_a = data[:2].decode() #Read '#N'
        data = data[2:]
        if header_a[0] != '#':
            raise RuntimeError('Header error: received {}'.format(header_a))
        header_b = data[:int(header_a[1])].decode()
        data = data[int(header_a[1]):]
        return data[:int(header_b)]

    def get_cmd_hist(self) -> list:
        return self._cmd_hist

    def _get_cmds(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = "THe:CAke:Is:A:LIe;cake;str;get_cake;lie;cake;str;0;Your trusty AI companion promised you a cake.;"

    def _get_idn(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = "Qblox,Pulsar Dummy,whatever,fwVersion=0.0.0 fwBuild=28/11/1967-00:00:00 fwHash=0xDEADBEAF fwDirty=0 kmodVersion=0.0.0 kmodBuild=15/07/1943-00:00:00 kmodHash=0x0D15EA5E kmodDirty=0 swVersion=0.0.0 swBuild=11/05/1924-00:00:00 swHash=0xBEEFBABE swDirty=0"

    def _reset(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self.__init__()

    def _get_system_error(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if len(self._system_error):
            self._data_out = '0,' + self._system_error[0]
            self._system_error = self._system_error[1:]
        else:
            self._data_out = "No error"

    def _get_system_error_cnt(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = str(len(self._system_error))

    def _get_assembler_status(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = str(int(self._asm_status))

    def _get_assembler_log(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._bin_out = self._encode_bin(self._asm_log.encode())



    def _set_sequencer_program(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        q1asm_str = self._decode_bin(bin_in).decode()
        fid = open("./tmp.q1asm", 'w')
        fid.write(q1asm_str)
        fid.close()

        if os.name == 'nt':
            assembler_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/assembler/q1asm_windows.exe")
            proc = subprocess.Popen([assembler_path, "-o", "tmp", "tmp.q1asm"], shell=True, text=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        elif sys.platform == 'darwin':
            assembler_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/assembler/q1asm_macos")
            proc = subprocess.Popen([assembler_path + " -o tmp tmp.q1asm"], shell=True, text=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            assembler_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/assembler/q1asm_linux")
            proc = subprocess.Popen([assembler_path + " -o tmp tmp.q1asm"], shell=True, text=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._asm_log     = proc.communicate()[0]
        self._asm_success = True if proc.returncode == 0 else False

        if self._asm_success == False:
            self._system_error.append("Assembly failed.")

    def _set_sequencer_config(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._cfg[cmd_params[0]] = self._decode_bin(bin_in)

    def _get_sequencer_config(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._cfg:
            self._bin_out = self._encode_bin(self._cfg[cmd_params[0]])
        else:
            self._bin_out = self._encode_bin(self._cfg_bin_size*b'\x00')



    def _add_awg_waveform(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                self._system_error.append("Waveform {} already in waveform list.".format(cmd_args[0]))
                return

            for index in range(0, len(self._awg_waveforms[cmd_params[0]]) + 1):
                idx_unused = True
                for name in self._awg_waveforms[cmd_params[0]]:
                    if self._awg_waveforms[cmd_params[0]][name]["index"] == index:
                        idx_unused = False
                        break
                if idx_unused == True:
                    break
        else:
            self._awg_waveforms[cmd_params[0]] = {}
            index = 0
        self._awg_waveforms[cmd_params[0]][cmd_args[0]] = {"wave": [], "index": index}

    def _del_awg_waveform(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_args[0].lower() == 'all':
            self._awg_waveforms[cmd_params[0]] = {}
        else:
            if cmd_params[0] in self._awg_waveforms:
                if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                    del self._awg_waveforms[cmd_params[0]][cmd_args[0]]
                    return
            self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _set_awg_waveform_data(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                self._awg_waveforms[cmd_params[0]][cmd_args[0]]["wave"] = self._decode_bin(bin_in)
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_awg_waveform_data(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                self._bin_out = self._encode_bin(self._awg_waveforms[cmd_params[0]][cmd_args[0]]["wave"])
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _set_awg_waveform_index(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                for name in self._awg_waveforms[cmd_params[0]]:
                    if self._awg_waveforms[cmd_params[0]][name]["index"] == cmd_args[1] and name != cmd_args[0]:
                        self._system_error.append("Waveform index {} already in use by {}.".format(cmd_args[0], name))
                        return
                self._awg_waveforms[cmd_params[0]][cmd_args[0]]["index"] = cmd_args[1]
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_awg_waveform_index(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                self._data_out = self._awg_waveforms[cmd_params[0]][cmd_args[0]]["index"]
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_awg_waveform_length(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            if cmd_args[0] in self._awg_waveforms[cmd_params[0]]:
                self._data_out = int(len(self._awg_waveforms[cmd_params[0]][cmd_args[0]]["wave"])/4)
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_awg_waveform_name(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            for name in self._awg_waveforms[cmd_params[0]]:
                if self._awg_waveforms[cmd_params[0]][name]["index"] == cmd_args[0]:
                    self._data_out = name[1:-1]
                    return
        self._system_error.append("Waveform index {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_num_awg_waveforms(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._awg_waveforms:
            self._data_out = len(self._awg_waveforms[cmd_params[0]])
        else:
            self._data_out = 0

    def _get_awg_waveforms(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = ""
        if cmd_params[0] in self._awg_waveforms:
            names = ''
            for name in self._awg_waveforms[cmd_params[0]]:
                names += name + ';'
            self._data_out = names
            return



    def _add_acq_waveform(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                self._system_error.append("Waveform {} already in waveform list.".format(cmd_args[0]))
                return

            for index in range(0, len(self._acq_waveforms[cmd_params[0]]) + 1):
                idx_unused = True
                for name in self._acq_waveforms[cmd_params[0]]:
                    if self._acq_waveforms[cmd_params[0]][name]["index"] == index:
                        idx_unused = False
                        break
                if idx_unused == True:
                    break
        else:
            self._acq_waveforms[cmd_params[0]] = {}
            index = 0
        self._acq_waveforms[cmd_params[0]][cmd_args[0]] = {"wave": [], "index": index}

    def _del_acq_waveform(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_args[0].lower() == 'all':
            self._acq_waveforms[cmd_params[0]] = {}
        else:
            if cmd_params[0] in self._acq_waveforms:
                if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                    del self._acq_waveforms[cmd_params[0]][cmd_args[0]]
                    return
            self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _set_acq_waveform_data(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                self._acq_waveforms[cmd_params[0]][cmd_args[0]]["wave"] = self._decode_bin(bin_in)
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_acq_waveform_data(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                self._bin_out = self._encode_bin(self._acq_waveforms[cmd_params[0]][cmd_args[0]]["wave"])
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _set_acq_waveform_index(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                for name in self._acq_waveforms[cmd_params[0]]:
                    if self._acq_waveforms[cmd_params[0]][name]["index"] == cmd_args[1] and name != cmd_args[0]:
                        self._system_error.append("Waveform index {} already in use by {}.".format(cmd_args[0], name))
                        return
                self._acq_waveforms[cmd_params[0]][cmd_args[0]]["index"] = cmd_args[1]
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_acq_waveform_index(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                self._data_out = self._acq_waveforms[cmd_params[0]][cmd_args[0]]["index"]
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_acq_waveform_length(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            if cmd_args[0] in self._acq_waveforms[cmd_params[0]]:
                self._data_out = int(len(self._acq_waveforms[cmd_params[0]][cmd_args[0]]["wave"])/4)
                return
        self._system_error.append("Waveform {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_acq_waveform_name(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            for name in self._acq_waveforms[cmd_params[0]]:
                if self._acq_waveforms[cmd_params[0]][name]["index"] == cmd_args[0]:
                    self._data_out = name[1:-1]
                    return
        self._system_error.append("Waveform index {} does not exist in waveform list.".format(cmd_args[0]))

    def _get_num_acq_waveforms(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_waveforms:
            self._data_out = len(self._acq_waveforms[cmd_params[0]])
        else:
            self._data_out = 0

    def _get_acq_waveforms(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = ""
        if cmd_params[0] in self._acq_waveforms:
            names = ''
            for name in self._acq_waveforms[cmd_params[0]]:
                names += name + ';'
            self._data_out = names
            return



    def _add_acq_acquisition(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                if cmd_args[0] in self._acq_acquisitions[cmd_params[0]][cmd_params[2]]:
                    self._system_error.append("Acquisition {} already in acquisition list.".format(cmd_args[0]))
                    return
                else:
                    self._acq_acquisitions[cmd_params[0]][cmd_params[2]][cmd_args[0]] = {"size": cmd_args[1], "data": []}
            else:
                self._acq_acquisitions[cmd_params[0]][cmd_params[2]] = {cmd_args[0]: {"size": cmd_args[1], "data": []}}
        else:
            self._acq_acquisitions[cmd_params[0]] = {cmd_params[2]: {cmd_args[0]: {"size": cmd_args[1], "data": []}}}

    def _del_acq_acquisition(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                if cmd_args[0].lower() == 'all':
                    self._acq_acquisition[cmd_params[0]][cmd_params[2]] = {}
                else:
                    if cmd_args[0] in self._acq_acquisitions[cmd_params[0]][cmd_params[2]]:
                        del self._acq_acquisitions[cmd_params[0]][cmd_params[2]][cmd_args[0]]
                        return
                    self._system_error.append("Acquisition {} does not exist in acquisition list.".format(cmd_args[0]))

    def _set_acq_acquisition_data(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                if cmd_args[0] in self._acq_acquisitions[cmd_params[0]][cmd_params[2]]:
                    size = int(self._acq_acquisitions[cmd_params[0]][cmd_params[2]][cmd_args[0]]["size"])
                    if size > 2**14-1:
                        size = 2**14-1
                    self._acq_acquisitions[cmd_params[0]][cmd_params[2]][cmd_args[0]]["data"] = struct.pack('f'*size, *[(1.0/size)*i for i in range(0, size)])
                    return
        self._system_error.append("Acquisition {} does not exist in acquisition list.".format(cmd_args[0]))

    def _get_acq_acquisition_data(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                if cmd_args[0] in self._acq_acquisitions[cmd_params[0]][cmd_params[2]]:
                    self._bin_out = self._encode_bin(self._acq_acquisitions[cmd_params[0]][cmd_params[2]][cmd_args[0]]["data"])
                    return
        self._system_error.append("Acquisition {} does not exist in acquisition list.".format(cmd_args[0]))

    def _get_acq_acquisition_length(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                if cmd_args[0] in self._acq_acquisitions[cmd_params[0]][cmd_params[2]]:
                    self._data_out = int(len(self._acq_acquisitions[cmd_params[0]][cmd_params[2]][cmd_args[0]]["data"])/4)
                    return
        self._system_error.append("Acquisition {} does not exist in acquisition list.".format(cmd_args[0]))

    def _get_num_acq_acquisitions(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = 0
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                self._data_out = len(self._acq_acquisitions[cmd_params[0]][cmd_params[2]])
                return

    def _get_acq_acquisitions(self, cmd_params: list, cmd_args: list, bin_in: bytes) -> None:
        self._data_out = ""
        if cmd_params[0] in self._acq_acquisitions:
            if cmd_params[2] in self._acq_acquisitions[cmd_params[0]]:
                names = ''
                for name in self._acq_acquisitions[cmd_params[0]][cmd_params[2]]:
                    names += name + ';'
                self._data_out = names
                return



#-- class ---------------------------------------------------------------------

class file_transport(transport):
    """
    Input/output from/to file to support driver testing
    """

    def __init__(self,
                out_file_name: str,
                in_file_name:  str = '') -> None:
        self._out_file = open(out_file_name, "wb+")

    def close(self) -> None:
        self._out_file.close()

    def write(self, cmd_str: str) -> None:
        out_str = cmd_str + '\n'
        self.write_binary(out_str.encode('ascii'))

    def write_binary(self, data: bytes) -> None:
        self._out_file.write(data)

    def read_binary(self, size: int) -> bytes:
        pass

    def readline(self) -> str:
        pass
