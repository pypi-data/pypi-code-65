from qiskit import QuantumCircuit
import kaleidoscope.qiskit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, range(1,2))

qc.statevector()