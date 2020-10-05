from qiskit.providers import BaseJob, JobStatus, JobError, BaseBackend
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData
from qiskit.qobj import QasmQobj, QobjExperimentHeader

from pytket.backends import ResultHandle, CircuitStatus, StatusEnum
from pytket.backends.backendresult import BackendResult
from pytket.circuit import Qubit, Bit, UnitID

from typing import List, Dict, Optional
from collections import Counter


class TketJob(BaseJob):
    """TketJob wraps a :py:class:`ResultHandle` list as a :py:class:`qiskit.providers.BaseJob`"""

    def __init__(
        self,
        backend: BaseBackend,
        handles: List[ResultHandle],
        qobj: QasmQobj,
        final_maps: List[Optional[Dict[UnitID, UnitID]]],
    ):
        super().__init__(backend, str(handles[0]))
        self._handles = handles
        self._qobj = qobj
        self._result = None
        self._final_maps = final_maps

    def submit(self):
        # Circuits have already been submitted before obtaining the job
        pass

    def result(self, **kwargs) -> Result:
        if self._result:
            return self._result
        result_list = []
        for h, ex, fm in zip(self._handles, self._qobj.experiments, self._final_maps):
            tk_result = self._backend._backend.get_result(h)
            result_list.append(
                ExperimentResult(
                    shots=self._qobj.config.shots,
                    success=True,
                    data=_convert_result(tk_result, ex.header, fm),
                    header=ex.header,
                )
            )
            self._backend._backend.pop_result(h)
        self._result = Result(
            backend_name=self._backend.name(),
            backend_version=self._backend.version(),
            qobj_id=self._qobj.qobj_id,
            job_id=self.job_id(),
            success=True,
            results=result_list,
        )
        return self._result

    def cancel(self):
        for h in self._handles:
            self._backend._backend.cancel(h)

    def status(self):
        status_list = [self._backend._backend.circuit_status(h) for h in self._handles]
        if any((s.status == StatusEnum.RUNNING for s in status_list)):
            return JobStatus.RUNNING
        elif any((s.status == StatusEnum.ERROR for s in status_list)):
            return JobStatus.ERROR
        elif any((s.status == StatusEnum.CANCELLED for s in status_list)):
            return JobStatus.CANCELLED
        elif all((s.status == StatusEnum.COMPLETED for s in status_list)):
            return JobStatus.DONE
        else:
            return JobStatus.INITIALIZING


def _convert_result(
    res: BackendResult,
    header: QobjExperimentHeader,
    final_map: Optional[Dict[UnitID, UnitID]],
) -> ExperimentResultData:
    data = dict()
    if res.contains_state_results:
        qbits = [Qubit(reg, ind) for reg, ind in header.qubit_labels[::-1]]
        if final_map:
            qbits = [final_map[q] for q in qbits]
        stored_res = res.get_result(qbits)
        if stored_res.state is not None:
            data["statevector"] = stored_res.state
        if stored_res.unitary is not None:
            data["unitary"] = stored_res.unitary
    if res.contains_measured_results:
        cbits = [Bit(reg, ind) for reg, ind in header.clbit_labels[::-1]]
        if final_map:
            cbits = [final_map[c] for c in cbits]
        stored_res = res.get_result(cbits)
        if stored_res.shots is not None:
            data["memory"] = [hex(i) for i in stored_res.shots.to_intlist()]
            data["counts"] = dict(Counter(data["memory"]))
        elif stored_res.counts is not None:
            data["counts"] = {hex(i): f for i, f in stored_res.counts.items()}
    return ExperimentResultData(**data)
