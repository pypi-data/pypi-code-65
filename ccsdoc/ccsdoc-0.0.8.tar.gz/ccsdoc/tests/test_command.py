from ccsdoc.command import Command
from ccsdoc.parameter import Argument

NAME = "setFilter"
TYPE = "ACTION"
LEVEL = "NORMAL"
DESCRIPTION = "Set filter."
ARGUMENT = Argument(name="filterId", ptype="str")


def test_command_simple():
    cmd = Command(name=NAME, cmdtype=TYPE, level=LEVEL, description=DESCRIPTION)

    assert repr(cmd) == f"{NAME}: {DESCRIPTION}"
    assert str(cmd) == f"Command[name={NAME}, type={TYPE}, level={LEVEL}, desc='{DESCRIPTION}']"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},{LEVEL},{DESCRIPTION},\n"

def test_command_with_arguments():
    cmd = Command(name=NAME, cmdtype=TYPE, level=LEVEL, description=DESCRIPTION, args=[ARGUMENT])

    assert repr(cmd) == f"{NAME}: {DESCRIPTION}"
    assert str(cmd) == f"Command[name={NAME}, type={TYPE}, level={LEVEL}, desc='{DESCRIPTION}', args=({repr(ARGUMENT)})]"
    assert cmd.to_csv("Toto") == f"Toto,{NAME},{TYPE},{LEVEL},{DESCRIPTION},{repr(ARGUMENT)}\n"
