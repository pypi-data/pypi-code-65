import os
import time
import bisect
import pickle
from functools import wraps

def hashArgsAndKwargs(args, kwargs):
    return hash((args, tuple(kwargs.items())))

class Cache:

    persistent = False
    cache={}
    filepath=None

    def __init__(self, filename=None, cacheDir=None):
        if cacheDir is not None and filename is not None:
            self.persistent = True
            os.makedirs(cacheDir, exist_ok=True)
            self.filepath = os.path.join(cacheDir, filename)
            self.loadCacheFromFile()

    def loadCacheFromFile(self):
        if os.path.isfile(self.filepath):
            with open(self.filepath, "rb") as f:
                self.cache = pickle.load(f)

    def __contains__(self, key):
        return key in self.cache
    
    def __getitem__(self, key):
        return self.cache[key]["value"]
    
    def __setitem__(self, key, value):
        self.cache[key] = {"timestamp": time.time(), "value": value}

        if self.persistent:
            with open(self.filepath, "wb") as f:
                pickle.dump(self.cache, f)

    def invalidateBefore(self, firstValidTime):
        toDel = []
        for key, stuff in self.cache.items():
            if stuff["timestamp"] < firstValidTime:
                toDel.append(key)
        
        for key in toDel:
            del self.cache[key]
        
        if self.persistent:
            with open(self.filepath, "wb") as f:
                pickle.dump(self.cache, f)

    def invalidateCall(self, *args, **kwargs):
        key = hashArgsAndKwargs(args, kwargs)
        if key in self.cache:
            del self.cache[key]

            if self.persistent:
                with open(self.filepath, "wb") as f:
                    pickle.dump(self.cache, f)

    def __repr__(self):
        s = f"filepath: {self.filepath}\n"
        s += f"cache: [\n"
        for stuff in self.cache.values():
            t = stuff['timestamp']
            t = time.asctime(time.localtime(t))

            val = stuff['value']
            s += f"    (t='{t}', val='{val}')\n"
        s += "]\n"
        return s


def cacheMe(filename=None, cacheDir="__cmoCache__"):
    
    def decorator(f):
        pastCalls = Cache(filename, cacheDir)

        @wraps(f)
        def fCached(*args, **kwargs):
            key = hashArgsAndKwargs(args, kwargs)

            if key in pastCalls:
                return pastCalls[key]

            result = f(*args, **kwargs)
            pastCalls[key] = result
            return result

        fCached.cmoCache = pastCalls

        return fCached

    return decorator
