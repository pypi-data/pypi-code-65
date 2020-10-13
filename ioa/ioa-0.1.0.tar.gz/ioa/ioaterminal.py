#! /usr/bin/python3

######################################################################
#
# 	IoA-Python: ioaagent.py
#
# 	This program connects to the local IoA TCP server,
# 	provides a IoA Shell to the user.
#
######################################################################

# TODO allow longer string receives and sends (see ioa, interpreter)

#####		Imports 		#####

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

#####		Functions		#####


def com(data=" ", device="localhost"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((device, settings["IOA_PORT"]))
        s.sendall(bytes(data + "\n", "utf8"))
        return str(s.recv(1024), "utf8")


#####	   Main Program		#####

try:
    com()
    while True:
        command = input(" > ")
        if command == "exit":
            print("Exiting...")
            exit()
        print(com(command))
except OSError:
    print("[Error] Make sure this device has IoA ready to connect")
except KeyboardInterrupt:
    print()
