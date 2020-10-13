""" Python implementation of Paradox HD7X cameras (and future other modules)."""


class ParadoxModuleError(Exception):
    """Generic exception for Paradox modules."""


class ParadoxCameraError(ParadoxModuleError):
    """Generic exception for Camera modules."""
