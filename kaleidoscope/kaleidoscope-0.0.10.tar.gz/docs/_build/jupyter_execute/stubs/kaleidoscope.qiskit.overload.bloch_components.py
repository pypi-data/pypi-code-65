from qiskit import QuantumCircuit
import kaleidoscope.qiskit

qc = QuantumCircuit(3)
qc.h(range(3))
qc.ch(0,1)
qc.s(2)
qc.cz(2,1)

qc.statevector().bloch_components()