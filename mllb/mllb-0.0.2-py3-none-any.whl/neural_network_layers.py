import numpy as np
from .layer_creation import *


class layers_class:
    
    """
    Layers class.

    Args:
        weights: (dict) weights dictionary with each value holding the weights for
                 each layer.

        A: (dict) activated outputs for each layer

        L: (int) number of layers

        acts: (dict) activation functions for each layer

        __X_dimx: (int) number of features in the traning example plus one

        __Y_dimx: (int) number of output values in the final layer
    
    """

    def __init__(self, X_dimx, Y_dimx):
        self.weights = {}
        self.A = {"1":np.zeros((X_dimx, 1))}
        self.L = 1

        self.acts = {"1":"none"}

        self.__X_dimx = X_dimx
        self.__Y_dimx = Y_dimx

    def create(self, *ly):

        """
        Create a layers for the network.

        Args:
            ly: (*functions [tuple]) this should be the activation functions contaning
                the number of nodes for each layer.

        Return:
            --

        """

        for l in range(len(ly)):
            if isinstance(ly[l], list) == True:
                if l == len(ly) - 1 and ly[l][0] != self.__Y_dimx:
                        raise ValueError("the " + ly[l][1] + " layer should have a value of " + str(self.__Y_dimx) + " as its input")

                if l == 0:
                    self.weights[f"{l + 2}"] = np.random.rand(ly[l][0], self.__X_dimx)
                else:
                    self.weights[f"{l + 2}"] = np.random.rand(ly[l][0], ly[l - 1][0])

                self.A[f"{l + 2}"] = np.zeros((ly[l][0], 1))
                self.acts[f"{l + 2}"] = ly[l][1]
                self.L += 1
            else:
                raise ValueError("invalid input, only use activation functions as inputs")

    def xavier_initialization(self):

        """
        Initialize weights with xavier.

        """

        for l in range(2, len(self.weights) + 2):
            dimy, dimx = self.weights[f"{l}"].shape
            if l == 2:
                for i in range(dimy):
                    for j in range(dimx):
                        self.weights[f"{l}"][i][j] = np.random.normal(0, np.sqrt(1 / self.__X_dimx))
                        
            else:
                prev_dimy, prev_dimx = self.weights[f"{l - 1}"].shape
                for i in range(dimy):
                    for j in range(dimx):
                        self.weights[f"{l}"][i][j] = np.random.normal(0, np.sqrt(1 / prev_dimy))
            #print(self.weights[f"{l}"][i][j])

    def he_initialization(self):

        """
        Initialize weights with he-et-al.

        """
        
        for l in range(2, len(self.weights) + 2):
            dimy, dimx = self.weights[f"{l}"].shape
            if l == 2:
                for i in range(dimy):
                    for j in range(dimx):
                        self.weights[f"{l}"][i][j] = np.random.normal(0, np.sqrt(2 / self.__X_dimx))
            else:
                prev_dimy, prev_dimx = self.weights[f"{l - 1}"].shape
                for i in range(dimy):
                    for j in range(dimx):
                        self.weights[f"{l}"][i][j] = np.random.normal(0, np.sqrt(2 / prev_dimy))