import logging

from aio_wx_widgets.core.sizers import AlignHorizontal, VertAlign
from aio_wx_widgets.containers.grid import Grid
from aio_wx_widgets.widgets.text import Text

_LOGGER = logging.getLogger(__name__)

__all__ = ["LabelledItem"]


class LabelledItem(Grid):
    def __init__(self, label_text: str, item, align_right=True):
        super().__init__()
        self.label_text = label_text
        self._item = item
        self.align_right = align_right

    def __call__(self, parent, *args, **kwargs):
        super().__call__(parent)
        if self.align_right:
            hor_alignment = AlignHorizontal.right
        else:
            hor_alignment = None
        self.add(
            Text(self.label_text),
            weight=1,
            align_horizontal=hor_alignment,
            ver_align=VertAlign.center,
        )
        self.add(self._item, weight=1)

        return self
