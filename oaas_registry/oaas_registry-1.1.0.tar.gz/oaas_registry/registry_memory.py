import collections
import functools
import uuid
from typing import Dict, Iterable, Set, Callable, TypeVar

from readerwriterlock import rwlock

from oaas_registry.registry import Registry
from oaas_registry.service_definition import ServiceDefinition

T = TypeVar("T")


def write_lock(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        self = args[0]
        try:
            self._wlock.acquire()
            return f(*args, **kw)
        finally:
            self._wlock.release()

    return wrapper


def read_lock(f: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(f)
    def wrapper(*args, **kw) -> T:
        self = args[0]
        try:
            self._rlock.acquire()
            return f(*args, **kw)
        finally:
            self._rlock.release()

    return wrapper


class RegistryMemory(Registry):
    def __init__(self) -> None:
        self._services: Dict[str, Set[ServiceDefinition]] = collections.defaultdict(set)
        self._rwlock = rwlock.RWLockWrite()
        self._wlock = self._rwlock.gen_wlock()
        self._rlock = self._rwlock.gen_wlock()

    @write_lock
    def register_service(
        self,
        *,
        protocol: str = "grpc",
        namespace: str = "default",
        name: str,
        version: str = "1",
        tags: Dict[str, str],
        locations: Iterable[str],
    ) -> ServiceDefinition:

        sd_tags = dict(tags)
        sd_tags["_instance_id"] = str(uuid.uuid4())

        sd = ServiceDefinition(
            protocol=protocol,
            namespace=namespace,
            name=name,
            version=version,
            tags=sd_tags,
            locations=locations,
        )

        _id = f"{protocol}:{namespace}:{name}:{version}"

        self._services[_id].add(sd)

        for tag_key, tag_value in sd_tags.items():
            self._services[f"{tag_key}={tag_value}"].add(sd)

        return sd

    @read_lock
    def resolve_service(
        self,
        *,
        protocol: str = "grpc",
        namespace: str = "default",
        name: str,
        version: str = "1",
        tags: Dict[str, str],
    ) -> Iterable[ServiceDefinition]:
        _id = f"{protocol}:{namespace}:{name}:{version}"

        if _id not in self._services:
            return set()

        # we need a copy, because we'll filter them out inplace
        current_services = set(self._services[_id])

        for tag_key, tag_value in tags.items():
            current_services.intersection_update(
                self._services[f"{tag_key}={tag_value}"]
            )

        return current_services

    @write_lock
    def unregister_service(self, *, instance_id: str) -> bool:
        sd_set = self._services[f"_instance_id={instance_id}"]

        if not sd_set:
            return False

        sd = sd_set.__iter__().__next__()

        _id = f"{sd.protocol}:{sd.namespace}:{sd.name}:{sd.version}"
        self._services[_id].remove(sd)

        if not self._services[_id]:
            del self._services[_id]

        for tag_key, tag_value in sd.tags.items():
            self._services[f"{tag_key}={tag_value}"].remove(sd)
            if not self._services[f"{tag_key}={tag_value}"]:
                del self._services[f"{tag_key}={tag_value}"]

        return True
