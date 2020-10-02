from typing import Any, Dict, List, Optional

import attr

from ..models.custom_entity import CustomEntity


@attr.s(auto_attribs=True)
class CustomEntityList:
    """  """

    custom_entities: Optional[List[CustomEntity]] = None
    next_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.custom_entities is None:
            custom_entities = None
        else:
            custom_entities = []
            for custom_entities_item_data in self.custom_entities:
                custom_entities_item = custom_entities_item_data.to_dict()

                custom_entities.append(custom_entities_item)

        next_token = self.next_token

        return {
            "customEntities": custom_entities,
            "nextToken": next_token,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "CustomEntityList":
        custom_entities = []
        for custom_entities_item_data in d.get("customEntities") or []:
            custom_entities_item = CustomEntity.from_dict(custom_entities_item_data)

            custom_entities.append(custom_entities_item)

        next_token = d.get("nextToken")

        return CustomEntityList(
            custom_entities=custom_entities,
            next_token=next_token,
        )
