# Copyright 2019 Cambridge Quantum Computing
#
# Licensed under a Non-Commercial Use Software Licence (the "Licence");
# you may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/pytket/build/html/licence.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for the specific language governing permissions and
# limitations under the Licence, but note it is strictly for non-commercial use.

"""Shared utility methods for ibm backends.
"""
from typing import List, Tuple, Iterator, Iterable, Sequence, Union, Type
from collections import Counter
import numpy as np

from qiskit.result import Result
from qiskit.providers import JobStatus, BaseJob
from pytket.circuit import BasisOrder, Bit, Qubit, UnitID
from pytket.backends.status import StatusEnum
from pytket.backends.backendresult import BackendResult
from pytket.utils.outcomearray import OutcomeArray
from pytket.utils.results import permute_rows_cols_in_unitary

_STATUS_MAP = {
    JobStatus.CANCELLED: StatusEnum.CANCELLED,
    JobStatus.ERROR: StatusEnum.ERROR,
    JobStatus.DONE: StatusEnum.COMPLETED,
    JobStatus.INITIALIZING: StatusEnum.SUBMITTED,
    JobStatus.VALIDATING: StatusEnum.SUBMITTED,
    JobStatus.QUEUED: StatusEnum.QUEUED,
    JobStatus.RUNNING: StatusEnum.RUNNING,
}


def _gen_uids(labels: Iterable[List], derived: Type[UnitID]) -> List[UnitID]:
    sorted_labels = sorted(labels, key=lambda x: x[0])
    return [
        derived(name, index) for name, size in sorted_labels for index in range(size)
    ]


def _hex_to_outar(hexes: Sequence[str], width: int) -> np.ndarray:
    ints = [int(hexst, 16) for hexst in hexes]
    return OutcomeArray.from_ints(ints, width)


def _convert_result(res) -> Iterator[BackendResult]:
    for result in res.results:
        header = result.header
        width = header.memory_slots
        c_bits = (
            _gen_uids(header.creg_sizes, Bit)[::-1]
            if hasattr(header, "creg_sizes")
            else None
        )
        q_bits = (
            _gen_uids(header.qreg_sizes, Qubit)[::-1]
            if hasattr(header, "qreg_sizes")
            else None
        )
        shots, counts, state, unitary = (None,) * 4
        datadict = result.data.to_dict()
        if "memory" in datadict:
            memory = datadict["memory"]
            shots = _hex_to_outar(memory, width)
        elif "counts" in datadict:
            qis_counts = datadict["counts"]
            counts = Counter(
                dict(
                    (_hex_to_outar([hexst], width), count)
                    for hexst, count in qis_counts.items()
                )
            )

        if "statevector" in datadict:
            state = datadict["statevector"]

        if "unitary" in datadict:
            unitary = datadict["unitary"]

        yield BackendResult(
            c_bits=c_bits,
            q_bits=q_bits,
            shots=shots,
            counts=counts,
            state=state,
            unitary=unitary,
        )
