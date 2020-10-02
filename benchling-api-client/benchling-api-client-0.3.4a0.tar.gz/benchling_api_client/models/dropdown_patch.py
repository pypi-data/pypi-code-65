from typing import Any, Dict, List

import attr


@attr.s(auto_attribs=True)
class DropdownPatch:
    """  """

    options: List[Dict[Any, Any]]

    def to_dict(self) -> Dict[str, Any]:
        options = []
        for options_item_data in self.options:
            options_item = options_item_data

            options.append(options_item)

        return {
            "options": options,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DropdownPatch":
        options = []
        for options_item_data in d["options"]:
            options_item = options_item_data

            options.append(options_item)

        return DropdownPatch(
            options=options,
        )
