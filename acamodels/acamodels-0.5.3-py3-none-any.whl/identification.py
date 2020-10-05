# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Any, Dict, Optional

from pydantic import root_validator

from acamodels.aca_base import ACABase

# -----------------------------------------------------------------------------
# Model
# -----------------------------------------------------------------------------


class Identification(ACABase):
    """File identification datamodel."""

    puid: Optional[str]
    signature: Optional[str]
    warning: Optional[str]

    @root_validator
    def check_puid_sig(cls, fields: Dict[Any, Any]) -> Dict[Any, Any]:
        """Validate that a PUID cannot have an empty signature
        or vice versa."""

        puid = fields.get("puid")
        signature = fields.get("signature")

        if puid is not None and signature is None:
            raise ValueError(f"Signature missing for PUID {puid}.")

        if signature is not None and puid is None:
            raise ValueError(f"PUID missing for signature {signature}.")

        return fields
