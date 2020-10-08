from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import kaleidoscope.qiskit
from kaleidoscope.interactive import qsphere

qc = QuantumCircuit(3)
qc.h(range(3))
qc.ch(0,1)
qc.s(2)
qc.cz(2,1)
state = qc.statevector()

qsphere(state)