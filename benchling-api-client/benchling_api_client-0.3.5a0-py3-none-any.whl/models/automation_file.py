from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class AutomationFile:
    """  """

    assay_run_id: Optional[str] = None
    automation_file_config: Optional[Dict[Any, Any]] = None
    file: Optional[Dict[Any, Any]] = None
    id: Optional[str] = None
    status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        assay_run_id = self.assay_run_id
        automation_file_config = self.automation_file_config if self.automation_file_config else None

        file = self.file if self.file else None

        id = self.id
        status = self.status

        return {
            "assayRunId": assay_run_id,
            "automationFileConfig": automation_file_config,
            "file": file,
            "id": id,
            "status": status,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AutomationFile":
        assay_run_id = d.get("assayRunId")

        automation_file_config = None
        if d.get("automationFileConfig") is not None:
            automation_file_config = d.get("automationFileConfig")

        file = None
        if d.get("file") is not None:
            file = d.get("file")

        id = d.get("id")

        status = d.get("status")

        return AutomationFile(
            assay_run_id=assay_run_id,
            automation_file_config=automation_file_config,
            file=file,
            id=id,
            status=status,
        )
