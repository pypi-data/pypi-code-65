import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import kaleidoscope.qiskit
from kaleidoscope import bloch_disc

vec = [1/np.sqrt(2), 1/np.sqrt(2), 0]
bloch_disc(vec)

qc = QuantumCircuit(1)
qc.ry(np.pi*np.random.random(), 0)
qc.rz(np.pi*np.random.random(), 0)

state = Statevector.from_instruction(qc)
bloch_disc(state)

qc = QuantumCircuit(1)
qc.ry(np.pi*np.random.random(), 0)
qc.rz(np.pi*np.random.random(), 0)

bloch_disc(qc.statevector())

from matplotlib.cm import cool_r

qc = QuantumCircuit(1)
qc.ry(1, 0)
qc.t(0)

bloch_disc(qc.statevector(), colormap=cool_r)

vec = [1/np.sqrt(3), 1/np.sqrt(3), -1/np.sqrt(3)]
bloch_disc(vec, title='My qubit')