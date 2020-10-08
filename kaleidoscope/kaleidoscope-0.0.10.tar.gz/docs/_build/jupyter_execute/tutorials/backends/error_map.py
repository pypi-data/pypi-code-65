from qiskit import IBMQ
IBMQ.load_account()
from kaleidoscope.qiskit.backends.interactive import system_error_map

pro = IBMQ.get_provider(group='open')
backend = pro.backends.ibmq_vigo
system_error_map(backend)

import datetime
# Grab ibmq_vigo properties on Jan. 1, 2020.
old_props = backend.properties(datetime=datetime.datetime(2020, 1, 1))
system_error_map(old_props)

from kaleidoscope.qiskit import system_error_map
from kaleidoscope.qiskit.services import Systems
from matplotlib.cm import cividis

backend = Systems.ibmq_santiago𖼯5Q𖼞
system_error_map(backend, colormap=cividis)