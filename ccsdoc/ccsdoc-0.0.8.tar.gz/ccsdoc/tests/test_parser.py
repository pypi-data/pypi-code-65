from ccsdoc.command import Command
from ccsdoc.parameter import Argument
from ccsdoc.parameter import ConfigurationParameter
from ccsdoc.parser import extract_command_info
from ccsdoc.parser import extract_param_info
from ccsdoc.parser import get_command_position
from ccsdoc.parser import get_param_position
from ccsdoc.parser import split_and_remove_whitespace
from ccsdoc.parser import parse_raw_text



SPACED_TEXT_RAW = """public class Carousel extends MobileItem implements HardwareController, FilterHolder, AlertRaiser {

    @ConfigurationParameter(description = "Position margin to terminate movement.")
    protected int deltaPosition = 1000;

    @Command(type = Command.CommandType.ACTION, level = Command.NORMAL, description = "Set filter.")
    public void setFilter(int filterId) {"""

SPACED_TEXT_CLEANED = [
    "public class Carousel extends MobileItem implements HardwareController, FilterHolder, AlertRaiser {",
    "",
    '@ConfigurationParameter(description = "Position margin to terminate movement.")',
    "protected int deltaPosition = 1000;",
    "",
    '@Command(type = Command.CommandType.ACTION, level = Command.NORMAL, description = "Set filter.")',
    "public void setFilter(int filterId) {",
]
COMMAND_EMPTY = "@Command()"
COMMAND_BASIC = '@Command(type = Command.CommandType.ACTION, level = Command.ENGINEERING1, description = "Connect the loader hardware.")'
COMMAND_TWO_LINES = [
    '@Command(type = Command.CommandType.QUERY, level = Command.NORMAL, description = "First line."',
    '+ "Second line.")'
]
COMMAND_WITH_OVERRIDE = [
    COMMAND_BASIC,
    "@Override"
]
CONFIG_PARAM_NO_ARGS = '@ConfigurationParameter'
CONFIG_PARAM_WITH_ARGS = '@ConfigurationParameter(range = "0..500000", units = "milliseconds", description = "in milliseconds; if rotation lasts more than rotationTimeout, rotation is halted and the subsystem goes in error state.")'
CONFIG_PARAM_WITH_ARGS_NO_UNITS = '@ConfigurationParameter(range = "0..500000", description = "in milliseconds; if rotation lasts more than rotationTimeout, rotation is halted and the subsystem goes in error state.")'
CONFIG_PARAM_MULTILINE = [
    '@ConfigurationParameter(range = "0..500000", units = "milliseconds",',
    'description = "in milliseconds; if rotation lasts more than rotationTimeout, rotation is halted and the subsystem goes in error state.")'
]

def test_split_and_remove_whitespace_simple():
    assert split_and_remove_whitespace("  public void foo()  ") == ["public void foo()"]


def test_split_and_remove_whitespace_real():
    assert split_and_remove_whitespace(SPACED_TEXT_RAW) == SPACED_TEXT_CLEANED

def test_get_param_position_single():
    input_ = ["", "", CONFIG_PARAM_NO_ARGS]
    expected = [2]
    assert get_param_position(input_) == expected

def test_get_param_position_multiple():
    input_ = ["", CONFIG_PARAM_NO_ARGS, "", CONFIG_PARAM_NO_ARGS]
    expected = [1, 3]
    assert get_param_position(input_) == expected

def test_get_param_position_single_with_args():
    input_ = ["", CONFIG_PARAM_WITH_ARGS,]
    expected = [1]
    assert get_param_position(input_) == expected

def test_get_param_position_multiple_with_args():
    input_ = [CONFIG_PARAM_WITH_ARGS, "", CONFIG_PARAM_WITH_ARGS]
    expected = [0, 2]
    assert get_param_position(input_) == expected

def test_get_param_position_real():
    assert get_param_position(SPACED_TEXT_CLEANED) == [2]

def test_get_command_position_single():
    input_ = ["", COMMAND_EMPTY, ""]
    expected = [1]
    assert get_command_position(input_) == expected

def test_get_command_position_multiple():
    input_ = [COMMAND_EMPTY, "", COMMAND_EMPTY, COMMAND_EMPTY]
    expected = [0, 2, 3]
    assert get_command_position(input_) == expected

def test_get_command_position_with_arguments():
    input_ = ["", COMMAND_BASIC, "", CONFIG_PARAM_NO_ARGS, COMMAND_BASIC]
    expected = [1, 4]
    assert get_command_position(input_) == expected

def test_get_command_position_real():
    assert get_command_position(SPACED_TEXT_CLEANED) == [5]

def test_extract_command_info_basic():
    input_ = [COMMAND_BASIC, "public void myCommand() {"]
    cmd_position = 0
    result = extract_command_info(input_, cmd_position)
    expected = Command(
        name="myCommand", cmdtype="ACTION", level="ENGINEERING1",
        description="Connect the loader hardware.", args=[]
    )
    assert result == expected

def test_extract_command_info_multiline():
    input_ = COMMAND_TWO_LINES + ["public void myCommand() {"]
    cmd_position = 0
    result = extract_command_info(input_, cmd_position)
    expected = Command(
        name="myCommand", cmdtype="QUERY", level="NORMAL",
        description="First line. Second line.", args=[]
    )
    assert result == expected

def test_extract_command_info_override():
    input_ = COMMAND_WITH_OVERRIDE + ["public void myCommand() {"]
    cmd_position = 0
    result = extract_command_info(input_, cmd_position)
    expected = Command(
        name="myCommand", cmdtype="ACTION", level="ENGINEERING1",
        description="Connect the loader hardware.", args=[]
    )
    assert result == expected

def test_extract_command_info_real():
    input_ = SPACED_TEXT_CLEANED
    cmd_position = 5
    result = extract_command_info(input_, cmd_position)
    expected = Command(
        name="setFilter", cmdtype="ACTION", level="NORMAL",
        description="Set filter.", args=[Argument(name="filterId", ptype="int")]
    )
    assert result == expected


def test_extract_param_info_no_args():
    input_ = ["", CONFIG_PARAM_NO_ARGS, "public void myParam"]
    param_position = 1
    result = extract_param_info(input_, param_position)
    expected = ConfigurationParameter(
        name="myParam",
        ptype="void",
    )
    assert result == expected

def test_extract_param_info_basic():
    input_ = [CONFIG_PARAM_WITH_ARGS, "private int myParam"]
    param_position = 0
    result = extract_param_info(input_, param_position)
    expected = ConfigurationParameter(
        name="myParam",
        ptype="int",
        units="milliseconds",
        low=0,
        high=500000,
        description="In milliseconds; if rotation lasts more than rotationTimeout rotation is halted and the subsystem goes in error state."
    )
    assert result == expected

def test_extract_param_info_no_units_basic():
    input_ = [CONFIG_PARAM_WITH_ARGS_NO_UNITS, "private int myParam"]
    param_position = 0
    result = extract_param_info(input_, param_position)
    expected = ConfigurationParameter(
        name="myParam",
        ptype="int",
        low=0,
        high=500000,
        description="In milliseconds; if rotation lasts more than rotationTimeout rotation is halted and the subsystem goes in error state."
    )
    assert result == expected

def test_extract_param_info_multiline():
    input_ = CONFIG_PARAM_MULTILINE + ["private int myParam"]
    param_position = 0
    result = extract_param_info(input_, param_position)
    expected = ConfigurationParameter(
        name="myParam",
        ptype="int",
        units="milliseconds",
        low=0,
        high=500000,
        description="In milliseconds; if rotation lasts more than rotationTimeout rotation is halted and the subsystem goes in error state."
    )
    assert result == expected


def test_extract_param_info_real():
    input_ = SPACED_TEXT_CLEANED
    param_position = 2
    result = extract_param_info(input_, param_position)
    expected = ConfigurationParameter(
        name="deltaPosition",
        ptype="int",
        description="Position margin to terminate movement."
    )
    assert result == expected


def test_parse_raw_text():
    expected_commands = [
        Command(
            name="setFilter", cmdtype="ACTION", level="NORMAL",
            description="Set filter.", args=[Argument(name="filterId", ptype="int")]
        )
    ]
    expected_parameters = [
        ConfigurationParameter(name="deltaPosition", ptype="int", description="Position margin to terminate movement.")
    ]
    res_commands, res_parameters = parse_raw_text(SPACED_TEXT_RAW)

    for exp_cmd, res_cmd in zip(expected_commands, res_commands):
        assert exp_cmd == res_cmd

    for exp_param, res_param in zip(expected_parameters, res_parameters):
        assert exp_param == res_param
