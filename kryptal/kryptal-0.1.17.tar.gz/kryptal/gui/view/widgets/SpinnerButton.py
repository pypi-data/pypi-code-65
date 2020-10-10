from PyQt5.QtWidgets import QWidget, QPushButton  #type: ignore
from PyQt5.QtGui import QIcon, QMovie  #type: ignore
from PyQt5.QtCore import QByteArray  #type: ignore
from kryptal.gui.view.icons import Icons
from typing import Optional
from typing_extensions import Final, final


@final
class SpinnerButtonLoadError(Exception):
    def __init__(self, reason: int):
        self._reason: Final = reason

    def message(self) -> str:
        return "Loading spinner button failed: %d" % self._reason


@final
class SpinnerButton(QPushButton):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.spinnerAnimation: Final = QMovie(Icons.get_path("spinner.gif"), QByteArray(), self)
        self.spinnerAnimation.frameChanged.connect(self._onSetCurrentFrame)
        self.spinnerAnimation.error.connect(self._onSpinnerError)
        self.spinnerAnimation.setCacheMode(QMovie.CacheAll)
        # if animation doesn't loop forever, force it to.
        if (self.spinnerAnimation.loopCount() != -1):
          self.spinnerAnimation.finished.connect(self.spinnerAnimation.start)

        # Test movie loaded correctly (QMovie only loads the file when the animation is started)
        self.error = None  #type: Optional[int]
        self.spinnerAnimation.start()
        self.spinnerAnimation.stop()
        self.setIcon(QIcon())
        if (self.error is not None):
            raise SpinnerButtonLoadError(self.error)

    def startSpinner(self) -> None:
        self.setEnabled(False)
        self.spinnerAnimation.start()

    def _onSetCurrentFrame(self, frame: int) -> None:
        self.setIcon(QIcon(self.spinnerAnimation.currentPixmap()))

    def _onSpinnerError(self, error: int) -> None:
        self.error = error

    def stopSpinner(self) -> None:
        self.spinnerAnimation.stop()
        self.setIcon(QIcon())
        self.setEnabled(True)
