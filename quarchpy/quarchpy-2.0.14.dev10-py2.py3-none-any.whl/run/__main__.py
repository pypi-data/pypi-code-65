'''
This script allows execution of select quarchpy scripts with out needing the full address.
'''

import sys
from quarchpy.debug.SystemTest import main as systemTestMain
from quarchpy.disk_test.driveTestCore import main as driveTestCoreMain
# from quarchpy.calibration.calibrationUtil import main as calibrationUtilMain
from quarchpy.qis.qisFuncs import startLocalQis
from quarchpy.qps.qpsFuncs import startLocalQps
from quarchpy.debug.upgrade_quarchpy import main as uprade_quarchpy_main
from quarchpy.user_interface import*

#TODO Use table to display all available options and help on each (in while loop) similar to user select device.

def main(argstring):

    if argstring.__len__() is 0 or argstring[0].lower is "h" or argstring[0].lower is "help":
        displayHelpMessage()
    elif "debug_info" in argstring[0].lower():
        systemTestMain() #quarchpy.debug.SystemTest
    elif "qcs" in argstring[0].lower():
        driveTestCoreMain(argstring[1:])#driveTestCore Backend
    # elif "calibration_tool" in argstring[0].lower():
    #     calibrationUtilMain(argstring[1:])#Calibration Tool
    elif "qis" in argstring[0].lower():
        terminal,headless = False, False
        if "--terminal" in argstring[0] or "-t" in argstring[0]:
            terminal = True
        if "--headless" in argstring[0] or "-H" in argstring[0]:
            headless = True
        startLocalQis(terminal=terminal, headless=headless)  #QIS
    elif "qps" in argstring[0].lower():
        startLocalQps()  #QPS
    elif "upgrade_quarchpy" in argstring[0].lower():
        uprade_quarchpy_main(argstring[1:])#Upgrade Quarchpy
    else:
        printText("Not a valid input")
        displayHelpMessage()

def displayHelpMessage():

    printText("Run parameters \n"
              "h, help:\n\tShow this help message\n"
              "debug_info:\n\tRuns SystemTest which displays useful information for debugging\n"
              "qcs:\n\tLaunches Quarch Compliance Suite server back end\n"
              "\tFor more info run : python -m quarchpy.run qcs -h\n"
              "calibration_tool:\n\tRuns The Quarch Calibration Tool to allow the calibration of Quarch modules\n"
              "\tFor more info run : python -m quarchpy.run calibration_tool -h\n"
              "qis:\n\tLaunches Quarch Instrument Server for communication with Quarch Power Modules\n"
              "qps:\n\tLaunches Quarch Power Studio for visualising power data\n"
              "upgrade_quarchpy:\n\tDetects if an update of Quarchpy is available and assists in the upgrade process\n")


if __name__ == "__main__":
    main (sys.argv[1:])