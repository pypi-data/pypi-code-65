from qiskit.assembler import disassemble
from qiskit.result import Result
from qiskit.providers import BaseBackend
from qiskit.providers.models import QasmBackendConfiguration
from qiskit.qobj import QasmQobj

from .qiskit_convert import qiskit_to_tk
from .tket_job import TketJob

from pytket import OpType
from pytket.backends import Backend
from pytket.passes import BasePass
from pytket.predicates import (
    NoClassicalControlPredicate,
    GateSetPredicate,
    CompilationUnit,
)

from typing import Optional, List

_optype_label_map = {
    OpType.noop: "id",
    OpType.X: "x",
    OpType.Y: "y",
    OpType.Z: "z",
    OpType.S: "s",
    OpType.Sdg: "sdg",
    OpType.T: "t",
    OpType.Tdg: "tdg",
    OpType.H: "h",
    OpType.Rx: "rx",
    OpType.Ry: "ry",
    OpType.Rz: "rz",
    OpType.U1: "u1",
    OpType.U2: "u2",
    OpType.U3: "u3",
    OpType.CX: "cx",
    OpType.CY: "cy",
    OpType.CZ: "cz",
    OpType.CH: "ch",
    OpType.SWAP: "swap",
    OpType.CCX: "ccx",
    OpType.CSWAP: "cswap",
    OpType.CRz: "crz",
    OpType.CU1: "cu1",
    OpType.CU3: "cu3",
    OpType.Measure: "measure",
    OpType.Barrier: "barrier",
    OpType.Reset: "reset",
}


def _extract_basis_gates(backend: Backend) -> List[str]:
    for pred in backend.required_predicates:
        if type(pred) == GateSetPredicate:
            return [
                _optype_label_map[optype]
                for optype in pred.gate_set
                if optype in _optype_label_map.keys()
            ]
    return []


class TketBackend(BaseBackend):
    """TketBackend wraps a :py:class:`Backend` as a :py:class:`qiskit.providers.BaseBackend`"""

    def __init__(self, backend: Backend, comp_pass: Optional[BasePass] = None):
        config = QasmBackendConfiguration(
            backend_name=("statevector_" if backend.supports_state else "")
            + "pytket/"
            + str(type(backend)),
            backend_version="0.0.1",
            n_qubits=len(backend.device.nodes) if backend.device else 40,
            basis_gates=_extract_basis_gates(backend),
            gates=[],
            local=False,
            simulator=False,
            conditional=not any(
                (
                    type(pred) == NoClassicalControlPredicate
                    for pred in backend.required_predicates
                )
            ),
            open_pulse=False,
            memory=backend.supports_shots,
            max_shots=10000,
            coupling_map=[[n.index[0], m.index[0]] for n, m in backend.device.coupling]
            if backend.device
            else None,
            max_experiments=10000,
        )
        super().__init__(configuration=config, provider=None)
        self._backend = backend
        self._comp_pass = comp_pass

    def run(self, qobj: QasmQobj) -> TketJob:
        module = disassemble(qobj)
        circ_list = [qiskit_to_tk(qc) for qc in module[0]]
        if self._comp_pass:
            final_maps = []
            compiled_list = []
            for c in circ_list:
                cu = CompilationUnit(c)
                self._comp_pass.apply(cu)
                compiled_list.append(cu.circuit)
                final_maps.append(cu.final_map)
            circ_list = compiled_list
        else:
            final_maps = [None for c in circ_list]
        handles = self._backend.process_circuits(circ_list, n_shots=qobj.config.shots)
        return TketJob(self, handles, qobj, final_maps)
