from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class Dropdown:
    """  """

    options: Optional[List[Dict[Any, Any]]] = None
    name: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.options is None:
            options = None
        else:
            options = []
            for options_item_data in self.options:
                options_item = options_item_data

                options.append(options_item)

        name = self.name
        id = self.id

        return {
            "options": options,
            "name": name,
            "id": id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Dropdown":
        options = []
        for options_item_data in d.get("options") or []:
            options_item = options_item_data

            options.append(options_item)

        name = d.get("name")

        id = d.get("id")

        return Dropdown(
            options=options,
            name=name,
            id=id,
        )
