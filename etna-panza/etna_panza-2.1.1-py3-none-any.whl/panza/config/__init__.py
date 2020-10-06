"""
Module providing helpers for panza's configuration
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AdditionalDockerDaemonConfiguration:
    network_bridge_mask: str
    dns: List[str] = field(default_factory=list)


@dataclass
class PanzaConfiguration:
    root_directory: str
    additional_docker_daemon: AdditionalDockerDaemonConfiguration


_config: Optional[PanzaConfiguration] = None


def init_config(config: PanzaConfiguration):
    """
    Initialize the configuration with given values

    :param config:                  the configuration to use for Panza
    """
    global _config
    _config = config


def get_config() -> PanzaConfiguration:
    """
    Retrieve the configuration
    """
    return _config
