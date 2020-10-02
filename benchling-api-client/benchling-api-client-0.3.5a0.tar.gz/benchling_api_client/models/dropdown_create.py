from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class DropdownCreate:
    """  """

    name: str
    options: List[Dict[Any, Any]]
    registry_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        options = []
        for options_item_data in self.options:
            options_item = options_item_data

            options.append(options_item)

        registry_id = self.registry_id

        return {
            "name": name,
            "options": options,
            "registryId": registry_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DropdownCreate":
        name = d["name"]

        options = []
        for options_item_data in d["options"]:
            options_item = options_item_data

            options.append(options_item)

        registry_id = d.get("registryId")

        return DropdownCreate(
            name=name,
            options=options,
            registry_id=registry_id,
        )
