import enum
import re
import typing

from scruf import compare, exception, test

_RawTest_T = typing.Dict["_TestFSM.States", typing.List[typing.Any]]


class TestParser:
    """
    Parser for parsing raw tests

    Attributes
    ----------
    indent : string
        The indentation to be used when parsing tests
    """

    def __init__(self, indent: str = "    ") -> None:
        self.tokeniser = _TestTokeniser(indent)
        self.fsm = _TestFSM(self.tokeniser)

        self._content_getter = {
            self.fsm.States.DESCRIPTION: self.tokeniser.get_description,
            self.fsm.States.SETUP_COMMAND: self.tokeniser.get_setup_command,
            self.fsm.States.TEST_COMMAND: self.tokeniser.get_test_command,
            self.fsm.States.CONTINUE: self.tokeniser.get_continue,
            self.fsm.States.OUTPUT_SPEC: self.tokeniser.get_result,
        }

    def parse(self, lines: typing.List[str]) -> typing.List[test.Test]:
        """Parse raw lines into `scruf.test.Test` objects

        Parameters
        ----------
        lines : list of str

        Returns
        -------
        list of `scruf.test.Test`

        Raises
        ------
        scruf.parse.ProgressionError
            If an invalid progression is found, e.g. the raw lines hold a description
            followed by a continuation line
        """

        prev_state = self.fsm.States.START
        tests = []
        test = self._new_test()

        for i, line in enumerate(lines):
            if self.tokeniser.is_comment(line) or self.tokeniser.is_empty(line):
                continue

            state = self.fsm.progress(prev_state, line)
            if state == self.fsm.States.START:
                tests.append(self._test_to_test_object(test))
                test = self._new_test()
                state = self.fsm.progress(state, line)

            if state is None:
                from_state = self.fsm.state_name(prev_state)
                expected_states = self.fsm.get_named_progressions(prev_state)
                raise ProgressionError(i, line, from_state, expected_states)
            # Preserve newlines for results
            if not state == self.fsm.States.OUTPUT_SPEC:
                line = line.rstrip()

            test[state].append(self._content_getter[state](line))
            prev_state = state

        tests.append(self._test_to_test_object(test))
        return tests

    def _new_test(self) -> _RawTest_T:
        return dict((key, []) for key in self._content_getter)

    def _test_to_test_object(self, raw_test: _RawTest_T) -> test.Test:
        output_parser = OutputParser()
        command = " ".join(
            raw_test[self.fsm.States.TEST_COMMAND] + raw_test[self.fsm.States.CONTINUE]
        )
        description = " ".join(raw_test[self.fsm.States.DESCRIPTION])
        output_specs = [
            output_parser.parse(line) for line in raw_test[self.fsm.States.OUTPUT_SPEC]
        ]
        setup_commands = raw_test[self.fsm.States.SETUP_COMMAND]
        return test.Test(
            command,
            setup_commands=setup_commands,
            description=description,
            output_specs=output_specs,
        )


class OutputParser:
    _EOL_CHARACTERS = "\n\r"
    _STDOUT_FLAG = "1:"
    _STDERR_FLAG = "2:"
    _REGEX_FLAG = "[RE]"
    _NO_EOL_FLAG = "[NEoL]"
    _ESCAPE_FLAG = "[ESC]"
    _RETURNCODE_REGEX = re.compile(r"\[(\d+)\]\s*$")

    @classmethod
    def parse(cls, raw_spec: str) -> test.OutputSpec:
        """Parse a raw output spec line and extract details

        Parameters
        ----------
        raw_spec : str
            The test line to process

        Returns
        -------
        test.OutputSpec
        """
        content, source = cls._get_source_and_content(raw_spec)

        if cls._startswith_flag(content, cls._REGEX_FLAG):
            parsed_content = cls._strip_flag(content, cls._REGEX_FLAG).rstrip(
                cls._EOL_CHARACTERS
            )
            return test.OutputSpec(
                comp_type=compare.ComparisonTypes.REGEX,
                content=parsed_content,
                source=source,
            )
        if cls._startswith_flag(content, cls._NO_EOL_FLAG):
            parsed_content = cls._strip_flag(content, cls._NO_EOL_FLAG).rstrip(
                cls._EOL_CHARACTERS
            )
            return test.OutputSpec(
                comp_type=compare.ComparisonTypes.NO_EOL,
                content=parsed_content,
                source=source,
            )
        if cls._startswith_flag(content, cls._ESCAPE_FLAG):
            parsed_content = cls._get_escape_content(
                cls._strip_flag(content, cls._ESCAPE_FLAG)
            )
            return test.OutputSpec(
                comp_type=compare.ComparisonTypes.ESCAPE,
                content=parsed_content,
                source=source,
            )
        if cls._has_returncode_flag(content):
            returncode = cls._get_returncode(content)
            return test.OutputSpec(
                comp_type=compare.ComparisonTypes.RETURNCODE,
                content=returncode,
                source=test.OutputSpec.Sources.RETURNCODE,
            )
        return test.OutputSpec(
            comp_type=compare.ComparisonTypes.BASIC,
            content=content,
            source=source,
        )

    @classmethod
    def _get_source_and_content(
        cls, line: str
    ) -> typing.Tuple[str, test.OutputSpec.Sources]:
        if cls._startswith_flag(line, cls._STDOUT_FLAG):
            return (
                cls._strip_flag(line, cls._STDOUT_FLAG),
                test.OutputSpec.Sources.STDOUT,
            )
        if cls._startswith_flag(line, cls._STDERR_FLAG):
            return (
                cls._strip_flag(line, cls._STDERR_FLAG),
                test.OutputSpec.Sources.STDERR,
            )
        return line, test.OutputSpec.Sources.STDOUT

    @classmethod
    def _has_returncode_flag(cls, line: str) -> bool:
        return cls._RETURNCODE_REGEX.match(line) is not None

    @classmethod
    def _get_returncode(cls, line: str) -> int:
        match = cls._RETURNCODE_REGEX.match(line)
        assert match is not None
        return int(match.group(1))

    @staticmethod
    def _get_escape_content(line: str) -> str:
        return escape_space(line).replace(r"\n", "\n")

    @staticmethod
    def _startswith_flag(line: str, flag: str) -> bool:
        return line.startswith(flag)

    @staticmethod
    def _strip_flag(line: str, flag: str) -> str:
        return OutputParser._lstrip_space(line[len(flag) :])

    @staticmethod
    def _lstrip_space(line: str) -> str:
        if line.startswith(" "):
            return line[1:]
        return line


class ProgressionError(exception.CramerError):
    """
    Exception for invalid progressions when parsing raw lines

    Attributes
    ----------
    line_num : int
    line_content : str
    from_state : str
        Human readable version of the state before the invalid line
    expected_states : list of str
        List of human readable version of the expected states given `from_state`

    """

    def __init__(
        self,
        line_num: int,
        line_content: str,
        from_state: str,
        expected_states: typing.List[str],
    ):
        message = "Failed to parse line {}: {}\nExpected line of type: {}".format(
            line_num,
            line_content.rstrip(),
            " or ".join(expected_states),
        )
        super().__init__(message)

        self.line_num = line_num
        self.from_state = from_state
        self.expected_states = expected_states


class _TestTokeniser:
    def __init__(self, indent: str) -> None:
        self.comment_character = "#"
        self.command_character = "$"
        self.continue_character = ">"
        self.indent = indent

        self.setup_command_prefix = "[SETUP]" + self.command_character
        self.command_prefix = self.indent + self.command_character
        self.continue_prefix = self.indent + self.continue_character

    def is_test_command(self, line: str) -> bool:
        return line.startswith(self.command_prefix)

    def is_setup_command(self, line: str) -> bool:
        return line.startswith(self.setup_command_prefix)

    def is_continue(self, line: str) -> bool:
        return line.startswith(self.continue_prefix)

    def is_description(self, line: str) -> bool:
        return (
            not line[0].isspace()
            and not self.is_comment(line)
            and not self.is_setup_command(line)
        )

    def is_comment(self, line: str) -> bool:
        return line.startswith(self.comment_character)

    def is_empty(self, line: str) -> bool:
        return not line or not line.startswith(self.indent) and line.isspace()

    def is_result(self, line: str) -> bool:
        return (
            line.startswith(self.indent)
            and not self.is_test_command(line)
            and not self.is_continue(line)
        )

    def get_test_command(self, line: str) -> str:
        return line[len(self.command_prefix) :].strip()

    def get_setup_command(self, line: str) -> str:
        return line[len(self.setup_command_prefix) :].strip()

    def get_continue(self, line: str) -> str:
        return line[len(self.continue_prefix) :].strip()

    def get_description(self, line: str) -> str:
        return line

    def get_result(self, line: str) -> str:
        return line[len(self.indent) :]


class _TestFSM:
    class States(enum.Enum):
        START = enum.auto()
        DESCRIPTION = enum.auto()
        SETUP_COMMAND = enum.auto()
        TEST_COMMAND = enum.auto()
        CONTINUE = enum.auto()
        OUTPUT_SPEC = enum.auto()

    STATE_NAMES = {
        States.START: "start",
        States.DESCRIPTION: "description",
        States.SETUP_COMMAND: "setup_command",
        States.TEST_COMMAND: "test_command",
        States.CONTINUE: "continue",
        States.OUTPUT_SPEC: "result",
    }

    def __init__(self, tokeniser: _TestTokeniser) -> None:
        self.tokeniser = tokeniser

        self.progressions = {
            self.States.START: {
                self.States.DESCRIPTION: self.tokeniser.is_description,
                self.States.SETUP_COMMAND: self.tokeniser.is_setup_command,
                self.States.TEST_COMMAND: self.tokeniser.is_test_command,
            },
            self.States.DESCRIPTION: {
                self.States.DESCRIPTION: self.tokeniser.is_description,
                self.States.SETUP_COMMAND: self.tokeniser.is_setup_command,
                self.States.TEST_COMMAND: self.tokeniser.is_test_command,
            },
            self.States.SETUP_COMMAND: {
                self.States.SETUP_COMMAND: self.tokeniser.is_setup_command,
                self.States.TEST_COMMAND: self.tokeniser.is_test_command,
            },
            self.States.TEST_COMMAND: {
                self.States.CONTINUE: self.tokeniser.is_continue,
                self.States.OUTPUT_SPEC: self.tokeniser.is_result,
                self.States.START: lambda line: self.tokeniser.is_description(line)
                or self.tokeniser.is_test_command(line)
                or self.tokeniser.is_setup_command(line),
            },
            self.States.CONTINUE: {
                self.States.CONTINUE: self.tokeniser.is_continue,
                self.States.OUTPUT_SPEC: self.tokeniser.is_result,
                self.States.START: lambda line: self.tokeniser.is_description(line)
                or self.tokeniser.is_test_command(line),
            },
            self.States.OUTPUT_SPEC: {
                self.States.OUTPUT_SPEC: self.tokeniser.is_result,
                self.States.START: lambda line: self.tokeniser.is_description(line)
                or self.tokeniser.is_test_command(line),
            },
        }

    def progress(
        self, from_state: "_TestFSM.States", line: str
    ) -> typing.Optional["_TestFSM.States"]:
        for to_state, condition in self.progressions[from_state].items():
            if condition(line):
                return to_state
        return None

    @classmethod
    def state_name(cls, state: States) -> str:
        return cls.STATE_NAMES[state]

    def get_named_progressions(self, state: States) -> typing.List[str]:
        progression_states = list(self.progressions[state].keys())

        # "Start" is just an internal state, so avoid presenting it
        if self.States.START in progression_states:
            del progression_states[progression_states.index(self.States.START)]
            progression_states += self.progressions[self.States.START].keys()
        return [self.state_name(s) for s in progression_states]


def escape_space(string: str) -> str:
    return string.replace(r"\s", " ").replace(r"\t", "\t")
