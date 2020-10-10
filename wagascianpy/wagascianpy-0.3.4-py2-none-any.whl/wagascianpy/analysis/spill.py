import abc
from collections import namedtuple

import numpy

# compatible with Python 2 *and* 3
from typing import Union, Type, List

try:
    # noinspection PyUnresolvedReferences
    IntTypes = (int, long)  # Python2
except NameError:
    IntTypes = int  # Python3

# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

_NON_INITIALIZED_VALUE = -2

WAGASCI_SPILL_BEAM_MODE = 1
WAGASCI_SPILL_NO_BEAM_MODE = 0
IS_GOOD_SPILL = 1
NOT_GOOD_SPILL = 0
WAGASCI_MINIMUM_SPILL = 32768
WAGASCI_MAXIMUM_SPILL = 65535

SpillArrayInfo = namedtuple('SpillArrayInfo', ['name', 'array', 'type_char', 'type_str'])


class VirtualSpill(ABC):

    def are_all_defined(self):
        # type: (...) -> bool
        """
        Check if all fields of the spill object are defined (not undefined)
        :return: true if all fields are defined, false otherwise
        """
        for key, value in self.__dict__.items():
            if isinstance(value, (IntTypes, float, bool)):
                assert (value != _NON_INITIALIZED_VALUE), "instance variable {} is still not initialized".format(key)
            elif isinstance(value, numpy.ndarray):
                assert (not numpy.allclose(value, numpy.zeros(8, dtype=numpy.float64)))
        return True

    def pretty_print(self):
        """
        Print information about the spill
        :return: None
        """
        for key, value in self.__dict__.items():
            print("%s = %s" % (key, value))

    def _get_type_char(self, var_name):
        # type: (str) -> str
        """
        Get the character corresponding to the type of an attribute of the object.
        Only float, int and bool types are supported
        :param var_name: name of the attribute
        :return: type character
        """
        assert (hasattr(self, var_name)), \
            "object {} has not an attribute named {}".format(type(self).__name__, var_name)
        var = getattr(self, var_name)
        assert (isinstance(var, (IntTypes, float, bool, numpy.ndarray))), \
            "type of variable {} is not supported : {}".format(var_name, type(var_name).__name__)
        if isinstance(var, numpy.ndarray):
            var = var[0]
        if isinstance(var, bool):
            type_char = 'o'
        elif isinstance(var, IntTypes):
            type_char = 'i'
        elif isinstance(var, float):
            type_char = 'd'
        else:
            raise NotImplementedError("Type not recognized")
        return type_char

    def _get_numpy_type(self, var_name):
        # type: (str) -> Type[Union[numpy.int32, numpy.float64, numpy.bool]]
        """
        Get the numpy type corresponding to the type of an attribute of the object.
                Only float, int and bool types are supported
        :param var_name: name of the attribute
        :return: numpy type
        """
        type_char = self._get_type_char(var_name)
        if type_char == 'i':
            type_string = numpy.int32
        elif type_char == 'd':
            type_string = numpy.float64
        elif type_char == 'o':
            type_string = numpy.bool
        else:
            raise NotImplementedError("Type character not recognized : %s" % type_char)
        return type_string

    def _get_type_str(self, var_name):
        # type: (str) -> str
        """
        Get a string corresponding to the type of an attribute of the object.
        Only float, int and bool types are supported. This string is going to
        be passed to a TTree when creating a TBranch.
        :param var_name: name of the attribute
        :return: numpy type
        """
        type_char = self._get_type_char(var_name)
        value = getattr(self, var_name)
        if isinstance(value, numpy.ndarray) and value.size > 1:
            return '{}[{}]/{}'.format(var_name.strip('_'), value.size, type_char.upper())
        else:
            return '{}/{}'.format(var_name.strip('_'), type_char.upper())

    def _get_array(self, var_name):
        # type: (str) -> numpy.array
        """
        Create a numpy array containing an attribute of the object.
        :param var_name: name of the attribute
        :return: numpy array
        """
        assert (hasattr(self, var_name)), \
            "object {} has not an attribute named {}".format(type(self).__name__, var_name)
        value = getattr(self, var_name)
        if not isinstance(value, numpy.ndarray):
            return numpy.array([value], dtype=self._get_numpy_type(var_name))
        else:
            return value

    def _set_array(self, array_info):
        # type: (SpillArrayInfo) -> None
        """
        Set the array field of the SpillArrayInfo tuple to the relative attribute of this object
        :param array_info: SpillArrayInfo tuple
        :return: None
        """
        assert (hasattr(self, array_info.name)), \
            "object {} has not an attribute named {}".format(type(self).__name__, array_info.name)
        value = getattr(self, array_info.name)
        if isinstance(value, numpy.ndarray):
            numpy.copyto(array_info.array, value)
        else:
            array_info.array[0] = getattr(self, array_info.name)

    def get_array_list(self):
        # type: (...) -> List[SpillArrayInfo]
        """
        Create a list of SpillArrayInfo where each element contains an attribute of the object
        :return: list of SpillArrayInfo
        """
        array_list = []
        for key in self.__dict__:
            array_info = SpillArrayInfo(name=key.strip('_'),
                                        array=self._get_array(key),
                                        type_char=self._get_type_char(key),
                                        type_str=self._get_type_str(key))
            array_list.append(array_info)
        return array_list

    def set_array_list(self, array_list):
        # type: (List[SpillArrayInfo]) -> None
        """
        Set each element of a list of SpillArrayInfo to the relative attribute of the object
        :param array_list:
        :return:
        """
        for array_info in array_list:
            self._set_array(array_info)


class BsdSpill(VirtualSpill):
    """
    BSD spill
    """

    def __init__(self):
        self._bsd_spill_number = int(_NON_INITIALIZED_VALUE)
        self._converted_spill_number = int(_NON_INITIALIZED_VALUE)
        self._pot = float(_NON_INITIALIZED_VALUE)
        self._timestamp = float(_NON_INITIALIZED_VALUE)
        self._bsd_good_spill_flag = int(_NON_INITIALIZED_VALUE)
        self._t2k_run = int(_NON_INITIALIZED_VALUE)
        self._main_ring_run = int(_NON_INITIALIZED_VALUE)
        self._neutrino_daq_run = int(_NON_INITIALIZED_VALUE)
        self._horn_current = float(_NON_INITIALIZED_VALUE)
        self._neutrino_mode = int(_NON_INITIALIZED_VALUE)
        self._bunch_pot = numpy.zeros(8, dtype=numpy.float64)

    @property
    def bsd_spill_number(self):
        return self._bsd_spill_number

    @bsd_spill_number.setter
    def bsd_spill_number(self, bsd_spill_number):
        self._bsd_spill_number = int(bsd_spill_number)

    @property
    def converted_spill_number(self):
        return self._converted_spill_number

    @converted_spill_number.setter
    def converted_spill_number(self, converted_spill_number):
        self._converted_spill_number = int(converted_spill_number)

    @property
    def pot(self):
        return self._pot

    @pot.setter
    def pot(self, pot):
        self._pot = float(pot)

    @property
    def t2k_run(self):
        return self._t2k_run

    @t2k_run.setter
    def t2k_run(self, t2k_run):
        self._t2k_run = int(t2k_run)

    @property
    def main_ring_run(self):
        return self._main_ring_run

    @main_ring_run.setter
    def main_ring_run(self, main_ring_run):
        self._main_ring_run = int(main_ring_run)

    @property
    def neutrino_daq_run(self):
        return self._neutrino_daq_run

    @neutrino_daq_run.setter
    def neutrino_daq_run(self, neutrino_daq_run):
        self._neutrino_daq_run = int(neutrino_daq_run)

    @property
    def neutrino_mode(self):
        return self._neutrino_mode

    @neutrino_mode.setter
    def neutrino_mode(self, neutrino_mode):
        self._neutrino_mode = int(neutrino_mode)

    @property
    def horn_current(self):
        return self._horn_current

    @horn_current.setter
    def horn_current(self, horn_current):
        self._horn_current = float(horn_current)

    @property
    def bsd_good_spill_flag(self):
        return self._bsd_good_spill_flag

    @bsd_good_spill_flag.setter
    def bsd_good_spill_flag(self, bsd_good_spill_flag):
        self._bsd_good_spill_flag = int(bsd_good_spill_flag)

    @property
    def bunch_pot(self):
        return self._bunch_pot

    @bunch_pot.setter
    def bunch_pot(self, bunch_pot):
        if isinstance(bunch_pot, list):
            self._bunch_pot = numpy.array(bunch_pot, dtype=numpy.float64)
        elif isinstance(bunch_pot, numpy.ndarray):
            self._bunch_pot = bunch_pot
        else:
            raise TypeError("invalid bunch_pot type : {}".format(type(bunch_pot)))

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = float(timestamp)


class WagasciSpill(VirtualSpill):
    """
    WAGASCI spill number
    """

    def __init__(self):
        self._spill_count = int(_NON_INITIALIZED_VALUE)
        self._spill_number = int(_NON_INITIALIZED_VALUE)
        self._converted_spill_number = int(_NON_INITIALIZED_VALUE)
        self._spill_mode = int(_NON_INITIALIZED_VALUE)
        self._good_spill_flag = bool(_NON_INITIALIZED_VALUE)
        self._temperature = 0.
        self._humidity = 0.
        self._wagasci_run = int(_NON_INITIALIZED_VALUE)

    @property
    def spill_count(self):
        return self._spill_count

    @spill_count.setter
    def spill_count(self, spill_count):
        self._spill_count = int(spill_count)

    @property
    def spill_number(self):
        return self._spill_number

    @spill_number.setter
    def spill_number(self, spill_number):
        self._spill_number = int(spill_number)

    @property
    def spill_mode(self):
        return self._spill_mode

    @spill_mode.setter
    def spill_mode(self, spill_mode):
        self._spill_mode = int(spill_mode)

    @property
    def converted_spill_number(self):
        return self._converted_spill_number

    @converted_spill_number.setter
    def converted_spill_number(self, converted_spill_number):
        self._converted_spill_number = int(converted_spill_number)

    @property
    def good_spill_flag(self):
        return self._good_spill_flag

    @good_spill_flag.setter
    def good_spill_flag(self, good_spill_flag):
        assert good_spill_flag in [0, 1, False, True, "0", "1", "False", "True", "false", "true"], \
            "Invalid value of good spill flag"
        self._good_spill_flag = bool(good_spill_flag)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, temperature):
        self._temperature = float(temperature)

    @property
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, humidity):
        self._humidity = float(humidity)

    @property
    def wagasci_run(self):
        return self._wagasci_run

    @wagasci_run.setter
    def wagasci_run(self, wagasci_run):
        self._wagasci_run = int(wagasci_run)


class WagasciBsdSpill(WagasciSpill, BsdSpill):
    """
    WAGASCI spill number after spill matching with BSD spill
    """

    def __init__(self):
        super(WagasciSpill, self).__init__()
        super(BsdSpill, self).__init__()


class SpillFactory:
    """
    Factory design pattern to produce new spill objects
    """

    def __init__(self):
        pass

    @staticmethod
    def get_spill(type_of_spill):
        # type: (str) -> Union[WagasciSpill, BsdSpill, WagasciBsdSpill]
        """
        Produce a new spill object according to the type of spill
        :param type_of_spill: type of spill object to produce
        :return: spill object
        """
        if type_of_spill.lower() == "wagasci":
            return WagasciSpill()
        elif type_of_spill.lower() == "bsd":
            return BsdSpill()
        elif type_of_spill.lower().replace('_', '').replace(' ', '').replace('-', '') == "wagascibsd":
            return WagasciBsdSpill()
        else:
            raise ValueError("spill type not recognized : {}".format(type_of_spill))
