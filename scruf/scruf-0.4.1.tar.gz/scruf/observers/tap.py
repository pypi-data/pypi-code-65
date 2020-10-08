import sys
import typing

from scruf import observe

if typing.TYPE_CHECKING:  # pragma: no cover
    from scruf import compare, execute, runner, test  # noqa F401


class TapObserver(observe.Observer):
    def notify_before_testing_file(self, filename: str) -> None:
        print(self._tap_comment_line("Testing: {}".format(filename)))

    def notify_before_tests_run(self, tests: typing.List["test.Test"]) -> None:
        print("1..{}".format(len(tests)))

    def notify_test_error(
        self,
        test: "test.Test",
        test_number: int,
        error: typing.Union["compare.RegexError", "execute.OutOfLinesError"],
    ) -> None:
        print(self._tap_failure(self._build_output_line(test, test_number)))
        print(self._tap_error_line(error), file=sys.stderr)

    def notify_test_success(self, test: "test.Test", test_number: int) -> None:
        print(self._tap_success(self._build_output_line(test, test_number)))

    def notify_test_comparison_failure(
        self,
        test: "test.Test",
        test_number: int,
        failed_results: typing.List["runner.Result"],
    ) -> None:
        print(self._tap_failure(self._build_output_line(test, test_number)))
        for result in failed_results:
            failure_lines = [
                self._tap_comment_line("\t" + line)
                for line in result.get_printable_failures()
            ]
            print("\n".join(failure_lines), file=sys.stderr)

    def notify_test_strict_failure(
        self,
        test: "test.Test",
        test_number: int,
        source_map: typing.Dict[str, typing.List[str]],
    ) -> None:
        print(self._tap_failure(self._build_output_line(test, test_number)))
        for source, remaining_lines in source_map.items():
            description = "Content still remaining for {}:".format(source)
            print(self._tap_comment_line(description), file=sys.stderr)
            for line in remaining_lines:
                print(self._tap_comment_line("\t" + line.rstrip()), file=sys.stderr)

    ######################
    # TAP specific methods
    ######################
    @staticmethod
    def _tap_success(content: str) -> str:
        return "ok " + content

    @staticmethod
    def _tap_failure(content: str) -> str:
        return "not ok " + content

    @staticmethod
    def _tap_comment_line(content: str) -> str:
        return "# " + content

    @classmethod
    def _tap_error_line(cls, error: Exception) -> str:
        error_lines = []
        for line in str(error).splitlines():
            error_lines.append(cls._tap_comment_line("\t" + line))
        return "\n".join(error_lines)

    @staticmethod
    def _build_output_line(test: "test.Test", test_number: int) -> str:
        output_line = str(test_number)
        if test.description:
            output_line += " - {}".format(test.description.rstrip())
        return output_line
