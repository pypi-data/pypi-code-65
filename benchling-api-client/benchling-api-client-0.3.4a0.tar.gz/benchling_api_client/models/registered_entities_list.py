from typing import Any, Dict, List, Optional

import attr

from ..models.entity import Entity


@attr.s(auto_attribs=True)
class RegisteredEntitiesList:
    """  """

    entities: Optional[List[Entity]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.entities is None:
            entities = None
        else:
            entities = []
            for entities_item_data in self.entities:
                entities_item = entities_item_data.to_dict()

                entities.append(entities_item)

        return {
            "entities": entities,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RegisteredEntitiesList":
        entities = []
        for entities_item_data in d.get("entities") or []:
            entities_item = Entity.from_dict(entities_item_data)

            entities.append(entities_item)

        return RegisteredEntitiesList(
            entities=entities,
        )
