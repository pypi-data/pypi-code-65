from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class DnaSequenceArchiveResponse:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of DNA sequences along with any IDs of batches that were archived / unarchived."""

    dna_sequence_ids: Optional[List[str]] = None
    batch_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.dna_sequence_ids is None:
            dna_sequence_ids = None
        else:
            dna_sequence_ids = self.dna_sequence_ids

        if self.batch_ids is None:
            batch_ids = None
        else:
            batch_ids = self.batch_ids

        return {
            "dnaSequenceIds": dna_sequence_ids,
            "batchIds": batch_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DnaSequenceArchiveResponse":
        dna_sequence_ids = d.get("dnaSequenceIds")

        batch_ids = d.get("batchIds")

        return DnaSequenceArchiveResponse(
            dna_sequence_ids=dna_sequence_ids,
            batch_ids=batch_ids,
        )
