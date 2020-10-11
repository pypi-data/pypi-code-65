from PyQt5.QtCore import Qt, QRect  # type: ignore
from PyQt5.QtTest import QTest  # type: ignore
from PyQt5.QtGui import QIcon, QImage, QPainter  # type: ignore
from kryptal.gui import Application
from kryptal.gui.view.widgets.SpinnerButton import SpinnerButton
import os
import tempfile
from kryptal.testutils.ApplicationHelpers import with_app
import unittest


class test_SpinnerButton(unittest.TestCase):
    @with_app
    def test_init_without_error(self) -> None:
        SpinnerButton(None)

    @with_app
    def test_init_without_icon(self) -> None:
        btn = SpinnerButton(None)
        self.assertTrue(btn.icon().isNull())

    @with_app
    def test_shows_icon_while_running(self) -> None:
        btn = SpinnerButton(None)
        self.assertTrue(btn.icon().isNull())
        btn.startSpinner()
        self.assertFalse(btn.icon().isNull())
        btn.stopSpinner()
        self.assertTrue(btn.icon().isNull())

        # try a second round
        btn.startSpinner()
        self.assertFalse(btn.icon().isNull())
        btn.stopSpinner()
        self.assertTrue(btn.icon().isNull())

    @with_app
    def test_is_disabled_while_running(self) -> None:
        btn = SpinnerButton(None)
        self.assertTrue(btn.isEnabled())
        btn.startSpinner()
        self.assertFalse(btn.isEnabled())
        btn.stopSpinner()
        self.assertTrue(btn.isEnabled())

        # try a second round
        btn.startSpinner()
        self.assertFalse(btn.isEnabled())
        btn.stopSpinner()
        self.assertTrue(btn.isEnabled())

    def _saveIcon(self, icon: QIcon, filename: str) -> None:
        img = QImage(800, 600, QImage.Format_RGB32)
        painter = QPainter()
        painter.begin(img)
        painter.fillRect(0, 0, 800, 600, Qt.cyan)
        icon.paint(painter, QRect(0, 0, 800, 600))
        painter.end()
        img.save(filename)

    def _files_equal(self, file1: str, file2: str) -> bool:
        with open(file1, 'rb') as loaded1, open(file2, 'rb') as loaded2:
            res: bool = loaded1.read() == loaded2.read()
            return res

    def _wait_for_frame_change(self, btn: SpinnerButton, msec: int) -> bool:
        with tempfile.TemporaryDirectory() as tmpdir:
            startFrameFile = os.path.join(tmpdir, "startFrame.bmp")
            currentFrameFile = os.path.join(tmpdir, "currentFrame.bmp")
            self._saveIcon(btn.icon(), startFrameFile)
            self._saveIcon(btn.icon(), currentFrameFile)
            # Without events running, the frame should not have changed (otherwise this test doesn't make sense)
            self.assertTrue(self._files_equal(startFrameFile, startFrameFile))

            iteration_count = 0
            while (self._files_equal(startFrameFile, currentFrameFile)):
                QTest.qWait(1)
                self._saveIcon(btn.icon(), currentFrameFile)
                iteration_count = iteration_count + 1
                if (iteration_count > msec):
                    # Didn't switch the frame in >msec time. Seems there is no animation running.
                    return False

            # We should only get here if the frame changed
            self.assertFalse(self._files_equal(
                startFrameFile, currentFrameFile))
            return True

    @with_app
    def test_changes_frames_while_running(self) -> None:
        btn = SpinnerButton(None)
        frame_was_changed = self._wait_for_frame_change(
            btn, 100)  # Wait 100msec for a frame change
        self.assertFalse(frame_was_changed)

        btn.startSpinner()
        frame_was_changed = self._wait_for_frame_change(
            btn, 100)  # Wait 100msec for a frame change
        self.assertTrue(frame_was_changed)

        btn.stopSpinner()
        frame_was_changed = self._wait_for_frame_change(
            btn, 100)  # Wait 100msec for a frame change
        self.assertFalse(frame_was_changed)
