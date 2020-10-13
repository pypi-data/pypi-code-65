from dis import get_instructions


class ClientVerifier(type):
    def __init__(self, classname, basesclass, classdict):
        methods = []
        for function in classdict:
            try:
                gener = get_instructions(classdict[function])
            except:
                pass
            else:
                for instruct in gener:
                    if instruct.opname == 'LOAD_GLOBAL':
                        if instruct.argval not in methods:
                            methods.append(instruct.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('Недопустимый метод в классе')
        if 'receive_message' not in methods and 'send_message' not in methods:
            raise TypeError('Функции, работающие с сокетами, отсутствуют')
        super().__init__(classname, basesclass, classdict)


class ServerVerifier(type):
    def __init__(self, classname, basesclass, classdict):
        methods = []
        attributes = []
        for function in classdict:
            try:
                gener = get_instructions(classdict[function])
            except:
                pass
            else:
                for instruct in gener:
                    if instruct.opname == 'LOAD_GLOBAL':
                        if instruct.argval not in methods:
                            methods.append(instruct.argval)
                    elif instruct.opname == 'LOAD_ATTR':
                        if instruct.argval not in attributes:
                            attributes.append(instruct.argval)
        if 'SOCK_STREAM' not in attributes and 'AF_INET' not in attributes:
            raise TypeError('Некорректная инициализация сокета')
        if 'connect' in methods:
            raise TypeError('Недопустимый метод в классе')
        super().__init__(classname, basesclass, classdict)
