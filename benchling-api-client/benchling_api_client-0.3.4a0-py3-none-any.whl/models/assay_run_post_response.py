from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class AssayRunPostResponse:
    """  """

    assay_runs: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.assay_runs is None:
            assay_runs = None
        else:
            assay_runs = self.assay_runs

        return {
            "assayRuns": assay_runs,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AssayRunPostResponse":
        assay_runs = d.get("assayRuns")

        return AssayRunPostResponse(
            assay_runs=assay_runs,
        )
