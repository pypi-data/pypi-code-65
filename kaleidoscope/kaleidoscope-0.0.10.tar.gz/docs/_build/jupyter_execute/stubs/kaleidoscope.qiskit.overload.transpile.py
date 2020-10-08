from qiskit import QuantumCircuit
import kaleidoscope.qiskit
from kaleidoscope.qiskit.services import Simulators

qc = QuantumCircuit(5) >> Simulators.aer_vigo_simulator
qc.h(0)
qc.cx(0, range(1,5))

new_qc = qc.transpile()
new_qc.draw('mpl')