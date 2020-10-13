import logging
import pathlib
import re
import shutil
import subprocess
import textwrap
from typing import Optional

import attr
import pytest

import tiamatpip

log = logging.getLogger(__name__)

CODE_ROOT = pathlib.Path(tiamatpip.__file__).resolve().parent.parent


@attr.s(frozen=True)
class ProcessResult:
    """
    This class serves the purpose of having a common result class which will hold the
    resulting data from a subprocess command.
    """

    exitcode = attr.ib()
    stdout = attr.ib()
    stderr = attr.ib()
    cmdline = attr.ib(default=None, kw_only=True)

    @exitcode.validator
    def _validate_exitcode(self, attribute, value):
        if not isinstance(value, int):
            raise ValueError(
                "'exitcode' needs to be an integer, not '{}'".format(type(value))
            )

    def __str__(self):
        message = self.__class__.__name__
        if self.cmdline:
            message += f"\n Command Line: {self.cmdline}"
        if self.exitcode is not None:
            message += f"\n Exitcode: {self.exitcode}"
        if self.stdout or self.stderr:
            message += "\n Process Output:"
        if self.stdout:
            message += f"\n   >>>>> STDOUT >>>>>\n{self.stdout}\n   <<<<< STDOUT <<<<<"
        if self.stderr:
            message += f"\n   >>>>> STDERR >>>>>\n{self.stderr}\n   <<<<< STDERR <<<<<"
        return message + "\n"


@attr.s(kw_only=True, slots=True)
class TestProject:
    name: str = attr.ib()
    path: pathlib.Path = attr.ib()
    pypath: Optional[pathlib.Path] = attr.ib(init=False)
    build_conf_contents: str = attr.ib()
    run_py_contents: str = attr.ib()
    requirements_txt_contents: str = attr.ib()
    build_conf: pathlib.Path = attr.ib(init=False)
    run_py: Optional[pathlib.Path] = attr.ib(init=False)
    requirements_txt: Optional[pathlib.Path] = attr.ib(init=False)

    @pypath.default
    def _default_pypath(self):
        pypath = self.path / "pypath"
        pypath.mkdir(parents=True, exist_ok=True, mode=0o755)
        return pypath

    @build_conf.default
    def _default_build_conf(self):
        return self.path / "build.conf"

    @build_conf_contents.default
    def _default_build_conf_contents(self):
        return textwrap.dedent(
            """\
        tiamat:
          name: {}
          dev_pyinstaller: True
        """.format(
                self.name
            )
        )

    @run_py.default
    def _default_run_py(self):
        return self.path / "run.py"

    @run_py_contents.default
    def _default_run_py_contents(self):
        return textwrap.dedent(
            """\
            #!/usr/bin/env python3

            import os
            import pprint
            import tiamatpip.cli
            import tiamatpip.configure

            tiamatpip.configure.set_user_site_packages_path({!r})


            def main(argv):
                if argv[1] == "shell":
                    py_shell()
                    return
                if tiamatpip.cli.should_redirect_argv(argv):
                    tiamatpip.cli.process_pip_argv(argv)

                # If we reached this far, it means we're not handling pip stuff

                if argv[1] == "test":
                    print("Tested!")
                else:
                    print("No command?!")

                sys.exit(0)


            def py_shell():
                import readline  # optional, will allow Up/Down/History in the console
                import code

                variables = globals().copy()
                variables.update(locals())
                shell = code.InteractiveConsole(variables)
                shell.interact()

            if __name__ == "__main__":
                if sys.platform.startswith("win"):
                    multiprocessing.freeze_support()
                main(sys.argv)
            """.format(
                str(self.pypath)
            )
        )

    @requirements_txt.default
    def _default_requirements_txt(self):
        return self.path / "requirements.txt"

    @requirements_txt_contents.default
    def _default_requirements_txt_contents(self):
        return textwrap.dedent(
            """\
            {}
        """.format(
                CODE_ROOT
            )
        )

    def __attrs_post_init__(self):
        self.build_conf.write_text(self.build_conf_contents)
        self.run_py.write_text(self.run_py_contents)
        self.requirements_txt.write_text(self.requirements_txt_contents)

    def run(self, *args, cwd=None, check=None, **kwargs):
        if cwd is None:
            cwd = str(self.path)
        cmdline = [str((self.path / "dist" / self.name).relative_to(self.path))]
        cmdline.extend(list(args))
        result = subprocess.run(
            cmdline,
            cwd=cwd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs,
        )
        if check is True:
            result.check_returncode()
        ret = ProcessResult(
            result.returncode,
            result.stdout.decode(),
            result.stderr.decode(),
            cmdline=args,
        )
        log.debug(ret)
        return ret

    def build(self):
        subprocess.run(
            ["tiamat", "--log-level=debug", "build", "-c", "build.conf"],
            cwd=self.path,
            check=True,
        )

    def delete_pypath(self):
        shutil.rmtree(self.pypath, ignore_errors=True)

    def __enter__(self):
        self.build()
        return self

    def __exit__(self, *args):
        shutil.rmtree(self.path, ignore_errors=True)


@pytest.fixture(scope="module")
def built_project(request, tmpdir_factory):
    name = request.node.name
    name = re.sub(r"[\W]", "_", name)
    MAXVAL = 30
    name = name[:MAXVAL]
    instance = TestProject(
        name=name, path=pathlib.Path(tmpdir_factory.mktemp(name, numbered=True))
    )
    with instance:
        yield instance


@pytest.fixture
def project(built_project):
    try:
        yield built_project
    finally:
        built_project.delete_pypath()
