from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from time import sleep

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class PerceptronClassification(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(PerceptronClassification, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Perceptron Classification", 3, "Click [Go] to send a fruit\ndown the belt to be\nclassified"
                          " by a perceptron\nnetwork.\n\nThe calculations for the\nperceptron will appear\nbelow.",
                          PACKAGE_PATH + "Logo/Logo_Ch_3.svg", None)

        if self.play_sound:
            self.start_sound1 = QtMultimedia.QSound(PACKAGE_PATH + "Sound/blip.wav")
            self.start_sound2 = QtMultimedia.QSound(PACKAGE_PATH + "Sound/bloop.wav")
            self.wind_sound = QtMultimedia.QSound(PACKAGE_PATH + "Sound/wind.wav")
            self.knock_sound = QtMultimedia.QSound(PACKAGE_PATH + "Sound/knock.wav")
            self.scan_sound = QtMultimedia.QSound(PACKAGE_PATH + "Sound/buzz.wav")
            self.classify_sound = QtMultimedia.QSound(PACKAGE_PATH + "Sound/classify.wav")

        self.make_plot(1, (15, 100, 500, 390))
        self.axis = Axes3D(self.figure)
        ys = np.linspace(-1, 1, 100)
        zs = np.linspace(-1, 1, 100)
        Y, Z = np.meshgrid(ys, zs)
        X = 0
        apple = np.array([-1, 1, -1])
        orange = np.array([1, 1, -1])
        self.axis.set_title("Input Space")
        self.axis.plot_surface(X, Y, Z, alpha=0.5)
        self.axis.set_xlabel("texture")
        self.axis.set_xticks([-1, 1])
        self.axis.set_ylabel("shape")
        self.axis.set_yticks([-1, 1])
        self.axis.set_zlabel("weight")
        self.axis.zaxis._axinfo['label']['space_factor'] = 0.1
        self.axis.set_zticks([-1, 1])
        self.axis.scatter(orange[0], orange[1], orange[2], color='green')
        self.axis.scatter(apple[0], apple[1], apple[2], color='orange')
        self.line1, self.line2, self.line3 = None, None, None
        self.axis.view_init(10, 110)
        self.canvas.draw()

        self.p, self.a, self.label = None, None, None

        self.make_label("label_w", "w = [1 0 0]", (550, 310, 150, 25))
        self.make_label("label_b", "b = 0", (550, 340, 150, 25))
        self.make_label("label_p", "", (550, 370, 150, 25))
        self.make_label("label_a_1", "", (550, 400, 150, 25))
        self.make_label("label_a_2", "", (550, 430, 150, 25))
        self.make_label("label_a_3", "", (550, 460, 150, 25))
        self.make_label("label_fruit", "", (550, 490, 150, 25))

        if self.dpi > 113.5:
            self.figure_w, self.figure_h = 575 / (self.dpi / 113.5), 190 / (self.dpi / 113.5)
        else:
            self.figure_w, self.figure_h = 575, 190
        self.icon3 = QtWidgets.QLabel(self)
        if self.running_on_windows:
            if self.dpi > 113.5:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.h_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
                self.icon3.setGeometry(28 * self.h_ratio * (self.dpi / 113.5), 485 * self.h_ratio, self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.h_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
                self.icon3.setGeometry(28 * self.h_ratio, 485 * self.h_ratio, self.figure_w * self.h_ratio, self.figure_h * self.h_ratio)
        else:
            if self.dpi > 113.5:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio / (self.dpi / 113.5), self.figure_h * self.h_ratio / (self.dpi / 113.5), QtGui.QIcon.Normal, QtGui.QIcon.On))
                self.icon3.setGeometry(28 * self.w_ratio * (self.dpi / 113.5), 485 * self.h_ratio, self.figure_w * self.w_ratio / (self.dpi / 113.5), self.figure_h * self.h_ratio / (self.dpi / 113.5))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
                self.icon3.setGeometry(28 * self.w_ratio, 485 * self.h_ratio, self.figure_w * self.w_ratio, self.figure_h * self.h_ratio)
        self.text_shape, self.text_texture, self.text_weight = "?", "?", "?"

        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
        self.make_button("run_button", "Go", (self.x_chapter_button, 525, self.w_chapter_button, self.h_chapter_button), self.on_run)

    def paintEvent(self, event):
        super(PerceptronClassification, self).paintEvent(event)
        painter = QtGui.QPainter(self.icon3.pixmap())
        if self.running_on_windows:
            w_ratio, h_ratio = self.h_ratio, self.h_ratio
        else:
            w_ratio, h_ratio = self.w_ratio, self.h_ratio
        if self.dpi > 113.5:
            w_ratio /= (self.dpi / 113.5)
            h_ratio /= (self.dpi / 113.5)
        painter.setFont(QtGui.QFont("times", 12 * (w_ratio + h_ratio) / 2))
        painter.drawText(QtCore.QPoint(100 * w_ratio, 28 * h_ratio), self.text_shape)
        painter.drawText(QtCore.QPoint(245 * w_ratio, 28 * h_ratio), self.text_texture)
        painter.drawText(QtCore.QPoint(410 * w_ratio, 28 * h_ratio), self.text_weight)

    def on_run(self):
        self.timer = QtCore.QTimer()
        self.idx = 0
        self.text_shape, self.text_texture, self.text_weight = "?", "?", "?"
        self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_1.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
        self.label_p.setText(""); self.label_a_1.setText(""); self.label_a_2.setText(""); self.label_a_3.setText(""); self.label_fruit.setText("")
        self.p = np.round(np.random.uniform(-1, 1, (1, 3)), 2)
        self.a = 1 * self.p[0, 0] + 0 * self.p[0, 1] + 0 * self.p[0, 2]
        self.label = 1 if self.a >= 0 else -1
        if self.line1:
            self.line1.pop().remove()
            self.line2.pop().remove()
            self.line3.pop().remove()
            self.canvas.draw()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1000)

    def update_label(self):
        if self.idx == 0:
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        if self.idx == 1:
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        if self.idx == 2:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_2.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_7.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 3:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
        elif self.idx == 4:
            self.text_shape, self.text_texture, self.text_weight = str(self.p[0, 0]), str(self.p[0, 1]), str(self.p[0, 2])
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_3.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_8.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            self.canvas.draw()
            if self.play_sound:
                self.scan_sound.play()
        elif self.idx == 5:
            self.line1 = self.axis.plot3D([self.p[0, 0]] * 10, np.linspace(-1, 1, 10), [self.p[0, 2]] * 10, color="g")
            self.line2 = self.axis.plot3D([self.p[0, 0]] * 10, [self.p[0, 1]] * 10, np.linspace(-1, 1, 10), color="g")
            self.line3 = self.axis.plot3D(np.linspace(-1, 1, 10), [self.p[0, 1]] * 10, [self.p[0, 2]] * 10, color="g")
            self.canvas.draw()
            if self.play_sound:
                self.classify_sound.play()
        elif self.idx == 6:
            self.label_p.setText("p = [{} {} {}]".format(self.p[0, 0], self.p[0, 1], self.p[0, 2]))
        elif self.idx == 7:
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_4.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_9.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            self.label_a_1.setText("a = hardlims(W * p + b)")
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 8:
            self.label_a_2.setText("a = hardlims({})".format(self.a))
            if self.play_sound:
                self.start_sound1.play()
                sleep(0.5)
                self.start_sound2.play()
        elif self.idx == 9:
            self.label_a_3.setText("a = " + str(self.label))
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_5.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_10.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            if self.play_sound:
                self.wind_sound.play()
        elif self.idx == 10:
            self.label_fruit.setText("Fruit = {}".format("Apple" if self.label == 1 else "Orange"))
            if self.label == 1:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_6.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            else:
                self.icon3.setPixmap(QtGui.QIcon(PACKAGE_PATH + "Figures/nnd3d1_11.svg").pixmap(self.figure_w * self.w_ratio, self.figure_h * self.h_ratio, QtGui.QIcon.Normal, QtGui.QIcon.On))
            if self.play_sound:
                self.knock_sound.play()
                sleep(0.5)
                self.knock_sound.play()
        else:
            pass
        self.idx += 1
