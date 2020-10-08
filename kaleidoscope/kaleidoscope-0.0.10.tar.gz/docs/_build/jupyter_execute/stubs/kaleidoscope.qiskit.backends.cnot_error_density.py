from qiskit import *
from kaleidoscope.qiskit.backends import cnot_error_density
provider = IBMQ.load_account()

backends = []
backends.append(provider.backends.ibmq_vigo)
backends.append(provider.backends.ibmq_ourense)
backends.append(provider.backends.ibmq_valencia)
backends.append(provider.backends.ibmq_santiago)

cnot_error_density(backends)