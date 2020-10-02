from typing import Any, Dict, List, Optional

import attr

from ..models.registry import Registry


@attr.s(auto_attribs=True)
class RegistryList:
    """  """

    registries: Optional[List[Registry]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.registries is None:
            registries = None
        else:
            registries = []
            for registries_item_data in self.registries:
                registries_item = registries_item_data.to_dict()

                registries.append(registries_item)

        return {
            "registries": registries,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RegistryList":
        registries = []
        for registries_item_data in d.get("registries") or []:
            registries_item = Registry.from_dict(registries_item_data)

            registries.append(registries_item)

        return RegistryList(
            registries=registries,
        )
