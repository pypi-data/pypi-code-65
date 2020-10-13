"""**neuroio-python**

A Python package for interacting with the NeuroIO API
"""
from .clients import AsyncClient, Client

__version__: str = "0.0.1"

__all__ = ["__version__", "Client", "AsyncClient"]
