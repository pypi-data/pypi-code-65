#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2019 Pintaudi Giorgio

from enum import Enum
from typing import Tuple, Optional, Dict, Union

import wagascianpy.pyrmod.pyrmod


class CCCModes(Enum):
    undefined = 0
    spill_off = 1
    continuous = 2
    internal_spill = 3


# noinspection PyTypeChecker
class CCC(wagascianpy.pyrmod.pyrmod.PyrameSlowModule):
    _module_id = "ccc_control"
    _module_name = "ccc"

    def __init__(self,
                 simulate=False,  # type: bool
                 simulation_dic=None,  # type: Optional[Dict[str, Tuple[int, str]]]
                 mode=CCCModes.undefined,  # type: CCCModes
                 period=260,  # type: int
                 active_time=5000  # type: int
                 ):
        # type: (...) -> None
        """ Create a CCC object

        Args:
            simulate         : True to simulate pyrame calls
            simulation_dic   : Dictionary with the return values of the simulated calls
            mode             : type of CCC operation mode
            period           : period between spills (only internal spill mode)
            active_time      : acquisition window duration (only internal spill mode)

        Returns:
            CCC object
        """

        if mode == CCCModes.undefined:
            conf_string = "ccc(ip=192.168.10.16,spill_type=undefined)"
        elif mode == CCCModes.spill_off:
            conf_string = "ccc(ip=192.168.10.16,spill_type=spill off)"
        elif mode == CCCModes.continuous:
            conf_string = "ccc(ip=192.168.10.16,spill_type=continuous)"
        elif mode == CCCModes.internal_spill:
            conf_string = "ccc(ip=192.168.10.16,spill_type=internal spill," \
                          "period={},active_time={})".format(period, active_time)
        else:
            conf_string = "ccc(ip=192.168.10.16,spill_type=undefined)"

        super(CCC, self).__init__(module_name=self._module_name,
                                  module_id=self._module_id,
                                  conf_string=conf_string,
                                  simulate=simulate,
                                  simulation_dic=simulation_dic)

    def switch_mode(self, mode, period=260, active_time=5000, ):
        # type: (CCCModes, int, int) -> Tuple[int, str]
        """ Create a CCCMode object

            Args:
                mode             : type of spill that CCC generates
                period (ms)      : period of the internal spill (default 260 ms)
                active_time (us) : width of the acquisition gate (default 5 ms)

            Returns:
                CCCMode object
        """
        if mode == CCCModes.undefined:
            mode_string = "undefined"
        elif mode == CCCModes.spill_off:
            mode_string = "spill off"
        elif mode == CCCModes.continuous:
            mode_string = "continuous"
        elif mode == CCCModes.internal_spill:
            mode_string = "internal spill"
        else:
            raise ValueError("mode not recognized : {}".format(mode))

        try:
            retcode, res = self.execcmd("switch_mode", mode_string, period, active_time)
        except RuntimeError as err:
            print("CCC : switch_mode : %s" % str(err))
            return 0, str(err)
        else:
            return retcode, res

    def spill_off(self):
        # type: (...) -> Tuple[int, str]
        """ CCC do not issue any trigger """
        return self.switch_mode(mode=CCCModes.spill_off)

    def spill_continuous(self):
        # type: (...) -> Tuple[int, str]
        """ CCC is triggered by the beam line trigger and issues one beam spill followed by six non beam spills """
        return self.switch_mode(mode=CCCModes.continuous)

    def spill_internal(self, period=260, active_time=5000):
        # type: (int, int) -> Tuple[int, str]
        """ CCC issues internally generated triggers spaced by period with an active time windows of active_time

            Args:
                period (ms)      : period of the internal spill (default 260 ms)
                active_time (us) : width of the acquisition gate (default 5 ms)
        """
        return self.switch_mode(mode=CCCModes.internal_spill, period=period, active_time=active_time)

    def get_spill_type(self):
        # type: (...) -> Tuple[int, str]
        """ Return the current spill type

            Returns:
                tuple (return code = 0 for error or 1 of success, spill type as string)
        """
        try:
            retcode, res = self.execcmd("get_spill_type", "no")
        except RuntimeError as err:
            print("CCC : get_spill_type : %s" % str(err))
            return 0, str(err)
        else:
            return retcode, res

    def get_spill_period(self):
        # type: (...) -> Tuple[int, Union[int, str]]
        """ Return the current spill period

            Returns:
                tuple (return code = 0 for error or 1 of success, spill period)
        """
        try:
            retcode, res = self.execcmd("get_spill_period")
        except RuntimeError as err:
            print("CCC : get_spill_period : %s" % str(err))
            return 0, str(err)
        else:
            return retcode, int(res)

    def get_active_time(self):
        # type: (...) -> Tuple[int, Union[int, str]]
        """Return the current gate window"""
        try:
            retcode, res = self.execcmd("get_active_time")
        except RuntimeError as err:
            print("CCC : get_active_time : %s" % str(err))
            return 0, str(err)
        else:
            return retcode, int(res)
