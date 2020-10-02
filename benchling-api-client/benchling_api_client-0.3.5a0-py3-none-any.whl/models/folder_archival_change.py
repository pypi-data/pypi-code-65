from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class FolderArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of folders along with any IDs of folder contents that were unarchived."""

    folder_ids: Optional[List[str]] = None
    entry_ids: Optional[List[str]] = None
    protocol_ids: Optional[List[str]] = None
    dna_sequence_ids: Optional[List[str]] = None
    aa_sequence_ids: Optional[List[str]] = None
    custom_entity_ids: Optional[List[str]] = None
    mixture_ids: Optional[List[str]] = None
    oligo_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.folder_ids is None:
            folder_ids = None
        else:
            folder_ids = self.folder_ids

        if self.entry_ids is None:
            entry_ids = None
        else:
            entry_ids = self.entry_ids

        if self.protocol_ids is None:
            protocol_ids = None
        else:
            protocol_ids = self.protocol_ids

        if self.dna_sequence_ids is None:
            dna_sequence_ids = None
        else:
            dna_sequence_ids = self.dna_sequence_ids

        if self.aa_sequence_ids is None:
            aa_sequence_ids = None
        else:
            aa_sequence_ids = self.aa_sequence_ids

        if self.custom_entity_ids is None:
            custom_entity_ids = None
        else:
            custom_entity_ids = self.custom_entity_ids

        if self.mixture_ids is None:
            mixture_ids = None
        else:
            mixture_ids = self.mixture_ids

        if self.oligo_ids is None:
            oligo_ids = None
        else:
            oligo_ids = self.oligo_ids

        return {
            "folderIds": folder_ids,
            "entryIds": entry_ids,
            "protocolIds": protocol_ids,
            "dnaSequenceIds": dna_sequence_ids,
            "aaSequenceIds": aa_sequence_ids,
            "customEntityIds": custom_entity_ids,
            "mixtureIds": mixture_ids,
            "oligoIds": oligo_ids,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "FolderArchivalChange":
        folder_ids = d.get("folderIds")

        entry_ids = d.get("entryIds")

        protocol_ids = d.get("protocolIds")

        dna_sequence_ids = d.get("dnaSequenceIds")

        aa_sequence_ids = d.get("aaSequenceIds")

        custom_entity_ids = d.get("customEntityIds")

        mixture_ids = d.get("mixtureIds")

        oligo_ids = d.get("oligoIds")

        return FolderArchivalChange(
            folder_ids=folder_ids,
            entry_ids=entry_ids,
            protocol_ids=protocol_ids,
            dna_sequence_ids=dna_sequence_ids,
            aa_sequence_ids=aa_sequence_ids,
            custom_entity_ids=custom_entity_ids,
            mixture_ids=mixture_ids,
            oligo_ids=oligo_ids,
        )
