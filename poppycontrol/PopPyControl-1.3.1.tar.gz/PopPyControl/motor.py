from PopPyControl.protocol import pingCommand, readCommand, writeCommand
import time
import json

testMotors = True


class Motor:
    def __init__(self, _serialPort, _name, _limits, _robot, motorID, typeMotor):
        self.serialPort = _serialPort
        self.name = _name
        self.id = motorID
        self.type = typeMotor
        self.limits = _limits
        self.robot = _robot

        if testMotors:
            tentativas = 0
            while True:
                ping = self.ping()
                if ping.status == 'OK':
                    break
                else:
                    p = 'Tentando conexao com o motor {} id {}'.format(
                        self.name,
                        self.id
                    )
                    print(p)
                    time.sleep(0.1)
                    if tentativas > 5:
                        p = 'Falha ao se conectar com o motor {} id {}'.format(
                            self.name,
                            self.id
                        )
                        print(p)
                        print('Programa abortado!')
                        self.robot.close()
                        exit()
                    tentativas += 1

        print(self)

    def __str__(self):
        if testMotors:
            ping = self.ping()
            if ping.status == 'OK':
                res = "<Motor "
                res += "id:{}; ".format(self.id)
                res += "name:{}; ".format(self.name)
                res += "position:{}; ".format(self.getPosition())
                res += "torque:{}; ".format(self.getTorque())
                res += "led:{}>".format(self.getLED())
                return res
            else:
                res = "<Motor "
                res += "id:{}; ".format(self.id)
                res += "name:{}; ".format(self.name)
                res += "error:{}>".format(ping.status)
                return res
        else:
            res = "<Motor "
            res += "id:{}; ".format(self.id)
            res += "name:{}>".format(self.name)
            return res

    def getLoad(self):
        response = self.read(40, 2)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def getSpeed(self):
        response = self.read(38, 2)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def getTemperature(self):
        response = self.read(43, 1)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def getPosition(self):
        response = self.read(30, 2)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def getTorque(self):
        response = self.read(24, 1)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def getLED(self):
        response = self.read(25, 1)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def getTorqueLimit(self):
        response = self.read(34, 2)

        if response.status != 'OK':
            print('Motor {} id {} erro {}!'.format(
                self.name,
                self.id,
                response.status
            ))

            _ = input("Pressione qualquer tecla para continuar!")
            return None
        else:
            return response.value

    def setPosition(self, position):
        if self.limits['min'] <= position <= self.limits['max']:
            return self.write(30, 2, position)
        else:
            print('Posicao {} fora dos limites do motor {} id {}!!!'.format(
                position,
                self.name,
                self.id
            ))
            print('Limites min {} e max {} desse motor!'.format(
                self.limits['min'],
                self.limits['max']
            ))
            print('Pressione ENTER para abortar o codigo!')
            a = input('Ou "C" + ENTER para continuar: ')

            if a == 'C':
                return "Error"
            else:
                self.robot.close()
                time.sleep(0.5)
                exit()

    def setLED(self, led):
        return self.write(25, 1, led)

    def setTorque(self, torque):
        return self.write(24, 1, torque)

    def setTorqueLimit(self, torqueLimit):
        return self.write(34, 2, torqueLimit)

    def ping(self):
        return pingCommand(self.serialPort, self.id)

    def read(self, address, size):
        return readCommand(self.serialPort, self.id, address, size)

    def write(self, address, size, value):
        return writeCommand(self.serialPort, self.id, address, size, value)

    def update(self):
        with open('data/motors.json') as motors:
            motorsData = json.load(motors)
            self.limits = {
                'min': motorsData['motors'][self.name]['angleLimits']['min'],
                'max': motorsData['motors'][self.name]['angleLimits']['max']
            }

        self.setTorque(0)
        self.write(6, 2, self.limits['min'])
        self.write(8, 2, self.limits['max'])

    def balance(self):
        torqueLimit = self.getTorqueLimit()

        self.setTorqueLimit(1023)
        while True:
            load = self.getLoad()
            position = self.getPosition()

            if type(position) == int and type(torqueLimit) == int:
                if 5 < load and load < 1024:
                    self.setPosition(position - 2)
                elif 1029 < load and load < 2048:
                    self.setPosition(position + 2)
                else:
                    self.setTorqueLimit(torqueLimit)
                    break
            else:
                break
