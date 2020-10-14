"""Settings module from fastnats package."""

from typing import Any, Optional
from pydantic import BaseSettings, validator


class NATSClientSettings(BaseSettings):
    """Configuration for NATS clients."""

    host: str = "127.0.0.1"
    port: int = 4222


class STANClientSettings(BaseSettings):
    """Configuration for NATS Streaming clients."""

    cluster: str = "test-cluster"
    client: str = "test-client"


class FastSTANSettings(BaseSettings):
    """Configuration for FastSTAN applications."""

    nats: Optional[NATSClientSettings] = None
    stan: Optional[STANClientSettings] = None

    @validator("nats", pre=True, always=True)
    def validate_nats(cls, value: Any) -> NATSClientSettings:
        """Validate NATS settings."""
        if value is None:
            return NATSClientSettings()
        return value

    @validator("stan", pre=True, always=True)
    def validate_stan(cls, value: Any) -> STANClientSettings:
        """Validate STAN settings."""
        if value is None:
            return STANClientSettings()
        elif isinstance(value, STANClientSettings):
            return value
        return STANClientSettings(**value)
