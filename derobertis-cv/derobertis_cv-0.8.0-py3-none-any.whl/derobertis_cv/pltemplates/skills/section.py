from typing import Sequence, List, Dict, Optional
from collections import defaultdict

import math
import pyexlatex as pl
from pyexlatex.typing import PyexlatexItem

from derobertis_cv.models.skill import SkillModel
from derobertis_cv.pltemplates.skills.skill import PyexlatexSkill


class SkillsSection(pl.Section):
    def __init__(self, skills: Sequence[SkillModel], skills_per_row: int = 4,
                 section_order: Optional[Sequence[str]] = None):
        self.skills = skills

        skill_items: Dict[str, List[SkillModel]] = defaultdict(lambda: [])
        for skill in self.skills:
            skill_items[skill.category.to_title_case_str()].append(skill)

        category_names = list(skill_items.keys())
        orig_category_names = category_names.copy()

        if section_order:
            so = list(section_order)

            def _skill_sort_key(skill_name: str) -> int:
                key = orig_category_names.index(skill_name)
                if skill_name in so:
                    key -= 1000 * so.index(skill_name)
                return key
            category_names.sort(key=_skill_sort_key, reverse=True)

        content: List[PyexlatexItem] = [PyexlatexSkill.legend, '']
        for category_skill_name in category_names:
            cat_skills = skill_items[category_skill_name]
            valid_skills = [skill for skill in cat_skills if not skill.to_title_case_str() in category_names]
            if not valid_skills:
                continue
            content.extend([pl.Bold(category_skill_name), ""])
            num_rows = math.ceil(len(valid_skills) / skills_per_row)
            table_data: List[List[PyexlatexItem]] = [[] for _ in range(num_rows)]
            for i in range(num_rows * skills_per_row):
                col_idx = i % num_rows
                try:
                    skill = valid_skills[i]
                except IndexError:
                    table_data[col_idx].append('')
                else:
                    table_data[col_idx].append(PyexlatexSkill(skill.to_title_case_str(), skill.level))

            vt = pl.ValuesTable.from_list_of_lists(table_data)
            num_cols = min(len(valid_skills), skills_per_row)
            align = "L{4.25cm}" * num_cols
            table = pl.Tabular([vt], align=align)
            content.append(table)

            content.append("")
        content = content[:-1]  # remove last spacer

        super().__init__(content, title="Skills")
