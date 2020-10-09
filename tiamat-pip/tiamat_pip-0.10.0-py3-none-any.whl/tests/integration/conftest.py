import pathlib
import re
import subprocess
import textwrap
from typing import Optional

import attr
import pytest

import tiamatpip

CODE_ROOT = pathlib.Path(tiamatpip.__file__).resolve().parent.parent


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
        if check is None:
            check = True
        cmdline = [str((self.path / "dist" / self.name).relative_to(self.path))]
        cmdline.extend(list(args))
        return subprocess.run(cmdline, cwd=cwd, check=check, **kwargs)


@pytest.fixture
def project(request, tmpdir_factory):
    name = request.node.name
    name = re.sub(r"[\W]", "_", name)
    MAXVAL = 30
    name = name[:MAXVAL]
    return TestProject(
        name=name, path=pathlib.Path(tmpdir_factory.mktemp(name, numbered=True))
    )
