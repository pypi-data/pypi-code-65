from scipy.linalg import orth
from scipy.optimize import approx_fprime
import numpy as np


class HiOSD(object):
    def __init__(self, func, seed):
        self.func = func
        self.seed = seed

    def fit(self, k, x0=None, eps_f=1e-4, *args):
        random_state = np.random.RandomState(self.seed)
        n = x0.size
        randP = random_state.normal(size=(n, k))
        P = orth(randP).T
        epsilon = np.ones_like(x0, shape=(n, 1))*1e-8
        fn = -approx_fprime(x0, self.func, epsilon, *args)
        n = 0
        xn = x0
        while(np.linalg.norm(fn) >= eps_f):
            gn = fn
            for i in range(0, k):
                gn -= 2*(np.dot(P[i], fn))*P[i]
            xnp1 = xn + beta * gn
            for i in range(0, k):
                fprime1 = approx_fprime(xnp1+l*P[i], self.func, epsilon, *args)
                fprime2 = approx_fprime(xnp1-l*P[i], self.func, epsilon, *args)
                ui = (fprime1 - fprime2)/(2*l)
                di = -ui+np.dot(P[i], ui)*P[i]
                for j in range(0, i-1):
                    di += 2*np.dot(P[j], ui)*p[j]
                vi_new = P[i] + gamma * di
                # gram-schmidt
                for j in range(0, i-1):
                    vi_new -= np.dot(P[j], vi_new)*P[j]
                    P[i] = vi_new/np.linalg.norm(vi_new)
            l = max(l/(1+beta), eps)
            xn = xnp1
            fn = -approx_fprime(xn, self.func, epsilon, *args)
            n += 1
