from qiskit import QuantumCircuit
import kaleidoscope.qiskit
from kaleidoscope.interactive import bloch_disc

qc = QuantumCircuit(1)
qc.h(0)
qc.tdg(0)

state = qc.statevector()

fig = bloch_disc(state)
fig.savefig('bloch_disc.png')

fig.savefig('bloch_disc.png', figsize=(800,600), scale=3, transparent=True)

fig._fig.write_html('bloch_disc.html')