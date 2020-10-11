"""Implement an API wrapper for accessing a TP-Link EAP."""
from pathlib import Path

from .client import Client
from .eap import Eap
from .error import CommunicationError, PytleapError

__all__ = [
    "Eap",
    "Client",
    "PytleapError",
    "CommunicationError",
]

__version__ = (Path(__file__).parent / "VERSION").read_text().strip()
