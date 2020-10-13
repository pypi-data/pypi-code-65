import logging
import opcode
import os
import pathlib
from distutils.sysconfig import get_python_inc

log = logging.getLogger(__name__)


def get_distutils_hidden_imports():
    # The reason why we use optcode to findout about the path of distutils
    # is because on virtualenvs, the real distutils package is not included
    # and it patches python at runtime to the real distutils package.
    # We're using the same approach to find out where the distutils package
    # really is.
    distutils_path = pathlib.Path(opcode.__file__).resolve().parent / "distutils"
    hidden_imports = set()
    for path in distutils_path.rglob("*.py"):
        # Get the relative path minus the file extension
        relpath = path.relative_to(distutils_path).with_suffix("")
        if relpath.name == "__init__":
            # We don't want to consider __init__.py as part of a package name
            relpath = relpath.parent

        # Relative module
        relmod = str(relpath).replace(os.sep, ".")
        if not relmod or relmod == ".":
            continue
        # Real module name
        module = f"{distutils_path.name}.{relmod}"
        if module.startswith(f"{distutils_path.name}.tests"):
            # Don't include tests
            continue
        hidden_imports.add(module)
    hidden_imports = sorted(list(hidden_imports))
    log.info(
        "adding the following distutils imports to hidden imports: %s", hidden_imports
    )
    return hidden_imports


def get_python_header_files():
    python_include_path = pathlib.Path(get_python_inc())
    datas = []
    for fname in python_include_path.rglob("*.h"):
        relpath = fname.relative_to(python_include_path)
        incpath = pathlib.Path("include") / "python" / relpath
        datas.append((str(fname), str(incpath.parent)))
    log.info("Including the following python header files: %s", sorted(datas))
    return datas


hiddenimports = get_distutils_hidden_imports()
datas = get_python_header_files()
