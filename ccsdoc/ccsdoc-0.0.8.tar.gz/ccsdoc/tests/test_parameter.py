from ccsdoc.parameter import Argument
from ccsdoc.parameter import Parameter
from ccsdoc.parameter import ConfigurationParameter

NAME = "standbyPosition"
TYPE = "int"
UNITS = "microns"
DESCRIPTION = "Position at standby on the trucks in microns"
RANGE_LOW = 0
RANGE_HIGH = 1000


def test_parameter_simple():
    cmd = Parameter(name=NAME, ptype=TYPE, description=DESCRIPTION)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(cmd) == f"Parameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}']"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},{DESCRIPTION}\n"

def test_parameter_nodescription():
    cmd = Parameter(name=NAME, ptype=TYPE, description=None)

    assert repr(cmd) == f"{TYPE} {NAME}"
    assert str(cmd) == f"Parameter[name={NAME}, type={TYPE}]"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},\n"

def test_configparameter_norange():
    cmd = ConfigurationParameter(name=NAME, ptype=TYPE, units=UNITS, description=DESCRIPTION)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}', units='{UNITS}', range=[UNDEFINED, UNDEFINED]]"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},{UNITS},UNDEFINED,UNDEFINED,{DESCRIPTION}\n"

def test_configparameter_nounits():
    cmd = ConfigurationParameter(name=NAME, ptype=TYPE, description=DESCRIPTION)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}', units='UNDEFINED', range=[UNDEFINED, UNDEFINED]]"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},UNDEFINED,UNDEFINED,UNDEFINED,{DESCRIPTION}\n"

def test_configparameter_norange_nounits():
    cmd = ConfigurationParameter(name=NAME, ptype=TYPE, description=DESCRIPTION)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}', units='UNDEFINED', range=[UNDEFINED, UNDEFINED]]"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},UNDEFINED,UNDEFINED,UNDEFINED,{DESCRIPTION}\n"


def test_configparameter_nohigh():
    cmd = ConfigurationParameter(
        name=NAME, ptype=TYPE, low=RANGE_LOW, units=UNITS, description=DESCRIPTION)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(
        cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}', units='{UNITS}', range=[{RANGE_LOW}, UNDEFINED]]"
    assert cmd.to_csv(
        "Toto") == f"Toto,{NAME},{TYPE},{UNITS},{RANGE_LOW},UNDEFINED,{DESCRIPTION}\n"


def test_configparameter_nolow():
    cmd = ConfigurationParameter(
        name=NAME, ptype=TYPE, high=RANGE_HIGH, units=UNITS, description=DESCRIPTION)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(
        cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}', units='{UNITS}', range=[UNDEFINED, {RANGE_HIGH}]]"
    assert cmd.to_csv(
        "Toto") == f"Toto,{NAME},{TYPE},{UNITS},UNDEFINED,{RANGE_HIGH},{DESCRIPTION}\n"

def test_configparameter_nodescription():
    cmd = ConfigurationParameter(name=NAME, ptype=TYPE, low=RANGE_LOW, high=RANGE_HIGH, units=UNITS, description=None)

    assert repr(cmd) == f"{TYPE} {NAME}"
    assert str(
        cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, units='{UNITS}', range=[{RANGE_LOW}, {RANGE_HIGH}]]"
    assert cmd.to_csv(
        "Toto") == f"Toto,{NAME},{TYPE},{UNITS},{RANGE_LOW},{RANGE_HIGH},\n"

def test_configparameter_deprecated():
    cmd = ConfigurationParameter(name=NAME, ptype=TYPE, units=UNITS, description=DESCRIPTION, is_deprecated=True)

    assert repr(cmd) == f"{TYPE} {NAME}: {DESCRIPTION}"
    assert str(
        cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, desc='{DESCRIPTION}', units='{UNITS}', range=[UNDEFINED, UNDEFINED]](DEPRECATED)"
    assert cmd.to_csv(
        "Toto") == f"Toto,{NAME},{TYPE},{UNITS},UNDEFINED,UNDEFINED,{DESCRIPTION}\n"

def test_configparameter_nodescription_deprecated():
    cmd = ConfigurationParameter(name=NAME, ptype=TYPE, units=UNITS, description=None, is_deprecated=True)

    assert repr(cmd) == f"{TYPE} {NAME}"
    assert str(
        cmd) == f"ConfigurationParameter[name={NAME}, type={TYPE}, units='{UNITS}', range=[UNDEFINED, UNDEFINED]](DEPRECATED)"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},{UNITS},UNDEFINED,UNDEFINED,\n"

def test_argument_simple():
    cmd = Argument(name=NAME, ptype=TYPE)

    assert repr(cmd) == f"{TYPE} {NAME}"
    assert str(cmd) == f"Argument[name={NAME}, type={TYPE}]"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},\n"
