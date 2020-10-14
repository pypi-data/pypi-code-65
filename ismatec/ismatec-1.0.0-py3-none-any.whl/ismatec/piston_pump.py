import logging
import time
import threading
import math
from typing import Union
from ftdi_serial import Serial
from ismatec.errors import PumpError, PumpOverloadError, CommandError
import atexit

# todo have not tested networking pumps

"""
Structure of commands:
The address is followed by a character. Some commands have additional parameters that always consist of 4 or
5 figures.

The command string is completed by a carriage return (ASCII 13, <CR>). The pump confirms most commands with an
asterix *, Yes/No inquiries are answered by + (yes) or - (no). Multi-digit replies are concluded by a
carriage return (ASCII 13, <CR>) and a line feed (ASCII 10, <LF>).

Incorrect commands are answered by #.
If the pump is in the state of overload, each command is responded with #
Numerical values are confirmed as 3 to 5-digit figures. 4 or 5 digits are numerals, one digit is either a decimal
    point or a preceding blank space
"""


class RegloCPF:
    """
    This module is for the pump software version 3.0.
    The pump: http://www.ismatec.com/int_e/pumps/p_reglo_cpf/reglo_cpf_drive.htm

    Setting the calibrated flow rate does not work in Windows 10
    """
    _CONNECTION_SETTINGS = {'baudrate': 9600, 'data_bits': Serial.DATA_BITS_8, 'stop_bits': Serial.STOP_BITS_1}
    # hex command characters for data transmission
    _CR_HEX = "\x0D"  # carriage return
    _LF_HEX = "\x0A"  # line feed
    # message terminators
    _COMMAND_LINE_ENDING = _CR_HEX  # each individual command is terminated with CR
    _MULTI_DIGIT_RESPONSE_LINE_ENDING = _CR_HEX + _LF_HEX
    _MULTI_DIGIT_RESPONSE_LINE_ENDING_ENCODED = _MULTI_DIGIT_RESPONSE_LINE_ENDING.encode()

    # constants for single character responses
    # responses other than multi digit responses are these single characters. Multi digit responses are concluded by
    # _MULTI_DIGIT_RESPONSE_LINE_ENDING
    _COMMON_CONFIRM_RESPONSE = '*'  # response pump uses to confirm most commands
    _INCORRECT_COMMAND_RESPONSE = '#'
    _OVERLOAD_RESPONSE = '#'
    _YES_RESPONSE = '+'
    _NO_RESPONSE = '-'
    _NON_MULTI_DIGIT_RESPONSES = [_COMMON_CONFIRM_RESPONSE, _INCORRECT_COMMAND_RESPONSE, _OVERLOAD_RESPONSE,
                                  _YES_RESPONSE, _NO_RESPONSE]

    # pump modes
    _PUMP_RPM = 'PUMP_RPM'
    _PUMP_FLOW_RATE = 'PUMP_FLOW_RATE'
    _DISPENSE_TIME = 'DISPENSE_TIME'
    _DISPENSE_VOLUME = 'DISPENSE_VOLUME'
    _PAUSE_TIME = 'PAUSE_TIME'
    _DISPENSE_TIME_AND_PAUSE_TIME = 'DISPENSE_TIME_AND_PAUSE_TIME'
    _DISPENSE_VOLUME_AND_PAUSE_TIME = 'DISPENSE_VOLUME_AND_PAUSE_TIME'
    _VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD = 'VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD'
    _TOTAL = 'TOTAL'
    _MODES = [_PUMP_RPM, _PUMP_FLOW_RATE, _DISPENSE_TIME, _DISPENSE_VOLUME, _PAUSE_TIME, _DISPENSE_TIME_AND_PAUSE_TIME,
              _DISPENSE_VOLUME_AND_PAUSE_TIME, _VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD, _TOTAL]

    # constants for commands - all responses are _COMMON_CONFIRM_RESPONSE unless otherwise specified
    # ------------------------------------
    # commands - general - all responses are _COMMON_CONFIRM_RESPONSE
    #   each command must begin with the pump address and end with a carriage return
    #   each cascaded must be allocated an individual address
    #   if the pump is in a state of overload each command is responded with #
    _SET_ADDRESS = "@"  # not preceded by the pump address, only followed by the address to set
    _RESET_OVERLOAD = "-"
    # ------------------------------------
    # commands - controlling the drive
    _START = 'H'  # response is _NO_RESPONSE under command G, in case of error message
    _STOP = 'I'
    _SET_REVOLUTION_CLOCKWISE = 'J'
    _SET_REVOLUTION_COUNTER_CLOCKWISE = 'K'
    _SWITCH_CONTROL_PANEL_TO_MANUAL_OPERATION = 'A'
    _SET_CONTROL_PANEL_INACTIVE = 'B'  # so that input vial control keys is not possible
    _WRITE_NUMBERS_TO_CONTROL_PANEL = 'D'  # followed by 5 digits (can also include - or .). Only visible if control
    # panel is inactive
    _WRITE_LETTERS_TO_CONTROL_PANEL = 'DA'  # followed by 4 letters (can also include -)
    # ------------------------------------
    # commands - selecting the operating mode
    _SET_MODE_PUMP_RPM = 'L'
    _SET_MODE_PUMP_FLOW_RATE = 'M'
    _SET_MODE_DISPENSE_TIME = 'N'
    _SET_MODE_DISPENSE_VOLUME = 'O'
    _SET_MODE_PAUSE_TIME = ']'
    _SET_MODE_DISPENSE_TIME_AND_PAUSE_TIME = 'P'
    _SET_MODE_DISPENSE_VOLUME_AND_PAUSE_TIME = 'Q'
    _SET_MODE_VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD = 'G'  # if the mode was set then _COMMON_CONFIRM_RESPONSE is
    # returned, but in the case of error 1111 (volume too small, time too long), _NO_RESPONSE is returned,
    # and in the case of error 9999 (volume too large, time too short), _YES_RESPONSE is returned
    _SET_MODE_TOTAL = 'R'
    # ------------------------------------
    # commands - inquiring and setting parameters
    _INQUIRE_PUMP_CURRENT_MODE_ACTIVE_OR_INACTIVE = 'E'  # returns _YES_RESPONSE or _NO_RESPONSE
    _INQUIRE_PUMP_TYPE_SOFTWARE_VERSION = '#'  # returns "REGLO DIGITAL {pump type, 3 digits} {software version, 3 digits}"
    _INQUIRE_SOFTWARE_VERSION = '('  # returns pump number as a 4 digit number
    _INQUIRE_PUMP_HEAD_IDENTIFICATION_NUMBER = ')'  # returns pump head identification number as a 4 digit number
    _SET_PUMP_HEAD_IDENTIFICATION_NUMBER = ')'  # followed by 4 digits
    _INQUIRE_SPEED = 'S'  # returns speed (rpm) identification number as a 4 digit number
    _SET_SPEED = 'S'  # followed by a 4 digit number between 0040 and 1800 (rpm)
    _INQUIRE_DEFAULT_FLOW_RATE = '?'  # returns the default flow rate (mL/min) at max speed 1800 rpm as "{5 digits
    # including decimal point} ml/min"
    # todo calibrated flow rate doesnt work in windows 10
    _INQUIRE_CALIBRATED_FLOW_RATE = '!'  # returns the calibrated flow rate (mL/min) at max speed 1800 rpm as
    # "{5 digits including decimal point} ml/min"
    _SET_CALIBRATED_FLOW_RATE = '!'  # followed by the calibrated flow rate (mL/min) at max speed 1800 rpm as a 4
    # digit number, the decimal point between the 3rd and 4th digits
    _INQUIRE_DIGITS_AFTER_DECIMAL = '['  # returns the number of digits after the decimal point at the max flow rate
    # and display with 4 digits
    _INQUIRE_DISPENSE_TIME_SECONDS = 'V'  # returns a number with units 1/10 second
    _SET_DISPENSE_TIME_SECONDS = 'V'  # followed by 4 digits (0000 - 9999) with units 1/10 second
    _SET_DISPENSE_TIME_MINUTES = 'VM'  # followed by 3 digits (000 - 899) with units minutes
    _SET_DISPENSE_TIME_HOURS = 'VH'  # followed by 3 digits (0000 - 999) with units hours
    _INQUIRE_DISPENSE_VOLUME_MODE_PISTON_STROKES = 'U'  # returns a number for the number of piston strokes for mode
    # dispense by volume
    _SET_DISPENSE_VOLUME_MODE_PISTON_STROKES = 'U'  # followed by the number of piston strokes for mode dispense by
    # volume as a 4 or 5 digit number (0001 - 65535)
    _SET_DISPENSE_VOLUME_MODE_PISTON_STROKES_65535_PLUS = 'u'  # followed by a 4 digit number Piston strokes = u * 65535
    # + U
    _INQUIRE_PISTON_STROKE_VOLUME = 'r'  # returns piston stroke volume in nanoliters as "{4 digit number}E{-|+}{1 digit}"
    _SET_PISTON_STROKE_VOLUME = 'r'  # followed by piston stroke volume in nanoliters as mmmmee where m is mantisse
    # and e is exponent (including -). returns the same return as _INQUIRE_PISTON_STROKE_VOLUME
    _SET_DEFAULT_ROLLER_STEP_VOLUME = 'r000000'
    _INQUIRE_FLOW_RATE = 'f'  # returns flow rate in mL/min as "{4 digit number}E{-|+}{1 digit}"
    _SET_FLOW_RATE = 'f'  # followed by flow rate in mL/min as mmmmee where m is mantisse  # and e is exponent
    # (including -). returns the same return as _INQUIRE_FLOW_RATE
    _INQUIRE_DISPENSE_VOLUME = 'v'  # returns dispensing volume in mL as "{4 digit number}E{-|+}{1 digit}"
    _SET_DISPENSE_VOLUME = 'v'  # followed by dispense volume in mL as mmmmee where m is mantisse and e is exponent
    # returns the same as _INQUIRE_DISPENSE_VOLUME
    _SET_DISPENSE_MODE_DISPENSE_VOLUME = '['  # followed by 5 digits. sets the dispense volume in mL for mode
    # dispense volume. the position of the decimal place depends on the pump-head and pump tubing. the entered
    # dispensing volume is rounded down to complete roller steps
    _INQUIRE_PISTON_STROKE_BACK_STEPS = '%'  # returns a number
    _SET_PISTON_STROKE_BACK_STEPS = '%'  # followed by a 4 digit number between 0000 - 0100
    _INQUIRE_PAUSE_TIME_SECONDS = 'T'  # returns a number,  units in 1/10 seconds
    _SET_PAUSE_TIME_SECONDS = 'T'  # followed by a 4 digit number between 0000 - 9999, units in 1/10 seconds
    _SET_PAUSE_TIME_MINUTES = 'TM'  # followed by a 3 digit number between 000 - 899, units in minutes
    _SET_PAUSE_TIME_HOURS = 'TH'  # followed by a 3 digit number between 000 - 999, units in hours
    _INQUIRE_N_DISPENSING_CYCLES = '"'  # returns the number of dispensing cycles
    _SET_N_DISPENSING_CYCLES = '"'  # followed by a 4 digit number between 0000 - 9999. the number of dispensing cycles
    _INQUIRE_TOTALLY_DELIVERED_V = ':'  # returns the totally delivered volume including a decimal point and the
    # units (ul, ml, or l)e.g. "4.983 ml"
    _RESET_TOTALLY_DELIVERED_V = 'W'  # resets totally delivered volume to 0
    _STORE_APPLICATION_PARAMETERS = '*'
    _SET_DEFAULT_VALUES = '0'
    # ------------------------------------
    # commands - input and outputs
    _INQUIRE_FOOTSWITCH = 'C'  # footswitch is Pin 6. returns _YES_RESPONSE or _NO_RESPONSE. yes if input is open,
    # no if input is closed
    _SET_MODE_FOOTSWITCH_TOGGLE = 'C0000'  # set mode footswitch to toggle
    _SET_MODE_FOOTSWITCH_DIRECT = 'C0001'  # set mode footswitch to direct
    # ------------------------------------
    # some commands themselves may be in multiple lists (commands that have input and no input version for setting or
    # inquiring about something). in the _send_and_receive function the common confirm response list is checked first
    # before the others

    # commands that will respond with _COMMON_CONFIRM_RESPONSE or _NO_RESPONSE
    _YES_COMMON_CONFIRM_RESPONSE_COMMANDS = [_START]

    # commands that will respond with _COMMON_CONFIRM_RESPONSE or _YES_RESPONSE, _NO_RESPONSE
    _YES_NO_COMMON_CONFIRM_RESPONSE_COMMANDS = [_SET_MODE_VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD]

    # the commands that will respond with _COMMON_CONFIRM_RESPONSE.
    _COMMON_CONFIRM_RESPONSE_COMMANDS = [_SET_ADDRESS, _RESET_OVERLOAD, _STOP, _SET_REVOLUTION_CLOCKWISE,
                                         _SET_REVOLUTION_COUNTER_CLOCKWISE,
                                         _SWITCH_CONTROL_PANEL_TO_MANUAL_OPERATION, _SET_CONTROL_PANEL_INACTIVE,
                                         _WRITE_NUMBERS_TO_CONTROL_PANEL, _WRITE_LETTERS_TO_CONTROL_PANEL,
                                         _SET_MODE_PUMP_RPM, _SET_MODE_PUMP_FLOW_RATE, _SET_MODE_DISPENSE_TIME,
                                         _SET_MODE_DISPENSE_VOLUME, _SET_MODE_PAUSE_TIME,
                                         _SET_MODE_DISPENSE_TIME_AND_PAUSE_TIME,
                                         _SET_MODE_DISPENSE_VOLUME_AND_PAUSE_TIME, _SET_MODE_TOTAL, ]

    # the commands that will respond with _YES_RESPONSE or _NO_RESPONSE
    _YES_NO_RESPONSE_COMMANDS = [_INQUIRE_PUMP_CURRENT_MODE_ACTIVE_OR_INACTIVE, _INQUIRE_FOOTSWITCH]

    # the commands that will respond with a multidigit reply (response will be concluded with
    # _MULTI_DIGIT_RESPONSE_LINE_ENDING)
    _MULTI_DIGIT_RESPONSE_COMMANDS = [_INQUIRE_SOFTWARE_VERSION, _INQUIRE_PUMP_TYPE_SOFTWARE_VERSION,
                                      _INQUIRE_PUMP_HEAD_IDENTIFICATION_NUMBER, _INQUIRE_SPEED,
                                      _INQUIRE_DEFAULT_FLOW_RATE, _INQUIRE_CALIBRATED_FLOW_RATE,
                                      _INQUIRE_DIGITS_AFTER_DECIMAL, _INQUIRE_DISPENSE_TIME_SECONDS,
                                      _INQUIRE_DISPENSE_VOLUME_MODE_PISTON_STROKES, _INQUIRE_PISTON_STROKE_VOLUME,
                                      _SET_PISTON_STROKE_VOLUME, _SET_DEFAULT_ROLLER_STEP_VOLUME, _INQUIRE_FLOW_RATE,
                                      _SET_FLOW_RATE, _INQUIRE_DISPENSE_VOLUME, _SET_DISPENSE_VOLUME,
                                      _INQUIRE_PISTON_STROKE_BACK_STEPS, _INQUIRE_PAUSE_TIME_SECONDS,
                                      _INQUIRE_N_DISPENSING_CYCLES, _INQUIRE_TOTALLY_DELIVERED_V]

    def __init__(self, device_port: str, address: int = 1):
        self._device_port = device_port
        self._address = address
        self.ser: Serial = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.logger.warning(f'The calibrated flow rate property is not supported in Windows 10. Using it will cause '
                            f'an error. Last fully compatible Windows OS is Windows 7')
        self.connect()

    @property
    def device_port(self) -> str:
        return self._device_port

    @property
    def address(self) -> int:
        return self._address

    @address.setter
    def address(self, value):
        response = self._send_and_receive(self._SET_ADDRESS, value)
        self.logger.debug(f'Set address to {value}')
        self._address = value

    @property
    def pump_type_software_version(self) -> str:
        response = self._send_and_receive(self._INQUIRE_PUMP_TYPE_SOFTWARE_VERSION)
        self.logger.debug(f'Pump type and software version: {response}')
        return response

    @property
    def pump_version(self) -> int:
        response = self._send_and_receive(self._INQUIRE_SOFTWARE_VERSION)
        self.logger.debug(f'Pump software version: {response}')
        return int(response)

    @property
    def pump_head_id_number(self) -> int:
        """ Read the pump head identification number"""
        response = self._send_and_receive(self._INQUIRE_PUMP_HEAD_IDENTIFICATION_NUMBER)
        self.logger.debug(f'Pump head ID number: {response}')
        return int(response)

    @pump_head_id_number.setter
    def pump_head_id_number(self, value) -> None:
        """
        Set the pump head identification number

        :param int, value: 4 digit identification number
        """
        id_number = value
        n_digits = 4
        if id_number is not None:
            if type(id_number) == int:
                if len(str(id_number)) < n_digits:
                    # pad with zeros
                    n_zeros_to_add = n_digits - len(str(id_number))
                    id_number = n_zeros_to_add * '0' + str(id_number)
                if len(str(id_number)) > n_digits:
                    raise CommandError(f'Pump id number must be a {n_digits} digit number')
                else:
                    id_number = (str(id_number))
                    # response is * if successful
                    response = self._send_and_receive(self._SET_PUMP_HEAD_IDENTIFICATION_NUMBER, id_number)
                    self.logger.debug(f'Set pump head ID number to {id_number}')

    def reset_overload(self) -> str:
        """

        :return: * if successful
        """
        response = self._send_and_receive(self._RESET_OVERLOAD)
        return response

    def connect(self):
        """Connect to the RegloCPF"""
        try:
            if self.ser is None:
                cn = Serial(device_port=self.device_port,
                            **self._CONNECTION_SETTINGS,
                            )
                self.ser = cn
            else:
                self.ser.connect()
            self.address = self.address
            self.logger.debug(f'Connected to RegloCPF, port: {self.device_port}, address: {self.address}')
            # Ensure that the serial port is closed on system exit
            atexit.register(self.disconnect)
        except Exception as e:
            self.logger.warning("Could not connect to an RegloCPF, make sure the right port was selected")
            raise PumpError("Could not connect to an RegloCPF, make sure the right port was selected")

    def disconnect(self):
        """Disconnect from the RegloCPF"""
        if self.ser is None:
            # if RegloCPF is already disconnected then self.ser is None
            return
        try:
            self.ser.disconnect()
            self.ser = None
            self.logger.debug('Disconnected from RegloCPF')
        except Exception as e:
            self.logger.warning("Could not disconnect from RegloCPF")
            raise PumpError("Could not disconnect from RegloCPF")

    def start(self) -> str:
        """
        :return: * if successful
        """
        response = self._send_and_receive(self._START)
        # response is _NO_RESPONSE under command G, in case of error message
        if response == self._NO_RESPONSE:
            raise PumpError(f'Failed to start RegloCPG, there is an error with the pump in the volume dependent '
                            f'dosing within a period mode')
        self.logger.debug('Start RegloCPF')
        return response

    def stop(self) -> str:
        """
        :return: * if successful
        """
        response = self._send_and_receive(self._STOP)
        self.logger.debug('Stop RegloCPF')
        return response

    def set_revolution_clockwise(self) -> str:
        """
        :return: * if successful
        """
        response = self._send_and_receive(self._SET_REVOLUTION_CLOCKWISE)
        self.logger.debug('Set revolution to clockwise')
        return response

    def set_revolution_counter_clockwise(self) -> str:
        """
        :return: * if successful
        """
        response = self._send_and_receive(self._SET_REVOLUTION_COUNTER_CLOCKWISE)
        self.logger.debug('Set revolution to counter clockwise')
        return response

    def set_control_panel_manual(self) -> str:
        """
        Switch control panel to manual operation

        :return: * if successful
        """
        response = self._send_and_receive(self._SWITCH_CONTROL_PANEL_TO_MANUAL_OPERATION)
        self.logger.debug('Switch control panel to manual operation')
        return response

    def inactivate_control_panel(self) -> str:
        """
        Set control panel inactive (input via control keys is not possible)

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_CONTROL_PANEL_INACTIVE)
        self.logger.debug('Set control panel inactive (input via control keys is not possible)')
        return response

    def write_to_control_panel(self, text: Union[str, float]) -> Union[str, None]:
        """
        Write the text to the control panel. Only 4 letters or 5 numbers (including decimal point) are allowed

        :return: * if successful
        """
        if type(text) == str:
            command = self._WRITE_LETTERS_TO_CONTROL_PANEL
            if len(text) > 4:
                text = input[:4]
        elif type(text) == float or type(text) == int:
            command = self._WRITE_NUMBERS_TO_CONTROL_PANEL
            if len(str(text)) > 5:
                text = float(str(str(text)[:5]))
        else:
            self.logger.warning(f'Cannot write {text} to the control panel, it must be letters or numbers only')
            return
        response = self._send_and_receive(command, text)
        self.logger.debug(f'Write {text} to the control panel')
        return response

    def set_mode(self, mode: str) -> str:
        """
        Set pump mode to one of self._MODES

        :return: * if successful, - or + means unsuccessful
        """
        if mode not in self._MODES:
            raise Exception()
        if mode == self._PUMP_RPM:
            response = self.set_mode_pump_rpm()
        elif mode == self._PUMP_FLOW_RATE:
            response = self.set_mode_pump_flow_rate()
        elif mode == self._DISPENSE_TIME:
            response = self.set_mode_dispense_time()
        elif mode == self._DISPENSE_VOLUME:
            response = self.set_mode_dispense_volume()
        elif mode == self._PAUSE_TIME:
            response = self.set_mode_pause_time()
        elif mode == self._DISPENSE_TIME_AND_PAUSE_TIME:
            response = self.set_mode_dispense_time_and_pause_time()
        elif mode == self._DISPENSE_VOLUME_AND_PAUSE_TIME:
            response = self.set_mode_dispense_volume_and_pause_time()
        elif mode == self._VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD:
            response = self.set_mode_volume_dependent_dosing_within_a_period()
        elif mode == self._TOTAL:
            response = self.set_mode_total()
        else:
            raise CommandError(f'Mode {mode} does not exist')
        return response

    def set_mode_pump_rpm(self) -> str:
        """
        Set pump mode to pump_rpm

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_PUMP_RPM)
        self.logger.debug('Set pump mode to pump rpm')
        return response

    def set_mode_pump_flow_rate(self) -> str:
        """
        Set pump mode to pump_flow_rate

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_PUMP_FLOW_RATE)
        self.logger.debug('Set pump mode to pump flow rate')
        return response

    def set_mode_dispense_time(self) -> str:
        """
        Set pump mode to dispense_time

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_DISPENSE_TIME)
        self.logger.debug('Set pump mode to dispense time')
        return response

    def set_mode_dispense_volume(self) -> str:
        """
        Set pump mode to dispense_volume

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_DISPENSE_VOLUME)
        self.logger.debug('Set pump mode to dispense volume')
        return response

    def set_mode_pause_time(self) -> str:
        """
        Set pump mode to pause_time

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_PAUSE_TIME)
        self.logger.debug('Set pump mode to pause time')
        return response

    def set_mode_dispense_time_and_pause_time(self) -> str:
        """
        Set pump mode to dispense_time_and_pause_time

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_DISPENSE_TIME_AND_PAUSE_TIME)
        self.logger.debug('Set pump mode to dispense time and pause time')
        return response

    def set_mode_dispense_volume_and_pause_time(self) -> str:
        """
        Set pump mode to dispense_volume_and_pause_time

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_DISPENSE_VOLUME_AND_PAUSE_TIME)
        self.logger.debug('Set pump mode to dispense volume and pause time')
        return response

    def set_mode_volume_dependent_dosing_within_a_period(self) -> str:
        """
        Set pump mode to volume_dependent_dosing_within_a_period

        :return: * if successful, - or + means unsuccessful
        """
        response = self._send_and_receive(self._SET_MODE_VOLUME_DEPENDENT_DOSING_WITHIN_A_PERIOD)
        # response is _NO_RESPONSE or _YES_RESPONSE then there is an error
        if response == self._NO_RESPONSE:
            self.logger.warning(f'Could not set pump mode to volume dependent dispensing within a period. \n'
                                f'Error indication 9999 (volume too large - time too short')

        elif response == self._YES_RESPONSE:
            self.logger.warning(f'Could not set pump mode to volume dependent dispensing within a period. \n'
                                f'Error indication 1111 (volume too small - time too long')
        else:
            self.logger.debug('Set pump mode to volume dependent dosing within a period')
        return response

    def set_mode_total(self) -> str:
        """
        Set pump mode to total

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_MODE_TOTAL)
        self.logger.debug('Set pump mode to total')
        return response

    def read_current_mode(self):
        """
        Read of the pump's current mode is active or inactive

        :return: + if active, - if inactive
        """
        r = '?'
        response = self._send_and_receive(self._INQUIRE_PUMP_CURRENT_MODE_ACTIVE_OR_INACTIVE)
        if response == self._YES_RESPONSE:
            r = 'active'
        elif response == self._NO_RESPONSE:
            r = 'inactive'
        self.logger.debug(f'Current pump mode active/inactive: {r}')
        return response

    @property
    def speed(self) -> int:
        """ Read the pump speed in rpm"""
        response = self._send_and_receive(self._INQUIRE_SPEED)
        self.logger.debug(f'Pump speed: {response} rpm')
        return int(response)

    @speed.setter
    def speed(self, value: int) -> None:
        """
        Set the pump speed with units rpm. Speed must be a 4 or 5 digit integer between 0040 and 1800

        :param int, value: speed (rpm) between 0040 to 1800, must be a 4 or 5 digit number
        """
        speed = value
        n_digits = 5
        if type(speed) == int:
            if len(str(speed)) < n_digits:
                # pad with zeros
                n_zeros_to_add = n_digits - len(str(speed))
                speed = n_zeros_to_add * '0' + str(speed)
            if int(speed) < 40 or int(speed) > 1800:
                raise CommandError(f'Speed must be between 0040 and 1800')
            else:
                speed = (str(speed))
                # response is * if successful
                response = self._send_and_receive(self._SET_SPEED, speed)
                self.logger.debug(f'Set speed to {speed} rpm')

    @property
    def default_flow_rate(self) -> float:
        """Read the default flow rate of the programmed pump-head in ml/min (at max. speed = 1800 rpm)"""
        response = self._send_and_receive(self._INQUIRE_DEFAULT_FLOW_RATE)
        self.logger.debug(f'Pump default flow rate: {response} at max. speed 1800 = 1800 rpm')
        response = response.replace('ml/min', '')
        return float(response)

    @property
    def calibrated_flow_rate(self) -> float:
        """Read the calibrated flow rate in mL/min (at max. speed = 1800 rpm)"""
        self.logger.warning('Not supported in Windows 10, will cause an error')
        response = self._send_and_receive(self._INQUIRE_CALIBRATED_FLOW_RATE)
        self.logger.debug(f'Pump calibrated flow rate: {response} at max. speed 1800 = 1800 rpm')
        response = response.replace('ml/min', '')
        return float(response)

    # todo not working right now, getting angle units back!!
    @calibrated_flow_rate.setter
    def calibrated_flow_rate(self, value: float) -> None:
        """
        Set the calibrated flow rate with units mL/min max. speed 1800 = 1800 rpm. To send the command to the pump,
        the command must have 4 digits only. The position of the decimal point depends on the programmed pump-head

        :param float, value: flow rate in mL/min, with a decimal point. e.g. 12.34
        """
        self.logger.warning('Not supported in Windows 10, will cause an error')
        n_digits = 4
        n_total = 5  # 4 digits plus decimal point
        n_digits_after_decimal = self.n_digits_after_decimal
        n_digits_before_decimal = n_digits - n_digits_after_decimal
        calibrated_flow_rate = value
        if type(calibrated_flow_rate) == float or type(calibrated_flow_rate) == int:
            if str(calibrated_flow_rate).find('.') == -1:
                # no decimal point so add one and trailing zeros
                calibrated_flow_rate = str(calibrated_flow_rate) + '.' + n_digits_after_decimal * '0'
            calibrated_flow_rate = str(calibrated_flow_rate)
            before_decimal_point = len(calibrated_flow_rate.split('.')[0])
            after_decimal_point = len(calibrated_flow_rate.split('.')[1])
            if after_decimal_point > n_digits_after_decimal:
                # too many digits after decimal point, remove them
                calibrated_flow_rate = calibrated_flow_rate[:before_decimal_point + 1 + n_digits_after_decimal]
            elif after_decimal_point < n_digits_after_decimal:
                # not enough digits after decimal point, add them
                n_zeros_to_add = n_digits_after_decimal - after_decimal_point
                calibrated_flow_rate = str(calibrated_flow_rate) + n_zeros_to_add * '0'
            if before_decimal_point > n_digits_before_decimal:
                # too many digits before decimal point
                raise CommandError(f'Calibrated flow rate must be a {n_digits} digit number with a decimal point and '
                                   f'{n_digits_after_decimal} digits after the decimal point')
            elif before_decimal_point < n_digits_before_decimal:
                # pad with zeros
                n_zeros_to_add = n_total - len(str(calibrated_flow_rate))
                calibrated_flow_rate = n_zeros_to_add * '0' + str(calibrated_flow_rate)
            calibrated_flow_rate = calibrated_flow_rate.replace('.', '')  # remove decimal point to send command to pump
            # response is * if successful
            response = self._send_and_receive(self._SET_CALIBRATED_FLOW_RATE, calibrated_flow_rate)
            self.logger.debug(f'Set calibrated flow rate to {calibrated_flow_rate} mL/min')

    @property
    def n_digits_after_decimal(self) -> int:
        """Read the number of digits after the decimal point (at max.flow rate) and display with 4 digits"""
        response = self._send_and_receive(self._INQUIRE_DIGITS_AFTER_DECIMAL)
        self.logger.debug(f'Number of digits after the decimal point (at max.flow rate) and display with 4 digits:'
                          f' {response}')
        return int(response)

    @property
    def dispensing_time(self) -> float:
        """Read the dispensing time rate in seconds"""
        response = self._send_and_receive(self._INQUIRE_DISPENSE_TIME_SECONDS)  # returned in 1/10 sec
        t = float(response) * 0.1
        self.logger.debug(f'Dispensing time: {t} seconds')
        return t

    def set_dispensing_time_s(self, t: int):
        """
        Set the dispensing time in seconds, between 0 and 999 seconds
        Command that gets sent to the pump can be sent as 0000-9999 1/10 sec

        :param float, t: dispensing time in seconds between 0 and 999 seconds
        """
        if type(t) != int:
            try:
                t = int(t)
            except Exception:
                raise CommandError('Dispensing time must be an integer')
        if t > 999 or t < 0:
            raise CommandError('Dispensing time must be between 0 and 999')
        # convert to 1/10 sec
        t = int(t / 0.1)
        n_digits = 4
        if len(str(t)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(t))
            t = n_zeros_to_add * '0' + str(t)
        # response is * if successful
        response = self._send_and_receive(self._SET_DISPENSE_TIME_SECONDS, t)
        self.logger.debug(f'Set dispensing time to {int(t) * 0.1} seconds')

    def set_dispensing_time_m(self, t: int):
        """
        Set the dispensing time in minutes, between 0 and 899 minutes
        Command that gets sent to the pump can be sent as 000-899 minutes

        :param float, t: dispensing time in min between 0 and 999 minutes
        """
        if type(t) != int:
            try:
                t = int(t)
            except Exception:
                raise CommandError('Dispensing time must be an integer')
        if t > 899 or t < 0:
            raise CommandError('Dispensing time must be between 0 and 999')
        n_digits = 3
        if len(str(t)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(t))
            t = n_zeros_to_add * '0' + str(t)
        # response is * if successful
        response = self._send_and_receive(self._SET_DISPENSE_TIME_MINUTES, t)
        self.logger.debug(f'Set dispensing time to {int(t)} minutes')

    def set_dispensing_time_h(self, t: int):
        """
        Set the dispensing time in hours, between 0 and 999 hours
        Command that gets sent to the pump can be sent as 000-999 hours

        :param float, t: dispensing time in hours between 0 and 999 hours
        """
        if type(t) != int:
            try:
                t = int(t)
            except Exception:
                raise CommandError('Dispensing time must be an integer')
        if t > 999 or t < 0:
            raise CommandError('Dispensing time must be between 0 and 999')
        n_digits = 3
        if len(str(t)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(t))
            t = n_zeros_to_add * '0' + str(t)
        # response is * if successful
        response = self._send_and_receive(self._SET_DISPENSE_TIME_HOURS, t)
        self.logger.debug(f'Set dispensing time to {int(t)} hours')

    @property
    def dispense_mode_piston_strokes(self) -> int:
        """Read the number of piston strokes for »MODE DISP Volume«"""
        response = self._send_and_receive(self._INQUIRE_DISPENSE_VOLUME_MODE_PISTON_STROKES)
        self.logger.debug(f'Piston strokes for MODE DISP Volume {response}"')
        return int(response)

    @dispense_mode_piston_strokes.setter
    def dispense_mode_piston_strokes(self, value: int):
        """
        Set the number of piston strokes for »MODE DISP Volume«. If the number to set is > 65535, then the
        _SET_DISPENSE_VOLUME_MODE_PISTON_STROKES_65535_PLUS command needs to be used.

        The total number of piston strokes is = (u * 65535) + U
        Where u is set by _SET_DISPENSE_VOLUME_MODE_PISTON_STROKES_65535_PLUS
            and U is set by _SET_DISPENSE_VOLUME_MODE_PISTON_STROKES

        :param int, value: number of piston strokes for mode dispense by volume
        :return:
        """
        if type(value) != int:
            try:
                value = int(value)
            except Exception:
                raise CommandError('Number of piston strokes for mode dispense by volume must be an integer')
        if value < 0:
            raise CommandError('Number of piston strokes for mode dispense by volume must be 0 or greater')
        U = value % 65535
        u = math.floor(value / 65535)
        n_strokes = (u * 65535) + U
        # to send the command to set U, the number needs to be either a 4 or 5 digit number
        if U > 9999:
            n_digits = 5
        else:
            n_digits = 4
        if len(str(U)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(U))
            U = n_zeros_to_add * '0' + str(U)
        # for u, number of digits must be 4
        if len(str(u)) < 4:
            # pad with zeros
            n_zeros_to_add = 4 - len(str(u))
            u = n_zeros_to_add * '0' + str(u)
        # response is * if successful
        response = self._send_and_receive(self._SET_DISPENSE_VOLUME_MODE_PISTON_STROKES, U)
        response = self._send_and_receive(self._SET_DISPENSE_VOLUME_MODE_PISTON_STROKES_65535_PLUS, u)
        self.logger.debug(f'Set number of piston strokes for mode dispense by volume to {n_strokes}')

    @property
    def piston_stroke_volume(self) -> float:
        """Read the piston stroke volume, units nanoliters. Command sends back E notation e.g. 9500E-1"""
        response = self._send_and_receive(self._INQUIRE_PISTON_STROKE_VOLUME)
        response = float(response)
        self.logger.debug(f'Piston stroke volume: {response} nL')
        return response

    # todo currently not working
    @piston_stroke_volume.setter
    def piston_stroke_volume(self, value: str) -> None:
        """
        Set the piston stroke volume, units nanoliters. Value should be in the form mmmmEee where m is mantisse and
        e is exponent (including + or -, and E is the letter E). e.g. 9500E-1

        Command to pump takes an argument as mmmmee where m is mantisse and e is exponent (including + or -,
        excluding E)
        Command sends back E notation e.g. 9500E-1
        Example: The command 1r9500-1 sets the piston stroke volume for pump at address 1 to 9500E-1 nL

        :param str, value: piston stroke volume in nanoliters as mmmmEee where m is mantisse and e is exponent (
            including + or -, and E is the letter E). e.g. 9500E-1
        """
        if type(value) != str:
            raise CommandError('Piston stroke volume must be a string in the format mmmmEee where m is mantisse and '
                               'e is exponent (including + or -, and E is the letter E). e.g. 9500E-1')
        if len(value) != 7:
            raise CommandError('Piston stroke volume must be a string in the format mmmmEee where m is mantisse and '
                               'e is exponent (including + or -, and E is the letter E). e.g. 9500E-1')
        value = value.replace('E', '')
        response = self._send_and_receive(self._SET_PISTON_STROKE_VOLUME, value)
        response = float(response)
        self.logger.debug(f'Set piston stroke volume: {float(response)} nL')

    @property
    def flow_rate(self) -> float:
        """Read flow rate, in mL/min"""
        response = self._send_and_receive(self._INQUIRE_FLOW_RATE)
        self.logger.debug(f'Flow rate: {float(response)} mL/min')
        return float(response)

    @flow_rate.setter
    def flow_rate(self, value: str) -> None:
        """
        Set the flow rate, units mL/min. Value should be in the form mmmmEee where m is mantisse and e is exponent (
        including + or -, and E is the letter E). e.g. 1200E-2

        Command to pump takes an argument as mmmmee where m is mantisse and e is exponent (including + or -,
        excluding E)
        Command sends back E notation e.g. 1200E-2
        Example: The command 1f1200-2 sets the flow rate for pump at address 1 to 1200E-2 mL/min

        :param str, value: flow rate in mL/min as mmmmEee where m is mantisse and e is exponent (
            including + or -, and E is the letter E). e.g. 1200E-2
        """
        if type(value) != str:
            raise CommandError('Flow rate (mL/min) must be a string in the format mmmmEee where m is mantisse and e '
                               'is exponent (including + or -, and E is the letter E). e.g. 1200E-2')
        if len(value) != 7:
            raise CommandError('Flow rate (mL/min) must be a string in the format mmmmEee where m is mantisse and e '
                               'is exponent (including + or -, and E is the letter E). e.g. 1200E-2')
        value = value.replace('E', '')
        response = self._send_and_receive(self._SET_FLOW_RATE, value)
        self.logger.debug(f'Set flow rate to: {response}')

    @property
    def dispensing_volume(self) -> float:
        """Read dispensing volume, mL"""
        response = self._send_and_receive(self._INQUIRE_DISPENSE_VOLUME)
        self.logger.debug(f'Dispensing volume: {float(response)} min')
        return float(response)

    @dispensing_volume.setter
    def dispensing_volume(self, value: str) -> None:
        """
        Set the dispensing volume, units mL. Value should be in the form mmmmEee where m is mantisse and e is exponent (
        including + or -, and E is the letter E). e.g. 6320E+1

        Command to pump takes an argument as mmmmee where m is mantisse and e is exponent (including + or -,
        excluding E)
        Command sends back E notation e.g. 6320E+1
        Example: The command 1v6320+1 sets the flow rate for pump at address 1 to 6320E+1 mL

        :param str, value: dispensing volume in mL as mmmmEee where m is mantisse and e is exponent (
            including + or -, and E is the letter E). e.g. 6320E+1
        """
        if type(value) != str:
            raise CommandError('Dispensing volume (mL) must be a string in the format mmmmEee where m is mantisse '
                               'and e is exponent (including + or -, and E is the letter E). e.g. 6320E+1')
        if len(value) != 7:
            raise CommandError('Dispensing volume (mL) must be a string in the format mmmmEee where m is mantisse '
                               'and e is exponent (including + or -, and E is the letter E). e.g. 6320E+1')
        value = value.replace('E', '')
        response = self._send_and_receive(self._SET_DISPENSE_VOLUME, value)
        response = float(response)
        self.logger.debug(f'Set dispensing volume to: {float(response)} mL/min')

    def set_dispense_mode_dispense_volume(self, volume: Union[int, float]):
        """
        Set the dispensing volume in mL for dispense mode. The entered dispensing volume is rounded down to complete
        roller steps The position of the decimal point depends on the programmed pump-head

        :param volume:
        :return: * if command is valid, # otherwise
        """
        n_digits = 5
        n_total = 6  # 5 digits plus decimal point
        n_digits_after_decimal = self.n_digits_after_decimal
        n_digits_before_decimal = n_digits - n_digits_after_decimal
        if type(volume) == float or type(volume) == int:
            if str(volume).find('.') == -1:
                # no decimal point so add one and trailing zeros
                volume = str(volume) + '.' + n_digits_after_decimal * '0'
            volume = str(volume)
            before_decimal_point = len(volume.split('.')[0])
            after_decimal_point = len(volume.split('.')[1])
            if after_decimal_point > n_digits_after_decimal:
                # too many digits after decimal point, remove them
                volume = volume[:before_decimal_point + 1 + n_digits_after_decimal]
            elif after_decimal_point < n_digits_after_decimal:
                # not enough digits after decimal point, add them
                n_zeros_to_add = n_digits_after_decimal - after_decimal_point
                volume = str(volume) + n_zeros_to_add * '0'
            if before_decimal_point > n_digits_before_decimal:
                # too many digits before decimal point
                raise CommandError(f'Dispense mode dispense volume must be a {n_digits} digit number with a decimal '
                                   f'point and {n_digits_after_decimal} digits after the decimal point')
            elif before_decimal_point < n_digits_before_decimal:
                # pad with zeros
                n_zeros_to_add = n_total - len(str(volume))
                volume = n_zeros_to_add * '0' + str(volume)
            volume_with_decimal = volume
            volume = volume.replace('.', '')  # remove decimal point to send command to pump
            # response is * if successful
            response = self._send_and_receive(self._SET_DISPENSE_MODE_DISPENSE_VOLUME, volume)
            self.logger.debug(f'Set dispense mode dispense volume rate to {volume_with_decimal} mL/min')

    @property
    def piston_stroke_back_steps(self) -> int:
        """Read the number of piston stroke back steps (between 0 - 100)"""
        response = self._send_and_receive(self._INQUIRE_PISTON_STROKE_BACK_STEPS)
        self.logger.debug(f'Number of piston stroke back steps: {float(response)}')
        return int(response)

    @piston_stroke_back_steps.setter
    def piston_stroke_back_steps(self, value: int):
        """
        Set the number of piston stroke back steps. Between 0 and 100 minutes
        Command that gets sent to the pump must be sent as a 4 digit number

        :param int, value: number of piston stroke back steps. Between 0 - 100
        """
        if type(value) != int:
            try:
                t = int(value)
            except Exception:
                raise CommandError('Number of piston stroke back steps must be an integer')
        if value > 100 or value < 0:
            raise CommandError('Number of piston stroke back strokes must be between 0 and 100')
        n_digits = 4
        if len(str(value)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(value))
            value = n_zeros_to_add * '0' + str(value)
        # response is * if successful
        response = self._send_and_receive(self._SET_PISTON_STROKE_BACK_STEPS, value)
        self.logger.debug(f'Set number of piston stroke back steps to {value}')

    @property
    def pause_time(self) -> float:
        """Read the pause time of the pump in seconds. Command sends back with units of 1/10 sec"""
        response = self._send_and_receive(self._INQUIRE_PAUSE_TIME_SECONDS)  # returned in 1/10 sec
        t = float(response) * 0.1
        self.logger.debug(f'Pause time: {t} seconds')
        return t

    def set_pause_time_s(self, t: int):
        """
        Set the pause time in seconds, between 0 and 999 seconds
        Command that gets sent to the pump can be sent as 0000-9999 1/10 sec

        :param float, t: pause time in seconds between 0 and 999 seconds
        """
        if type(t) != int:
            try:
                t = int(t)
            except Exception:
                raise CommandError('Pause time must be an integer')
        if t > 999 or t < 0:
            raise CommandError('Pause time must be between 0 and 999')
        # convert to 1/10 sec
        t = int(t / 0.1)
        n_digits = 4
        if len(str(t)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(t))
            t = n_zeros_to_add * '0' + str(t)
        # response is * if successful
        response = self._send_and_receive(self._SET_PAUSE_TIME_SECONDS, t)
        self.logger.debug(f'Set pause time to {t} seconds')

    def set_pause_time_m(self, t: int):
        """
        Set the pause time in minutes, between 0 and 899 minutes
        Command that gets sent to the pump can be sent as 000-899 minutes

        :param float, t: pause time in min between 0 and 999 minutes
        """
        if type(t) != int:
            try:
                t = int(t)
            except Exception:
                raise CommandError('Pause time must be an integer')
        if t > 899 or t < 0:
            raise CommandError('Pause time must be between 0 and 999')
        n_digits = 3
        if len(str(t)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(t))
            t = n_zeros_to_add * '0' + str(t)
        # response is * if successful
        response = self._send_and_receive(self._SET_PAUSE_TIME_MINUTES, t)
        self.logger.debug(f'Set pause time to {t} minutes')

    def set_pause_time_h(self, t: int):
        """
        Set the pause time in hours, between 0 and 999 hours
        Command that gets sent to the pump can be sent as 000-999 hours

        :param float, t: pause time in hours between 0 and 999 hours
        """
        if type(t) != int:
            try:
                t = int(t)
            except Exception:
                raise CommandError('Pause time must be an integer')
        if t > 999 or t < 0:
            raise CommandError('Pause time must be between 0 and 999')
        n_digits = 3
        if len(str(t)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(t))
            t = n_zeros_to_add * '0' + str(t)
        # response is * if successful
        response = self._send_and_receive(self._SET_PAUSE_TIME_HOURS, t)
        self.logger.debug(f'Set pause time to {t} hours')

    @property
    def dispense_cycles(self) -> int:
        """Read the number of dispensing cycles"""
        response = self._send_and_receive(self._INQUIRE_N_DISPENSING_CYCLES)
        self.logger.debug(f'Number of dispensing cycles: {response}')
        return int(response)

    @dispense_cycles.setter
    def dispense_cycles(self, value: int):
        """
        Set the number of dispense cycles. Number 0 and 9999
        Command that gets sent to the pump must be sent as a 4 digit number

        :param int, value: number of piston stroke back steps. Between 0 - 9999
        """
        if type(value) != int:
            try:
                t = int(value)
            except Exception:
                raise CommandError('Number of dispense cycles back steps must be an integer')
        if value > 9999 or value < 0:
            raise CommandError('Number of dispense cycles back must be between 0 and 9999')
        n_digits = 4
        if len(str(value)) < n_digits:
            # pad with zeros
            n_zeros_to_add = n_digits - len(str(value))
            value = n_zeros_to_add * '0' + str(value)
        # response is * if successful
        response = self._send_and_receive(self._SET_N_DISPENSING_CYCLES, value)
        self.logger.debug(f'Set number of dispense cycles to {value}')

    @property
    def total_volume(self) -> float:
        """Read the totally delivered volume (mL). Command sends back a number with ul, ml, or l attached to the end"""
        response = self._send_and_receive(self._INQUIRE_TOTALLY_DELIVERED_V)
        if response.find('ul') != -1:
            vol = float(response[:-2]) * 0.001
        elif response.find('ml') != -1:
            vol = float(response[:-2])
        else:
            vol = float(response[:-2]) * 1000
        self.logger.debug(f'Totally delivered volume: {vol} mL')
        return vol

    def reset_total_volume(self) -> str:
        """Resets the total delivered volume to 0 mL. Return * if successful"""
        response = self._send_and_receive(self._RESET_TOTALLY_DELIVERED_V)
        self.logger.debug(f'Reset totally delivered volume to 0 mL')
        return response

    # todo check if this works or not
    def set_roller_default_volume(self) -> float:
        """
        Set the default roller step volume. Command sends back E notation e.g. 9500E-1

        :return: default roller step volume. Units not specified in documentation but should be nL
        """
        response = self._send_and_receive(self._SET_DEFAULT_ROLLER_STEP_VOLUME)
        self.logger.debug(f'Set roller step volume to default volume: {response} nL')
        return float(response)

    def store_application_parameters(self):
        """:return: * if successful"""
        response = self._send_and_receive(self._STORE_APPLICATION_PARAMETERS)
        self.logger.debug('Store application parameters')
        return response

    def set_default_values(self) -> str:
        """
        Set pump values to default

        :return: * if successful
        """
        response = self._send_and_receive(self._SET_DEFAULT_VALUES)
        self.logger.debug('Set pump values to default')
        return response

    @property
    def footswitch(self) -> str:
        """Read if the footswitch is open (return _NO_RESPONSE) or grounded (return _YES_RESPONSE)"""
        response = self._send_and_receive(self._INQUIRE_FOOTSWITCH)
        if response == self._NO_RESPONSE:
            self.logger.debug(f'Footswitch is: open')

        elif response == self._YES_RESPONSE:
            self.logger.debug(f'Footswitch is: grounded')
        return response

    def set_footswitch_mode_toggle(self):
        """Set footswitch mode to toggle. Return * if success"""
        response = self._send_and_receive(self._SET_MODE_FOOTSWITCH_TOGGLE)
        self.logger.debug('Set footswitch mode to: toggle')
        return response

    def set_footswitch_mode_direct(self):
        """Set footswitch mode to direct. Return * if success"""
        response = self._send_and_receive(self._SET_MODE_FOOTSWITCH_DIRECT)
        self.logger.debug('Set footswitch mode to: direct')
        return response

    def _send_and_receive(self,
                          command: str,
                          parameter: str = None,
                          ) -> str:
        """
        Send a command, get a response back, and return the response. Some commands may send back a response with the
        multidigit response line ending or just the common response (*) depending if parameters are included in

        :param str, command: the string command to send to the RegloCPF
        :param str, parameter: any parameter to go with a command

        :return:
        """
        with self._lock:
            original_command = command
            # format the command if it should have the address in front of the command
            if command != self._SET_ADDRESS:
                command: str = str(self._address) + command
            # format the command if it has some parameter
            if parameter is not None:
                command: str = command + str(parameter)
            # format the command to have the command line ending
            command: str = command + self._COMMAND_LINE_ENDING
            command_encoded = command.encode()

            self.ser.write(data=command_encoded)
            response = self._read()
            if original_command in self._MULTI_DIGIT_RESPONSE_COMMANDS:
                if self._MULTI_DIGIT_RESPONSE_LINE_ENDING in response:
                    response = response.replace(self._MULTI_DIGIT_RESPONSE_LINE_ENDING, '')

            if response == self._OVERLOAD_RESPONSE or response == self._INCORRECT_COMMAND_RESPONSE:
                raise PumpOverloadError()
            return response

    def _read(self):
        time.sleep(0.055)
        num_bytes = self.ser.in_waiting
        # always read at least 1 byte, because that is the minimum response back from the pump
        bytes_to_read = num_bytes if num_bytes != 0 else 1
        data = self.ser.read(bytes_to_read)
        response = data.decode()
        return response




