from typing import Any, Dict, List, Optional

import attr

from ..models.assay_run import AssayRun


@attr.s(auto_attribs=True)
class AssayRunList:
    """  """

    assay_runs: Optional[List[AssayRun]] = None
    next_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.assay_runs is None:
            assay_runs = None
        else:
            assay_runs = []
            for assay_runs_item_data in self.assay_runs:
                assay_runs_item = assay_runs_item_data.to_dict()

                assay_runs.append(assay_runs_item)

        next_token = self.next_token

        return {
            "assayRuns": assay_runs,
            "nextToken": next_token,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AssayRunList":
        assay_runs = []
        for assay_runs_item_data in d.get("assayRuns") or []:
            assay_runs_item = AssayRun.from_dict(assay_runs_item_data)

            assay_runs.append(assay_runs_item)

        next_token = d.get("nextToken")

        return AssayRunList(
            assay_runs=assay_runs,
            next_token=next_token,
        )
