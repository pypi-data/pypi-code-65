from qiskit import *
import kaleidoscope.qiskit
from kaleidoscope.qiskit.services import Simulators
from kaleidoscope.interactive import probability_distribution

sim = Simulators.aer_vigo_simulator

qc = QuantumCircuit(3, 3) >> sim
qc.h(1)
qc.cx(1,0)
qc.cx(1,2)
qc.measure(range(3), range(3))

counts = qc.transpile().sample().result_when_done()
probability_distribution(counts)