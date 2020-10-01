# -*- coding: utf-8 -*-
# **********************************************************************
#
# Copyright (c) 2003-2017 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************
#
# Ice version 3.6.4
#
# <auto-generated>
#
# Generated from file `Units.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy

# Start of module omero
_M_omero = Ice.openModule('omero')
__name__ = 'omero'

# Start of module omero.model
_M_omero.model = Ice.openModule('omero.model')
__name__ = 'omero.model'

# Start of module omero.model.enums
_M_omero.model.enums = Ice.openModule('omero.model.enums')
__name__ = 'omero.model.enums'

if 'UnitsElectricPotential' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsElectricPotential = Ice.createTempClass()
    class UnitsElectricPotential(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsElectricPotential.YOTTAVOLT = UnitsElectricPotential("YOTTAVOLT", 0)
    UnitsElectricPotential.ZETTAVOLT = UnitsElectricPotential("ZETTAVOLT", 1)
    UnitsElectricPotential.EXAVOLT = UnitsElectricPotential("EXAVOLT", 2)
    UnitsElectricPotential.PETAVOLT = UnitsElectricPotential("PETAVOLT", 3)
    UnitsElectricPotential.TERAVOLT = UnitsElectricPotential("TERAVOLT", 4)
    UnitsElectricPotential.GIGAVOLT = UnitsElectricPotential("GIGAVOLT", 5)
    UnitsElectricPotential.MEGAVOLT = UnitsElectricPotential("MEGAVOLT", 6)
    UnitsElectricPotential.KILOVOLT = UnitsElectricPotential("KILOVOLT", 7)
    UnitsElectricPotential.HECTOVOLT = UnitsElectricPotential("HECTOVOLT", 8)
    UnitsElectricPotential.DECAVOLT = UnitsElectricPotential("DECAVOLT", 9)
    UnitsElectricPotential.VOLT = UnitsElectricPotential("VOLT", 10)
    UnitsElectricPotential.DECIVOLT = UnitsElectricPotential("DECIVOLT", 11)
    UnitsElectricPotential.CENTIVOLT = UnitsElectricPotential("CENTIVOLT", 12)
    UnitsElectricPotential.MILLIVOLT = UnitsElectricPotential("MILLIVOLT", 13)
    UnitsElectricPotential.MICROVOLT = UnitsElectricPotential("MICROVOLT", 14)
    UnitsElectricPotential.NANOVOLT = UnitsElectricPotential("NANOVOLT", 15)
    UnitsElectricPotential.PICOVOLT = UnitsElectricPotential("PICOVOLT", 16)
    UnitsElectricPotential.FEMTOVOLT = UnitsElectricPotential("FEMTOVOLT", 17)
    UnitsElectricPotential.ATTOVOLT = UnitsElectricPotential("ATTOVOLT", 18)
    UnitsElectricPotential.ZEPTOVOLT = UnitsElectricPotential("ZEPTOVOLT", 19)
    UnitsElectricPotential.YOCTOVOLT = UnitsElectricPotential("YOCTOVOLT", 20)
    UnitsElectricPotential._enumerators = { 0:UnitsElectricPotential.YOTTAVOLT, 1:UnitsElectricPotential.ZETTAVOLT, 2:UnitsElectricPotential.EXAVOLT, 3:UnitsElectricPotential.PETAVOLT, 4:UnitsElectricPotential.TERAVOLT, 5:UnitsElectricPotential.GIGAVOLT, 6:UnitsElectricPotential.MEGAVOLT, 7:UnitsElectricPotential.KILOVOLT, 8:UnitsElectricPotential.HECTOVOLT, 9:UnitsElectricPotential.DECAVOLT, 10:UnitsElectricPotential.VOLT, 11:UnitsElectricPotential.DECIVOLT, 12:UnitsElectricPotential.CENTIVOLT, 13:UnitsElectricPotential.MILLIVOLT, 14:UnitsElectricPotential.MICROVOLT, 15:UnitsElectricPotential.NANOVOLT, 16:UnitsElectricPotential.PICOVOLT, 17:UnitsElectricPotential.FEMTOVOLT, 18:UnitsElectricPotential.ATTOVOLT, 19:UnitsElectricPotential.ZEPTOVOLT, 20:UnitsElectricPotential.YOCTOVOLT }

    _M_omero.model.enums._t_UnitsElectricPotential = IcePy.defineEnum('::omero::model::enums::UnitsElectricPotential', UnitsElectricPotential, (), UnitsElectricPotential._enumerators)

    _M_omero.model.enums.UnitsElectricPotential = UnitsElectricPotential
    del UnitsElectricPotential

if 'UnitsFrequency' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsFrequency = Ice.createTempClass()
    class UnitsFrequency(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsFrequency.YOTTAHERTZ = UnitsFrequency("YOTTAHERTZ", 0)
    UnitsFrequency.ZETTAHERTZ = UnitsFrequency("ZETTAHERTZ", 1)
    UnitsFrequency.EXAHERTZ = UnitsFrequency("EXAHERTZ", 2)
    UnitsFrequency.PETAHERTZ = UnitsFrequency("PETAHERTZ", 3)
    UnitsFrequency.TERAHERTZ = UnitsFrequency("TERAHERTZ", 4)
    UnitsFrequency.GIGAHERTZ = UnitsFrequency("GIGAHERTZ", 5)
    UnitsFrequency.MEGAHERTZ = UnitsFrequency("MEGAHERTZ", 6)
    UnitsFrequency.KILOHERTZ = UnitsFrequency("KILOHERTZ", 7)
    UnitsFrequency.HECTOHERTZ = UnitsFrequency("HECTOHERTZ", 8)
    UnitsFrequency.DECAHERTZ = UnitsFrequency("DECAHERTZ", 9)
    UnitsFrequency.HERTZ = UnitsFrequency("HERTZ", 10)
    UnitsFrequency.DECIHERTZ = UnitsFrequency("DECIHERTZ", 11)
    UnitsFrequency.CENTIHERTZ = UnitsFrequency("CENTIHERTZ", 12)
    UnitsFrequency.MILLIHERTZ = UnitsFrequency("MILLIHERTZ", 13)
    UnitsFrequency.MICROHERTZ = UnitsFrequency("MICROHERTZ", 14)
    UnitsFrequency.NANOHERTZ = UnitsFrequency("NANOHERTZ", 15)
    UnitsFrequency.PICOHERTZ = UnitsFrequency("PICOHERTZ", 16)
    UnitsFrequency.FEMTOHERTZ = UnitsFrequency("FEMTOHERTZ", 17)
    UnitsFrequency.ATTOHERTZ = UnitsFrequency("ATTOHERTZ", 18)
    UnitsFrequency.ZEPTOHERTZ = UnitsFrequency("ZEPTOHERTZ", 19)
    UnitsFrequency.YOCTOHERTZ = UnitsFrequency("YOCTOHERTZ", 20)
    UnitsFrequency._enumerators = { 0:UnitsFrequency.YOTTAHERTZ, 1:UnitsFrequency.ZETTAHERTZ, 2:UnitsFrequency.EXAHERTZ, 3:UnitsFrequency.PETAHERTZ, 4:UnitsFrequency.TERAHERTZ, 5:UnitsFrequency.GIGAHERTZ, 6:UnitsFrequency.MEGAHERTZ, 7:UnitsFrequency.KILOHERTZ, 8:UnitsFrequency.HECTOHERTZ, 9:UnitsFrequency.DECAHERTZ, 10:UnitsFrequency.HERTZ, 11:UnitsFrequency.DECIHERTZ, 12:UnitsFrequency.CENTIHERTZ, 13:UnitsFrequency.MILLIHERTZ, 14:UnitsFrequency.MICROHERTZ, 15:UnitsFrequency.NANOHERTZ, 16:UnitsFrequency.PICOHERTZ, 17:UnitsFrequency.FEMTOHERTZ, 18:UnitsFrequency.ATTOHERTZ, 19:UnitsFrequency.ZEPTOHERTZ, 20:UnitsFrequency.YOCTOHERTZ }

    _M_omero.model.enums._t_UnitsFrequency = IcePy.defineEnum('::omero::model::enums::UnitsFrequency', UnitsFrequency, (), UnitsFrequency._enumerators)

    _M_omero.model.enums.UnitsFrequency = UnitsFrequency
    del UnitsFrequency

if 'UnitsLength' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsLength = Ice.createTempClass()
    class UnitsLength(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsLength.YOTTAMETER = UnitsLength("YOTTAMETER", 0)
    UnitsLength.ZETTAMETER = UnitsLength("ZETTAMETER", 1)
    UnitsLength.EXAMETER = UnitsLength("EXAMETER", 2)
    UnitsLength.PETAMETER = UnitsLength("PETAMETER", 3)
    UnitsLength.TERAMETER = UnitsLength("TERAMETER", 4)
    UnitsLength.GIGAMETER = UnitsLength("GIGAMETER", 5)
    UnitsLength.MEGAMETER = UnitsLength("MEGAMETER", 6)
    UnitsLength.KILOMETER = UnitsLength("KILOMETER", 7)
    UnitsLength.HECTOMETER = UnitsLength("HECTOMETER", 8)
    UnitsLength.DECAMETER = UnitsLength("DECAMETER", 9)
    UnitsLength.METER = UnitsLength("METER", 10)
    UnitsLength.DECIMETER = UnitsLength("DECIMETER", 11)
    UnitsLength.CENTIMETER = UnitsLength("CENTIMETER", 12)
    UnitsLength.MILLIMETER = UnitsLength("MILLIMETER", 13)
    UnitsLength.MICROMETER = UnitsLength("MICROMETER", 14)
    UnitsLength.NANOMETER = UnitsLength("NANOMETER", 15)
    UnitsLength.PICOMETER = UnitsLength("PICOMETER", 16)
    UnitsLength.FEMTOMETER = UnitsLength("FEMTOMETER", 17)
    UnitsLength.ATTOMETER = UnitsLength("ATTOMETER", 18)
    UnitsLength.ZEPTOMETER = UnitsLength("ZEPTOMETER", 19)
    UnitsLength.YOCTOMETER = UnitsLength("YOCTOMETER", 20)
    UnitsLength.ANGSTROM = UnitsLength("ANGSTROM", 21)
    UnitsLength.ASTRONOMICALUNIT = UnitsLength("ASTRONOMICALUNIT", 22)
    UnitsLength.LIGHTYEAR = UnitsLength("LIGHTYEAR", 23)
    UnitsLength.PARSEC = UnitsLength("PARSEC", 24)
    UnitsLength.THOU = UnitsLength("THOU", 25)
    UnitsLength.LINE = UnitsLength("LINE", 26)
    UnitsLength.INCH = UnitsLength("INCH", 27)
    UnitsLength.FOOT = UnitsLength("FOOT", 28)
    UnitsLength.YARD = UnitsLength("YARD", 29)
    UnitsLength.MILE = UnitsLength("MILE", 30)
    UnitsLength.POINT = UnitsLength("POINT", 31)
    UnitsLength.PIXEL = UnitsLength("PIXEL", 32)
    UnitsLength.REFERENCEFRAME = UnitsLength("REFERENCEFRAME", 33)
    UnitsLength._enumerators = { 0:UnitsLength.YOTTAMETER, 1:UnitsLength.ZETTAMETER, 2:UnitsLength.EXAMETER, 3:UnitsLength.PETAMETER, 4:UnitsLength.TERAMETER, 5:UnitsLength.GIGAMETER, 6:UnitsLength.MEGAMETER, 7:UnitsLength.KILOMETER, 8:UnitsLength.HECTOMETER, 9:UnitsLength.DECAMETER, 10:UnitsLength.METER, 11:UnitsLength.DECIMETER, 12:UnitsLength.CENTIMETER, 13:UnitsLength.MILLIMETER, 14:UnitsLength.MICROMETER, 15:UnitsLength.NANOMETER, 16:UnitsLength.PICOMETER, 17:UnitsLength.FEMTOMETER, 18:UnitsLength.ATTOMETER, 19:UnitsLength.ZEPTOMETER, 20:UnitsLength.YOCTOMETER, 21:UnitsLength.ANGSTROM, 22:UnitsLength.ASTRONOMICALUNIT, 23:UnitsLength.LIGHTYEAR, 24:UnitsLength.PARSEC, 25:UnitsLength.THOU, 26:UnitsLength.LINE, 27:UnitsLength.INCH, 28:UnitsLength.FOOT, 29:UnitsLength.YARD, 30:UnitsLength.MILE, 31:UnitsLength.POINT, 32:UnitsLength.PIXEL, 33:UnitsLength.REFERENCEFRAME }

    _M_omero.model.enums._t_UnitsLength = IcePy.defineEnum('::omero::model::enums::UnitsLength', UnitsLength, (), UnitsLength._enumerators)

    _M_omero.model.enums.UnitsLength = UnitsLength
    del UnitsLength

if 'UnitsPower' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsPower = Ice.createTempClass()
    class UnitsPower(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsPower.YOTTAWATT = UnitsPower("YOTTAWATT", 0)
    UnitsPower.ZETTAWATT = UnitsPower("ZETTAWATT", 1)
    UnitsPower.EXAWATT = UnitsPower("EXAWATT", 2)
    UnitsPower.PETAWATT = UnitsPower("PETAWATT", 3)
    UnitsPower.TERAWATT = UnitsPower("TERAWATT", 4)
    UnitsPower.GIGAWATT = UnitsPower("GIGAWATT", 5)
    UnitsPower.MEGAWATT = UnitsPower("MEGAWATT", 6)
    UnitsPower.KILOWATT = UnitsPower("KILOWATT", 7)
    UnitsPower.HECTOWATT = UnitsPower("HECTOWATT", 8)
    UnitsPower.DECAWATT = UnitsPower("DECAWATT", 9)
    UnitsPower.WATT = UnitsPower("WATT", 10)
    UnitsPower.DECIWATT = UnitsPower("DECIWATT", 11)
    UnitsPower.CENTIWATT = UnitsPower("CENTIWATT", 12)
    UnitsPower.MILLIWATT = UnitsPower("MILLIWATT", 13)
    UnitsPower.MICROWATT = UnitsPower("MICROWATT", 14)
    UnitsPower.NANOWATT = UnitsPower("NANOWATT", 15)
    UnitsPower.PICOWATT = UnitsPower("PICOWATT", 16)
    UnitsPower.FEMTOWATT = UnitsPower("FEMTOWATT", 17)
    UnitsPower.ATTOWATT = UnitsPower("ATTOWATT", 18)
    UnitsPower.ZEPTOWATT = UnitsPower("ZEPTOWATT", 19)
    UnitsPower.YOCTOWATT = UnitsPower("YOCTOWATT", 20)
    UnitsPower._enumerators = { 0:UnitsPower.YOTTAWATT, 1:UnitsPower.ZETTAWATT, 2:UnitsPower.EXAWATT, 3:UnitsPower.PETAWATT, 4:UnitsPower.TERAWATT, 5:UnitsPower.GIGAWATT, 6:UnitsPower.MEGAWATT, 7:UnitsPower.KILOWATT, 8:UnitsPower.HECTOWATT, 9:UnitsPower.DECAWATT, 10:UnitsPower.WATT, 11:UnitsPower.DECIWATT, 12:UnitsPower.CENTIWATT, 13:UnitsPower.MILLIWATT, 14:UnitsPower.MICROWATT, 15:UnitsPower.NANOWATT, 16:UnitsPower.PICOWATT, 17:UnitsPower.FEMTOWATT, 18:UnitsPower.ATTOWATT, 19:UnitsPower.ZEPTOWATT, 20:UnitsPower.YOCTOWATT }

    _M_omero.model.enums._t_UnitsPower = IcePy.defineEnum('::omero::model::enums::UnitsPower', UnitsPower, (), UnitsPower._enumerators)

    _M_omero.model.enums.UnitsPower = UnitsPower
    del UnitsPower

if 'UnitsPressure' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsPressure = Ice.createTempClass()
    class UnitsPressure(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsPressure.YOTTAPASCAL = UnitsPressure("YOTTAPASCAL", 0)
    UnitsPressure.ZETTAPASCAL = UnitsPressure("ZETTAPASCAL", 1)
    UnitsPressure.EXAPASCAL = UnitsPressure("EXAPASCAL", 2)
    UnitsPressure.PETAPASCAL = UnitsPressure("PETAPASCAL", 3)
    UnitsPressure.TERAPASCAL = UnitsPressure("TERAPASCAL", 4)
    UnitsPressure.GIGAPASCAL = UnitsPressure("GIGAPASCAL", 5)
    UnitsPressure.MEGAPASCAL = UnitsPressure("MEGAPASCAL", 6)
    UnitsPressure.KILOPASCAL = UnitsPressure("KILOPASCAL", 7)
    UnitsPressure.HECTOPASCAL = UnitsPressure("HECTOPASCAL", 8)
    UnitsPressure.DECAPASCAL = UnitsPressure("DECAPASCAL", 9)
    UnitsPressure.PASCAL = UnitsPressure("PASCAL", 10)
    UnitsPressure.DECIPASCAL = UnitsPressure("DECIPASCAL", 11)
    UnitsPressure.CENTIPASCAL = UnitsPressure("CENTIPASCAL", 12)
    UnitsPressure.MILLIPASCAL = UnitsPressure("MILLIPASCAL", 13)
    UnitsPressure.MICROPASCAL = UnitsPressure("MICROPASCAL", 14)
    UnitsPressure.NANOPASCAL = UnitsPressure("NANOPASCAL", 15)
    UnitsPressure.PICOPASCAL = UnitsPressure("PICOPASCAL", 16)
    UnitsPressure.FEMTOPASCAL = UnitsPressure("FEMTOPASCAL", 17)
    UnitsPressure.ATTOPASCAL = UnitsPressure("ATTOPASCAL", 18)
    UnitsPressure.ZEPTOPASCAL = UnitsPressure("ZEPTOPASCAL", 19)
    UnitsPressure.YOCTOPASCAL = UnitsPressure("YOCTOPASCAL", 20)
    UnitsPressure.BAR = UnitsPressure("BAR", 21)
    UnitsPressure.MEGABAR = UnitsPressure("MEGABAR", 22)
    UnitsPressure.KILOBAR = UnitsPressure("KILOBAR", 23)
    UnitsPressure.DECIBAR = UnitsPressure("DECIBAR", 24)
    UnitsPressure.CENTIBAR = UnitsPressure("CENTIBAR", 25)
    UnitsPressure.MILLIBAR = UnitsPressure("MILLIBAR", 26)
    UnitsPressure.ATMOSPHERE = UnitsPressure("ATMOSPHERE", 27)
    UnitsPressure.PSI = UnitsPressure("PSI", 28)
    UnitsPressure.TORR = UnitsPressure("TORR", 29)
    UnitsPressure.MILLITORR = UnitsPressure("MILLITORR", 30)
    UnitsPressure.MMHG = UnitsPressure("MMHG", 31)
    UnitsPressure._enumerators = { 0:UnitsPressure.YOTTAPASCAL, 1:UnitsPressure.ZETTAPASCAL, 2:UnitsPressure.EXAPASCAL, 3:UnitsPressure.PETAPASCAL, 4:UnitsPressure.TERAPASCAL, 5:UnitsPressure.GIGAPASCAL, 6:UnitsPressure.MEGAPASCAL, 7:UnitsPressure.KILOPASCAL, 8:UnitsPressure.HECTOPASCAL, 9:UnitsPressure.DECAPASCAL, 10:UnitsPressure.PASCAL, 11:UnitsPressure.DECIPASCAL, 12:UnitsPressure.CENTIPASCAL, 13:UnitsPressure.MILLIPASCAL, 14:UnitsPressure.MICROPASCAL, 15:UnitsPressure.NANOPASCAL, 16:UnitsPressure.PICOPASCAL, 17:UnitsPressure.FEMTOPASCAL, 18:UnitsPressure.ATTOPASCAL, 19:UnitsPressure.ZEPTOPASCAL, 20:UnitsPressure.YOCTOPASCAL, 21:UnitsPressure.BAR, 22:UnitsPressure.MEGABAR, 23:UnitsPressure.KILOBAR, 24:UnitsPressure.DECIBAR, 25:UnitsPressure.CENTIBAR, 26:UnitsPressure.MILLIBAR, 27:UnitsPressure.ATMOSPHERE, 28:UnitsPressure.PSI, 29:UnitsPressure.TORR, 30:UnitsPressure.MILLITORR, 31:UnitsPressure.MMHG }

    _M_omero.model.enums._t_UnitsPressure = IcePy.defineEnum('::omero::model::enums::UnitsPressure', UnitsPressure, (), UnitsPressure._enumerators)

    _M_omero.model.enums.UnitsPressure = UnitsPressure
    del UnitsPressure

if 'UnitsTemperature' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsTemperature = Ice.createTempClass()
    class UnitsTemperature(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsTemperature.KELVIN = UnitsTemperature("KELVIN", 0)
    UnitsTemperature.CELSIUS = UnitsTemperature("CELSIUS", 1)
    UnitsTemperature.FAHRENHEIT = UnitsTemperature("FAHRENHEIT", 2)
    UnitsTemperature.RANKINE = UnitsTemperature("RANKINE", 3)
    UnitsTemperature._enumerators = { 0:UnitsTemperature.KELVIN, 1:UnitsTemperature.CELSIUS, 2:UnitsTemperature.FAHRENHEIT, 3:UnitsTemperature.RANKINE }

    _M_omero.model.enums._t_UnitsTemperature = IcePy.defineEnum('::omero::model::enums::UnitsTemperature', UnitsTemperature, (), UnitsTemperature._enumerators)

    _M_omero.model.enums.UnitsTemperature = UnitsTemperature
    del UnitsTemperature

if 'UnitsTime' not in _M_omero.model.enums.__dict__:
    _M_omero.model.enums.UnitsTime = Ice.createTempClass()
    class UnitsTime(Ice.EnumBase):

        def __init__(self, _n, _v):
            Ice.EnumBase.__init__(self, _n, _v)

        def valueOf(self, _n):
            if _n in self._enumerators:
                return self._enumerators[_n]
            return None
        valueOf = classmethod(valueOf)

    UnitsTime.YOTTASECOND = UnitsTime("YOTTASECOND", 0)
    UnitsTime.ZETTASECOND = UnitsTime("ZETTASECOND", 1)
    UnitsTime.EXASECOND = UnitsTime("EXASECOND", 2)
    UnitsTime.PETASECOND = UnitsTime("PETASECOND", 3)
    UnitsTime.TERASECOND = UnitsTime("TERASECOND", 4)
    UnitsTime.GIGASECOND = UnitsTime("GIGASECOND", 5)
    UnitsTime.MEGASECOND = UnitsTime("MEGASECOND", 6)
    UnitsTime.KILOSECOND = UnitsTime("KILOSECOND", 7)
    UnitsTime.HECTOSECOND = UnitsTime("HECTOSECOND", 8)
    UnitsTime.DECASECOND = UnitsTime("DECASECOND", 9)
    UnitsTime.SECOND = UnitsTime("SECOND", 10)
    UnitsTime.DECISECOND = UnitsTime("DECISECOND", 11)
    UnitsTime.CENTISECOND = UnitsTime("CENTISECOND", 12)
    UnitsTime.MILLISECOND = UnitsTime("MILLISECOND", 13)
    UnitsTime.MICROSECOND = UnitsTime("MICROSECOND", 14)
    UnitsTime.NANOSECOND = UnitsTime("NANOSECOND", 15)
    UnitsTime.PICOSECOND = UnitsTime("PICOSECOND", 16)
    UnitsTime.FEMTOSECOND = UnitsTime("FEMTOSECOND", 17)
    UnitsTime.ATTOSECOND = UnitsTime("ATTOSECOND", 18)
    UnitsTime.ZEPTOSECOND = UnitsTime("ZEPTOSECOND", 19)
    UnitsTime.YOCTOSECOND = UnitsTime("YOCTOSECOND", 20)
    UnitsTime.MINUTE = UnitsTime("MINUTE", 21)
    UnitsTime.HOUR = UnitsTime("HOUR", 22)
    UnitsTime.DAY = UnitsTime("DAY", 23)
    UnitsTime._enumerators = { 0:UnitsTime.YOTTASECOND, 1:UnitsTime.ZETTASECOND, 2:UnitsTime.EXASECOND, 3:UnitsTime.PETASECOND, 4:UnitsTime.TERASECOND, 5:UnitsTime.GIGASECOND, 6:UnitsTime.MEGASECOND, 7:UnitsTime.KILOSECOND, 8:UnitsTime.HECTOSECOND, 9:UnitsTime.DECASECOND, 10:UnitsTime.SECOND, 11:UnitsTime.DECISECOND, 12:UnitsTime.CENTISECOND, 13:UnitsTime.MILLISECOND, 14:UnitsTime.MICROSECOND, 15:UnitsTime.NANOSECOND, 16:UnitsTime.PICOSECOND, 17:UnitsTime.FEMTOSECOND, 18:UnitsTime.ATTOSECOND, 19:UnitsTime.ZEPTOSECOND, 20:UnitsTime.YOCTOSECOND, 21:UnitsTime.MINUTE, 22:UnitsTime.HOUR, 23:UnitsTime.DAY }

    _M_omero.model.enums._t_UnitsTime = IcePy.defineEnum('::omero::model::enums::UnitsTime', UnitsTime, (), UnitsTime._enumerators)

    _M_omero.model.enums.UnitsTime = UnitsTime
    del UnitsTime

# End of module omero.model.enums

__name__ = 'omero.model'

# End of module omero.model

__name__ = 'omero'

# End of module omero
