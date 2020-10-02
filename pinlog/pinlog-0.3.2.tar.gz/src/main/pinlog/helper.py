from pinlog.log import Log
from pintrace.tracer import latency, start, end, pin, unpin, trace, filter

def get_wrapper(base):
    class Wrapper(base):
        # def __init__(self, string1):
        #     print('1 : ', string1)

        def wrap(string1):
            print('2 : ', string1)
            print(len(string1))

    return Wrapper

class SuperWrapper():
    def __init__(self):
        print('1 : ', string1)

    def wrap1(self, xxx):
        print("wrap1 : ", xxx)

    def wrap2(self, xxx):
        print("wrap2")

        


@start(Log.Console, Log.Logstash, Log.Graylog)
def start(req, child, payload):
    print("START INPUT: ", payload)
    # output = payload.copy()
    # output['extension'] = 'START'
    # print("OUTPUT: ", output)
    return None

@end(Log.Console, Log.Logstash, Log.Graylog)
def end(req, child, payload):
    print("END INPUT: ", payload)
    # output = payload.copy()
    # output['extension'] = 'END'
    # print("OUTPUT: ", output)
    return None

@pin
def pin(p):
    pass

@unpin
def unpin(p):
    pass

@trace
def trace(p1, payload):
    pass

@latency
def latency(p1, p2):
    pass

@filter
def filter(log, keys):
    pass


def Logger(*_args):
    def inner(func):
        def wrapper(*__args, **__kwargs):
            # print('Class name : ', func.__name__)
            c = func(*__args, **__kwargs)
            # print('Class object : ', type(c))
            # return get_wrapper(client.__class__)
            # return get_wrapper(func)
            # func.pin = pin
            c.pin = pin
            c.trace = trace
            c.latency = latency
            c.unpin = unpin
            return c
            # return None
        return wrapper
    return inner

def Console(*_args):
    def inner(func):
        def wrapper(*__args, **__kwargs):
            filter('console', _args)
            c = func(*__args, **__kwargs)
            # func.pin = pin
            return c
            # return None
        return wrapper
    return inner

def Logstash(*_args):
    def inner(func):
        def wrapper(*__args, **__kwargs):
            filter('logstash', _args)
            c = func(*__args, **__kwargs)
            # func.wrap = SuperWrapper.wrap1
            return c
            # return None
        return wrapper
    return inner

def Graylog(*_args):
    def inner(func):
        def wrapper(*__args, **__kwargs):
            filter('graylog', _args)
            c = func(*__args, **__kwargs)
            # func.wrap = SuperWrapper.wrap1
            return c
            # return None
        return wrapper
    return inner

def Filters(*_args):
    def inner(func):
        def wrapper(*__args, **__kwargs):
            # filter('filters', _args)
            filter( _args)
            c = func(*__args, **__kwargs)
            c.pin = pin
            c.trace = trace
            c.latency = latency
            c.unpin = unpin
            return c
        return wrapper
    return inner
