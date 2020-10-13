#!/usr/bin/env python
'''
This example runs the calibration process for a HD PPM
It products a calibrated PPM and a calibration file for later use

########### VERSION HISTORY ###########

05/04/2019 - Andy Norrie     - First Version

########### INSTRUCTIONS ###########

1- Connect the PPM on LAN and power up
2- Connect the Keithley 2460 until on LAN, power up and check its IP address
3- Connect the calibration switch unit to the output ports of the PPM and Keithley

####################################
'''

# Global resources
#import quarchpy.calibration.calibrationConfig
from time import sleep,time
import datetime
import logging,os
import sys

# Quarch device control
from quarchpy.device import *

# Calibration control
#from quarchpy.calibration import *
from quarchpy.calibration.keithley_2460_control import *
from quarchpy.calibration.calibration_classes import *
from quarchpy.calibration.HDPowerModule import *
from quarchpy.calibration.QTL2347 import *
from quarchpy.calibration.calibrationConfig import *
from quarchpy.calibration import calibrationConfig
# UI functions
from quarchpy.user_interface import *

# Performs a standard calibration of the PPM
def runCalibration (instrAddress=None, calPath=None, ppmAddress=None, switchboxAddress=None, logLevel="warning", calAction=None, userMode="testcenter"):

    try:
        # Display the app title to the user
        printText("********************************************************")
        printText("          Quarch Technology Calibration System")
        printText("             (C) 2019, All rights reserved")
        printText("                          V" + quarchpy.calibration.calCodeVersion)
        printText("********************************************************")
        printText("")

        # Process parameters
        inputOK = False
        while inputOK is False:
            if (calPath is None):
                calPath = os.path.expanduser("~")
                calPath = requestDialog("Enter Report Path", "Enter the desired save path for the calibration report. Leave blank to defaut to ["+calPath+"] :",desiredType = "path", defaultUserInput=os.path.expanduser("~"))

            if (os.path.isdir(calPath) == False):
                printText ("Supplied calibration path is invalid: " + calPath)
                inputOK = False
                calPath = None
            else:
                inputOK = True

        #check log file is present or writeable
        numeric_level = getattr(logging, logLevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)

        # Creates the calibration header information object for this test run
        calHeader = CalibrationHeaderInformation()
        # Store the current cal header as a resource that can be accessed later
        calibrationResources["CalHeader"] = calHeader


        if ppmAddress != None:
            ppmPassed = True
        else:
            ppmPassed = False
        # main execution loop
        while(True):

            # If no address specified, the user must select the module to calibrate
            if (calAction != None and 'select' in calAction) or (ppmAddress == None):
                # Request user to select the (QTL1999) PPM to calibrate
                ppmAddress = userSelectDevice (scanFilterStr = ["QTL1999","QTL1995","QTL1944","QTL2312"], nice=True, message="Select device for calibration")

                if (ppmAddress.lower() == 'quit'):
                    printText("User Quit Program")
                    return
                if (calAction != None and 'select' in calAction):
                    calAction = None
                ppmPassed = True

                myPpmDevice = quarchDevice(ppmAddress)
                serialNumber = myPpmDevice.sendCommand("*SERIAL?")

                success = False
                # Identify and create a power module object
                if ('1944' in serialNumber):
                    # create HD Power Module Object
                    dut = HDPowerModule(myPpmDevice)
                    success = True
                elif ('2312' in serialNumber):
                    # this is a Power Analysis Module, we need to detect the fixture
                    fixtureId = myPpmDevice.sendCommand("read 0xA401")
                    if ('2347' in fixtureId):
                       dut = QTL2347(myPpmDevice)
                       success = True

                if (success == False):
                    raise ValueError("ERROR - Serial number not recogised as a valid power module")

#TODO: check what device is being calibrated and call appropriate populateCalHeader for that device.
            #    # populate device information in to the cal header
                populateCalHeader_HdPpm(calHeader, dut.dut, calAction)
            #    # populate system information in to the cal header
                populateCalHeader_System(calHeader)

                storeDeviceInfo(serial=calHeader.quarchEnclosureSerial, idn=calHeader.idnStr)
            #    ppmPassed = False

            # create calibration File Name
            # if its a x6, append the port number
            if 'QTL1995' in calHeader.quarchEnclosureSerial.upper():
                calFilename = calHeader.quarchEnclosureSerial + "-" + calHeader.quarchEnclosurePosition
            else:
                calFilename = calHeader.quarchEnclosureSerial


            # keep track of overall pass/fail status, this is set false if we fail a test. it should only be set back to true
            # here, or if the user initiates another test.
            calHeader.result = True                        

            # If no calibration action is selected, request one
            if (calAction == None):

                actionList = []
                actionList.append("calibrate=Calibrate the power module")
                actionList.append("verify=Verify existing calibration on the power module")
                actionList.append("select=Select a different power module")
                #actionList.append("read=Read calibration data from the power module to disk")
                #actionList.append("write=Write calibration data from disk to the power module")
                actionList.append("quit=Quit")
                actionList = ','.join(actionList)

                calAction = listSelection("Select an action","Please select an action to perform",actionList)

            if (calAction == 'quit'):
                if userMode == "testcenter":
                    return calHeader
                else:
                    sys.exit(0)

            # If a read is requested
            if ('read' in calAction):
                
                savedCalibration = dut.readCalibration()

            elif ('write' in calAction):

                dut.writeCalibration(savedCalibration)

            elif ('calibrate' in calAction) or ('verify' in calAction):

                # Creates the calibration header information object for this test run
                #calHeader = CalibrationHeaderInformation()
                # Store the current cal header as a resource that can be accessed later
                #calibrationResources["CalHeader"] = calHeader

                calHeader.calibrationType = calAction

                # If no calibration instrument is provided, request it
                while(True):
                    if (instrAddress == None):
                        instrAddress = userSelectCalInstrument (scanFilterStr = "Keithley 2460", nice=True)
                    try:
                        # Connect to the calibration instrument
                        myCalInstrument = keithley2460 (instrAddress)
                        # Open the connection
                        myCalInstrument.openConnection ()
                        populateCalHeader_Keithley(calHeader, myCalInstrument)
                        break
                    # In fail, allow the user to try again with a new selection
                    except:
                        printText ("Unable to communicate with selected instrument!")
                        printText("")
                        instrAddress = None


                # check self test
                # TODO : check status here

                # open report for writing
                fileName = calPath + "\\" + calFilename + "_" + datetime.datetime.now().strftime("%d-%m-%y_%H-%M" + "-" + calAction + ".txt")
                printText("")
                printText("Report file: " + fileName)
                reportFile = open(fileName,"a+")
                reportFile.write(calHeader.toReportText())
    
                # If a calibration is requested
                if ('calibrate' in calAction):

                    retTupple = dut.calibrate(myCalInstrument, reportFile, calHeader)
                    report = retTupple[0]
                    calHeader = retTupple[1]
                    formatFinalReport(reportFile)

                    if report:
                        printText("\n===================\n|Calibration Passed|\n===================")
                        printText("More information at : " + fileName+"\n\n")
                        reportFile.write("\n===================\n|Calibration Passed|\n===================")
                    else:
                        printText("\n===================\n|Calibration Failed|\n===================")
                        printText("More information at : " + fileName+"\n\n")
                        reportFile.write("\n===================\n|Calibration Failed|\n===================")
                        calHeader.result = False

                    reportFile.write("")
                # If a verify is required
                if ('verify' in calAction):


                    retTupple= dut.verify(myCalInstrument,reportFile, calHeader)
                    report = retTupple[0]
                    calHeader = retTupple[1]
                    formatFinalReport(reportFile)
                    if report:
                        printText("\n====================\n|Verification Passed|\n====================")
                        printText("More information at : " + fileName +"\n\n")
                        reportFile.write("\n====================\n|Verification Passed|\n====================")
                    else:
                        printText("\n====================\n|Verification Failed|\n====================")
                        printText("More information at : " + fileName+"\n\n")
                        reportFile.write("\n====================\n|Verification Failed|\n====================")
                        calHeader.result = False

                # Close all instruments
                myCalInstrument.closeConnection()                 

                reportFile.close()

            # End of Loop
            # if we've done a calibrate, always verify next
            if 'calibrate' in calAction:
                if report:
                    calAction = 'verify'
                else:
                    printText("Not verifying this module because calibration failed")
                    calAction = "quit"
            # else, unless we're selecting a new ppm, clear calAction
            elif 'select' in calAction:
                # Close the current module connection
                myPpmDevice.closeConnection()
            # if we're in testcenter, always exit before selecting a new module
            elif userMode == "testcenter":
                myPpmDevice.closeConnection()
                calAction = "quit"
            else:
                calAction = None
    
    except Exception as thisException:
        try:
            myCalInstrument.setLoadCurrent(0)
            myCalInstrument.closeConnection()
        # Handle case where exception may have been thrown before instrument was set up
        except:
            pass
        logging.error(thisException)

        raise thisException

# Returns a resource from the previous calibration. This is the mechanism for getting results and similar back to
# a higher level automated script.
def getCalibrationResource (resourceName):
    try:
        return calibrationConfig.calibrationResources[resourceName]
    except:
        return None



def formatFinalReport(reportFile):
    with open(reportFile.name, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        overview = []
        for line in lines:
            if not line.__contains__("worst case:"):
                f.write(line)
            else:
                overview.append(line)
        for i in overview:
            f.write(i)

def getFailuresFromReport(reportFile):
    with open(reportFile.name, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        listOfFailures = []
        for line in lines:
            if line.__contains__("worst case:") and line.__contains__("False"):
                listOfFailures.append(line)
    listOfFailures = ''.join(listOfFailures)
    return listOfFailures;

def main(argstring):
    import argparse
    # Handle expected command line arguments here using a flexible parsing system
    parser = argparse.ArgumentParser(description='Calibration utility parameters')
    parser.add_argument('-a', '--action', help='Calibration action to perform', choices=['calibrate', 'verify'], type=str.lower)
    parser.add_argument('-m', '--module', help='IP Address or netBIOS name of power module to calibrate', type=str.lower)
    parser.add_argument('-s', '--switchbox', help='The Switchbox between the module and the calibration instrument', type=str.lower)
    parser.add_argument('-i', '--instr', help='IP Address or netBIOS name of calibration instrument', type=str.lower)
    parser.add_argument('-p', '--path', help='Path to store calibration logs', type=str.lower)
    parser.add_argument('-l', '--logging', help='Level of logging to report', choices=['warning', 'error', 'debug'], type=str.lower,default='warning')
    parser.add_argument('-u', '--userMode', help='User mode',choices=['console','testcenter'], type=str.lower,default='console')
    parser.add_argument('-t', '--temperature', help='Temperature of the enclosure that the unit is calibrated inside. Should be 25C', type=str.lower)
    args = parser.parse_args(argstring)
    
    # Create a user interface object
    thisInterface = User_interface(args.userMode)

    # Call the main calibration function, passing the provided arguments
    runCalibration(instrAddress = args.instr, calPath = args.path, ppmAddress = args.module,switchboxAddress = args.switchbox, logLevel = args.logging, calAction = args.action, userMode = args.userMode)

#Command to run from terminal.
#python -m quarchpy.calibration -mUSB:QTL1999-01-002 -acalibrate -i192.168.1.210 -pC:\\Users\\sboon\\Desktop\\calData
# --path C:\Users\sboon\Desktop\calData
if __name__ == "__main__":
    #main(['-musb::QTL1999-02-001','-acalibrate','-i192.168.1.210','-pC:\\Users\\sboon\\Desktop\\Boon Cave\\CalDump'])
    main (sys.argv[1:])
    #main (sys.argv)