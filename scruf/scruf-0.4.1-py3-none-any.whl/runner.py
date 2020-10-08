"""Test runner"""
import typing

from scruf import compare, execute, test


class Result:
    """
    The result of comparing a `test.OutputSpec` line vs. the corresponding
    `execute.Output` line
    """

    def __init__(
        self,
        result_line: str,
        result_source: test.OutputSpec.Sources,
        test_line: str,
        success: bool,
        type: compare.ComparisonTypes,
    ) -> None:
        self.result_line = result_line
        self.result_source = result_source
        self.test_line = test_line
        self.success = success
        self.type = type

    def get_printable_failures(self) -> typing.List[str]:
        """Get a printable representation of a failed comparison """

        comparison_type = self.type

        return {
            compare.ComparisonTypes.BASIC: _basic_comparison_failure_lines,
            compare.ComparisonTypes.ESCAPE: _basic_comparison_failure_lines,
            compare.ComparisonTypes.NO_EOL: _no_eol_comparison_failure_lines,
            compare.ComparisonTypes.REGEX: _regex_comparison_failure_lines,
            compare.ComparisonTypes.RETURNCODE: _returncode_comparison_failure_lines,
        }[comparison_type](self.test_line, self.result_line)


def compare_result(test: test.Test, exec_result: execute.Output) -> typing.List[Result]:
    """Compare a test's expected output against an execute result"""
    summary = []

    for output_spec in test.output_specs:
        result_content = get_content_for_comparison(exec_result, output_spec.source)
        success = output_spec.compare(result_content)
        summary.append(
            Result(
                str(result_content),
                output_spec.source,
                str(output_spec.content),
                success,
                output_spec.comp_type,
            )
        )
    return summary


def get_content_for_comparison(
    output: execute.Output, source: test.OutputSpec.Sources
) -> typing.Union[int, str]:
    if source == test.OutputSpec.Sources.RETURNCODE:
        return output.returncode

    stream = _get_stream_for_source(source)
    return output.next_line(stream)


def _get_stream_for_source(source: test.OutputSpec.Sources) -> execute.Output.Streams:
    source_to_stream_map = {
        test.OutputSpec.Sources.STDOUT: execute.Output.Streams.STDOUT,
        test.OutputSpec.Sources.STDERR: execute.Output.Streams.STDERR,
    }
    return source_to_stream_map[source]


def _format_content(content: str) -> str:
    formatted_content = repr(content)

    if not content.endswith("\n"):
        formatted_content += " (no eol)"
    return formatted_content


def _basic_comparison_failure_lines(
    comparison_content: str, result_content: str
) -> typing.List[str]:
    return [
        "got: " + _format_content(result_content),
        "expected: " + _format_content(comparison_content),
    ]


def _no_eol_comparison_failure_lines(
    comparison_content: str, result_content: str
) -> typing.List[str]:
    return _basic_comparison_failure_lines(
        comparison_content.rstrip("\r\n"), result_content
    )


def _regex_comparison_failure_lines(
    comparison_content: str, result_content: str
) -> typing.List[str]:
    return [
        "got: " + _format_content(result_content),
        "Does not match: '{}'".format(comparison_content),
    ]


def _returncode_comparison_failure_lines(
    expected_returncode: str, got_returncode: str
) -> typing.List[str]:
    return [
        "got return code: {} != {}".format(
            str(got_returncode), str(expected_returncode)
        )
    ]
