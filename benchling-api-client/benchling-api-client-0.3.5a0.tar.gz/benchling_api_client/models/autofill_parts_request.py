from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class AutofillPartsRequest:
    """  """

    dna_sequence_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.dna_sequence_ids is None:
            dna_sequence_ids = None
        else:
            dna_sequence_ids = self.dna_sequence_ids

        return {
            "dnaSequenceIds": dna_sequence_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AutofillPartsRequest":
        dna_sequence_ids = d.get("dnaSequenceIds")

        return AutofillPartsRequest(
            dna_sequence_ids=dna_sequence_ids,
        )
