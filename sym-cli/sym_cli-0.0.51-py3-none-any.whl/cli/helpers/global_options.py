import inspect
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Type

from ..errors import SAMLClientNotFound
from ..helpers import segment
from ..saml_clients.chooser import choose_saml_client
from ..saml_clients.saml_client import SAMLClient


@dataclass
class GlobalOptions:
    saml_client_type: Type[SAMLClient] = field(
        default_factory=lambda: choose_saml_client("auto", none_ok=True)
    )
    saml_clients: Dict[str, SAMLClient] = field(default_factory=dict)

    debug: bool = False
    log_dir: Optional[str] = None

    def dprint(self, *s: Sequence[str], **kwargs):
        s = list(map(str, filter(None, s)))
        if s and self.debug:
            message = " ".join(s)
            if kwargs:
                message += ": " + ",".join([f"{k}={v}" for k, v in kwargs.items()])
            mod = inspect.getmodule(inspect.stack()[1][0])
            logging.getLogger(mod.__name__).debug(message)

    def create_saml_client(self, resource: str) -> SAMLClient:
        if not self.saml_client_type:
            raise SAMLClientNotFound()
        segment.track("Resource Requested", resource=resource)
        if resource not in self.saml_clients:
            self.saml_clients[resource] = self.saml_client_type(resource, options=self)
        return self.saml_clients[resource]

    def to_dict(self):
        return {"debug": self.debug, "saml_client": str(self.saml_client_type)}
