import os
import subprocess
import sys

from pycsp3.compiler import Compilation
from pycsp3.tools.utilities import BLUE, WHITE

cwd = os.getcwd()
seriesName = sys.argv[1].lower()


def dirFor(name):
    os.chdir(cwd)
    if seriesName == "all" or seriesName == name.lower():
        os.mkdir(name)
        os.chdir(name)
        return True
    return False


def execute(model, *, variant=None, data=None, dataformat=None):
    command = "python3 " + model + (" -variant=" + variant if variant else "") + (" -data=" + data if data else "") + (" -dataformat=" + dataformat if dataformat else "")
    print(BLUE + "Command:" + WHITE, command)
    subprocess.call(command.split())


path = os.sep + "home" + os.sep + "lecoutre" + os.sep + "workspace" + os.sep + "pycsp3" + os.sep + "problems" + os.sep + "csp" + os.sep + "academic" + os.sep
print(path)

if dirFor("AllInterval"):
    for i in list(range(5, 21)) + list(range(25, 101, 5)):
        execute(path + "AllInterval.py", data=str(i), dataformat="{:03d}")
os.chdir(cwd)
execute(path + "AllInterval.py", data="8")
execute(path + "ColouredQueens.py", data="8")

Compilation.done = True
