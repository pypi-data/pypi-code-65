import pyexlatex as pl

from derobertis_cv.pltemplates.skills.skill_dot import SkillDot


LEGEND_SPACER_SIZE = 0.4

class PyexlatexSkill(pl.Template):
    legend = [
        pl.Center(
            [
                SkillDot(5),
                '= 5',
                pl.HSpace(LEGEND_SPACER_SIZE),
                '|',
                pl.HSpace(LEGEND_SPACER_SIZE),
                SkillDot(4),
                '= 4',
                pl.HSpace(LEGEND_SPACER_SIZE),
                '|',
                pl.HSpace(LEGEND_SPACER_SIZE),
                SkillDot(3),
                '= 3',
                pl.HSpace(LEGEND_SPACER_SIZE),
                '|',
                pl.HSpace(LEGEND_SPACER_SIZE),
                SkillDot(2),
                '= 2',
                pl.HSpace(LEGEND_SPACER_SIZE),
                '|',
                pl.HSpace(LEGEND_SPACER_SIZE),
                SkillDot(1),
                '= 1',
            ]
        )

    ]

    def __init__(self, skill_name: str, level: int):
        self.skill_name = skill_name
        self.level = level
        self.contents = [SkillDot(level), skill_name]
        super().__init__()
