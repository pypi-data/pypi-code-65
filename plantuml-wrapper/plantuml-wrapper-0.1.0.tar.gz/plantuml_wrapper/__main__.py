"""Plantuml wrapper script
"""

import os
import sys
import shutil
from subprocess import Popen

JARFILE = "plantuml.jar"


def is_self(path):
    """Return True if path links back to this script.

    TODO: this is rather hackish, is there a better way?
    """
    with open(path, "rb") as file:
        if b"plantuml_wrapper" in file.read():
            return True
    return False


def find_plantuml():
    """Return path to existing plantuml executable."""
    env_path = os.environ.get("PATH", "")
    bin_path = None
    for path in env_path.split(os.pathsep):
        os.environ["PATH"] = path
        bin_path = shutil.which("plantuml")
        if bin_path and not is_self(bin_path):
            break
    os.environ["PATH"] = env_path
    return bin_path


def find_java():
    """Return path to java executable."""
    java_path = shutil.which("java")
    if not java_path:
        raise FileNotFoundError("java executable not found in PATH")
    return java_path


def find_plantuml_jar():
    """Return path to java plantuml.jar."""
    for path in os.environ.get("PATH", "").split(os.pathsep):
        jar_path = os.path.join(path, JARFILE)
        if os.path.isfile(jar_path):
            return jar_path
    raise FileNotFoundError("%s not found in PATH" % JARFILE)


def main():
    """Script entry point."""
    plantuml = find_plantuml()
    if plantuml:
        cmd = [plantuml]
    else:
        java = find_java()
        plantuml_jar = find_plantuml_jar()
        cmd = [java, "-jar", plantuml_jar]
    cmd += sys.argv[1:]
    proc = Popen(cmd, stdin=sys.stdin.buffer, stdout=sys.stdout.buffer)
    proc.communicate()
    if proc.returncode:
        raise Exception("plantuml failed")


if __name__ == "__main__":
    main()
