import functools
import unittest

def qotp(_, ck_b):
    #print('.', end='', flush=True) 
    def prep_classical(c):
        if c == 1: q = _.PREP()
        elif c == 2: q = _.X(_.PREP())
        elif c == 3: q = _.H(_.PREP())
        elif c == 4: q = _.Z(_.H(_.PREP()))
        elif c == 5: q = _.K(_.PREP())
        elif c == 6: q = _.Z(_.K(_.PREP()))
        else: raise NameError("Cannot prepare this state")
        return q

    def meas_classical(q, c):
        if c == 1: m = _.MEAS(q)
        elif c == 2: m = _.MEAS(_.X(q))
        elif c == 3: m = _.MEAS(_.H(q))
        elif c == 4: m = _.MEAS(_.H(_.Z(q)))
        elif c == 5: m = _.MEAS(_.K(q))
        elif c == 6: m = _.MEAS(_.K(_.Z(q)))
        else: raise NameError("Cannot measure in this basis")
        return m

    c_b, k_b = zip(*ck_b) # create a list for classical input values, and a list with the encoding key
    q_b = [prep_classical(c) for c in c_b] # create a list of qubits according to the classical inputs
    qenc_b = _.pres.qotp(q_b, k_b) # encode
    qdec_b = _.pres.qotp(qenc_b, k_b) #decode
    meas_results = [meas_classical(q, c) for q, c in zip(qdec_b, c_b)] #measure the result given the classical input

    assert functools.reduce(lambda acc, cur: acc and (cur == 0), meas_results, True) # make sure the value is 0 on all measured qubits
