from dataclasses import dataclass
from typing import Optional, Sequence

from derobertis_cv.pltemplates.logo import HasLogo


@dataclass
class Organization(HasLogo):
    title: str
    location: str
    abbreviation: Optional[str] = None
    logo_url: Optional[str] = None
    logo_svg_text: Optional[str] = None
    logo_base64: Optional[str] = None
    logo_fa_icon_class_str: Optional[str] = None
    address_lines: Optional[Sequence[str]] = None

    def __post_init__(self):
        if self.abbreviation is None:
            self.abbreviation = self.title