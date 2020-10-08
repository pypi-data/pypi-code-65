"""
It is worth mentioning that the pySEED-algorithm was designed to deal with maximization problems.
For minimization problems, the functions must be transformed into a maximization case.

To do this we simply apply the next operation: return 1E8 - value_of_the_function
"""

import numpy as np


class Sphere:
    def evaluate(self, x):
        sphere = np.sum(x ** 2)
        return 1E8 - sphere


class Rosenbrock:
    def evaluate(self, x):
        rosenbrock = 0
        for i in range(0, len(x) - 1):
            rosenbrock += (100 * (x[i + 1] - x[i]**2)**2 + (x[i] - 1)**2)
        return 1E8 - rosenbrock


class Rastrigin:
    def evaluate(self, x):
        rastrigin = 10 * len(x) + np.sum(x**2 - 10 * np.cos(2*np.pi*x))
        return 1E8 - rastrigin


class Ackley:
    def evaluate(self, x):
        ackley = -20 * np.exp(-0.2 * np.sqrt((1 / len(x)) * np.sum(x**2))) - \
                 np.exp((1 / len(x)) * np.sum(np.cos(2 * np.pi * x))) + 20 + np.e
        return 1E8 - ackley


class Griewangk:
    def evaluate(self, x):
        prod = 1
        for i in range(0, len(x)): prod *= np.cos(x[i] / np.sqrt(i + 1))
        griewangk = (1/4000) * np.sum(x**2) + - prod + 1
        return 1E8 - griewangk