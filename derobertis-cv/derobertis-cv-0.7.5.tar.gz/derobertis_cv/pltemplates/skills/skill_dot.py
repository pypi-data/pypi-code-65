from typing import Union

import pyexlatex as pl
from pyexlatex.typing import PyexlatexItems

partial_circle_def = pl.Raw(
r"""
\tikzset{%
    pics/partialcircle/.style args={#1/#2/#3}{code={%
        \ifstrequal{#2}{0}{%
            \node[circle,minimum width=1.35mm,draw,fill=#1] {};
        }{%
            \tkzDefPoint(0,0){O}
            \tkzDrawSector[R,fill=#1](O,1.35mm)(90,90-#2)
            \tkzDrawSector[R,fill=#3](O,1.35mm)(90-#2,90-360)
    }
    }},
}
"""
)


class PartialCircle(pl.Template):

    def __init__(self, fill: float = 0.5, bg_color: Union[str, pl.TextColor] = 'white',
                 fg_color: Union[str, pl.TextColor] = 'black'):
        self.fill = fill
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.init_data()
        self.add_package('etoolbox')
        self.add_package('tkz-euclide')
        self.data.packages.extend([
            # pl.Raw(r'\usetkzobj{all}'),  # required in overleaf but not with newer version of tkz-euclide
            partial_circle_def
        ])
        self.contents = self._get_contents()
        super().__init__()

    def _validate_contents(self):
        if self.fill < 0 or self.fill > 1:
            raise ValueError(f'fill must be between 0 and 1, got {self.fill}')
        super()._validate_contents()

    @property
    def _circle_fill(self) -> int:
        full = 360
        return int(full * self.fill)

    def _get_contents(self) -> PyexlatexItems:
        if self.fill == 1:
            fill_def = str(self.fg_color) + '/0/'
        else:
            fill_def = (
                str(self.bg_color) +
                '/' +
                str(self._circle_fill) +
                '/' +
                str(self.fg_color)
            )

        return [
            pl.TextSize(-3),
            r'\tikz[baseline=-0.9ex]\pic{partialcircle=' + fill_def + '};',
            pl.TextSize(0),
        ]


class SkillDot(PartialCircle):

    def __init__(self, level: int, max_level: int = 5):
        fill = (level - 1) * 1 / (max_level - 1)
        super().__init__(fill)