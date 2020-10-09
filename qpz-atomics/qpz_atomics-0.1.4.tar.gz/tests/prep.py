import functools
import unittest

def pauli(_, bit, base):
    #print('.', end='', flush=True) 
    q = _.prep.pauli(bit, base)

    if base == 1: m = _.MEAS(_.H(q))
    elif base == 2: m = _.MEAS(q)
    elif base == 3: m = _.MEAS(_.K(q))

    assert (m == bit)

def ghz(_, nb_target_nodes, basis):
    #print('.', end= '', flush=True)
    def meas(q, basis):
        if basis == 1: #X measurement
            return _.MEAS(_.H(q))
        elif basis == 2: #Z measurement
            return _.MEAS(q)

    ghz_state = _.prep.ghz(nb_target_nodes)
    meas_results = [meas(q, basis) for q in ghz_state]
    nb_parties = 1 + nb_target_nodes

    assert functools.reduce(lambda acc, cur: acc + cur, meas_results, 0) % (2 if basis == 1 else nb_parties) == 0
