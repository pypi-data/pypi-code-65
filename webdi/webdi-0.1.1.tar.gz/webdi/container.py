"""Contains the ContainerDefinition and Container classes."""
import inspect
from typing import (Any, Awaitable, Callable, MutableMapping, Optional,
                    Sequence, Union, cast)


class Container:
    """DependencyInjection container instance."""

    def __init__(self, container_definition: "ContainerDefinition") -> None:
        self.container_definition = container_definition
        self.services: MutableMapping[str, Any] = {}

    def has(self, key: str) -> bool:
        return key in self.services

    def get(self, key: str) -> Any:
        if key not in self.services:
            self.services[key] = self.container_definition.get(key)(self)
        return self.services[key]

    async def reset(self, key: str) -> "Container":
        await self.cleanup(key)
        del self.services[key]
        return self

    async def reset_all(self) -> "Container":
        await self.cleanup_all()
        self.services = {}
        return self

    async def cleanup(self, key: str):
        """Cleanup a single service if it has been booted and it has a cleanup function
        registered.
        """
        if key not in self.services:
            return

        cleanup = self.container_definition.get_cleanup(key)

        if not cleanup:
            return

        service = self.services[key]
        result = cleanup(service)
        if inspect.isawaitable(result):
            await cast(Awaitable[Any], result)

    async def cleanup_all(self):
        """Iterate through all services that have been created, and call the associated cleanup
        method for that service, if there is one.
        """
        for key in self.services:
            await self.cleanup(key)
        return


Factory = Callable[[Container], Any]
SyncCleanup = Callable[[Any], None]
AsyncCleanup = Callable[[Any], Awaitable[None]]
Cleanup = Union[SyncCleanup, AsyncCleanup]


class ContainerDefinition:
    """Maps dependency keys to factories."""

    def __init__(self, *, allow_overwrite: bool = False) -> None:
        self.allow_overwrite: bool = allow_overwrite
        self.services: MutableMapping[str, Factory] = {}
        self.cleanup: MutableMapping[str, Cleanup] = {}

    def add(
        self, key: str, factory: Factory, cleanup: Optional[Cleanup] = None
    ) -> "ContainerDefinition":
        """Map a key to a factory."""
        if not self.allow_overwrite:
            if key in self.services:
                raise KeyError(f"Key {key} already added to container")
        self.services[key] = factory
        if cleanup:
            self.cleanup[key] = cleanup
        return self

    def add_service(
        self,
        key: str,
        dependencies: Sequence[str],
        factory: Callable,
        cleanup: Optional[Cleanup] = None,
    ) -> "ContainerDefinition":
        """Simple method to add a service that depends only on things defined in the container."""
        return self.add(key, key_list_factory(dependencies, factory), cleanup)

    def get(self, key: str) -> Factory:
        return self.services[key]

    def get_container(self) -> Container:
        return Container(self)

    def get_cleanup(self, key: str) -> Optional[Cleanup]:
        return self.cleanup.get(key, None)


def key_list_factory(dependencies: Sequence[str], factory: Callable) -> Factory:
    def build(container: Container) -> Any:
        return factory(*[container.get(key) for key in dependencies])

    return build
