#! /usr/bin/python3

######################################################################
#
# 	IoA-Python: interpreter/__init__.py
#
# 	Interprets commands of the IoA language.
#
######################################################################

# TODO allow longer string receives and sends (see ioa/__init__.py)
# TODO better variable names in the interpreter "cgroup" et cetera

# TODO add more resources
# TODO add a documentation for the different commands / the Language

#####		Imports		#####

import json

settings = {
    "IOA_PORT": 13409,
    "LOCAL_IP": "",
    "ESP32_LDR_IP": "",
    "LIGHTIFY_GATEWAY_IP": "",
    "LIGHTIFY_GROUP": "All",
    "LIGHTAGENT_OPTIMUM": 1200,
    "LIGHTAGENT_TOLERANCE": 70,
}

import socket

import resources

#####	 Interpreter	#####


class Interpreter:
    enumeration = {}
    resources = []
    devices = {}

    class Resource:
        def __init__(self, cgroup, name, interpret, operations):
            self.cgroup = cgroup
            self.name = name
            self.interpret = interpret
            self.operations = operations

    def addResource(resource):
        if resource.cgroup not in Interpreter.enumeration:
            Interpreter.enumeration[resource.cgroup] = {}
        Interpreter.enumeration[resource.cgroup][resource.name] = resource.operations
        Interpreter.resources.append(resource)

    def getDeviceInactivity(ipAddress):
        if ipAddress in Interpreter.devices:
            return Interpreter.devices[ipAddress]
        else:
            return -1

    def markActiveDevice(ipAddress):
        if ipAddress not in [settings["LOCAL_IP"], "127.0.0.1", "localhost"]:
            Interpreter.devices[ipAddress] = 0

    def removeInactiveDevices():
        updatedDevices = {}
        deviceIpList = list(Interpreter.devices.keys())

        for deviceIp in deviceIpList:
            deviceInactivity = Interpreter.getDeviceInactivity(deviceIp)
            if deviceInactivity < 4:
                updatedDevices[deviceIp] = deviceInactivity + 1

        for deviceIp in list(Interpreter.devices.keys()):
            if deviceIp not in updatedDevices:
                del Interpreter.devices[deviceIp]
            else:
                Interpreter.devices[deviceIp] = updatedDevices[deviceIp]

    def interpret(command):
        cgroup = getArgument(command, 0)  # capability
        name = getArgument(command, 1)  # resource

        if cgroup == "":
            return "."

        if cgroup == "enum":
            if name == "":
                return json.dumps(Interpreter.enumeration)
            elif name in Interpreter.enumeration:
                res = getArgument(command, 2)
                if res == "":
                    return json.dumps(Interpreter.enumeration[name])
                elif res in Interpreter.enumeration[name]:
                    return json.dumps(Interpreter.enumeration[name][res])
                else:
                    return "[Error] unknown resource"
            else:
                return "[Error] unknown cgroup"

        if cgroup == "dev":
            if name == "":
                return str(list(Interpreter.devices.keys()))
            else:
                tcpCommand = getArgument(command, 2)  # dev <name> <tcpCommand>
                if name == ".":
                    responses = ""
                    ipList = list(Interpreter.devices.keys())
                    for ip in ipList:
                        responses += Interpreter.tcpInterpret(ip, tcpCommand)
                        if ip != ipList[-1]:
                            responses += "\n"
                    return responses
                elif name in Interpreter.devices:
                    return Interpreter.tcpInterpret(name, tcpCommand)
                else:
                    return "[Error] unknown device"

        for resource in Interpreter.resources:
            if (resource.cgroup == cgroup) and (resource.name == name):
                return resource.interpret(command)

        return "[Error] unknown capability group"

    def tcpInterpret(host, data):
        if data == "":
            data = " "
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpC:
                tcpC.connect((host, settings["IOA_PORT"]))
                tcpC.sendall(bytes(data + "\n", "utf8"))
                return "[TCP " + host + "] " + str(tcpC.recv(1024), "utf8")
        except:
            return "[Error] Not connected"


#####	Add Resources	#####

Interpreter.addResource(
    Interpreter.Resource(
        "act",
        "lamps",
        resources.act.interpret_lamps,
        ["init", "brightness (<int>)", "rgb <r> <g> <b>", "temp <temperature>"],
    )
)
