import functools
import unittest

def pauli(_, bit, base):
    #print('.', end='', flush=True) 
    q = _.prep.pauli(bit, base)
    m = _.meas.pauli(q, base)

    assert (m == bit)
