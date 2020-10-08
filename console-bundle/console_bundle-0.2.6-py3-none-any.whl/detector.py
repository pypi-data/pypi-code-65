import sys
from consolebundle.CommandRunner import runCommand

def isRunningInConsole():
    return runCommand.__module__ in sys.modules
