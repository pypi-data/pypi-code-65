from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class Annotation:
    """  """

    color: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    name: Optional[str] = None
    strand: Optional[int] = None
    type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        color = self.color
        start = self.start
        end = self.end
        name = self.name
        strand = self.strand
        type = self.type

        return {
            "color": color,
            "start": start,
            "end": end,
            "name": name,
            "strand": strand,
            "type": type,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Annotation":
        color = d.get("color")

        start = d.get("start")

        end = d.get("end")

        name = d.get("name")

        strand = d.get("strand")

        type = d.get("type")

        return Annotation(
            color=color,
            start=start,
            end=end,
            name=name,
            strand=strand,
            type=type,
        )
