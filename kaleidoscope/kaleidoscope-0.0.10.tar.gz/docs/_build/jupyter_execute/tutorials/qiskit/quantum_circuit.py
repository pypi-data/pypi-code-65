import numpy as np
from qiskit import QuantumCircuit
import kaleidoscope.qiskit
from kaleidoscope import probability_distribution
from kaleidoscope.qiskit.services import Simulators

sim = Simulators.aer_vigo_simulator
qc = QuantumCircuit(5, 5) >> sim

print(qc.target_backend)

qc = QuantumCircuit(5, 5) >> sim
qc.h(0)
qc.cx(0, range(1,5))
qc.measure(range(5), range(5))

new_qc = qc.transpile()

new_qc.draw('mpl')

new_sim = Simulators.aer_valencia_simulator

new_qc = qc.transpile(backend=new_sim)

print(new_qc.target_backend)
new_qc.draw('mpl')

counts = new_qc.sample(shots=2048).result_when_done()
probability_distribution(counts)

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, range(1,3))
qc.measure(range(3), range(3))

qc.statevector()

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, range(1,3))
qc.measure(range(3), range(3))

qc.unitary()