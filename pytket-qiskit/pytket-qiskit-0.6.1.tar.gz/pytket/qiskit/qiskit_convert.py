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


"""Methods to allow conversion between Qiskit and pytket circuit classes
"""
from math import pi
from typing import Dict, List, Optional, Tuple, Union
import warnings
import sympy
import qiskit.circuit.library.standard_gates as qiskit_gates
from qiskit import (
    ClassicalRegister,
    QuantumCircuit,  # type: ignore
    QuantumRegister,
)
from qiskit.circuit import (
    Barrier,
    Instruction,
    Measure,
    Parameter,
    ParameterExpression,
    Reset,
)
from qiskit.extensions.unitary import UnitaryGate
from qiskit.providers import BaseBackend
from pytket.circuit import CircBox, Circuit, Node, OpType, Unitary2qBox, UnitType
from pytket.device import Device, QubitErrorContainer
from pytket.routing import Architecture, FullyConnected

_known_qiskit_gate = {
    # Exact equivalents (same signature except for factor of pi in each parameter):
    qiskit_gates.C3XGate: OpType.CnX,
    qiskit_gates.C4XGate: OpType.CnX,
    qiskit_gates.CCXGate: OpType.CCX,
    qiskit_gates.CHGate: OpType.CH,
    qiskit_gates.CPhaseGate: OpType.CU1,
    qiskit_gates.CRYGate: OpType.CnRy,
    qiskit_gates.CRZGate: OpType.CRz,
    qiskit_gates.CSwapGate: OpType.CSWAP,
    qiskit_gates.CU1Gate: OpType.CU1,
    qiskit_gates.CU3Gate: OpType.CU3,
    qiskit_gates.CXGate: OpType.CX,
    qiskit_gates.CYGate: OpType.CY,
    qiskit_gates.CZGate: OpType.CZ,
    qiskit_gates.HGate: OpType.H,
    qiskit_gates.IGate: OpType.noop,
    qiskit_gates.iSwapGate: OpType.ISWAPMax,
    qiskit_gates.PhaseGate: OpType.U1,
    qiskit_gates.RGate: OpType.PhasedX,
    qiskit_gates.RXGate: OpType.Rx,
    qiskit_gates.RXXGate: OpType.XXPhase,
    qiskit_gates.RYGate: OpType.Ry,
    qiskit_gates.RYYGate: OpType.YYPhase,
    qiskit_gates.RZGate: OpType.Rz,
    qiskit_gates.RZZGate: OpType.ZZPhase,
    qiskit_gates.SdgGate: OpType.Sdg,
    qiskit_gates.SGate: OpType.S,
    qiskit_gates.SwapGate: OpType.SWAP,
    qiskit_gates.SXdgGate: OpType.Vdg,
    qiskit_gates.SXGate: OpType.V,
    qiskit_gates.TdgGate: OpType.Tdg,
    qiskit_gates.TGate: OpType.T,
    qiskit_gates.U1Gate: OpType.U1,
    qiskit_gates.U2Gate: OpType.U2,
    qiskit_gates.U3Gate: OpType.U3,
    qiskit_gates.UGate: OpType.U3,
    qiskit_gates.XGate: OpType.X,
    qiskit_gates.YGate: OpType.Y,
    qiskit_gates.ZGate: OpType.Z,
    # Multi-controlled gates (qiskit expects a list of controls followed by the target):
    qiskit_gates.MCXGate: OpType.CnX,
    qiskit_gates.MCXGrayCode: OpType.CnX,
    qiskit_gates.MCXRecursive: OpType.CnX,
    qiskit_gates.MCXVChain: OpType.CnX,
    # Special types:
    Barrier: OpType.Barrier,
    Instruction: OpType.CircBox,
    Measure: OpType.Measure,
    Reset: OpType.Reset,
    UnitaryGate: OpType.Unitary2qBox,
}
# Not included in the above list:
# qiskit_gates.CUGate != OpType.CU3 : CUGate has an extra phase parameter

# Some qiskit gates are aliases (e.g. UGate and U3Gate).
# In such cases this reversal will select one or the other.
_known_qiskit_gate_rev = {v: k for k, v in _known_qiskit_gate.items()}

# Ensure U3 maps to U3Gate. (UGate not yet fully supported in Qiskit.)
_known_qiskit_gate_rev[OpType.U3] = qiskit_gates.U3Gate


class CircuitBuilder:
    def __init__(
        self,
        qregs: List[QuantumRegister],
        cregs: List[ClassicalRegister] = [],
        name: Optional[str] = None,
        phase: Optional[float] = 0.0,
    ):
        self.qregs = qregs
        self.cregs = cregs
        self.tkc = Circuit(name=name)
        self.tkc.add_phase(phase)
        self.qregmap = {}
        for reg in qregs:
            tk_reg = self.tkc.add_q_register(reg.name, len(reg))
            self.qregmap.update({reg: tk_reg})
        self.cregmap = {}
        for reg in cregs:
            tk_reg = self.tkc.add_c_register(reg.name, len(reg))
            self.cregmap.update({reg: tk_reg})

    def circuit(self):
        return self.tkc

    def add_qiskit_data(self, data):
        for i, qargs, cargs in data:
            condition_kwargs = {}
            if i.condition is not None:
                cond_reg = self.cregmap[i.condition[0]]
                condition_kwargs = {
                    "condition_bits": [cond_reg[k] for k in range(len(cond_reg))],
                    "condition_value": i.condition[1],
                }
            optype = _known_qiskit_gate[type(i)]
            qubits = [self.qregmap[qbit.register][qbit.index] for qbit in qargs]
            bits = [self.cregmap[bit.register][bit.index] for bit in cargs]
            if optype == OpType.Unitary2qBox:
                u = i.to_matrix()
                ubox = Unitary2qBox(u)
                self.tkc.add_unitary2qbox(
                    ubox, qubits[0], qubits[1], **condition_kwargs
                )
            elif optype == OpType.Barrier:
                self.tkc.add_barrier(qubits)
            elif optype == OpType.CircBox:
                qregs = [QuantumRegister(i.num_qubits, "q")] if i.num_qubits > 0 else []
                cregs = (
                    [ClassicalRegister(i.num_clbits, "c")] if i.num_clbits > 0 else []
                )
                builder = CircuitBuilder(qregs, cregs)
                builder.add_qiskit_data(i.definition)
                cbox = CircBox(builder.circuit())
                self.tkc.add_circbox(cbox, qubits + bits, **condition_kwargs)
            else:
                params = [param_to_tk(p) for p in i.params]
                self.tkc.add_gate(optype, params, qubits + bits, **condition_kwargs)


def qiskit_to_tk(qcirc: QuantumCircuit) -> Circuit:
    """Convert a :py:class:`qiskit.QuantumCircuit` to a :py:class:`Circuit`.

    :param qcirc: A circuit to be converted
    :type qcirc: QuantumCircuit
    :return: The converted circuit
    :rtype: Circuit
    """
    builder = CircuitBuilder(
        qregs=qcirc.qregs,
        cregs=qcirc.cregs,
        name=qcirc.name,
        phase=qcirc.global_phase / pi,
    )
    builder.add_qiskit_data(qcirc.data)
    return builder.circuit()


def param_to_tk(p: Union[float, ParameterExpression]) -> sympy.Expr:
    if isinstance(p, ParameterExpression):
        return p._symbol_expr / sympy.pi
    else:
        return p / sympy.pi


def param_to_qiskit(
    p: sympy.Expr, symb_map: Dict[Parameter, sympy.Symbol]
) -> Union[float, ParameterExpression]:
    ppi = p * sympy.pi
    if len(ppi.free_symbols) == 0:
        return float(ppi.evalf())
    else:
        return ParameterExpression(symb_map, ppi)


def append_tk_command_to_qiskit(
    op, args, qcirc, qregmap, cregmap, symb_map
) -> Instruction:
    optype = op.type
    if optype == OpType.Measure:
        qubit = args[0]
        bit = args[1]
        qb = qregmap[qubit.reg_name][qubit.index[0]]
        b = cregmap[bit.reg_name][bit.index[0]]
        return qcirc.measure(qb, b)

    if optype == OpType.Reset:
        qb = qregmap[args[0].reg_name][args[0].index[0]]
        return qcirc.reset(qb)

    if optype in [OpType.CircBox, OpType.ExpBox, OpType.PauliExpBox]:
        subcircuit = op.get_circuit()
        subqc = tk_to_qiskit(subcircuit)
        n_qb = subcircuit.n_qubits
        qargs = []
        cargs = []
        for a in args:
            if a.type == UnitType.qubit:
                qargs.append(qregmap[a.reg_name][a.index[0]])
            else:
                cargs.append(cregmap[a.reg_name][a.index[0]])
        return qcirc.append(subqc.to_instruction(), qargs, cargs)
    if optype == OpType.Unitary2qBox:
        qargs = [qregmap[q.reg_name][q.index[0]] for q in args]
        u = op.get_matrix()
        g = UnitaryGate(u)
        return qcirc.append(g, qargs=qargs)
    if optype == OpType.Barrier:
        qargs = [qregmap[q.reg_name][q.index[0]] for q in args]
        g = Barrier(len(args))
        return qcirc.append(g, qargs=qargs)
    if optype == OpType.ConditionalGate:
        width = op.width
        regname = args[0].reg_name
        if len(cregmap[regname]) != width:
            raise NotImplementedError("OpenQASM conditions must be an entire register")
        for i, a in enumerate(args[:width]):
            if a.reg_name != regname:
                raise NotImplementedError(
                    "OpenQASM conditions can only use a single register"
                )
            if a.index != [i]:
                raise NotImplementedError(
                    "OpenQASM conditions must be an entire register in order"
                )
        instruction = append_tk_command_to_qiskit(
            op.op, args[width:], qcirc, qregmap, cregmap, symb_map
        )

        instruction.c_if(cregmap[regname], op.value)
        return instruction
    # normal gates
    qargs = [qregmap[q.reg_name][q.index[0]] for q in args]
    if optype == OpType.CnX:
        return qcirc.mcx(qargs[:-1], qargs[-1])
    # others are direct translations
    try:
        gatetype = _known_qiskit_gate_rev[optype]
    except KeyError as error:
        raise NotImplementedError(
            "Cannot convert tket Op to Qiskit gate: " + op.get_name()
        ) from error
    params = [param_to_qiskit(p, symb_map) for p in op.params]
    g = gatetype(*params)
    return qcirc.append(g, qargs=qargs)


def tk_to_qiskit(
    tkcirc: Circuit,
) -> Union[QuantumCircuit, Tuple[QuantumCircuit, sympy.Expr]]:
    """Convert back

    :param tkcirc: A circuit to be converted
    :type tkcirc: Circuit
    :return: The converted circuit
    :rtype: QuantumCircuit
    """
    tkc = tkcirc
    qcirc = QuantumCircuit(name=tkc.name)
    qreg_sizes: Dict[str, int] = {}
    for qb in tkc.qubits:
        if len(qb.index) != 1:
            raise NotImplementedError("Qiskit registers must use a single index")
        if (qb.reg_name not in qreg_sizes) or (qb.index[0] >= qreg_sizes[qb.reg_name]):
            qreg_sizes.update({qb.reg_name: qb.index[0] + 1})
    creg_sizes: Dict[str, int] = {}
    for b in tkc.bits:
        if len(b.index) != 1:
            raise NotImplementedError("Qiskit registers must use a single index")
        if (b.reg_name not in creg_sizes) or (b.index[0] >= creg_sizes[b.reg_name]):
            creg_sizes.update({b.reg_name: b.index[0] + 1})
    qregmap = {}
    for reg_name, size in qreg_sizes.items():
        qis_reg = QuantumRegister(size, reg_name)
        qregmap.update({reg_name: qis_reg})
        qcirc.add_register(qis_reg)
    cregmap = {}
    for reg_name, size in creg_sizes.items():
        qis_reg = ClassicalRegister(size, reg_name)
        cregmap.update({reg_name: qis_reg})
        qcirc.add_register(qis_reg)
    symb_map = {Parameter(str(s)): s for s in tkc.free_symbols()}
    for command in tkc:
        append_tk_command_to_qiskit(
            command.op, command.args, qcirc, qregmap, cregmap, symb_map
        )
    try:
        a = float(tkc.phase)
        qcirc.global_phase += a * pi
    except TypeError:
        warnings.warn("Qiskit circuits cannot have symbolic global phase: ignoring.")
    return qcirc


def process_characterisation(backend: BaseBackend) -> dict:
    """Convert a :py:class:`qiskit.BaseBackend` to a dictionary containing device Characteristics

    :param backend: A backend to be converted
    :type backend: BaseBackend
    :return: A dictionary containing device characteristics
    :rtype: dict
    """
    properties = backend.properties()
    gate_str_2_optype = {
        "u1": OpType.U1,
        "u2": OpType.U2,
        "u3": OpType.U3,
        "cx": OpType.CX,
        "id": OpType.noop,
    }

    def return_value_if_found(iterator, name):
        try:
            first_found = next(filter(lambda item: item.name == name, iterator))
        except StopIteration:
            return None
        if hasattr(first_found, "value"):
            return first_found.value
        return None

    config = backend.configuration()
    coupling_map = config.coupling_map
    n_qubits = config.n_qubits
    if coupling_map is None:
        # Assume full connectivity
        arc = FullyConnected(n_qubits)
        link_ers_dict = {}
    else:
        arc = Architecture(coupling_map)
        link_ers_dict = {
            tuple(pair): QubitErrorContainer({OpType.CX}) for pair in coupling_map
        }

    node_ers_dict = {}
    supported_single_optypes = {OpType.U1, OpType.U2, OpType.U3, OpType.noop}

    t1_times_dict = {}
    t2_times_dict = {}
    frequencies_dict = {}
    gate_times_dict = {}

    if properties is not None:
        for index, qubit_info in enumerate(properties.qubits):
            error_cont = QubitErrorContainer(supported_single_optypes)
            error_cont.add_readout(return_value_if_found(qubit_info, "readout_error"))

            t1_times_dict[index] = return_value_if_found(qubit_info, "T1")
            t2_times_dict[index] = return_value_if_found(qubit_info, "T2")
            frequencies_dict[index] = return_value_if_found(qubit_info, "frequency")

            node_ers_dict[index] = error_cont

        for gate in properties.gates:
            name = gate.gate
            if name in gate_str_2_optype:
                optype = gate_str_2_optype[name]
                qubits = gate.qubits
                gate_error = return_value_if_found(gate.parameters, "gate_error")
                gate_error = gate_error if gate_error else 0.0
                gate_length = return_value_if_found(gate.parameters, "gate_length")
                gate_length = gate_length if gate_length else 0.0
                gate_times_dict[(optype, tuple(qubits))] = gate_length
                # add gate fidelities to their relevant lists
                if len(qubits) == 1:
                    node_ers_dict[qubits[0]].add_error((optype, gate_error))
                elif len(qubits) == 2:
                    link_ers_dict[tuple(qubits)].add_error((optype, gate_error))
                    opposite_link = tuple(qubits[::-1])
                    if opposite_link not in coupling_map:
                        # to simulate a worse reverse direction square the fidelity
                        link_ers_dict[opposite_link] = QubitErrorContainer({OpType.CX})
                        link_ers_dict[opposite_link].add_error((optype, 2 * gate_error))

    # convert qubits to architecture Nodes
    node_ers_dict = {Node(q_index): ers for q_index, ers in node_ers_dict.items()}
    link_ers_dict = {
        (Node(q_indices[0]), Node(q_indices[1])): ers
        for q_indices, ers in link_ers_dict.items()
    }

    characterisation = dict()
    characterisation["NodeErrors"] = node_ers_dict
    characterisation["EdgeErrors"] = link_ers_dict
    characterisation["Architecture"] = arc
    characterisation["t1times"] = t1_times_dict
    characterisation["t2times"] = t2_times_dict
    characterisation["Frequencies"] = frequencies_dict
    characterisation["GateTimes"] = gate_times_dict

    return characterisation
