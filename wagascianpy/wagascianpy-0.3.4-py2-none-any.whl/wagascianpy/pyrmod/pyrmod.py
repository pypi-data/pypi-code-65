#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2019 Pintaudi Giorgio

""" Apply the high voltage to the MPPCs """

import random
import re

try:
    import bindpyrame
except ImportError:
    bindpyrame = False

from six import string_types
from typing import Optional, Callable, Dict, Tuple


def _silent_simulator(method):
    # type: (Callable) -> Callable
    def call(self, *args, **kwargs):
        # type: (PyrameModule, *str, **str) -> None
        if self.simulate:
            return
        else:
            return method(self, *args, **kwargs)
    return call


def _int_simulator(method):
    # type: (Callable) -> Callable
    def call(self, *args, **kwargs):
        # type: (PyrameModule, *str, **str) -> int
        if self.simulate:
            return random.randint(1, 1000)
        else:
            return method(self, *args, **kwargs)
    return call


def _pyrame_simulator(method):
    # type: (Callable) -> Callable

    def call(self, function, *args):
        # type: (PyrameModule, str, *str) -> Tuple[int, str]
        if self.simulate:
            function_name = re.match('(.+)_' + self.module_name, function).group(1)
            if function_name in self.simulation_dic:
                return self.simulation_dic[function_name]
            else:
                return 1, "ok"
        else:
            return method(self, function, *args)
    return call


class PyrameModule(object):

    def __init__(self, module_name, simulate=False, simulation_dic=None):
        # type: (str, bool, Dict[str, Tuple[int, str]]) -> None
        # Arguments sanity checks
        if not isinstance(module_name, string_types):
            raise ValueError("Pyrame module name is not a string")
        # Attributes initialization
        self._module_name = module_name.lower()
        self._port_name = module_name.upper() + "_PORT"
        self._socket_is_open = False
        self._socket = None
        self._simulate = simulate
        self._simulation_dic = {} if simulation_dic is None else simulation_dic
        # Open socket
        self._get_socket()

    @property
    def module_name(self):
        # type: (...) -> str
        return self._module_name

    @property
    def port_name(self):
        # type: (...) -> str
        return self._port_name

    @property
    def simulate(self):
        # type: (...) -> bool
        return self._simulate

    @property
    def simulation_dic(self):
        # type: (...) -> Dict[str, Tuple[int, str]]
        return self._simulation_dic

    @_int_simulator
    def _open_socket(self):
        # type: (...) -> int
        return bindpyrame.open_socket("localhost", bindpyrame.get_port(self.port_name))

    def _get_socket(self):
        # type: (...) -> None
        self._socket = self._open_socket()
        if not self._socket:
            raise RuntimeError("Error in opening socket")
        self._socket_is_open = True

    @_silent_simulator
    def _close_socket(self):
        # type: (...) -> None
        bindpyrame.close_socket(self._socket)

    def __del__(self):
        # type: (...) -> None
        if self._socket_is_open:
            self._close_socket()
            self._socket_is_open = False

    @_pyrame_simulator
    def pyrame_execcmd(self, function, *argv):
        # type: (str, *str) -> Tuple[int, 
        return bindpyrame.execcmd(self._socket, function, *argv)

    def execcmd(self, function, *argv):
        # type: (str, *str) -> Tuple[int, str]
        # Argument sanity checks
        arguments = [str(i) for i in argv]
        if not isinstance(function, string_types):
            raise ValueError("Function name is not a string")
        retcode, res = self.pyrame_execcmd(function + "_" + self.module_name, *arguments)
        if retcode == 0:
            raise RuntimeError("module name '%s' : function %s : arguments %s : retcode=%d res=%s"
                               % (self.module_name, function, ','.join(arguments), retcode, res))
        else:
            return retcode, res


#################################################################################################

class PyrameSlowModule(PyrameModule):
    """Class to control a generic Pyrame module"""
    _modules_id_list = []

    def __init__(self, module_name, module_id=None, conf_string=None, simulate=False, simulation_dic=None):
        # type: (str, Optional[str], Optional[str], bool, Optional[Dict[str, Tuple[int, str]]]) -> None
        super(PyrameSlowModule, self).__init__(module_name=module_name, simulate=simulate,
                                               simulation_dic=simulation_dic)
        # Object members
        self._initialized = False
        self._configured = False
        self._module_id = module_id
        # Arguments sanity checks
        if conf_string is not None and not isinstance(conf_string, string_types):
            raise ValueError("Configuration string is not a string")
        # Members initialization
        if not self.module_id:
            self._module_id = "%s_%d" % (self.module_name, random.randint(10000, 99999))
            while self._module_id in self._modules_id_list:
                self._module_id = "%s_%d" % (self.module_name, random.randint(10000, 99999))
        self._modules_id_list.append(self._module_id)
        # Initialize module
        self._initialize(conf_string)
        # Configure module
        self._configure()

    @property
    def module_id(self):
        # type: (...) -> str
        return self._module_id

    def _initialize(self, conf_string=None):
        # type: (Optional[str]) -> None
        try:
            retcode, res = self.execcmd("id_exists")
            if retcode == 1 and res.lower() == "yes":
                self._configure()
                self._deinitialize()
        except RuntimeError:
            pass
        if conf_string is None:
            retcode, res = self.execcmd("init")
        else:
            retcode, res = self.execcmd("init", conf_string)
        if retcode == 0:
            raise RuntimeError("module name '%s' with module ID '%s' : initialize error : retcode=%d res=%s"
                               % (self.module_name, self.module_id, retcode, res))
        self._initialized = True

    def _configure(self):
        # type: (...) -> None
        retcode, res = self.execcmd("config")
        if retcode == 0:
            raise RuntimeError("module name '%s' with module ID '%s' : configure error : retcode=%d res=%s"
                               % (self.module_name, self.module_id, retcode, res))
        self._configured = True

    def _invalidate(self):
        # type: (...) -> None
        retcode, res = self.execcmd("inval")
        if retcode == 0:
            print("module name '%s' with module ID '%s' : invalidate error : retcode=%d res=%s"
                  % (self.module_name, self.module_id, retcode, res))
        self._configured = False

    def _deinitialize(self):
        # type: (...) -> None
        retcode, res = self.execcmd("deinit")
        if retcode == 0:
            print("module name '%s' with module ID '%s' : deinitialize error : retcode=%d res=%s"
                  % (self.module_name, self.module_id, retcode, res))
        self._initialized = False

    def __del__(self):
        # type: (...) -> None
        if self._configured:
            self._invalidate()
        if self._initialized:
            self._deinitialize()
        self._modules_id_list.remove(self.module_id)
        super(PyrameSlowModule, self).__del__()

    def execcmd(self, function, *argv):
        # type: (str, *str) -> Tuple[int, str]
        # Argument sanity checks
        if not isinstance(function, string_types):
            raise ValueError("Function name is not a string")
        retcode, res = super(PyrameSlowModule, self).execcmd(function, self.module_id, *argv)
        if retcode == 0:
            raise RuntimeError("module name '%s' with module ID '%s' : %s error : retcode=%d res=%s"
                               % (self.module_name, self.module_id, function, retcode, res))
        else:
            return retcode, res
