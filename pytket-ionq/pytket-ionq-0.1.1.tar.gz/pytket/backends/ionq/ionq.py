# Copyright 2020 Cambridge Quantum Computing
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
# limitations under the Licence, but note it is strictly for
# non-commercial use.

from ast import literal_eval
from requests import post, get, put
from typing import Optional, List, Iterable, Counter
import json
import time
from pytket.backends import Backend, ResultHandle, CircuitStatus, StatusEnum
from pytket.backends.backend import KwargTypes
from pytket.backends.resulthandle import _ResultIdTuple
from pytket.backends.backendresult import BackendResult
from pytket.backends.backend_exceptions import CircuitNotRunError
from pytket.circuit import Circuit, OpType, Qubit
from pytket.passes import (
    BasePass,
    SequencePass,
    SynthesiseIBM,
    FullPeepholeOptimise,
    SquashCustom,
    DecomposeBoxes,
    FlattenRegisters,
    RenameQubitsPass,
)
from pytket.predicates import (
    GateSetPredicate,
    MaxNQubitsPredicate,
    NoClassicalControlPredicate,
    NoFastFeedforwardPredicate,
    NoMidMeasurePredicate,
    NoSymbolsPredicate,
    Predicate,
)
from pytket.routing import FullyConnected
from pytket.utils.outcomearray import OutcomeArray
from pytket.device import Device
from .ionq_convert import ionq_pass, ionq_gates, ionq_singleqs, tk_to_ionq

IONQ_JOBS_URL = "https://api.ionq.co/v0.1/jobs/"

IONQ_N_QUBITS = 11

_STATUS_MAP = {
    "completed": StatusEnum.COMPLETED,
    "failed": StatusEnum.ERROR,
    "ready": StatusEnum.SUBMITTED,
    "running": StatusEnum.RUNNING,
    "canceled": StatusEnum.CANCELLED,
}

_DEBUG_HANDLE_PREFIX = "_MACHINE_DEBUG_"


class IonQBackend(Backend):
    """
    Interface to an IonQ device.
    """

    _supports_counts = True
    _persistent_handles = True

    def __init__(
        self,
        api_key: str,
        device_name: Optional[str] = "qpu",
        label: Optional[str] = "job",
    ):
        """
        Construct a new IonQ backend.

        :param      api_key: IonQ API key
        :type       api_key: string
        :param      device_name:  device name, either "qpu" or "simulator". Default is "qpu".
        :type       device_name:  Optional[string]
        :param      label:        label to apply to submitted jobs. Default is "job".
        :type       label:        Optional[string]
        """
        super().__init__()
        self._url = IONQ_JOBS_URL
        self._device_name = device_name
        self._label = label
        self._header = {"Authorization": f"apiKey {api_key}"}
        self._max_n_qubits = IONQ_N_QUBITS
        self._device = Device(FullyConnected(self._max_n_qubits))
        self._qm = {Qubit(i): node for i, node in enumerate(self._device.nodes)}
        self._MACHINE_DEBUG = False

    @property
    def device(self) -> Optional[Device]:
        return self._device

    @property
    def required_predicates(self) -> List[Predicate]:
        preds = [
            NoClassicalControlPredicate(),
            NoFastFeedforwardPredicate(),
            NoMidMeasurePredicate(),
            NoSymbolsPredicate(),
            GateSetPredicate(ionq_gates),
            MaxNQubitsPredicate(self._max_n_qubits),
        ]
        return preds

    def default_compilation_pass(self, optimisation_level: int = 1) -> BasePass:
        assert optimisation_level in range(3)
        if optimisation_level == 0:
            return SequencePass(
                [
                    DecomposeBoxes(),
                    FlattenRegisters(),
                    RenameQubitsPass(self._qm),
                    ionq_pass,
                ]
            )
        elif optimisation_level == 1:
            return SequencePass(
                [
                    DecomposeBoxes(),
                    SynthesiseIBM(),
                    FlattenRegisters(),
                    RenameQubitsPass(self._qm),
                    ionq_pass,
                ]
            )
        else:
            return SequencePass(
                [
                    DecomposeBoxes(),
                    FullPeepholeOptimise(),
                    FlattenRegisters(),
                    RenameQubitsPass(self._qm),
                    ionq_pass,
                    SquashCustom(
                        ionq_singleqs,
                        lambda a, b, c: Circuit(1).Rz(c, 0).Rx(b, 0).Rz(a, 0),
                    ),
                ]
            )

    @property
    def _result_id_type(self) -> _ResultIdTuple:
        # job id, qubit no., measure permutation
        return (str, int, str)

    def process_circuits(
        self,
        circuits: Iterable[Circuit],
        n_shots: Optional[int] = None,
        valid_check: bool = True,
        **kwargs: KwargTypes,
    ) -> List[ResultHandle]:
        """
        See :py:meth:`pytket.backends.Backend.process_circuits`.
        Supported kwargs: none.
        """
        if not n_shots:
            raise ValueError("Parameter n_shots is required")

        if valid_check:
            self._check_all_circuits(circuits)
        basebody = {
            "lang": "json",
            "body": None,
            "target": self._device_name,
            "shots": n_shots,
        }
        handles = []
        for i, circ in enumerate(circuits):
            bodycopy = basebody.copy()
            (bodycopy["body"], measures) = tk_to_ionq(circ)
            bodycopy["name"] = circ.name if circ.name else f"{self._label}_{i}"
            if self._MACHINE_DEBUG:
                handles.append(
                    ResultHandle(
                        _DEBUG_HANDLE_PREFIX + str(circ.n_qubits),
                        n_shots,
                        measures,
                    )
                )
            else:
                header = self._header.copy()
                header["Content-Type"] = "application/json"
                try:
                    # post job
                    resp = post(self._url, json.dumps(bodycopy), headers=header).json()
                    if "error" in resp:
                        raise RuntimeError(resp["error"])
                    if resp["status"] == "failed":
                        raise RuntimeError("Unknown error while submitting job.")
                except ConnectionError:
                    raise ConnectionError(
                        f"{self._label} Connection Error: Error during submit..."
                    )

                # extract job ID from response
                job_id = resp["id"]
                handle = ResultHandle(job_id, n_shots, measures)
                handles.append(handle)

        for handle in handles:
            self._cache[handle] = dict()
        return handles

    def cancel(self, handle: ResultHandle) -> None:
        if not self._MACHINE_DEBUG:
            jobid = handle[0]
            resp = put(
                self._url + jobid + "/status/cancel", headers=self._header
            ).json()
            if "error" in resp:
                raise RuntimeError(resp["error"])
            if resp["status"] == "failed":
                raise RuntimeError("Unknown error while cancelling job.")

    def circuit_status(self, handle: ResultHandle) -> CircuitStatus:
        self._check_handle_type(handle)
        jobid = handle[0]
        n_shots = handle[1]
        if self._MACHINE_DEBUG:
            n_qubits = literal_eval(jobid[len(_DEBUG_HANDLE_PREFIX) :])
            zero_counts = Counter()
            zero_array = OutcomeArray.from_ints(
                ints=[0],
                width=n_qubits,
                big_endian=False,
            )
            zero_counts[zero_array] = n_shots
            if handle in self._cache:
                self._cache[handle].update(
                    {"result": BackendResult(counts=zero_counts)}
                )
            else:
                self._cache[handle] = {"result": BackendResult(counts=zero_counts)}
            statenum = StatusEnum.COMPLETED
        else:
            measure_permutations = json.loads(handle[2])
            url = self._url + str(jobid)
            resp = get(url, headers=self._header).json()
            status = resp["status"]
            statenum = _STATUS_MAP.get(status)
            if statenum is StatusEnum.COMPLETED:
                ionq_counts = resp["data"]["histogram"]
                tket_counts = Counter()
                # reverse engineer counts. Imprecise, due to rounding.
                max_counts = 0
                max_array = None
                for outcome_key, prob in ionq_counts.items():
                    array = OutcomeArray.from_ints(
                        ints=[int(outcome_key)],
                        width=int(resp["qubits"]),
                        big_endian=False,
                    )
                    array = array.choose_indices(measure_permutations)
                    array_counts = round(n_shots * float(prob))
                    tket_counts[array] = array_counts
                    if array_counts > max_counts:
                        max_counts = array_counts
                        max_array = array
                # account for rounding error
                sum_counts = sum(tket_counts.values())
                diff = n_shots - sum_counts
                tket_counts[max_array] += diff
                if handle in self._cache:
                    self._cache[handle].update(
                        {"result": BackendResult(counts=tket_counts)}
                    )
                else:
                    self._cache[handle] = {"result": BackendResult(counts=tket_counts)}
        return CircuitStatus(statenum)

    def get_result(self, handle: ResultHandle, **kwargs: KwargTypes) -> BackendResult:
        """
        See :py:meth:`pytket.backends.Backend.get_result`.
        Supported kwargs: `timeout`, `wait`.
        """
        try:
            return super().get_result(handle)
        except CircuitNotRunError:
            timeout = kwargs.get("timeout")
            wait = kwargs.get("wait", 1.0)
            # Wait for job to finish; result will then be in the cache.
            end_time = (time.time() + timeout) if (timeout is not None) else None
            while (end_time is None) or (time.time() < end_time):
                circuit_status = self.circuit_status(handle)
                if circuit_status.status is StatusEnum.COMPLETED:
                    return self._cache[handle]["result"]
                if circuit_status.status is StatusEnum.ERROR:
                    raise RuntimeError(circuit_status.message)
                time.sleep(wait)
            raise RuntimeError(f"Timed out: no results after {timeout} seconds.")
