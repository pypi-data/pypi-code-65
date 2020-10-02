from typing import Any, Dict, List, Optional

import attr

from ..models.automation_file import AutomationFile


@attr.s(auto_attribs=True)
class AutomationFileInputList:
    """  """

    automation_input_generators: Optional[List[AutomationFile]] = None
    next_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.automation_input_generators is None:
            automation_input_generators = None
        else:
            automation_input_generators = []
            for automation_input_generators_item_data in self.automation_input_generators:
                automation_input_generators_item = automation_input_generators_item_data.to_dict()

                automation_input_generators.append(automation_input_generators_item)

        next_token = self.next_token

        return {
            "automationInputGenerators": automation_input_generators,
            "nextToken": next_token,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AutomationFileInputList":
        automation_input_generators = []
        for automation_input_generators_item_data in d.get("automationInputGenerators") or []:
            automation_input_generators_item = AutomationFile.from_dict(automation_input_generators_item_data)

            automation_input_generators.append(automation_input_generators_item)

        next_token = d.get("nextToken")

        return AutomationFileInputList(
            automation_input_generators=automation_input_generators,
            next_token=next_token,
        )
