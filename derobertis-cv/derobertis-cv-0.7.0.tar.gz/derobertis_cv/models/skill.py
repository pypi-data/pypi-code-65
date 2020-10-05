from weakref import WeakSet
from dataclasses import dataclass, field
from typing import Optional, Sequence, List, Set, Callable, Union, cast

from weakreflist import WeakList

from derobertis_cv.models.cased import CasedModel
from derobertis_cv.models.category import CategoryModel
from derobertis_cv.models.nested import NestedModel
from derobertis_cv.pltemplates.logo import HasLogo


@dataclass(unsafe_hash=True)
class SkillModel(CasedModel, NestedModel, HasLogo):
    title: str
    level: int
    flexible_case: bool = True
    logo_url: Optional[str] = None
    logo_svg_text: Optional[str] = None
    logo_base64: Optional[str] = None
    logo_fa_icon_class_str: Optional[str] = None
    case_lower_func: Callable[[str], str] = lambda x: x.lower()
    case_title_func: Callable[[str], str] = lambda x: x.title()
    case_capitalize_func: Callable[[str], str] = lambda x: x.capitalize()
    parents: Optional[Sequence['NestedModel']] = tuple()
    children: WeakList = field(default_factory=lambda: WeakList(), hash=False)
    primary_category: Optional[Union['SkillModel', str]] = None

    def __post_init__(self):
        super().__init__()

    @property
    def category(self) -> 'SkillModel':
        if self.primary_category is not None:
            if self.primary_category == 'self':
                return self
            elif isinstance(self.primary_category, str):
                raise ValueError('only str passed for primary_category should be self')
            return self.primary_category
        if self.parents:
            return cast('SkillModel', self.parents[0])
        return self

