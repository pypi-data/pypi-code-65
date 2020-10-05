# Copyright 2019-2020 Cambridge Quantum Computing
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

import itertools
import logging
from ast import literal_eval
from typing import Dict, Iterable, List, Optional, Tuple, Union
from warnings import warn

import numpy as np
import qiskit
from qiskit import IBMQ
from qiskit.compiler import assemble
from qiskit.qobj import QobjExperimentHeader
from qiskit.providers.ibmq.exceptions import IBMQBackendApiError
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.result import Result, models
from qiskit.tools.monitor import job_monitor

from pytket import Circuit, OpType
from pytket.backends import Backend, CircuitNotRunError, CircuitStatus, ResultHandle
from pytket.backends.backendresult import BackendResult
from pytket.backends.resulthandle import _ResultIdTuple
from pytket.qiskit import process_characterisation
from pytket.circuit import BasisOrder
from pytket.device import Device
from pytket.passes import (
    BasePass,
    RebaseIBM,
    SequencePass,
    SynthesiseIBM,
    CXMappingPass,
    DecomposeBoxes,
    FullPeepholeOptimise,
    CliffordSimp,
)
from pytket.predicates import (
    NoMidMeasurePredicate,
    NoSymbolsPredicate,
    DirectednessPredicate,
    GateSetPredicate,
    NoClassicalControlPredicate,
    NoFastFeedforwardPredicate,
    Predicate,
)
from pytket.qiskit.qiskit_convert import tk_to_qiskit
from pytket.routing import NoiseAwarePlacement, Architecture
from pytket.utils.results import KwargTypes
from .ibm_utils import _STATUS_MAP, _convert_result

_DEBUG_HANDLE_PREFIX = "_MACHINE_DEBUG_"


def _gen_debug_results(n_qubits: int, shots: int, index: int) -> Result:
    raw_counts = {"0x0": shots}
    raw_memory = ["0x0"] * shots
    base_result_args = dict(
        backend_name="test_backend",
        backend_version="1.0.0",
        qobj_id="id-123",
        job_id="job-123",
        success=True,
    )
    data = models.ExperimentResultData(counts=raw_counts, memory=raw_memory)
    exp_result_header = QobjExperimentHeader(
        creg_sizes=[["c", n_qubits]], memory_slots=n_qubits
    )
    exp_result = models.ExperimentResult(
        shots=shots,
        success=True,
        meas_level=2,
        data=data,
        header=exp_result_header,
        memory=True,
    )
    results = [exp_result] * (index + 1)
    return Result(results=results, **base_result_args)


class NoIBMQAccountError(Exception):
    """Raised when there is no IBMQ account available for the backend"""

    def __init__(self):
        super().__init__(
            "No IBMQ credentials found on disk, store your account using qiskit first."
        )


class IBMQBackend(Backend):
    _supports_shots = True
    _supports_counts = True
    _persistent_handles = True

    def __init__(
        self,
        backend_name: str,
        hub: Optional[str] = None,
        group: Optional[str] = None,
        project: Optional[str] = None,
        monitor: bool = True,
    ):
        """A backend for running circuits on remote IBMQ devices.

        :param backend_name: Name of the IBMQ device, e.g. `ibmqx4`, `ibmq_16_melbourne`.
        :type backend_name: str
        :param hub: Name of the IBMQ hub to use for the provider. If None, just uses the first hub found. Defaults to None.
        :type hub: Optional[str], optional
        :param group: Name of the IBMQ group to use for the provider. Defaults to None.
        :type group: Optional[str], optional
        :param project: Name of the IBMQ project to use for the provider. Defaults to None.
        :type project: Optional[str], optional
        :param monitor: Use the IBM job monitor. Defaults to True.
        :type monitor: bool, optional
        :raises ValueError: If no IBMQ account is loaded and none exists on the disk.
        """
        super().__init__()
        if not IBMQ.active_account():
            if IBMQ.stored_account():
                IBMQ.load_account()
            else:
                raise NoIBMQAccountError()
        provider_kwargs = {}
        if hub:
            provider_kwargs["hub"] = hub
        if group:
            provider_kwargs["group"] = group
        if project:
            provider_kwargs["project"] = project

        try:
            if provider_kwargs:
                provider = IBMQ.get_provider(**provider_kwargs)
            else:
                provider = IBMQ.providers()[0]
        except qiskit.providers.ibmq.exceptions.IBMQProviderError as err:
            logging.warn(
                (
                    "Provider was not specified enough, specify hub,"
                    "group and project correctly (check your IBMQ account)."
                )
            )
            raise err
        self._backend = provider.get_backend(backend_name)
        self._config = self._backend.configuration()

        if hasattr(self._config, "max_experiments"):
            self._max_per_job = self._config.max_experiments
        else:
            self._max_per_job = 1

        self._characterisation = process_characterisation(self._backend)
        self._device = Device(
            self._characterisation.get("NodeErrors", {}),
            self._characterisation.get("EdgeErrors", {}),
            self._characterisation.get("Architecture", Architecture([])),
        )
        self._monitor = monitor

        self._MACHINE_DEBUG = False

    @property
    def characterisation(self) -> Optional[dict]:
        return self._characterisation

    @property
    def device(self) -> Optional[Device]:
        return self._device

    @property
    def required_predicates(self) -> List[Predicate]:
        return [
            NoClassicalControlPredicate(),
            NoFastFeedforwardPredicate(),
            NoMidMeasurePredicate(),
            NoSymbolsPredicate(),
            GateSetPredicate(
                {
                    OpType.CX,
                    OpType.U1,
                    OpType.U2,
                    OpType.U3,
                    OpType.noop,
                    OpType.Measure,
                    OpType.Barrier,
                }
            ),
            DirectednessPredicate(self._device.architecture),
        ]

    def default_compilation_pass(self, optimisation_level: int = 1) -> BasePass:
        assert optimisation_level in range(3)
        passlist = [DecomposeBoxes()]
        if optimisation_level == 0:
            passlist.append(RebaseIBM())
        elif optimisation_level == 1:
            passlist.append(SynthesiseIBM())
        elif optimisation_level == 2:
            passlist.append(FullPeepholeOptimise())
        passlist.append(
            CXMappingPass(
                self._device,
                NoiseAwarePlacement(self._device),
                directed_cx=True,
                delay_measures=True,
            )
        )
        if optimisation_level == 1:
            passlist.append(SynthesiseIBM())
        if optimisation_level == 2:
            passlist.extend([CliffordSimp(False), SynthesiseIBM()])
        return SequencePass(passlist)

    @property
    def _result_id_type(self) -> _ResultIdTuple:
        return (str, int)

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
        handle_list = []
        for chunk in itertools.zip_longest(*([iter(circuits)] * self._max_per_job)):
            filtchunk = list(filter(lambda x: x is not None, chunk))
            if valid_check:
                self._check_all_circuits(filtchunk)
            qcs = [tk_to_qiskit(tkc) for tkc in filtchunk]
            qobj = assemble(qcs, shots=n_shots, memory=self._config.memory)
            if self._MACHINE_DEBUG:
                handle_list += [
                    ResultHandle(_DEBUG_HANDLE_PREFIX + str((c.n_qubits, n_shots)), i)
                    for i, c in enumerate(filtchunk)
                ]
            else:
                job = self._backend.run(qobj)
                jobid = job.job_id()
                handle_list += [ResultHandle(jobid, i) for i in range(len(filtchunk))]
        for handle in handle_list:
            self._cache[handle] = dict()
        return handle_list

    def _retrieve_job(self, jobid: str) -> IBMQJob:
        return self._backend.retrieve_job(jobid)

    def cancel(self, handle: ResultHandle) -> None:
        if not self._MACHINE_DEBUG:
            jobid = handle[0]
            job = self._retrieve_job(jobid)
            cancelled = job.cancel()
            if not cancelled:
                warn(f"Unable to cancel job {jobid}")

    def circuit_status(self, handle: ResultHandle) -> CircuitStatus:
        self._check_handle_type(handle)
        ibmstatus = self._retrieve_job(handle[0]).status()
        return CircuitStatus(_STATUS_MAP[ibmstatus], ibmstatus.value)

    def get_result(self, handle: ResultHandle, **kwargs: KwargTypes) -> BackendResult:
        """
        See :py:meth:`pytket.backends.Backend.get_result`.
        Supported kwargs: `timeout`, `wait`.
        """
        try:
            return super().get_result(handle)
        except CircuitNotRunError:
            jobid, _ = handle
            if self._MACHINE_DEBUG or jobid.startswith(_DEBUG_HANDLE_PREFIX):
                n_qubits, shots = literal_eval(handle[0][len(_DEBUG_HANDLE_PREFIX) :])
                res = _gen_debug_results(n_qubits, shots, handle[1])
            else:
                try:
                    job = self._retrieve_job(jobid)
                except IBMQBackendApiError:
                    raise CircuitNotRunError(handle)

                if self._monitor and job:
                    job_monitor(job)

                res = job.result(timeout=kwargs.get("timeout"), wait=kwargs.get("wait"))
            backresults = list(_convert_result(res))
            self._cache.update(
                (ResultHandle(jobid, circ_index), {"result": backres})
                for circ_index, backres in enumerate(backresults)
            )

            return self._cache[handle]["result"]
