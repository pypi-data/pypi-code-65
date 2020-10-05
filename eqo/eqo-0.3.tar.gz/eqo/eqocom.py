import bitarray as B
import itertools
import numpy as np
import os
import socket
import sys
import time
from math import ceil
from tqdm import tqdm

from .qubo          import Ising, columns, ising_to_qubo
from .qubo.analyze  import parameterBounds

def green(s):
    return "\u001b[32m" + s + "\u001b[0m"

def blue(s):
    return "\u001b[34m" + s + "\u001b[0m"

def limitLength(s, l):
    actual_l = len(s)
    if actual_l > l:
        return '...' + s[actual_l-l:]
    else:
        return s

def bytesToHexString(bs):
    return "".join('{:02x}'.format(b) for b in bs)

def bytesToBitarray(bs):
    ba = B.bitarray(endian='big')
    ba.frombytes(bs)
    return ba

def bytesToDict(bs, crop=0):
    ba = B.bitarray(endian='big')
    ba.frombytes(bs)
    ba.reverse()
    if crop > 0:
        return { i: int(ba[i]) for i in range(crop) }
    else:
        return { i: int(b) for i, b in enumerate(ba) }

def bitarrayToBytes(ba):
    if ba.endian == 'little':
        raise ValueError('bitarray must be big endian')
    else:
        return ba.tobytes()

class EQOCom:
    def __init__(self, connection=("192.168.1.128", 1234), verbose=False):
        # create socket for UDP communication
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__connection = connection

        self.__started   = False
        
        self.__dim        = None
        self.__offspring  = None
        self.__paramWidth = None
        
        self.__seed    = None
        self.__parent  = None
        self.__timeout = None
        self.__ixmask    = None
        
        self.verbose = verbose
       
    def __enter__(self):
        self.reset()
        # silently retrieve status info
        tmp = self.verbose
        self.verbose = False
        self.info()
        self.verbose = tmp
        return self

    def __exit__(self, *args):
        self.reset()
        if not self.__socket._closed:
            self.__socket.close()

    def __check_configuring(self):
        if self.__started:
            raise RuntimeError("Optimization already started")
        
    def disconnect(self):
        self.__report("disconnect")
        self.__socket.close()
        self.__connected = False
    
    def __write(self, bytestr):
        self.__socket.sendto(bytestr, self.__connection)
    
    def __read(self, b=1):
        data, _ = self.__socket.recvfrom(b)
        return data
        
    def __report(self, *args, **kwargs):
        if self.verbose:
            print(green(" > "), end='')
            print(*args, **kwargs)
    
    @property
    def dimension(self):
        if self.__dim is None:
            self.info()
        return self.__dim
    
    @property
    def indexMask(self):
        return self.__ixmask
    
    @property
    def offspring(self):
        if self.__offspring is None:
            self.info()
        return self.__offspring

    @property
    def paramWidth(self):
        if self.__paramWidth is None:
            self.info()
        return self.__paramWidth

    @property
    def seed(self):
        if self.__seed is None:
            self.info()
        return self.__seed

    @property
    def parent(self):
        #if self.__parent is None:
            #self.info()
        return self.__parent
    
    @property
    def timeout(self):
        if self.__timeout is None:
            self.info()
        return self.__timeout
    
    @seed.setter
    def seed(self, seed):
        self.__check_configuring()
        if seed is None:
            seed = os.urandom(20)
        self.__report("set seed to", bytesToHexString(seed))
        self.__write(b'x' + seed[::-1])
        self.__seed = seed
        
    @parent.setter
    def parent(self, parent):
        self.__check_configuring()
        if parent is None:
            parentBytes = (self.dimension+7)//8
            parent = os.urandom(parentBytes)
        
        self.__report("set parent to", bytesToHexString(parent))
        self.__write(b'p' + parent[::-1])
        self.__parent = parent
            
    @timeout.setter
    def timeout(self, timeout):
        self.__check_configuring()
        if timeout < 0 or timeout > 2**31-1:
            raise ValueError("timeout value out of range [0 .. 2*31-1]")
        
        self.__report("set timeout to", timeout, "generations")
        self.__write(b't' + int.to_bytes(timeout, length=4, byteorder='little'))
        self.__timeout = timeout
            
    @indexMask.setter
    def indexMask(self, mask):
        self.__check_configuring()
        
        # mask is assumed to be in little endian order!
        self.__report(f"set index mask to {format(int.from_bytes(mask, byteorder='little'), '016b')}")
        self.__write(b'm' + mask)
        self.__ixmask = mask
    
    def reset(self):
        self.__report("reset")
        self.__write('r'.encode())
        self.__started   = False
        self.__seed      = None
    
    def start(self):
        self.__check_configuring()
        
        self.__report("start")
        self.__write('s'.encode())
        self.__started = True
    
    def randomize(self):
        self.parent = None
        self.seed   = None
    
    def loadParameters(self, params, chunksize=768):
        self.__check_configuring()

        expectedParams = self.dimension ** 2
        paramBytes     = ceil(self.paramWidth/8.0)
        
        self.__report("send", expectedParams, "parameters,", paramBytes, "Byte(s) each ... ")
        
        payload = b''
        progress = tqdm(total=expectedParams, desc='Upload', disable=not self.verbose)
        for parameter, _ in itertools.zip_longest(params, range(expectedParams), fillvalue=0):
            assert isinstance(parameter, int), 'Attempted to upload non-integer parameter to EQO'

            # check if payload buffer needs to be flushed
            if len(payload) >= chunksize:
                self.__write(payload[:chunksize])
                payload = payload[chunksize:]

            # encode parameter and append to payload buffer
            payload += 'c'.encode()
            payload += parameter.to_bytes(paramBytes, byteorder='little', signed=True)
            progress.update(1)

        # flush remaining payload buffer
        if len(payload) > 0:
            self.__write(payload)

        progress.close()

    def status(self):
        self.__report("request status info ...")
        self.__write('o'.encode())
        
        result = self.__read((self.dimension+7)//8 + 28)
        #self.__report("  raw result:", result)
        
        self.__mutrate     = int.from_bytes(result[0:4], byteorder='little', signed=False)
        self.__generation  = int.from_bytes(result[4:10], byteorder='little', signed=False)
        self.__imp_clockcycle = int.from_bytes(result[10:18], byteorder='little', signed=False)
        self.__imp_generation = int.from_bytes(result[18:24], byteorder='little', signed=False)
        self.__improvement = int.from_bytes(result[24:28], byteorder='little', signed=True)
        self.__solution    = result[:27:-1]
        
        self.__report(f"  x = {blue(limitLength(bytesToHexString(self.__solution), 64))} ({green(str(self.__improvement))})")
        self.__report(f"  found in gen. {self.__imp_generation}, cycle {self.__imp_clockcycle}")
        self.__report(f"  currently in gen. {self.__generation} with mut. rate {'{:.1%}'.format(self.__mutrate/(2**16-1))} (ca. {format((2**16)/(2**16-self.__mutrate), '.2f')} flips per mut.)")

        #return self.__solution, self.__improvement, self.__imp_generation, self.__imp_clockcycle, self.__generation, self.__mutrate
        return { 'solution':    self.__solution,
                 'improvement': self.__improvement,
                 'impgen':      self.__imp_generation,
                 'impclk':      self.__imp_clockcycle,
                 'generation':  self.__generation,
                 'mutrate':     self.__mutrate }

    def info(self):
        self.__report("request configuration info ...")
        self.__write(b'i')
        
        result = self.__read(b=28)
        self.__report("  raw result:  ", ':'.join(list(map(lambda x: hex(x)[2:], result))), f"{len(result)}B")

        self.__dim        = int.from_bytes(result[0:2], byteorder='little')
        self.__offspring  = int(result[2]) 
        self.__paramWidth = int(result[3])
        self.__seed       = result[-5:3:-1] # seed in reverse order to correct endianness
        self.__timeout    = int.from_bytes(result[-4:], byteorder='little')
         
        self.__report(f"  n={self.__dim}, λ={self.__offspring}, b={self.__paramWidth}, T={self.__timeout}")
        self.__report(f"  seed={bytesToHexString(self.__seed)}")

        #return self.__dim, self.__offspring, self.__paramWidth, self.__seed, self.__timeout
        return { 'dimension': self.__dim,
                 'offspring': self.__offspring,
                 'parambits': self.__paramWidth,
                 'seed':      self.__seed,
                 'timeout':   self.__timeout }
    
    def loadQUBO(self, qubo, scale=True, skipRound=False): 
        n = qubo.n
        
        if n > self.dimension:
            raise RuntimeError(f"QUBO dimension {qubo.n} larger than max. dimension {self.dimension}")
        
        if isinstance(qubo, Ising):
            sys.stdout.write('Convert Ising model to QUBO? [Y/n]')
            choice = input().lower()
            if choice not in { 'no', 'n' }:
                qubo = ising_to_qubo(qubo)

        self.__report(f"loading QUBO instance with dimension {n}")     
        if scale:
            self.__report(f"scaling and rounding parameters to {self.paramWidth} bit integers")
            
            factor = (2**(self.paramWidth-1)-1) / qubo.absmax()
            qubo = qubo.scaled(factor).rounded()
        else:
            # rounding must be done in any case
            self.__report("round parameters")
            factor = 1.0
            if not skipRound:
                qubo = qubo.rounded()
            (a, b) = parameterBounds(qubo, ignoreBias=True)
            if a < -(2 ** (self.paramWidth-1)) or b > 2 ** (self.paramWidth-1) - 1:
                raise RuntimeError(f"QUBO parameters out of {self.paramWidth}-bit range (current range is [{a}, {b}])")
        
        if n > 0:
            mask = int.to_bytes(
                max(1, int(2**(np.ceil(np.log2(n)))-1)),
                length=2,
                byteorder='little',
                signed=False)
        else:
            mask = '\x01\x00'
        self.indexMask = mask
        self.__report("loading parameters")
        self.loadParameters(qubo.columns(n=self.dimension))
        return factor

