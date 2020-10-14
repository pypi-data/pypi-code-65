from typing import Dict, Iterable


class ServiceDefinition:
    def __init__(
        self,
        *,
        namespace: str = "default",
        name: str,
        version: str = "1",
        protocol: str = "grpc",
        tags: Dict[str, str],
        locations: Iterable[str],
    ) -> None:
        self.protocol = protocol
        self.namespace = namespace
        self.name = name
        self.version = version
        self.tags = tags
        self.locations = locations

    @property
    def instance_id(self) -> str:
        return self.tags["_instance_id"]

    def __repr__(self) -> str:
        return f"svc:{self.protocol}:{self.namespace}:{self.name}:{self.version}"
