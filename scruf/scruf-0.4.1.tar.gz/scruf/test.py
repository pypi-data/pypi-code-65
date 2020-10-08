import enum
import typing

from scruf import compare


class OutputSpec:
    """
    Specification of the expected output of a test

    Attributes
    ----------
    type: scruf.compare.ComparisonTypes
    content: str
        The expected output content
    source: str
        The expected source for the line, one of "stdout", "stderr", or
        "returncode"
    """

    class Sources(enum.Enum):
        STDOUT = enum.auto()
        STDERR = enum.auto()
        RETURNCODE = enum.auto()

    def __init__(
        self,
        comp_type: compare.ComparisonTypes = compare.ComparisonTypes.BASIC,
        content: typing.Union[str, int] = "",
        source: Sources = Sources.STDOUT,
    ) -> None:
        self.comp_type = comp_type
        self.content = content
        self.source = source

    def compare(self, result_content: typing.Union[str, int]) -> bool:
        return compare.get_comparer(self.comp_type)(self.content, result_content)


class Test:
    """
    A runable test

    Attributes
    ----------
    command : string
        The command the test is to compare against
    description : string
    output_specs : list of strings
         The expected result of the command
    """

    def __init__(
        self,
        command: str,
        setup_commands: typing.Optional[typing.List[str]] = None,
        description: str = "",
        output_specs: typing.Optional[typing.List[OutputSpec]] = None,
    ) -> None:
        self.command = command
        self.description = description
        self.output_specs = [] if output_specs is None else output_specs
        self.setup_commands = [] if setup_commands is None else setup_commands
