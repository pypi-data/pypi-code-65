from typing import Optional

import oaas
from oaas_registry_api import OaasRegistryStub

_oaas_registry: Optional[OaasRegistryStub] = None


def oaas_registry() -> OaasRegistryStub:
    """
    Get a reference to the `oaas-registry`
    """
    global _oaas_registry

    if _oaas_registry:
        return _oaas_registry

    _oaas_registry = oaas.get_client(OaasRegistryStub)  # type: ignore

    return _oaas_registry
