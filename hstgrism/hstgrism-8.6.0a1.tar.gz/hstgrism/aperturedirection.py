import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ApertureDirection:
    """
    ApertureDirection computes a one unit vector from (trace.xh,trace.yh) towards the direction specified by phi_degree.
    ##########
    Inputs:
     - trace_csv = trace.csv produced by HSTGRISM. Require: trace.dydx, trace.xh, and trace.yh
     - phi_degree = angle in degrees w.r.t. tangent line at (trace.xh,trace.yh). Tangent line is computed from trace.dydx.
    Compute:
     - Use self.compute() after properly instantiate.
    Outputs:
     - self.dx, self.dy = arrays of x and y pixels from (0,0) center towards the direction
    Demo:
     - To see demo, instantiate t = ApertureDirection(None,None). Then, t.demo(phi_degree,radius). This will print console messages and a plot.
     - Change phi_degree and radius to see a plot of different phi_degree and radius.
     - Messages provide the code template.
    """
    def __init__(self,trace_csv,phi_degree):
        self.trace_csv = trace_csv
        self.phi_degree = phi_degree
    def compute(self):
        trace = pd.read_csv(self.trace_csv)
        self.trace_poly1d = np.poly1d(trace.dydx.values[np.argwhere(np.isfinite(trace.dydx.values)).flatten()][-1::-1])
        self.trace_poly1d_deriv = self.trace_poly1d.deriv()
        self.theta_radian = self.trace_poly1d_deriv(trace.xh.values)
        self.alpha_radian = self.theta_radian + np.radians(self.phi_degree)
        self.dx = np.cos(self.alpha_radian)
        self.dy = np.sin(self.alpha_radian)
    def demo(self,phi_degree=90.,radius=1.):
        X = np.arange(-3,3);print('X = np.arange(-3,3)')
        poly1d_coef = [1.,0.,0.];print('poly1d_coef = [1.,0.,0.]')
        L1 = np.poly1d(poly1d_coef);print('L1 = np.poly1d(poly1d_coef)')
        Y = L1(X);print('Y = L1(X)')
        L1_deriv = L1.deriv();print('L1_derive = L1.deriv()')
        theta_x = np.arctan(L1_deriv(X));print('theta_x = np.arctan(L1_deriv(X))')
        dx = np.cos(np.radians(phi_degree) + theta_x);print('dx = np.cos(np.radians(angle_degree) + theta_x)')
        dy = np.sin(np.radians(phi_degree) + theta_x);print('dy = np.sin(np.radians(angle_degree) + theta_x)')
        plt.figure()
        plt.plot(X,Y)
        for ii,i in enumerate(X):
            tx = X[ii] + radius * np.array([dx[ii],-dx[ii]])
            ty = Y[ii] + radius * np.array([dy[ii],-dy[ii]])
            tl = plt.plot(X[ii],Y[ii],'x')
            tc = tl[0].get_color()
            tp = plt.plot(tx,ty,color=tc,ls=':')
        plt.axis('equal')
        plt.plot(X,Y)      
    