from PyQt5 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class OrthogonalLeastSquares(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(OrthogonalLeastSquares, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Orthogonal Least Squares", 17, "\n\nUse the slide bars to\nchoose the network or\nfunction values.\n\n"
                                                          "Click [Add Neuron] to\nincrease the size of\nHidden Layer.\n\n"
                                                          "The function is shown in\nblue and the network\nresponse in red.",
                          PACKAGE_PATH + "Logo/Logo_Ch_17.svg", None)

        self.randseq = [-0.7616, -1.0287, 0.5348, -0.8102, -1.1690, 0.0419, 0.8944, 0.5460, -0.9345, 0.0754,
                        -0.7616, -1.0287, 0.5348, -0.8102, -1.1690, 0.0419, 0.8944, 0.5460, -0.9345, 0.0754]

        self.make_plot(1, (20, 100, 450, 300))
        self.make_plot(2, (20, 390, 450, 140))
        self.figure2.set_tight_layout(True)
        self.canvas2.draw()

        self.make_combobox(1, ["Yes", "No"], (self.x_chapter_usual, 420, self.w_chapter_slider, 50), self.change_auto_bias,
                           "label_f", "Auto Bias", (self.x_chapter_usual + 60, 420 - 20, 100, 50))
        self.auto_bias = True

        self.make_label("label_w1_1", "Hidden Neurons:", (35, 530, self.w_chapter_slider, 50))
        self.make_label("label_w1_2", "- Requested: 0", (45, 550, self.w_chapter_slider, 50))
        self.make_label("label_w1_3", "- Calculated: 0", (45, 570, self.w_chapter_slider, 50))
        self.S1 = 0

        self.make_slider("slider_b1_2", QtCore.Qt.Horizontal, (2, 20), QtWidgets.QSlider.TicksBelow, 1, 10,
                         (170, 560, 150, 50), self.graph, "label_b1_2", "Number of Points: 10", (180, 530, 150, 50))
        self.make_slider("slider_b", QtCore.Qt.Horizontal, (10, 1000), QtWidgets.QSlider.TicksBelow, 1, 100,
                         (320, 560, 150, 50), self.graph, "label_b", "b: 1.00", (380, 530, 150, 50))

        self.make_slider("slider_w2_2", QtCore.Qt.Horizontal, (0, 10), QtWidgets.QSlider.TicksBelow, 1, 0,
                         (20, 630, 150, 50), self.graph, "label_w2_2", "Stdev Noise: 0.0", (50, 600, 150, 50))
        self.make_slider("slider_b2", QtCore.Qt.Horizontal, (25, 100), QtWidgets.QSlider.TicksBelow, 1, 50,
                         (170, 630, 150, 50), self.graph, "label_b2", "Function Frequency: 0.50", (175, 600, 150, 50))
        self.make_slider("slider_fp", QtCore.Qt.Horizontal, (0, 360), QtWidgets.QSlider.TicksBelow, 1, 90,
                         (320, 630, 150, 50), self.graph, "label_fp", "Function Phase: 90", (340, 600, 150, 50))

        self.make_button("run_button", "Add Neuron", (self.x_chapter_button, 350, self.w_chapter_button, self.h_chapter_button), self.on_run)

        self.make_button("reset_button", "Reset", (self.x_chapter_button, 380, self.w_chapter_button, self.h_chapter_button), self.on_reset)

        self.graph(plot_red=False)

    def on_reset(self):
        self.S1 = 0
        self.label_w1_2.setText("- Requested: 0")
        self.label_w1_3.setText("- Calculated: 0")
        self.graph()

    def on_run(self):
        self.S1 += 1
        self.label_w1_2.setText("- Requested: " + str(self.S1))
        self.label_w1_3.setText("- Calculated: " + str(self.S1 - 1))
        self.graph()

    def graph(self, plot_red=True):

        axis = self.figure.add_subplot(1, 1, 1)
        axis.clear()  # Clear the plot
        axis.set_xlim(-2, 2)
        axis.set_ylim(-2, 4)
        # a.set_xticks([0], minor=True)
        # a.set_yticks([0], minor=True)
        # a.set_xticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.set_yticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.grid(which="minor")
        axis.set_xticks([-2, -1, 0, 1])
        axis.set_yticks([-2, -1, 0, 1, 2, 3])
        axis.plot(np.linspace(-2, 2, 10), [0]*10, color="black", linestyle="--", linewidth=0.2)
        axis.set_title("Function Approximation")
        axis.set_xlabel("$p$")
        axis.xaxis.set_label_coords(1, -0.025)
        axis.set_ylabel("$a^2$")
        axis.yaxis.set_label_coords(-0.025, 1)

        axis2 = self.figure2.add_subplot(1, 1, 1)
        axis2.clear()  # Clear the plot
        axis2.set_xlim(-2, 2)
        axis2.set_ylim(0, 1)
        # a.set_xticks([0], minor=True)
        # a.set_yticks([0], minor=True)
        # a.set_xticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.set_yticks([-2, -1.5, -1, -0.5, 0.5, 1, 1.5])
        # a.grid(which="minor")
        axis2.set_xticks([-2, -1, 0, 1])
        axis2.set_yticks([0, 0.5])
        axis2.set_xlabel("$p$")
        axis2.xaxis.set_label_coords(1, -0.025)
        axis2.set_ylabel("$a^1$")
        axis2.yaxis.set_label_coords(-0.025, 1)

        # ax.set_xticks(major_ticks)
        # ax.set_xticks(minor_ticks, minor=True)
        # ax.set_yticks(major_ticks)
        # ax.set_yticks(minor_ticks, minor=True)
        #
        # # And a corresponding grid
        # ax.grid(which='both')
        #
        # # Or if you want different settings for the grids:
        # ax.grid(which='minor', alpha=0.2)
        # ax.grid(which='major', alpha=0.5)

        if self.auto_bias:
            bias = 1
            self.slider_b.setValue(bias * 100)
            self.label_b.setText("b: 1.00")
        bias = self.get_slider_value_and_update(self.slider_b, self.label_b, 1 / 100, 2)
        n_points = self.get_slider_value_and_update(self.slider_b1_2, self.label_b1_2)
        # n_points = self.slider_b1_2.value()
        sigma = self.get_slider_value_and_update(self.slider_w2_2, self.label_w2_2, 1 / 10, 2)
        freq = self.get_slider_value_and_update(self.slider_b2, self.label_b2, 1 / 100, 2)
        phase = self.get_slider_value_and_update(self.slider_fp, self.label_fp)

        d1 = (2 - -2) / (n_points - 1)
        p = np.arange(-2, 2 + 0.0001, d1)
        t = np.sin(2 * np.pi * (freq * p + phase / 360)) + 1 + sigma * np.array(self.randseq[:len(p)])
        c = np.copy(p)
        # delta = (2 - -2) / (S1 - 1)
        if self.auto_bias:
            bias = np.ones(p.shape)
            # self.slider_b.setValue(bias * 100)
            # self.label_b.setText("b: " + str(bias))
        else:
            bias = np.ones(p.shape) * bias
        n = self.S1
        W1, b1, W2, b2, mf, of, indf = self.rb_ols(p, t, c, bias, n)

        if type(W1) == np.float64:
            S1 = 1
        else:
            S1 = len(W1)
        total = 2 - -2
        Q = len(p)
        pp = np.repeat(p.reshape(1, -1), S1, 0)
        if S1 == 0:
            n1, a1 = 0, 0
            n2 = np.dot(b2, np.ones((1, Q)))
        else:
            n1 = np.abs(pp - np.dot(W1, np.ones((1, Q)))) * np.dot(b1, np.ones((1, Q)))
            a1 = np.exp(-n1 ** 2)
            a2 = np.dot(W2, a1) + b2

        p2 = np.arange(-2, 2 + total / 1000, total / 1000)
        Q2 = len(p2)
        if S1 == 0:
            a12 = 0
            a22 = np.dot(b2, np.ones((1, Q2)))
        else:
            pp2 = np.repeat(p2.reshape(1, -1), S1, 0)
            n12 = np.abs(pp2 - np.dot(W1, np.ones((1, Q2)))) * np.dot(b1, np.ones((1, Q2)))
            a12 = np.exp(-n12 ** 2)
            a22 = np.dot(W2, a12) + b2
        t_exact = np.sin(2 * np.pi * (freq * p2 + phase / 360)) + 1
        if S1 == 0:
            temp = b2 * np.ones((1, Q2))
        else:
            temp = np.vstack((np.dot(W2.T, np.ones((1, Q2))) * a12, b2 * np.ones((1, Q2))))

        axis.scatter(p, t, color="white", edgecolor="black")
        for i in range(len(temp)):
            axis.plot(p2, temp[i], linestyle="--", color="black", linewidth=0.5)
        axis.plot(p2, t_exact, color="blue", linewidth=2)
        if plot_red:
            axis.plot(p2, a22.reshape(-1), color="red", linewidth=1)
        if S1 == 0:
            axis2.plot(p2, [a12] * len(p2), color="black")
        else:
            for i in range(len(a12)):
                axis2.plot(p2, a12[i], color="black")

        self.canvas.draw()
        self.canvas2.draw()

    def change_auto_bias(self, idx):
        self.auto_bias = idx == 0
        self.graph()

    @staticmethod
    def rb_ols(p, t, c, b, n):

        p = p.reshape(-1, 1)
        c = c.reshape(-1, 1)
        b = b.reshape(-1, 1)
        t = t.reshape(-1, 1)
        q = len(p)
        nc = len(c)
        o = np.zeros((nc + 1, 1))
        h = np.zeros((nc + 1, 1))
        rr = np.eye(nc + 1)
        indexT = list(range(nc + 1))
        if n > nc + 1:
            n = nc + 1
        bindex = []
        sst = np.dot(t.T, t).item()

        temp = np.dot(p.reshape(-1, 1), np.ones((1, nc))) - np.dot(np.ones((q, 1)), c.T.reshape(1, -1))
        btot = np.dot(np.ones((q, 1)), b.T.reshape(1, -1))
        uo = np.exp(-(temp * btot) ** 2)
        uo = np.hstack((uo, np.ones((q, 1))))
        u = uo
        m = u

        for i in range(nc + 1):
            ssm = np.dot(m[:, i].T, m[:, i])
            h[i] = np.dot(m[:, i].T, t) / ssm
            o[i] = h[i] ** 2 * ssm / sst
        o1, ind1 = np.max(o), np.argmax(o)
        of = o1
        hf = [h[ind1]]

        mf = m[:, ind1].reshape(-1, 1)
        ssmf = np.dot(mf.T, mf)
        u = np.delete(u, ind1, 1)
        if indexT[ind1] == nc:
            bindex = 1
            indf = []
        else:
            indf = indexT[ind1]
        indexT.pop(ind1)
        m = np.copy(u)

        for k in range(2, n + 1):
            o = np.zeros((nc + 2 - k, 1))
            h = np.zeros((nc + 2 - k, 1))
            r = np.zeros((q - k + 1, k, k))
            for i in range(q - k + 1):
                for j in range(k - 1):
                    if type(ssmf) == np.float64:
                        r[i, j, k - 1] = np.dot(mf, u[:, i]) / ssmf
                        m[:, i] = m[:, i] - r[i, j, k - 1] * mf[j]
                    else:
                        r[i, j, k - 1] = np.dot(mf[:, j].reshape(1, -1), u[:, i][..., None]) / ssmf[0, j]
                        m[:, i] = m[:, i] - r[i, j, k - 1] * mf[:, j]
                ssm = m[:, i].T.dot(m[:, i])
                h[i] = m[:, i].T.dot(t) / ssm
                o[i] = h[i] ** 2 * ssm / sst
            o1, ind1 = np.max(o), np.argmax(o)
            mf = np.hstack((mf, m[:, ind1].reshape(-1, 1)))
            if type(ssmf) == np.float64:
                ssmf = m[:, ind1].T.dot(m[:, ind1])
            else:
                try:
                    ssmf = np.vstack((ssmf.T, m[:, ind1].T.dot(m[:, ind1]))).T
                except:
                    print("!")
            of = np.hstack((of, o1))
            u = np.delete(u, ind1, 1)
            hf.append(h[ind1].item())
            for j in range(k - 1):
                rr[j, k - 1] = r[ind1, j, k - 1]
            if indexT[ind1] == nc + 1:
                bindex = k - 1
            else:
                indf = np.hstack((indf, indexT[ind1]))
            indexT.pop(ind1)
            m = np.copy(u)

        nn = len(hf)
        xx = np.zeros((nn, 1))
        xx[nn - 1] = hf[nn - 1]
        for i in list(range(nn - 1))[::-1]:
            xx[i] = hf[i]
            for j in list(range(i + 1, nn))[::-1]:
                xx[i] = xx[i] - rr[i, j] * xx[j]

        if len(indf) != 0:
            w1 = c[indf.astype(np.int)]
            b1 = b[indf.astype(np.int)]
        else:
            w1, b1 = [], []
        if bindex:
            if xx[:bindex - 1]:
                w2 = np.hstack((xx[:bindex - 1], xx[bindex: nn])).T
            else:
                w2 = xx[bindex: nn].T
            b2 = xx[0, bindex - 1]
            # indf = int(np.hstack((np.hstack((indf[:bindex - 1], nc + 1)), indf[bindex:])).item()) - 1
            # if indf:
            #     uu = uo[:, np.int(np.array(indf)) - 1]
            # else:
            #     uu = uo[:, []]
        else:
            b2 = 0
            w2 = xx.T
            # uu = uo[:, np.int(indf)]
        return w1, b1, w2, b2, mf, of, indf
