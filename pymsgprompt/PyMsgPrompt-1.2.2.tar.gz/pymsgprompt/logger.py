from pymsgprompt.prompt import log


def perror(message, file=None):
    '''
    message takes a str object, which will be printed as a error message
    file is _io.TextIOWrpper object, or it can also be None which refers stderr
    '''
    return log(message, logtype='error', timestamp=True, file=file, reset=True)


def pwarn(message, file=None):
    '''
    message takes a str object, which will be printed as a warning message
    file is _io.TextIOWrpper object, or it can also be None which refers stderr
    '''
    return log(message, logtype='warn', timestamp=True, file=file, reset=True)


def pinfo(message, file=None):
    '''
    message takes a str object, which will be printed as a information message
    file is _io.TextIOWrpper object, or it can also be None which refers stdout
    '''
    return log(message, logtype='info', timestamp=True, file=file, reset=True)



