from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class Primer:
    """  """

    bases: Optional[str] = None
    bind_position: Optional[int] = None
    color: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    name: Optional[str] = None
    oligo_id: Optional[str] = None
    overhang_length: Optional[int] = None
    strand: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        bases = self.bases
        bind_position = self.bind_position
        color = self.color
        start = self.start
        end = self.end
        name = self.name
        oligo_id = self.oligo_id
        overhang_length = self.overhang_length
        strand = self.strand

        return {
            "bases": bases,
            "bindPosition": bind_position,
            "color": color,
            "start": start,
            "end": end,
            "name": name,
            "oligoId": oligo_id,
            "overhangLength": overhang_length,
            "strand": strand,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Primer":
        bases = d.get("bases")

        bind_position = d.get("bindPosition")

        color = d.get("color")

        start = d.get("start")

        end = d.get("end")

        name = d.get("name")

        oligo_id = d.get("oligoId")

        overhang_length = d.get("overhangLength")

        strand = d.get("strand")

        return Primer(
            bases=bases,
            bind_position=bind_position,
            color=color,
            start=start,
            end=end,
            name=name,
            oligo_id=oligo_id,
            overhang_length=overhang_length,
            strand=strand,
        )
