"""Plantuml wrapper script
"""

import os
import sys
import shutil
from subprocess import Popen

JARFILE = "plantuml.jar"


def find_java():
    """Return path to java executable."""
    path = shutil.which("java")
    if not path:
        raise FileNotFoundError("java executable not found in PATH")
    return path


def find_plantuml():
    """Return path to java plantuml.jar."""
    for path in os.environ["path"].split(os.pathsep):
        path = os.path.join(path, JARFILE)
        if os.path.isfile(path):
            return path
    raise FileNotFoundError("%s not found in PATH" % JARFILE)


def main():
    """Script entry point."""
    java = find_java()
    plantuml = find_plantuml()
    cmd = [java, "-jar", plantuml] + sys.argv[1:]
    proc = Popen(cmd, stdin=sys.stdin.buffer, stdout=sys.stdout.buffer)
    proc.communicate()
    if proc.returncode:
        raise Exception("plantuml failed")


if __name__ == "__main__":
    main()
