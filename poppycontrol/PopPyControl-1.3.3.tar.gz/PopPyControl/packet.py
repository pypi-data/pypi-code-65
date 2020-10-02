class Packet:
    def __init__(self, reqByte, resByte):
        self.value = 0
        if len(reqByte) == 0:
            self.status = 'Request Null'
        self.req = reqByte

        if len(resByte) == 0:
            self.status = 'Response Null'
        else:
            if hex(resByte[0]) == '0x0':
                del(resByte[0])

            if hex(resByte[-1]) == '0x0':
                del(resByte[-1])

        self.res = resByte

        reqStr = []
        for byte in reqByte:
            reqStr.append(str(hex(byte)).replace('0x', ''))
        self.reqStr = ' '.join(reqStr)

        resStr = []
        for byte in resByte:
            resStr.append(str(hex(byte)).replace('0x', ''))
        self.resStr = ' '.join(resStr)

        if len(resByte) >= 6:
            self._infos()
        else:
            self.status = 'Response Null'

    def _infos(self):
        self.id = self.res[2]
        self._initErrors()

        value = self.res[5:-1][::-1]

        if value == []:
            self.value = None
        else:
            for val in value:
                self.value *= 256
                self.value += val

    def _initErrors(self):
        self.errorsList = []
        error = self.res[4]

        if error == 0:
            self.status = 'OK'
            return True

        if error >= 64:
            self.errorsList.append('Instruction error')
            error -= 64

        if error >= 32:
            self.errorsList.append('Overload error')
            error -= 32

        if error >= 16:
            self.errorsList.append('Checksum Error')
            error -= 16

        if error >= 8:
            self.errorsList.append('Range Error')
            error -= 8

        if error >= 4:
            self.errorsList.append('Overheating Error')
            error -= 4

        if error >= 2:
            self.errorsList.append('Angle Limit Error')
            error -= 2

        if error >= 1:
            self.errorsList.append('Input Voltage Error')
            error -= 1

        self.status = ' / '.join(self.errorsList)
