from typing import Any, Dict, List, Optional

import attr

from ..models.dna_sequence import DnaSequence


@attr.s(auto_attribs=True)
class DnaSequenceBulkGetResponse:
    """  """

    dna_sequences: Optional[List[DnaSequence]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.dna_sequences is None:
            dna_sequences = None
        else:
            dna_sequences = []
            for dna_sequences_item_data in self.dna_sequences:
                dna_sequences_item = dna_sequences_item_data.to_dict()

                dna_sequences.append(dna_sequences_item)

        return {
            "dnaSequences": dna_sequences,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "DnaSequenceBulkGetResponse":
        dna_sequences = []
        for dna_sequences_item_data in d.get("dnaSequences") or []:
            dna_sequences_item = DnaSequence.from_dict(dna_sequences_item_data)

            dna_sequences.append(dna_sequences_item)

        return DnaSequenceBulkGetResponse(
            dna_sequences=dna_sequences,
        )
