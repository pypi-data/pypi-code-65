"""Collection of utility functions"""
from typing import Optional


def normalize_mac(mac: Optional[str]) -> Optional[str]:
    """Given a MAC address, return the normalized version."""
    if mac is None:
        return None
    return mac.replace("-", ":").lower()
