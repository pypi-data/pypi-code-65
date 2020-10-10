from PyQt5.QtWidgets import QWidget, QLabel  #type: ignore
from PyQt5.QtGui import QIcon, QMovie  #type: ignore
from PyQt5.QtCore import QByteArray  #type: ignore
from kryptal.gui.view.icons import Icons
from typing import Optional
from typing_extensions import Final, final


@final
class SpinnerLabelLoadError(Exception):
    def __init__(self, reason: int):
        self._reason: Final = reason

    def message(self) -> str:
        return "Loading spinner label failed: %d" % self._reason


@final
class SpinnerLabel(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.spinnerAnimation: Final = QMovie(Icons.get_path("spinner.gif"), QByteArray(), self)
        self.spinnerAnimation.error.connect(self._onSpinnerError)
        self.spinnerAnimation.setCacheMode(QMovie.CacheAll)
        # if animation doesn't loop forever, force it to.
        if (self.spinnerAnimation.loopCount() != -1):
          self.spinnerAnimation.finished.connect(self.spinnerAnimation.start)

        # Test movie loaded correctly (QMovie only loads the file when the animation is started)
        self.error = None  #type: Optional[int]
        self.spinnerAnimation.start()
        self.spinnerAnimation.stop()
        self.clear()
        if (self.error is not None):
            raise SpinnerLabelLoadError(self.error)

    def start(self) -> None:
        self.setMovie(self.spinnerAnimation)
        self.spinnerAnimation.start()

    def _onSpinnerError(self, error: int) -> None:
        self.error = error

    def stop(self) -> None:
        self.clear()
        self.spinnerAnimation.stop()
