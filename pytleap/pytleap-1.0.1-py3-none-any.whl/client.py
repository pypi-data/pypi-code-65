"""Model of a Wifi client"""
# pylint: disable=R0903,C0103
from typing import Optional

from .utils import normalize_mac


class Client:
    """Represent a client of the EAP."""

    def __init__(self, entry):
        self.entry = entry

    @property
    def mac_address(self) -> str:
        """Return the MAC address of the client."""
        return normalize_mac(self.entry["MAC"])

    @property
    def hostname(self) -> Optional[str]:
        """Return the hostname of the client, None if unknown."""
        hostname = self.entry["hostname"]
        return hostname if hostname != "Unknown" else None

    @property
    def ip(self) -> Optional[str]:
        """Return the IP of the client."""
        ip = self.entry["IP"]
        if ip == "--":
            return None
        return ip

    def __repr__(self):
        """Client representation."""
        return f"<Client{{{self.mac_address}}}>"
