import pytest

from ccsdoc.text import clean_command_level
from ccsdoc.text import clean_command_type
from ccsdoc.text import clean_description
from ccsdoc.text import extract_command_arguments
from ccsdoc.text import extract_command_name
from ccsdoc.text import extract_method_arguments
from ccsdoc.text import extract_parameter_arguments
from ccsdoc.text import extract_parameter_name_and_type
from ccsdoc.text import extract_range_values
from ccsdoc.text import is_command
from ccsdoc.text import is_config_parameter
from ccsdoc.text import is_correct_command_entry
from ccsdoc.text import is_correct_parameter_entry

METHOD_RAW = "    public List<String> listLoaderHardwareNames() {"
METHOD_NO_ARG = "public void setFilter() {"
METHOD_SINGLE_ARG = "public void setFilter(int filterID) {"
METHOD_MULTIPLE_ARG = "public void setFilter(int filterID, boolean isTrue) {"
COMMAND_EMPTY = "@Command()"
COMMAND_BASIC = '@Command(type = Command.CommandType.ACTION, level = Command.ENGINEERING1, description = "Connect the loader hardware.")'
COMMAND_DESCRIPTION_WITH_COMA = '@Command(type = Command.CommandType.QUERY, level = Command.ENGINEERING1, description = "Do this, and that.")'
COMMAND_MISSING_DESCRIPTION = '@Command(type = Command.CommandType.ACTION, level = Command.NORMAL)'
COMMAND_RAW = r"""@Command(type = Command.CommandType.QUERY, level = Command.NORMAL, description = "Return true if autochanger trucks are at ONLINE. " + "This command doesn't read again the sensors.")"""
CONFIG_PARAM_WITH_RANGE = '@ConfigurationParameter(range = "-4500000..4500000", description = " carousel position when this socket is at standby")'
CONFIG_PARAM_WITH_COMA = '@ConfigurationParameter(description = "Carousel position, when this socket is at standby")'
PARAM_NAME = "private int standbyPosition;"
PARAM_NAME_WITH_DEFAULT_VALUE = "private int onlinePosition = 77000;"

def test_is_command():
    assert is_command(COMMAND_BASIC)
    assert is_command(COMMAND_EMPTY)
    assert is_command(COMMAND_RAW)
    assert not is_command(METHOD_NO_ARG)
    assert not is_command(METHOD_RAW)
    assert not is_command(CONFIG_PARAM_WITH_RANGE)


def test_is_config_parameter():
    assert is_config_parameter(CONFIG_PARAM_WITH_COMA)
    assert is_config_parameter(CONFIG_PARAM_WITH_RANGE)
    assert not is_config_parameter(COMMAND_BASIC)
    assert not is_config_parameter(COMMAND_EMPTY)
    assert not is_config_parameter(COMMAND_RAW)
    assert not is_config_parameter(METHOD_NO_ARG)
    assert not is_config_parameter(METHOD_RAW)



def test_is_correct_command_entry():
    assert is_correct_command_entry("type")
    assert is_correct_command_entry("level")
    assert is_correct_command_entry("description")
    assert is_correct_command_entry("timeout")
    assert is_correct_command_entry("autoAck")
    assert is_correct_command_entry("alias")
    assert not is_correct_command_entry("name")
    assert not is_correct_command_entry("command")


def test_is_correct_parameter_entry():
    assert is_correct_parameter_entry("range")
    assert is_correct_parameter_entry("description")
    assert is_correct_parameter_entry("category")
    assert is_correct_parameter_entry("is_final")
    assert not is_correct_parameter_entry("alias")
    assert not is_correct_parameter_entry("level")
    assert not is_correct_parameter_entry("timeout")
    assert not is_correct_parameter_entry("autoAck")


def test_extract_command_arguments_basic():
    args = dict(
        type="Command.CommandType.ACTION",
        level="Command.ENGINEERING1",
        description='"Connect the loader hardware."'
    )
    assert extract_command_arguments(COMMAND_BASIC) == args


def test_extract_command_arguments_with_coma():
    args = dict(
        type="Command.CommandType.QUERY",
        level="Command.ENGINEERING1",
        description='"Do this and that."'
    )
    assert extract_command_arguments(COMMAND_DESCRIPTION_WITH_COMA) == args


def test_extract_command_arguments_raw():
    args = dict(
        type="Command.CommandType.QUERY",
        level="Command.NORMAL",
        description='''"Return true if autochanger trucks are at ONLINE. " + "This command doesn't read again the sensors."'''
    )
    assert extract_command_arguments(COMMAND_RAW) == args


def test_extract_command_arguments_missing_arguments():
    with pytest.raises(ValueError):
        extract_command_arguments(COMMAND_MISSING_DESCRIPTION)


def test_extract_command_name_no_args():
    assert extract_command_name(METHOD_NO_ARG) == "setFilter"


def test_extract_command_name_raw():
    assert extract_command_name(METHOD_RAW) == "listLoaderHardwareNames"


def test_extract_method_arguments_no_args():
    res_no_arg = extract_method_arguments(METHOD_NO_ARG)
    assert res_no_arg == {}


def test_extract_method_arguments_single_arg():
    res_single_arg = extract_method_arguments(METHOD_SINGLE_ARG)
    assert res_single_arg == {"filterID": "int"}


def test_extract_method_arguments_multiple_args():
    res_multiple_arg = extract_method_arguments(METHOD_MULTIPLE_ARG)
    assert res_multiple_arg == {"filterID": "int", "isTrue": "boolean"}


def test_extract_parameter_name_and_type():
    assert extract_parameter_name_and_type(PARAM_NAME) == ("standbyPosition", "int")
    assert extract_parameter_name_and_type(PARAM_NAME_WITH_DEFAULT_VALUE) == ("onlinePosition", "int")


def test_extract_parameters_arguments():
    expected = dict(
        description='"Carousel position when this socket is at standby"'
    )
    assert extract_parameter_arguments(CONFIG_PARAM_WITH_COMA) == expected

def test_extract_parameters_arguments_with_range():
    expected = dict(
        range='"-4500000..4500000"',
        description='" carousel position when this socket is at standby"'
    )
    assert extract_parameter_arguments(CONFIG_PARAM_WITH_RANGE) == expected

def test_extract_range_values():
    assert extract_range_values('"-450..450"') == (-450, 450)
    assert extract_range_values('-450..450') == (-450, 450)
    assert extract_range_values('"..450"') == (None, 450)
    assert extract_range_values('"0.."') == (0, None)

def test_clean_command_level():
    assert clean_command_level("Command.ENGINEERING1") == "ENGINEERING1"
    assert clean_command_level("Command.NORMAL") == "NORMAL"
    assert clean_command_level("NORMAL") == "NORMAL"


def test_clean_command_type():
    assert clean_command_type("Command.CommandType.QUERY") == "QUERY"
    assert clean_command_type("CommandType.ACTION") == "ACTION"
    assert clean_command_type("QUERY") == "QUERY"


def test_clean_description_basic():
    expected = "Connect the loader hardware."
    assert clean_description('"Connect the loader hardware."') == expected


def test_clean_description_raw():
    expected = "Return true if autochanger trucks are at online. This command doesn't read again the sensors."
    assert clean_description('''"Return true if autochanger trucks are at ONLINE. " + "This command doesn't read again the sensors."''') == expected
