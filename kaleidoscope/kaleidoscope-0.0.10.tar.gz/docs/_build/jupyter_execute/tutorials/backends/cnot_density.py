import datetime
from qiskit import IBMQ
from kaleidoscope.qiskit.backends import cnot_error_density

IBMQ.load_account()
provider = IBMQ.get_provider(group='open')

backends = []
backends.append(provider.backends.ibmq_vigo)
backends.append(provider.backends.ibmq_ourense)
backends.append(provider.backends.ibmq_valencia)
backends.append(provider.backends.ibmq_santiago)

cnot_error_density(backends)

cnot_error_density(backends, scale='linear')

backend = provider.backends.ibmq_vigo
props = [backend.properties(datetime=datetime.datetime(2020, kk, 1)) for kk in range(2, 7)]
cnot_error_density(props, offset=200,
                   colors=['#d6d6d6', '#bebebe', '#a6a6a6', '#8e8e8e', '#ff007f'])

cnot_error_density(backends, text_xval=3)

cnot_error_density(backends, offset=300)

cnot_error_density(backends, covariance_factor=0.5)

cnot_error_density(backends, xlim=[0.1,5])