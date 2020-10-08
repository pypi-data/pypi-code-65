import numpy as np
from qiskit import QuantumCircuit
import kaleidoscope.qiskit
from kaleidoscope.qiskit.services import Simulators
from kaleidoscope import probability_distribution

counts = {'000': 0.5, '111': 0.5}

probability_distribution(counts)

qc = QuantumCircuit(3, 3) >> Simulators.aer_vigo_simulator
qc.h(0)
qc.cx(0, [1,2])
qc.measure(range(3), range(3))

counts = qc.transpile().sample().result_when_done()

probability_distribution(counts)

qc = QuantumCircuit(3, 3) >> Simulators.aer_vigo_simulator
qc.h(range(3))
qc.measure(range(3), range(3))

counts = qc.transpile().sample().result_when_done()

probability_distribution(counts, colors='#2c3d63')

probability_distribution(counts, colors=[['#2c3d63', '#ff6f5e']*4])

probability_distribution(counts, background_color='#000000')

qc = QuantumCircuit(3, 3) >> Simulators.aer_vigo_simulator
qc.h(range(3))
qc.measure(range(3), range(3))

counts = qc.transpile().sample().result_when_done()
counts2 = qc.transpile(backend=Simulators.aer_valencia_simulator).sample().result_when_done()

probability_distribution([counts, counts2], legend=['Vigo sim', 'Rome sim'])

probability_distribution([counts, counts2], legend=['Vigo sim', 'Rome sim'],
                         colors=['#2c3d63', '#f2d58f'])

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0,1)
qc.cx(0,2)
qc.measure_all()

counts = qc.sample().result_when_done()
counts2 = qc.sample().result_when_done()

probability_distribution([counts, counts2],
                         title='Counts distributions',
                         legend=['counts1', 'counts2'],
                         state_labels=["\U0001D70B/4", 'chips'])