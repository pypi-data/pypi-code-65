import base64
import time
import traceback
from pycachedb.embedded_cache import EmbeddedCache

db = EmbeddedCache()

def start(*logs):
    def inner(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            db.insert(args[0], args[1], start_time)
            payload = {
                'function': func.__name__,
                # 'inbound': base64.b64encode(f'{args[2]}'.encode()),
                'params': args,
                'additionals': kwargs
            }

            for key in logs[0].keys():
                if args[2][key] == None:
                    continue
                payload[key] = args[2][key]

            payload['timestamp'] = start_time
            result = None
            try:
                result = func(*args, **kwargs)
            except Exception:
                # result = f'================================\n{traceback.format_exc()}================================'
                payload['error'] = traceback.format_exc()
            # latency = time.time() - start_time
            # payload['outbound'] = base64.b64encode(f'{result}'.encode())
            # payload['latency'] = latency
            # print("--- %.8f seconds first execution ---" % (latency))
            # return result
            return payload
        return wrapper
    return inner

def end(*logs):
    def inner(func):
        def wrapper(*args, **kwargs):
            start_time = db.search(args[0], args[1])
            db.delete(args[0], args[1])
            payload = {
                'function': func.__name__,
                # 'inbound': base64.b64encode(f'{args[2]}'.encode()),
                'params': args,
                'additionals': kwargs
            }

            for key in logs[0].keys():
                if args[2][key] == None:
                    continue
                payload[key] = args[2][key]

            result = None
            try:
                result = func(*args, **kwargs)
            except Exception:
                # result = f'================================\n{traceback.format_exc()}================================'
                payload['error'] = traceback.format_exc()
            latency = time.time() - start_time
            # payload['outbound'] = base64.b64encode(f'{result}'.encode())
            payload['latency'] = latency
            # print("--- %.8f seconds first execution ---" % (latency))
            return payload
        return wrapper
    return inner

def pin(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        db.insert(args[0], None, start_time)
        return None
    return wrapper

def unpin(func):
    def wrapper(*args, **kwargs):
        db.delete(args[0], None)
        return None
    return wrapper

def trace(func):
    def wrapper(*args, **kwargs):
        start_time = db.search(args[0], None)
        payload = {}

        # if db.search('filters', None):
        #     for key in db.search('filters', None):
        if db.get_filters():
            for key in db.get_filters():
                if not args[1].get(key):
                    payload[key] = None
                    continue
                payload[key] = args[1][key]
        else:
            payload = args[1]

        if start_time:
            # db.delete(args[0], None)
            payload['latency'] = (time.time() - start_time)*1000
        else:
            payload['latency'] = 0

        return payload
    return wrapper

def latency(func):
    def wrapper(*args, **kwargs):
        start_time = db.search(args[0], None)
        end_time = db.search(args[1], None)
        if start_time and end_time:
            # db.delete(args[0], None)
            # db.delete(args[1], None)
            return (end_time - start_time)*1000
        else:
            return 0
    return wrapper

def filter(func):
    def wrapper(*args, **kwargs):
        # db.insert(args[0], None, args[1])
        db.set_filters(args[0])
        return None
    return wrapper

