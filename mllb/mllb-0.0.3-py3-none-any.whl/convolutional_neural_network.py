"""
Convolutional Neural netork class
"""


import numpy as np
from .learning_rate import learning_rate_class
from .neural_network_layers import layers_class
from .activation_functions import activate, activate_prime
import copy
from random import randint


class cnn:

    """
    Creates a Convolutional Neural Network class.

    Args:
        X: (np.ndarray or list) this should be the training examples without the classifiers
           or labels. Whether the value is a list or a NumPy array, it must not have more than
           two dimensions.

        Y: (np.ndarray or lsit) this should be the classifiers of X. Whether Y is a list or a 
           NumPy array, it must not have more than two dimensions.

    """

    def __init__(self, X, Y):

        """
        Args:
            __m: (int) number of training examples

            __n: (int) number of features plus one

            __X: (np.ndarray) input 'examples' to be used for training

            __Y: (np.ndarray) classifiers to be used for training

            layers: (layers_class) neural network layers

            learning_rate: (learning_rate_class) learning rate object

        """

        import numpy as np

        checked = self.__X_Y_creation(X, Y)

        self.__m, self.__n, self.__X, self.__Y = checked
        self.layers = layers_class(self.__n, self.__Y.shape[1]) # self.__Y.shape[1] = y_dimx
        self.learning_rate = learning_rate_class()
        
        
        
                

        # import numpy as np

        # if X.ndim != 2 or Y.ndim != 2:
        #     raise ValueError("dimensionality of both arrays must be 2")
        # X_dimy, X_dimx = X.shape
        # Y_dimy, Y_dimx = Y.shape

        # if X_dimy != Y_dimy:
        #     raise ValueError("inputs and classifiers must have equal number of rows")

        # self.__X = np.hstack((np.ones((X_dimy, 1)), X))
        # self.__Y = Y
        # self.layers = layers_class(X_dimx + 1, Y_dimx)
        # self.learning_rate = learning_rate_class()

        # self.__n = X_dimx + 1
        # self.__m = X_dimy


    def __X_Y_creation(self, X, Y):

        # Checking X and ensuring a NumPy array is created

        import copy
        if isinstance(X, list):

            if set([isinstance(i, list) for i in X]) == {True}:
                x = np.array(copy.deepcopy(X))

            elif set([isinstance(i, int) or isinstance(i, float) for i in X]) == {True}:
                x = np.array([[j] for j in X])

            else:
                raise ValueError("mixed datatypes within the first argument")

        elif isinstance(X, np.ndarray):

            if X.ndim == 1:
                x = X.reshape((X.shape[0], 1))

            elif X.ndim == 2:
                x = copy.deepcopy(X)

            else:
                raise ValueError("the NumPy array of the first argument must not have more than 2 dimensions")

        else:
            raise ValueError("datatype of the first argument is invalid, only NumPy arrays and lists are allowed")

        # Checking Y and ensuring a NumPy array is created
        
        if isinstance(Y, list):

            if set([isinstance(i, list) for i in Y]) == {True}:
                y = np.array(copy.deepcopy(Y))

            elif set([isinstance(i, int) or isinstance(i, float) for i in Y]) == {True}:
                y = np.array([[j] for j in Y])

            else:
                raise ValueError("mixed datatypes within the first argument")

        elif isinstance(Y, np.ndarray):

            if Y.ndim == 1:
                y = Y.reshape((Y.shape[0], 1))

            elif X.ndim == 2:
                y = copy.deepcopy(Y)

            else:
                raise ValueError("the NumPy array of the second argument must not have more than 2 dimensions")

        else:
            raise ValueError("datatype of the second argument is invalid, only NumPy arrays and lists are allowed")

        x_dimy, x_dimx = x.shape
        y_dimy, y_dimx = y.shape

        if x_dimy != y_dimy:
            raise ValueError("both arguments should have equal number of examples and classifiers")
        
        one = np.ones((x_dimy, 1))
        x = np.hstack((one, x))

        return x_dimy, x_dimx + 1, x, y


    def train(self, epochs, optimizer = 'sgd', batch_size=1):

        """
        Train the model.

        Args:
            epochs: (int) the number of traning circles

            optimizer: (str) its value is either 'sgd' or 'bgd'

                       'sgd' for Stochastic Gradient Descent, 'bgd' for Batch 
                       Gradient Descent.

            batch_size: (int) batch_size signifies the batch size in Batch Gradient Descent.
                        
                        This value is only used within the code when the optimer used is 'bgd'

        Return:
            --
        """

        if isinstance(epochs, int) == False:
            raise ValueError("epochs must be an integer value")
        if isinstance(batch_size, int) == False:
            raise ValueError("batch_size must be an integer value")

        if optimizer == "bgd":
            self.__batch_gradient_descent(epochs, batch_size)

        elif optimizer == "sgd":
            self.__stochastic_gradient_descent(epochs)

        else:
            raise ValueError("invalid optimizer, use either 'sgd' or 'bgd'")


    def __batch_gradient_descent(self, epochs, batch_size):

        # Batch Gradient Descent

        number_of_batches = (self.__m // batch_size) + 1

        batch_X = []
        batch_Y = []

        for batch_number in range(1, number_of_batches):
            if batch_number != number_of_batches:
                batch_X.append(self.__X[((batch_number - 1) * batch_size):(batch_number * batch_size), :])
                batch_Y.append(self.__Y[((batch_number - 1) * batch_size):(batch_number * batch_size), :])
            elif (batch_number - 1) * batch_size != self.__m:
                batch_X.append(self.__X[((batch_number - 1) * batch_size):self.__m, :])
                batch_Y.append(self.__Y[((batch_number - 1) * batch_size):self.__m, :])

        epoch = 0
        same_error = 0
        prev_error = 0

        for times in range(1, epochs + 1):
            batch = randint(0, len(batch_X) - 1)

            _X = batch_X[batch]
            _Y = batch_Y[batch]

            _X_m, _X_n = _X.shape

            dC = {}

            for i in range(_X_m):
                x_ = _X[[i], :].T
                self.layers.A["1"] = x_

                y_ = _Y[[i], :].T


                for l in range(2, self.layers.L + 1):

                    self.layers.A[f"{l}"] = activate(np.dot(self.layers.weights[f"{l}"], self.layers.A[f"{l - 1}"]), self.layers.acts[f"{l}"])

                error = np.multiply(np.subtract(self.layers.A[f"{self.layers.L}"], y_).T, (self.layers.A[f"{self.layers.L}"] - y_)) / (2 * self.__m)

                error_derivative = np.divide((self.layers.A[f"{self.layers.L}"] - y_), self.layers.A[f"{self.layers.L}"].size)

                delta = {}

                delta[f"{self.layers.L}"] = np.multiply(error_derivative, activate_prime(self.layers.A[f"{self.layers.L}"], self.layers.acts[f"{self.layers.L}"]))
                for l in range(1, self.layers.L):

                    delta[f"{self.layers.L - l}"] = np.multiply(np.dot(self.layers.weights[f"{self.layers.L - l + 1}"].T, (delta[f"{self.layers.L - l + 1}"])), (activate_prime(self.layers.A[f"{self.layers.L - l}"], self.layers.acts[f"{self.layers.L - l}"])))

                for l in range(2, self.layers.L + 1):
                    delta_temp = delta[f"{self.layers.L - l + 2}"].copy()
                    Wl_dimy, Wl_dimx = self.layers.weights[f"{self.layers.L - l + 2}"].shape

                    for k in range(Wl_dimx - 1):
                        delta_temp = np.hstack((delta_temp, delta[f"{self.layers.L - l + 2}"]))

                    A_temp = self.layers.A[f"{self.layers.L - l + 1}"].T
                    for k in range(self.layers.A[f"{self.layers.L - l + 2}"].size - 1):
                        A_temp = np.vstack((A_temp, self.layers.A[f"{self.layers.L - l + 1}"].T))

                    if i == 0:
                        dC[f"{l}"] = np.multiply(delta_temp, A_temp)
                    else:
                        dC[f"{l}"] = dC[f"{l}"] + np.multiply(delta_temp, A_temp)

            for l in range(2, self.layers.L + 1):
                self.layers.weights[f"{self.layers.L - l + 2}"] = self.layers.weights[f"{self.layers.L - l + 2}"] - ((dC[f"{l}"] / _X_m) * self.learning_rate.lr_value)

            print(f"Epoch       :    {times}    =     {error[0][0]}")

            self.learning_rate.lr_value *= self.learning_rate.lr_increase


    def __stochastic_gradient_descent(self, epochs):

        # Stochastic Gradient Descent

        for times in range(1, epochs + 1):
            i = randint(0, self.__m - 1)

            self.layers.A["1"] = self.__X[[i], :].T

            y_ = self.__Y[[i], :].T

            for l in range(2, self.layers.L + 1):

                self.layers.A[f"{l}"] = activate(np.dot(self.layers.weights[f"{l}"], self.layers.A[f"{l - 1}"]), self.layers.acts[f"{l}"])

            error = np.multiply(np.subtract(self.layers.A[f"{self.layers.L}"], y_).T, (self.layers.A[f"{self.layers.L}"] - y_)) / (2 * self.__m)

            error_derivative = np.divide((self.layers.A[f"{self.layers.L}"] - y_), self.layers.A[f"{self.layers.L}"].size)

            delta = {}

            delta[f"{self.layers.L}"] = np.multiply(error_derivative, activate_prime(self.layers.A[f"{self.layers.L}"], self.layers.acts[f"{self.layers.L}"]))
            for l in range(1, self.layers.L):

                delta[f"{self.layers.L - l}"] = np.multiply(np.dot(self.layers.weights[f"{self.layers.L - l + 1}"].T, (delta[f"{self.layers.L - l + 1}"])), (activate_prime(self.layers.A[f"{self.layers.L - l}"], self.layers.acts[f"{self.layers.L - l}"])))

            for l in range(2, self.layers.L + 1):
                delta_temp = delta[f"{self.layers.L - l + 2}"].copy()
                Wl_dimy, Wl_dimx = self.layers.weights[f"{self.layers.L - l + 2}"].shape 

                for k in range(Wl_dimx - 1):
                    delta_temp = np.hstack((delta_temp, delta[f"{self.layers.L - l + 2}"]))

                A_temp = self.layers.A[f"{self.layers.L - l + 1}"].T
                for k in range(self.layers.A[f"{self.layers.L - l + 2}"].size - 1):
                    A_temp = np.vstack((A_temp, self.layers.A[f"{self.layers.L - l + 1}"].T))

                dC = np.multiply(delta_temp, A_temp)
                self.layers.weights[f"{self.layers.L - l + 2}"] = self.layers.weights[f"{self.layers.L - l + 2}"] - (dC * self.learning_rate.lr_value)

            print(f"Epoch       :    {times}    =     {error[0][0]}")

            self.learning_rate.lr_value *= self.learning_rate.lr_increase


    def predict(self, value):

        """
        Predict a value.

        Args:
            value: (list) a list containing the values in the right order to the predicted

        Return:
            ans: (np.ndarray) predicted value
        """

        if isinstance(value, list):
            if len(value) != self.__n - 1:
                raise ValueError("'value' should have " + str(self.__n - 1) +
                                    " elements within it")
            data = copy.deepcopy(value)
            data.insert(0, 1)
            ans = np.array([data]).T
            for l in range(2, self.layers.L + 1):
                ans = activate(self.layers.weights[f"{l}"].dot(ans), self.layers.acts[f"{l}"])
            ans = ans.T

            return ans
            
        else:
            raise ValueError("input should be a list")