import enum
import os
import shutil
import subprocess
import tempfile
import typing

from scruf import exception

EXECUTOR_ENV_T = typing.MutableMapping[str, str]


class Output:
    """
    Represents the result of executing a command

    Attributes
    ----------
    returncode : int
    stdout : str
    stderr : str
    """

    class Streams(enum.Enum):
        STDOUT = enum.auto()
        STDERR = enum.auto()

        def __repr__(self) -> str:
            return self.name.lower()

        __str__ = __repr__

    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode

        self.streams = {
            self.Streams.STDOUT: stdout,
            self.Streams.STDERR: stderr,
        }

        self._indexes = {
            self.Streams.STDOUT: 0,
            self.Streams.STDERR: 0,
        }
        self._lines = {
            self.Streams.STDOUT: stdout.splitlines(True),
            self.Streams.STDERR: stderr.splitlines(True),
        }

    @property
    def stdout(self) -> str:
        return self.streams[self.Streams.STDOUT]

    @property
    def stderr(self) -> str:
        return self.streams[self.Streams.STDERR]

    """Get the next line from the given stream

    Parameters
    ----------
    stream : { "stdout", "stderr" }
        The stream to extra the next line from

    Returns
    -------
    str
        The next line from the stream

    Raises
    ------
    scruf.execute.OutOfLinesError
        If there are no more lines available for the given stream
    """

    def next_line(self, stream: Streams) -> str:
        index = self._indexes[stream]
        lines = self._lines[stream]

        if index == len(lines):
            raise OutOfLinesError(self, stream)
        else:
            current_line = self._lines[stream][self._indexes[stream]]
            self._indexes[stream] += 1
            return current_line

    def has_remaining_lines(self, stream: Streams) -> bool:
        return self._indexes[stream] <= len(self._lines[stream]) - 1

    def get_remaining_lines(self, stream: Streams) -> typing.List[str]:
        index = self._indexes[stream]
        return self._lines[stream][index:]


class OutOfLinesError(exception.CramerError):
    def __init__(self, result: Output, stream: Output.Streams) -> None:
        message = "No more lines available for {}:\n".format(stream)
        for stream_name in result.Streams:
            message += "\t" + self._build_stream_content_msg(result, stream_name)
        super().__init__(message)

        self.result = result
        self.stream = stream

    @staticmethod
    def _build_stream_content_msg(result: Output, stream: Output.Streams) -> str:
        content = result.streams[stream]
        msg = "{} was: ".format(stream)
        if content:
            return msg + content
        return msg + "(no content)\n"


class FailedToCreateTestDirError(exception.CramerError):
    def __init__(
        self,
        dir_name: str,
        file_error: typing.Union[PermissionError, FileNotFoundError],
    ) -> None:
        message = "Could not create temporary directory at {}: {}".format(
            dir_name, str(file_error)
        )
        super().__init__(message)

        self.dir_name = dir_name


class Executor:
    """
    Class for executing commands

    Attributes
    ----------
    shell : str
        The shell to be used to run the command
    cleanup : bool
        Weather or not to remove created temporary directories once a command is run
    path : str
        Path to use in the 'TESTDIR' environment variable when executing commands
    tmpdir : str
        Directory under which the testdir will be created for running commands
    env : dict
        Environment to be used when running the command, defaults to `os.environ`

    Raises
    ------
    scruf.execute.FailedToCreateTestDirError
        If unable to create a directory under `tmpdir`. Specifically, if attempting to
        create this directory raises `PermissionError`or `FileNotFoundError`
    """

    def __init__(
        self,
        shell: str = "/bin/sh",
        cleanup: bool = True,
        path: str = os.getcwd(),
        tmpdir: str = "/tmp",
        env: typing.Optional[EXECUTOR_ENV_T] = None,
    ) -> None:
        self.cleanup = cleanup
        self.shell = shell
        self.env = self._setup_env(env, path)

        # Might raise exception, so set this last
        self.testdir = self._mktestdir(tmpdir)

    def execute(self, command: str) -> Output:
        """Execute a command

        Parameters
        ----------
        command : str


        Returns
        -------
        tuple
            int : The return code from executing the command
            string : The stdout generated from the command
            string : The stderr generated from the command
        """

        p = subprocess.Popen(
            [self.shell, "-"],
            cwd=self.testdir,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
        stdout, stderr = p.communicate(command)

        return Output(p.returncode, stdout, stderr)

    def __del__(self) -> None:
        if self.cleanup and hasattr(self, "testdir"):
            shutil.rmtree(self.testdir)

    @classmethod
    def _setup_env(
        cls, env: typing.Optional[EXECUTOR_ENV_T], path: str
    ) -> EXECUTOR_ENV_T:
        if env is None:
            env = os.environ
        cls._maybe_add_to_env(env, "TESTDIR", path)
        return env

    @staticmethod
    def _mktestdir(tmpdir: str) -> str:
        try:
            testdir = tempfile.mkdtemp(dir=tmpdir, suffix="scruf")
        except (PermissionError, FileNotFoundError) as e:
            raise FailedToCreateTestDirError(tmpdir, e)
        return testdir

    @staticmethod
    def _maybe_add_to_env(env: EXECUTOR_ENV_T, name: str, value: str) -> None:
        if name not in env:
            env[name] = value
