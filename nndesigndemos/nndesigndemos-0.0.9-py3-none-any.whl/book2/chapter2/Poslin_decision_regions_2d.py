from PyQt5 import QtWidgets
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
import ast

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class PoslinDecisionRegions2D(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(PoslinDecisionRegions2D, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Poslin Decision Regions 2D", 2, "\nAlter the network's\nparameters by clicking\nthe "
                                                           "buttons and\nmodifying the input text.\n\n"
                                                           "Choose the output transfer\nfunction f below.",
                          PACKAGE_PATH + "Chapters/2_D/Logo_Ch_2.svg", PACKAGE_PATH + "Figures/poslinNet2Ddemo.svg",
                          icon_move_left=120, description_coords=(535, 100, 450, 200))

        self.make_plot(1, (85, 300, 370, 370))

        self.make_label("label_w1", "W1: [[1, 1], [-1, -1],\n         [-1, 1], [1, -1]]", (self.x_chapter_button + 20, 320 + 30, 150, 50))
        self.make_button("button_w1", "Change W1", (self.x_chapter_button, 365 + 30, self.w_chapter_button, self.h_chapter_button), self.change_w1)
        self.w1 = np.array([[1, 1], [-1, - 1], [-1, 1], [1, - 1]])

        self.make_label("label_w2", "W2: [[-1], [-1], [-1], [-1]]", (self.x_chapter_button + 15, 390 + 30, 150, 50))
        self.make_button("button_w2", "Change W2", (self.x_chapter_button, 425 + 30, self.w_chapter_button, self.h_chapter_button), self.change_w2)
        self.w2 = np.array([[-1], [-1], [-1], [-1]])

        self.make_label("label_b1", "b1: [[-1], [3], [1], [1]]", (self.x_chapter_button + 25, 450 + 30, 150, 50))
        self.make_button("button_b1", "Change b1", (self.x_chapter_button, 485 + 30, self.w_chapter_button, self.h_chapter_button), self.change_b1)
        self.b1 = np.array([[-1], [3], [1], [1]])

        self.make_label("label_b2", "b2: [5]", (self.x_chapter_button + 60, 510 + 30, 100, 50))
        self.make_button("button_b2", "Change b2", (self.x_chapter_button, 545 + 30, self.w_chapter_button, self.h_chapter_button), self.change_b2)
        self.b2 = np.array([5])

        self.combobox_funcs = [self.poslin, self.hardlim, self.hardlims, self.purelin, self.satlin, self.satlins, self.logsig, self.tansig]
        self.combobox_funcs_str = ["poslin", "hardlim", "hardlims", "purelin", "satlin", "satlins", "logsig", "tansig"]
        self.make_combobox(1, self.combobox_funcs_str, (self.x_chapter_usual, 290, self.w_chapter_slider, 50), self.change_transfer_f, "label_f", "f")
        self.func1 = self.poslin

        self.graph()

    def change_transfer_f(self, idx):
        self.func1 = self.combobox_funcs[idx]
        self.graph()

    def change_w1(self):
        weight1, ok = QtWidgets.QInputDialog.getText(self, 'Change Weight', 'Change W1:', QtWidgets.QLineEdit.Normal, str(self.w1.tolist()))
        if ok:
            try:
                w1 = ast.literal_eval(weight1)
            except:
                print("Please enter value in the following format: [[a11,a12], [a21,a22]]")
                return
            self.w1 = np.array(w1)
            str_w1 = str(self.w1.tolist())
            splits = str_w1.split("],")
            str_w1 = splits[0] + "]," + splits[1] + "],\n        " + splits[2] + "]," + splits[3]
            self.label_w1.setText("W1: " + str_w1)
            self.graph()

    def change_w2(self):
        weight2, ok = QtWidgets.QInputDialog.getText(self, 'Change Weight', 'Change W2:', QtWidgets.QLineEdit.Normal, str(self.w2.tolist()))
        if ok:
            try:
                w2 = ast.literal_eval(weight2)
            except:
                print("Please enter value in the following format: [[a11,a12], [a21,a22]]")
                return
            self.label_w2.setText("W2: " + str(w2))
            self.w2 = np.array(w2)
            self.graph()

    def change_b1(self):
        bias1, ok = QtWidgets.QInputDialog.getText(self, 'Change Bias', 'Change b1:', QtWidgets.QLineEdit.Normal, str(self.b1.tolist()))
        if ok:
            try:
                b1 = ast.literal_eval(bias1)
            except:
                print("Please enter value in the following format: [[a11,a12], [a21,a22]]")
                return
            self.label_b1.setText("b1: " + str(b1))
            self.b1 = np.array(b1)
            self.graph()

    def change_b2(self):
        bias2, ok = QtWidgets.QInputDialog.getText(self, 'Change Bias', 'Change b2:', QtWidgets.QLineEdit.Normal, str(self.b2.tolist()))
        if ok:
            try:
                b2 = ast.literal_eval(bias2)
            except:
                print("Please enter value in the following format: [[a11,a12], [a21,a22]]")
                return
            self.label_b2.setText("b2: " + str(b2))
            self.b2 = np.array(b2)
            self.graph()

    def graph(self):

        a = self.figure.add_subplot(111)
        a.clear()
        a.grid(True, which='both')

        p1 = np.linspace(-1, 3, 41)
        p2 = np.linspace(-1, 3, 41)
        P1, P2 = np.meshgrid(p1, p2)
        n1, n2 = P1.shape
        nump = n1 * n2
        pp1 = np.reshape(P1, nump, order='F')
        pp2 = np.reshape(P2, nump, order='F')
        p = np.concatenate((pp1.reshape(-1, 1).T, pp2.reshape(-1, 1).T), axis=0)
        func = np.vectorize(self.func1, otypes=[np.float])

        a1 = np.dot(self.w2.T, func(np.dot(self.w1, p) + np.dot(self.b1, np.ones((1, nump))))) + np.dot(self.b2, np.ones( (1, nump)))
        aa = np.reshape(a1, (n1, n2), order='F')

        a.contourf(P1, P2, aa, [0, 1000])

        a.grid(True, which='both')
        a.axhline(y=0, color='k')
        a.axvline(x=0, color='k')
        self.canvas.draw()
