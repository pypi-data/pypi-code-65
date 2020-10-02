from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class SampleGroup:
    """ Represents a sample group that is an input to a request. A sample group is a set of samples upon which work in the request should be done. """

    id: Optional[str] = None
    samples: Optional[Dict[Any, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        samples = self.samples if self.samples else None

        return {
            "id": id,
            "samples": samples,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SampleGroup":
        id = d.get("id")

        samples = None
        if d.get("samples") is not None:
            samples = d.get("samples")

        return SampleGroup(
            id=id,
            samples=samples,
        )
