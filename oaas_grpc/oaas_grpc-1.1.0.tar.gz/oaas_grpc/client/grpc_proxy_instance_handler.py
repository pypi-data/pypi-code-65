from typing import Optional, Dict, TypeVar, Type

import grpc
from grpc import Channel
from oaas_grpc.client import registry_discovery
from oaas_grpc.client.connection_test import is_someone_listening
from oaas_grpc.client.oaas_registry import oaas_registry
from oaas_grpc.client.proxy import ProxyInstanceHandler
from oaas_registry_api.rpc.registry_pb2 import (
    OaasServiceDefinition,
    OaasResolveServiceResponse,
    OaasServiceId,
)

T = TypeVar("T")


def is_unavailable_service(oaas_grpc_exception):
    if not hasattr(oaas_grpc_exception, "args"):
        return False

    if not oaas_grpc_exception.args:
        return False

    if oaas_grpc_exception.args[0].code == grpc.StatusCode.UNAVAILABLE:
        return True

    return False


class GrpcProxyInstanceHandler(ProxyInstanceHandler):
    def __init__(
        self,
        *,
        namespace: str,
        name: str,
        version: str,
        tags: Optional[Dict[str, str]],
        code: Type[T]
    ):
        self.namespace = namespace
        self.name = name
        self.version = version
        self.tags = tags
        self.code = code

        self._channels: Dict[str, Channel] = dict()
        self._failed_tries = 0

    def initial_instance(self):
        # the ooas-registry is only hosted on the grpc
        if (
            self.namespace == "default"
            and self.name == "oaas-registry"
            and self.version == "1"
        ):
            resolve_response = registry_discovery.find_registry()
        else:
            resolve_response = oaas_registry().resolve_service(
                OaasServiceDefinition(
                    namespace=self.namespace,
                    name=self.name,
                    version=self.version,
                    tags=self.tags,
                )
            )

        channel = self.find_channel(resolve_response)
        return self.code(channel=channel)

    def call_error(self, oaas_grpc_proxy, oaas_grpc_exception, *args, **kw):
        # FIXME: this should recreate the instance only if the call is a grpc unavailable
        # exception.
        if not is_unavailable_service(oaas_grpc_exception) or self._failed_tries >= 5:
            self._failed_tries = 0
            raise oaas_grpc_exception

        self._failed_tries += 1

        # FIXME: the channels should be managed externally by a channel manager
        self._channels.clear()
        oaas_grpc_proxy._delegate = self.initial_instance()

        return oaas_grpc_proxy._delegate

    def call_success(self):
        self._failed_tries = 0

    def find_channel(self, resolve_response: OaasResolveServiceResponse) -> Channel:
        for service_definition in resolve_response.services:
            for location in service_definition.locations:
                if location in self._channels:
                    return self._channels[location]

                if is_someone_listening(location):
                    channel = grpc.insecure_channel(location)
                    self._channels[location] = channel

                    return channel

            # none of the locations for that definition were accessible
            # unregister the service by the client.
            # FIXME: make unregistering by clients configurable
            # FIXME: shoulnd't have hardcoded values on _instance_id, but types
            oaas_registry().unregister_service(
                OaasServiceId(id=service_definition.tags["_instance_id"])
            )

        raise Exception("Unable to find any listening service on any of the locations.")
