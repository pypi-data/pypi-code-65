import random
from hypothesis import given, example, settings
from hypothesis.strategies import text
import hypothesis.strategies as st

from qpz_atomics import qpz_atomics 
import prep, meas, pres

## tests using simulaqron backend on a single node
from cqc.pythonLib import CQCConnection
from qpz_atomics.mappings.simulaqron import mapping

## Tests for presentation layer
@settings(deadline=None)
@given(st.lists(st.tuples(st.integers(min_value=1, max_value=6), st.integers(min_value=0, max_value=3)), min_size=1, max_size=10))
def test_pres_qotp(ck_b):
    with CQCConnection("Alice") as Alice:
        _ = qpz_atomics.lib(mapping, Alice)
        pres.qotp(_, ck_b)

## Tests for preparations
@given(st.integers(min_value=0, max_value=1), st.integers(min_value=1, max_value=3))
@settings(deadline=None)
def test_prep_pauli(bit, base):
    with CQCConnection("Alice") as Alice:
        _ = qpz_atomics.lib(mapping, Alice)
        prep.pauli(_, bit, base)

@given(st.integers(min_value=1, max_value=3), st.integers(min_value=1, max_value=2))
@settings(deadline=None)
def test_prep_ghz(nb_target_nodes, basis):
    with CQCConnection("Alice") as Alice:
        _ = qpz_atomics.lib(mapping, Alice)
        prep.ghz(_, nb_target_nodes, basis)
        
## Tests for measurements
@given(st.integers(min_value=0, max_value=1), st.integers(min_value=1, max_value=3))
@settings(deadline=None)
def test_meas_pauli(bit, base):
    with CQCConnection("Alice") as Alice:
        _ = qpz_atomics.lib(mapping, Alice)
        meas.pauli(_, bit, base)
        
