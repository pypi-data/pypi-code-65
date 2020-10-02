from typing import Any, Dict

import attr


@attr.s(auto_attribs=True)
class WarehouseCredentialsRequest:
    """  """

    expires_in: int

    def to_dict(self) -> Dict[str, Any]:
        expires_in = self.expires_in

        return {
            "expiresIn": expires_in,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "WarehouseCredentialsRequest":
        expires_in = d["expiresIn"]

        return WarehouseCredentialsRequest(
            expires_in=expires_in,
        )
