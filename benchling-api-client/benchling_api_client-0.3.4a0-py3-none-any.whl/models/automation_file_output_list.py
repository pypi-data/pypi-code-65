from typing import Any, Dict, List, Optional

import attr

from ..models.automation_file import AutomationFile


@attr.s(auto_attribs=True)
class AutomationFileOutputList:
    """  """

    automation_output_processors: Optional[List[AutomationFile]] = None
    next_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.automation_output_processors is None:
            automation_output_processors = None
        else:
            automation_output_processors = []
            for automation_output_processors_item_data in self.automation_output_processors:
                automation_output_processors_item = automation_output_processors_item_data.to_dict()

                automation_output_processors.append(automation_output_processors_item)

        next_token = self.next_token

        return {
            "automationOutputProcessors": automation_output_processors,
            "nextToken": next_token,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AutomationFileOutputList":
        automation_output_processors = []
        for automation_output_processors_item_data in d.get("automationOutputProcessors") or []:
            automation_output_processors_item = AutomationFile.from_dict(automation_output_processors_item_data)

            automation_output_processors.append(automation_output_processors_item)

        next_token = d.get("nextToken")

        return AutomationFileOutputList(
            automation_output_processors=automation_output_processors,
            next_token=next_token,
        )
