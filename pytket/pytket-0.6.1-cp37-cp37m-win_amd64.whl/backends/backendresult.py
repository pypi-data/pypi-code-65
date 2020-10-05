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

"""`BackendResult` class and associated methods."""
from typing import (
    Optional,
    Any,
    Sequence,
    Iterable,
    List,
    Tuple,
    Dict,
    Counter,
    NamedTuple,
    Collection,
    TypeVar,
)
import operator
from functools import reduce
import numpy as np
import warnings

from pytket.circuit import BasisOrder, Bit, Qubit, UnitID
from pytket.utils.results import (
    probs_from_state,
    get_n_qb_from_statevector,
    permute_statearray_qb_labels,
)
from pytket.utils.outcomearray import OutcomeArray, readout_counts

from .backend_exceptions import InvalidResultType


class StoredResult(NamedTuple):
    """NamedTuple with optional fields for all result types."""

    counts: Optional[Counter[OutcomeArray]] = None
    shots: Optional[OutcomeArray] = None
    state: Optional[np.ndarray] = None
    unitary: Optional[np.ndarray] = None


class BackendResult:
    """Encapsulate generic results from pytket Backend instances.

    Results can either be measured (shots or counts), or ideal simulations in
    the form of statevector or unitary arrays. For measured results, a map of
    Bit identifiers to its stored outcome index is also stored (e.g.
    {Bit(1):2} tells us Qubit(1) corresponds to the 1 reading in the bitstring
    0010). Likewise, for state results a map of Qubit identifiers to qubit
    location in basis vector labelling is stored (e.g. statevector index 3
    corresponds to bitwise encoding 011, and a mapping {Qubit(2): 0} tells us
    the 0 in the bitwise encoding corresponds to Qubit(2)).
    """

    def __init__(
        self,
        *,
        q_bits: Iterable[Qubit] = None,
        c_bits: Iterable[Bit] = None,
        counts: Counter[OutcomeArray] = None,
        shots: OutcomeArray = None,
        state: Any = None,
        unitary: Any = None,
    ):
        self._counts = counts
        self._shots = shots

        self._state = state
        self._unitary = unitary

        self.c_bits: Dict[Bit, int] = {}
        self.q_bits: Dict[Qubit, int] = {}

        def _process_unitids(var, attr, lent, uid):
            if var is not None:
                setattr(self, attr, dict(reversed(pair) for pair in enumerate(var)))
                if lent != len(var):
                    raise ValueError(
                        (
                            f"Length of {attr} ({len(var)}) does not"
                            f" match input data dimensions ({lent})."
                        )
                    )
            else:
                setattr(self, attr, dict((uid(i), i) for i in range(lent)))

        if self.contains_measured_results:
            _bitlength = 0
            if self._counts is not None:
                if shots is not None:
                    raise ValueError(
                        "Provide either counts or shots, both is not valid."
                    )
                _bitlength = next(self._counts.elements()).width

            if self._shots is not None:
                _bitlength = self._shots.width

            _process_unitids(c_bits, "c_bits", _bitlength, Bit)

        if self.contains_state_results:
            _n_qubits = 0
            if self._unitary is not None:
                _n_qubits = int(np.log2(self._unitary.shape[-1]))
            elif self._state is not None:
                _n_qubits = get_n_qb_from_statevector(self._state)

            _process_unitids(q_bits, "q_bits", _n_qubits, Qubit)

    @property
    def contains_measured_results(self) -> bool:
        """Whether measured type results (shots or counts) are stored"""
        return (self._counts is not None) or (self._shots is not None)

    @property
    def contains_state_results(self) -> bool:
        """Whether state type results (state vector or unitary) are stored"""
        return (self._state is not None) or (self._unitary is not None)

    def __eq__(self, other) -> bool:
        return (
            self.q_bits == other.q_bits
            and self.c_bits == other.c_bits
            and self._shots == other._shots
            and self._counts == other._counts
            and np.array_equal(self._state, other._state)
            and np.array_equal(self._unitary, other._unitary)
        )

    def get_bitlist(self) -> List[Bit]:
        """Return list of Bits in internal storage order.

        :raises AttributeError: No Bits in BackendResult.
        :return: Sorted list of Bits.
        :rtype: List[Bit]
        """
        if self.c_bits:
            return _sort_keys_by_val(self.c_bits)
        raise AttributeError

    def get_qbitlist(self) -> List[Qubit]:
        """Return list of Qubits in internal storage order.

        :raises AttributeError: No Qubits in BackendResult.
        :return: Sorted list of Qubits.
        :rtype: List[Qubit]
        """

        if self.q_bits:
            return _sort_keys_by_val(self.q_bits)
        raise AttributeError

    def _get_measured_res(self, bits: Sequence[Bit]) -> StoredResult:
        vals: Dict[str, Any] = {}

        if not self.contains_measured_results:
            raise InvalidResultType("shots/counts")
        if self.c_bits is None:
            raise RuntimeError("Classical bits not set.")
        try:
            chosen_readouts = [self.c_bits[bit] for bit in bits]
        except KeyError:
            raise ValueError("Requested Bit not in result.")

        if self._counts is not None:
            vals["counts"] = reduce(
                operator.add,
                (
                    Counter({outcome.choose_indices(chosen_readouts): count})
                    for outcome, count in self._counts.items()
                ),
            )
        if self._shots is not None:
            vals["shots"] = self._shots.choose_indices(chosen_readouts)

        return StoredResult(**vals)

    def _get_state_res(self, qubits: Sequence[Qubit]) -> StoredResult:
        vals: Dict[str, Any] = {}
        if not self.contains_state_results:
            raise InvalidResultType("state/unitary")
        if self.q_bits is None:
            raise RuntimeError("Qubits not set.")

        if not _check_permuted_sequence(qubits, self.q_bits):
            raise ValueError(
                "For state/unitary results only a permutation of all qubits can be requested."
            )
        qb_mapping = {selfqb: qubits[index] for selfqb, index in self.q_bits.items()}
        if self._state is not None:
            vals["state"] = permute_statearray_qb_labels(
                self._state, self.get_qbitlist(), qb_mapping
            )
        if self._unitary is not None:
            vals["unitary"] = permute_statearray_qb_labels(
                self._unitary, self.get_qbitlist(), qb_mapping
            )
        return StoredResult(**vals)

    def get_result(
        self, request_ids: Optional[Sequence[UnitID]] = None
    ) -> StoredResult:
        """Retrieve all results, optionally according to a specified UnitID ordering or subset.

        :param request_ids: Ordered set of either Qubits or Bits for which to
            retrieve results, defaults to None in which case all results are returned.
            For statevector/unitary results some permutation of all qubits must be requested.
            For measured results (shots/counts), some subset of the relevant bits must be requested.
        :type request_ids: Optional[Sequence[UnitID]], optional
        :raises ValueError: Requested UnitIds (request_ids) contain a mixture of qubits and bits.
        :raises RuntimeError: Classical bits not set.
        :raises ValueError: Requested (Qu)Bit not in result.
        :raises RuntimeError: "Qubits not set."
        :raises ValueError: For state/unitary results only a permutation of all
            qubits can be requested.
        :return: All stored results corresponding to requested IDs.
        :rtype: StoredResult
        """
        if request_ids is None:
            return StoredResult(self._counts, self._shots, self._state, self._unitary)

        if all(isinstance(i, Bit) for i in request_ids):
            return self._get_measured_res(request_ids)

        if all(isinstance(i, Qubit) for i in request_ids):
            return self._get_state_res(request_ids)

        raise ValueError(
            "Requested UnitIds (request_ids) contain a mixture of qubits and bits."
        )

    def get_shots(
        self, cbits: Optional[Sequence[Bit]] = None, basis: BasisOrder = BasisOrder.ilo
    ) -> np.ndarray:
        """Return shots if available.

        :param cbits: ordered subset of Bits, returns all results by default, defaults to None
        :type cbits: Optional[Sequence[Bit]], optional
        :param basis: Toggle between ILO (increasing lexicographic order of bit ids) and
            DLO (decreasing lexicographic order) for column ordering if cbits is None.
            Defaults to BasisOrder.ilo.
        :raises InvalidResultType: Shot results are not available
        :return: 2D array of readouts, each row a separate outcome and each column a bit value.
        :rtype: np.ndarray

        The order of the columns follows the order of `cbits`, if provided.
        """
        if cbits is None:
            cbits = sorted(self.c_bits.keys(), reverse=(basis == BasisOrder.dlo))
        res = self.get_result(cbits)
        if res.shots is not None:
            return res.shots.to_readouts()
        if not self.c_bits:  # No classical bits.
            warnings.warn("The circuit has no measurement gates.")
        raise InvalidResultType("shots")

    def get_counts(
        self, cbits: Optional[Sequence[Bit]] = None, basis: BasisOrder = BasisOrder.ilo
    ) -> Counter[Tuple[int]]:
        """Return counts of outcomes if available.

        :param cbits: ordered subset of Bits, returns all results by default, defaults to None
        :type cbits: Optional[Sequence[Bit]], optional
        :param basis: Toggle between ILO (increasing lexicographic order of bit ids) and
            DLO (decreasing lexicographic order) for column ordering if cbits is None.
            Defaults to BasisOrder.ilo.
        :raises InvalidResultType: Counts are not available
        :return: Counts of outcomes
        :rtype: Counter[Tuple(int)]
        """
        if cbits is None:
            cbits = sorted(self.c_bits.keys(), reverse=(basis == BasisOrder.dlo))
        res = self.get_result(cbits)
        if res.counts is not None:
            return readout_counts(res.counts)
        if res.shots is not None:
            return readout_counts(res.shots.counts())
        raise InvalidResultType("counts")

    def get_state(
        self,
        qbits: Optional[Sequence[Qubit]] = None,
        basis: BasisOrder = BasisOrder.ilo,
    ) -> np.ndarray:
        """Return statevector if available.

        :param qbits: permutation of Qubits, defaults to None
        :type qbits: Optional[Sequence[Qubit]], optional
        :param basis: Toggle between ILO (increasing lexicographic order of qubit ids)
            and DLO (decreasing lexicographic order) for column ordering if qbits is
            None. Defaults to BasisOrder.ilo.
        :raises InvalidResultType: Statevector not available
        :return: Statevector, (complex 1-D numpy array)
        :rtype: np.ndarray
        """
        if qbits is None:
            qbits = sorted(self.q_bits.keys(), reverse=(basis == BasisOrder.dlo))
        res = self.get_result(qbits)
        if res.state is not None:
            return res.state
        if res.unitary is not None:
            return res.unitary[:, 0]
        raise InvalidResultType("state")

    def get_unitary(
        self,
        qbits: Optional[Sequence[Qubit]] = None,
        basis: BasisOrder = BasisOrder.ilo,
    ) -> np.ndarray:
        """Return unitary if available.

        :param qbits: permutation of Qubits, defaults to None
        :type qbits: Optional[Sequence[Qubit]], optional
        :param basis: Toggle between ILO (increasing lexicographic order of qubit ids)
            and DLO (decreasing lexicographic order) for column ordering if qbits is
            None. Defaults to BasisOrder.ilo.
        :raises InvalidResultType: Statevector not available
        :return: Unitary, (complex 2-D numpy array)
        :rtype: np.ndarray
        """
        if qbits is None:
            qbits = sorted(self.q_bits.keys(), reverse=(basis == BasisOrder.dlo))
        res = self.get_result(qbits)
        if res.unitary is not None:
            return res.unitary
        raise InvalidResultType("unitary")

    def get_distribution(
        self, units: Optional[Sequence[UnitID]] = None
    ) -> Dict[Tuple[int], float]:
        """Calculate an exact or approximate probability distribution over outcomes.

        If the exact statevector is known, the exact probability distribution is
        returned. Otherwise, if measured results are available the distribution
        is estimated from these results.
        """
        try:
            state = self.get_state(units)
            return probs_from_state(state)
        except InvalidResultType:
            counts = self.get_counts(units)
            total = sum(counts.values())
            dist = {outcome: count / total for outcome, count in counts.items()}
            return dist

    def to_dict(self) -> Dict[str, Any]:
        outdict = dict()
        if self.q_bits:
            outdict["qubits"] = [q.to_list() for q in self.get_qbitlist()]
        if self.c_bits:
            outdict["bits"] = [c.to_list() for c in self.get_bitlist()]
        if self._shots is not None:
            outdict["shots"] = self._shots.to_dict()
        if self._counts:
            outdict["counts"] = [
                {"outcome": oc.to_dict(), "count": count}
                for oc, count in self._counts.items()
            ]

        if self._state is not None:
            outdict["state"] = _complex_ar_to_dict(self._state)
        if self._unitary is not None:
            outdict["unitary"] = _complex_ar_to_dict(self._unitary)

        return outdict

    @classmethod
    def from_dict(cls, res_dict: Dict[str, Any]) -> "BackendResult":
        init_dict = dict.fromkeys(
            ("q_bits", "c_bits", "shots", "counts", "state", "unitary")
        )

        if "qubits" in res_dict:
            init_dict["q_bits"] = [Qubit.from_list(tup) for tup in res_dict["qubits"]]
        if "bits" in res_dict:
            init_dict["c_bits"] = [Bit.from_list(tup) for tup in res_dict["bits"]]
        if "shots" in res_dict:
            init_dict["shots"] = OutcomeArray.from_dict(res_dict["shots"])
        if "counts" in res_dict:
            init_dict["counts"] = Counter(
                {
                    OutcomeArray.from_dict(elem["outcome"]): elem["count"]
                    for elem in res_dict["counts"]
                }
            )
        if "state" in res_dict:
            init_dict["state"] = _complex_ar_from_dict(res_dict["state"])
        if "unitary" in res_dict:
            init_dict["unitary"] = _complex_ar_from_dict(res_dict["unitary"])

        return BackendResult(**init_dict)


T = TypeVar("T")


def _sort_keys_by_val(dic: Dict[T, int]) -> List[T]:
    vals, _ = zip(*sorted(dic.items(), key=lambda x: x[1]))
    return list(vals)


def _check_permuted_sequence(first: Collection[Any], second: Collection[Any]) -> bool:
    return len(first) == len(second) and set(first) == set(second)


def _complex_ar_to_dict(ar: np.ndarray) -> Dict[str, List]:
    """Dictionary of real, imaginary parts of complex array, each in list form."""
    return {"real": ar.real.tolist(), "imag": ar.imag.tolist()}


def _complex_ar_from_dict(dic: Dict[str, List]) -> np.ndarray:
    """Construct complex array from dictionary of real and imaginary parts"""

    out = np.array(dic["real"], dtype=np.complex)
    out.imag = np.array(dic["imag"], dtype=np.float)
    return out
