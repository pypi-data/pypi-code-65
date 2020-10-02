from typing import Any, Dict, List, Optional

import attr

from ..models.assay_result import AssayResult


@attr.s(auto_attribs=True)
class RequestResponse:
    """  """

    samples: Optional[List[Dict[Any, Any]]] = None
    results: Optional[List[AssayResult]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.samples is None:
            samples = None
        else:
            samples = []
            for samples_item_data in self.samples:
                samples_item = samples_item_data

                samples.append(samples_item)

        if self.results is None:
            results = None
        else:
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()

                results.append(results_item)

        return {
            "samples": samples,
            "results": results,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RequestResponse":
        samples = []
        for samples_item_data in d.get("samples") or []:
            samples_item = samples_item_data

            samples.append(samples_item)

        results = []
        for results_item_data in d.get("results") or []:
            results_item = AssayResult.from_dict(results_item_data)

            results.append(results_item)

        return RequestResponse(
            samples=samples,
            results=results,
        )
