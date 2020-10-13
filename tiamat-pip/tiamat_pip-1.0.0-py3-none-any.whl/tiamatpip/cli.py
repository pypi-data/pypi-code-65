"""
    tiamatpip.cli
    ~~~~~~~~~~~~~

    PIP handling for tiamat packaged python projects
"""
import code
import os
import pathlib
import sys
from typing import List
from typing import Sequence

from pip._internal.cli.main import main as pip_main

from tiamatpip import configure
from tiamatpip.utils import debug_print
from tiamatpip.utils import patch_pip_get_installed_distributions
from tiamatpip.utils import patched_environ
from tiamatpip.utils import patched_sys_argv


def should_redirect_argv(argv):
    debug_print("should_redirect_argv", argv)
    if configure.ENVIRON_VARIABLE_NAME in os.environ:
        # A pip command is already in progress. This is usually
        # hit when pip is building the dependencies of a package
        return True
    if argv[1] == configure.get_pip_command_name():
        # We should intercept pip comands
        return True
    # Do nothing
    return False


def process_argv(argv: List[str]) -> bool:
    pypath = configure.get_user_site_packages_path()
    debug_print("process_argv", argv, pypath=pypath, pypath_exists=pypath.exists())
    if configure.ENVIRON_VARIABLE_NAME not in os.environ:
        return False

    c_include_path = os.environ.get("CPATH") or None
    included_python_headers_path = str(
        pathlib.Path(sys._MEIPASS).resolve() / "include" / "python"
    )
    if c_include_path is None:
        c_include_path = included_python_headers_path
    else:
        c_include_path_parts = c_include_path.split(os.pathsep)
        if included_python_headers_path not in c_include_path_parts:
            c_include_path_parts.append(included_python_headers_path)
        c_include_path = os.pathsep.join(c_include_path_parts)
    with patched_environ(C_INCLUDE_PATH=c_include_path, CPATH=c_include_path):
        if argv[1] == "-c":
            # Example:
            #   python -c "print 'Foo!'"
            run_code(argv[2:])
            return
        elif argv[1] == "-u" and argv[2] == "-c":
            # Example:
            #   python -u -c "print 'Foo!'"
            run_code(argv[3:])
            return

        try:
            argv1_file = pathlib.Path(argv[1]).resolve()
            if argv1_file.is_file() and not str(argv1_file).endswith(f"{os.sep}pip"):
                # Example:
                #   python this-is-a-script.py arg1 arg2
                run_python_file(argv[1:])
                return
        except ValueError:
            # Not a valid file
            pass

        if argv[1] == "-m" and argv[2] == "pip":
            # Example:
            #   python -m pip install foo
            argv.pop(1)
        redirect_to_pip(argv)
        return True


def process_pip_argv(argv: List[str]) -> None:
    pypath = configure.get_user_site_packages_path()
    debug_print("process_pip_argv", argv, pypath=pypath, pypath_exists=pypath.exists())
    if pypath is None:
        raise RuntimeError(
            "You need to run 'tiamatpip.configure.set_user_site_packages_path(<path>)' "
            "before calling tiamatpip.cli.process_pip_argv()"
        )

    if not pypath.is_dir():
        print(
            f"The path '{pypath}' does not exist or could not be created.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    environ = {
        configure.ENVIRON_VARIABLE_NAME: "1",
        f"{configure.ENVIRON_VARIABLE_NAME}_PYPATH": str(pypath),
    }
    with patched_environ(environ=environ):
        return process_argv(argv)


def redirect_to_pip(argv: List[str]) -> None:
    pypath = configure.get_user_site_packages_path()
    debug_print("redirect_to_pip", argv, pypath=pypath, pypath_exists=pypath.exists())
    targets: Sequence[str] = ("install", "list", "freeze", "uninstall")
    try:
        cmd = argv[2]
    except IndexError:
        msg: str = "Must pass in available pip command which are:"
        for cmd in targets:
            msg += f"\n - {cmd}"
        print(msg, file=sys.stderr, flush=True)
        sys.exit(1)

    extra_environ = {}

    # Valid command found

    user_site_path = configure.get_user_site_packages_path()
    if cmd == "install":
        args = [cmd]
        for arg in argv:
            if arg == "--prefix" or arg.startswith("--prefix="):
                # When pip is building dependencies it might build them in isolation
                # or pass --prefix.
                # We should not inject our --target in this scnario
                break
        else:
            # Install into our custom site packages target path
            args.extend(["--target", str(user_site_path)])
    elif cmd == "uninstall":
        args = [cmd]
        patch_pip_get_installed_distributions()
        extra_environ[f"{configure.ENVIRON_VARIABLE_NAME}_UNINSTALL"] = "1"
        # print("pip uninstall is a feature in progress", file=sys.stderr, flush=True)
        # sys.exit(1)
    elif cmd in ("list", "freeze"):
        args = [cmd, "--path", str(user_site_path)]
    else:
        args = [cmd]
    args.extend(argv[3:])
    with patched_environ(
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        # The environment variable PYTHONUSERBASE can also be used to
        # tell pip where to install packages into
        PYTHONUSERBASE=str(user_site_path),
    ):
        # Call pip
        with patched_environ(environ=extra_environ):
            try:
                sys.exit(pip_main(args))
            finally:
                pypath = configure.get_user_site_packages_path()
                debug_print(
                    "redirect_to_pip finally",
                    args,
                    pypath=pypath,
                    pypath_exists=pypath.exists(),
                )


def run_code(argv):
    source, *_ = argv
    with patched_sys_argv(argv):
        debug_print("run_code", argv)
        interpreter = code.InteractiveInterpreter()
        interpreter.runsource(source)


def run_python_file(argv):
    debug_print("run_python_file", argv)
    python_file, *_ = argv
    with open(python_file) as rfh:
        source = rfh.read()
        with patched_sys_argv(argv):
            # We want scripts which have an 'if __name__ == "__main__":'
            # section to run it
            interpreter = code.InteractiveInterpreter({"__name__": "__main__"})
            interpreter.runsource(source, filename=python_file, symbol="exec")
