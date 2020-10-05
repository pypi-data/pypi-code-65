from typing import Optional, List, TYPE_CHECKING

from qiskit.providers.aer.noise import NoiseModel

from .aer import AerBackend
from .ibm import IBMQBackend

if TYPE_CHECKING:
    from pytket.device import Device
    from pytket.predicates import Predicate
    from pytket.passes import BasePass


class IBMQEmulatorBackend(AerBackend):
    """A backend which uses the AerBackend to emulate the behaviour of IBMQBackend.
    Attempts to perform the same compilation and predicate checks as IBMQBackend.
    Requires a valid IBMQ account.

    """

    _supports_shots = True
    _supports_counts = True
    _persistent_handles = False

    def __init__(
        self,
        backend_name: str,
        hub: Optional[str] = None,
        group: Optional[str] = None,
        project: Optional[str] = None,
    ):
        """Construct an IBMQEmulatorBackend. Identical to :py:class:`IBMQBackend` constructor,
        except there is no `monitor` parameter. See :py:class:`IBMQBackend` docs for more details.
        """

        self._ibmq = IBMQBackend(backend_name, hub, group, project)
        self._backend = self._ibmq._backend
        noise_model = NoiseModel.from_backend(self._backend)

        super().__init__(noise_model=noise_model)

    @property
    def device(self) -> Optional["Device"]:
        return self._ibmq._device

    @property
    def required_predicates(self) -> List["Predicate"]:
        return self._ibmq.required_predicates

    def default_compilation_pass(self, optimisation_level: int = 1) -> "BasePass":
        return self._ibmq.default_compilation_pass(optimisation_level)
