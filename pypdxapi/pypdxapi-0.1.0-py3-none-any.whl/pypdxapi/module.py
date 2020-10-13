""" Python implementation of Paradox modules."""
from typing import Optional


class ParadoxModule:
    _name: Optional[str] = None
    _model: Optional[str] = None
    _serial: Optional[str] = None
    _version: Optional[str] = None

    def __init__(self, host: str, port: int, module_password: str) -> None:
        """ Initialize """
        self._host: str = host
        self._port: int = port
        self._module_password: str = module_password

    @property
    def name(self) -> Optional[str]:
        """ Return module name. """
        return self._name

    @property
    def model(self) -> Optional[str]:
        """ Return module model. """
        return self._model

    @property
    def serial(self) -> Optional[str]:
        """ Return module serial. """
        return self._serial

    @property
    def version(self) -> Optional[str]:
        """ Return module SW version."""
        return self._version
