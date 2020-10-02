from typing import Any, Dict, List, Optional

import attr


@attr.s(auto_attribs=True)
class Translation:
    """  """

    start: Optional[int] = None
    end: Optional[int] = None
    strand: Optional[int] = None
    amino_acids: Optional[str] = None
    regions: Optional[List[Dict[Any, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        start = self.start
        end = self.end
        strand = self.strand
        amino_acids = self.amino_acids
        if self.regions is None:
            regions = None
        else:
            regions = []
            for regions_item_data in self.regions:
                regions_item = regions_item_data

                regions.append(regions_item)

        return {
            "start": start,
            "end": end,
            "strand": strand,
            "aminoAcids": amino_acids,
            "regions": regions,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Translation":
        start = d.get("start")

        end = d.get("end")

        strand = d.get("strand")

        amino_acids = d.get("aminoAcids")

        regions = []
        for regions_item_data in d.get("regions") or []:
            regions_item = regions_item_data

            regions.append(regions_item)

        return Translation(
            start=start,
            end=end,
            strand=strand,
            amino_acids=amino_acids,
            regions=regions,
        )
