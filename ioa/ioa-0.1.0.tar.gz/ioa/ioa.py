#! /usr/bin/python3

######################################################################
#
# 	IoA-Python: ioa/__init__.py
#
# 	Handles the protocols / servers:
#
# 	+ remotely interpret IoA-Commands (TCP Server)
# 	+ every 5sec: notify every device with beacon (UDP Client)
# 		and check to devices inactivity
# 	+ receive the beacons from other targets (UDP Server)
#
######################################################################

# TODO allow longer string receives and sends (see interpreter/__init__.py)
# TODO more info in the beacons

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
import time
from threading import Thread

from interpreter import Interpreter

#####		IoA		#####


class IoA:
    # Start all the server processes
    def takeOver():
        tcpServer = Thread(target=IoA.tcpServerTask, daemon=True)
        tcpServer.start()
        IoA.debug("tcp server setup done")

        udpBroadcaster = Thread(target=IoA.udpBroadcastTask, daemon=True)
        udpBroadcaster.start()
        IoA.debug("udp broadcaster setup done")

        udpServer = Thread(target=IoA.udpReceiverTask, daemon=True)
        udpServer.start()
        IoA.debug("udp receiver setup done")

    # prevent IOErrors
    def debug(message):
        try:
            print("[Debug]", message)
        except IOError:
            pass

    # remotely interpret IoA-Commands (TCP Server)
    def tcpServerTask():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpS:
            tcpS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            tcpS.bind(("", settings["IOA_PORT"]))
            tcpS.listen(5)

            while True:
                conn, addr = tcpS.accept()
                Interpreter.markActiveDevice(addr[0])
                with conn:
                    data = str(conn.recv(1024), "utf8")
                    conn.send(bytes(Interpreter.interpret(data.split("\n")[0]), "utf8"))

    # every 5sec: notify every device with beacon (UDP Client)
    # 	and check to devices inactivity
    def udpBroadcastTask():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udpC:
            udpC.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            udpC.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udpC.settimeout(0.2)  # don't block

            while True:
                try:
                    udpC.sendto(b"[HBeacon]", ("<broadcast>", settings["IOA_PORT"]))
                except OSError:
                    IoA.debug("[Error] Can't broadcast UDP")
                    time.sleep(5)
                Interpreter.removeInactiveDevices()
                time.sleep(5)

    # receive the beacons from other targets (UDP Server)
    def udpReceiverTask():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udpS:
            udpS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            udpS.bind(("<broadcast>", settings["IOA_PORT"]))

            while True:
                data, addr = udpS.recvfrom(1024)
                Interpreter.markActiveDevice(addr[0])
