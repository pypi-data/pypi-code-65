from typing import Literal, Optional, Type

from ..errors import SAMLClientNotFound
from ..helpers.os import has_command
from ..helpers.util import requires_all_imports
from . import import_all
from .saml_client import SAMLClient

SAMLClientName = Literal["auto", "aws-okta", "saml2aws", "aws-profile"]


@requires_all_imports(import_all)
def option_values():
    return ["auto"] + [x.option_value for x in SAMLClient.sorted_subclasses()]


@requires_all_imports(import_all)
def choose_saml_client(
    saml_client_name: SAMLClientName, none_ok=False
) -> Optional[Type[SAMLClient]]:
    if saml_client_name == "auto":
        for client in SAMLClient.sorted_subclasses():
            if has_command(client.binary):
                return client
    else:
        for client in SAMLClient.sorted_subclasses():
            if client.option_value == saml_client_name:
                return client

    if not none_ok:
        raise SAMLClientNotFound()
