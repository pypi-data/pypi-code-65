from PopPyControl.motor import Motor
from PopPyControl.protocol import clearPort
from serial import Serial, SerialException
import json
import time
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

motorsLegs = []
motorsTorso = []


class Poppy:
    def __init__(self):
        self.motors = {}

        self.serialPortLegs = Serial()
        self.serialPortTorso = Serial()

        with open(dir_path + "/data/ports.json") as ports:
            portsData = json.load(ports)
            dataLegs = portsData['legs']
            dataTorso = portsData['torso']
            try:
                self.serialPortLegs.port = dataLegs['port']
                self.serialPortLegs.baudrate = int(dataLegs['baudrate'])
                self.serialPortLegs.timeout = float(dataLegs['timeout'])
                self.serialPortLegs.open()
            except SerialException:
                print('Leg port is already being used!')
                print('Aborted program!')
                self.serialPortLegs.close()
                exit()

            time.sleep(1.5)

            try:
                self.serialPortTorso.port = dataTorso['port']
                self.serialPortTorso.baudrate = int(dataTorso['baudrate'])
                self.serialPortTorso.timeout = float(dataTorso['timeout'])
                self.serialPortTorso.open()
            except SerialException:
                print('Torso port is already being used!')
                print('Aborted program!')
                self.serialPortLegs.close()
                self.serialPortTorso.close()
                exit()

            time.sleep(1.5)
            clearPort(self.serialPortLegs)
            clearPort(self.serialPortTorso)

        with open(dir_path + "/data/motors.json") as motors:
            motorsData = json.load(motors)

            for motorName in motorsData['motors']:
                if motorsData['motors'][motorName]['type'] == 'legs':
                    motorsLegs.append(motorsData['motors'][motorName]['name'])
                if motorsData['motors'][motorName]['type'] == 'torso':
                    motorsTorso.append(motorsData['motors'][motorName]['name'])

        for motor in motorsLegs:
            name = str(motorsData['motors'][motor]['name'])
            limits = {
                'min': motorsData['motors'][motor]['angleLimits']['min'],
                'max': motorsData['motors'][motor]['angleLimits']['max']
            }
            motorObj = Motor(
                _serialPort=self.serialPortLegs,
                _name=name,
                _limits=limits,
                _robot=self,
                motorID=int(motorsData['motors'][motor]['id']),
                typeMotor=str(motorsData['motors'][motor]['type'])
            )

            self.__dict__[name] = motorObj
            self.motors[int(motorsData['motors'][motor]['id'])] = motorObj

            name = ''
            limits = {}

        for motor in motorsTorso:
            name = str(motorsData['motors'][motor]['name'])
            limits = {
                'min': motorsData['motors'][motor]['angleLimits']['min'],
                'max': motorsData['motors'][motor]['angleLimits']['max']
            }
            motorObj = Motor(
                _serialPort=self.serialPortTorso,
                _name=name,
                _limits=limits,
                _robot=self,
                motorID=int(motorsData['motors'][motor]['id']),
                typeMotor=str(motorsData['motors'][motor]['type'])
            )

            self.__dict__[name] = motorObj
            self.motors[int(motorsData['motors'][motor]['id'])] = motorObj

            name = ''
            limits = {}

    def open(self):
        self.serialPortLegs.open()
        self.serialPortTorso.open()

    def close(self):
        self.clear()
        self.serialPortLegs.close()
        self.serialPortTorso.close()

    def status(self):
        for id, motor in self.motors.items():
            print(str(motor))

    def balance(self, motorsID):
        while True:
            test = False

            for motID in motorsID:
                load = self.motors[motID].getLoad()
                position = self.motors[motID].getPosition()

                if type(position) == int and type(load) == int:
                    if 14 < load and load < 1024:
                        test = True
                        self.motors[motID].setPosition(position - 4)
                    elif 1038 < load and load < 2048:
                        test = True
                        self.motors[motID].setPosition(position + 4)

            if not test:
                break

    def clear(self):
        clearPort(self.serialPortLegs)
        clearPort(self.serialPortTorso)

    def deactivate(self):
        self.clear()
        self.close()
