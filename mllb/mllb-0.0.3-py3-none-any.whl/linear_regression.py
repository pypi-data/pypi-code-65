"""
Linear Regression class.

"""

import random

import numpy as np
from .learning_rate import *

class linear_regression:

    """
    Create a Linear Regression class.

    Args:

    """

    def __init__(self, X, Y):

        """
        Args:
            __m: (int) number of training examples

            __n: (int) number of features plus one

            __X: (np.ndarray) input 'examples' to be used for training

            __Y: (np.ndarray) classifiers to be used for training

            __weights: (np.ndarray) linear regression weights

            learning_rate: (learning_rate_class) learning rate object

        """

        import numpy as np

        checked = self.__X_Y_creation(X, Y)

        self.__m, self.__n, self.__X, self.__Y = checked
        self.__weights = np.array([[0] for j in range(self.__n)])
        self.learning_rate = learning_rate_class()

        print(self.__X)
        print("\n")
        print(self.__Y)
        
    
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


    def __initialize_weights(self):

        # Weights are initialized
        import numpy as np
        
        self.__weights = [list(i) for i in self.__weights]
        if self.__m != 1:
            for j in range(1, self.__n):
                for i in range(1, self.__m):
                    base_difference = self.__X[i][j] - self.__X[i - 1][j]

                    if base_difference != 0:
                        self.__weights[j][0] = self.__weights[j][0] + (self.__Y[i][0] - self.__Y[i - 1][0]) / base_difference

                self.__weights[j][0] /= float(self.__m - 1)

        else:
            for j in range(1, self.__n):
                self.__weights[j][0] = self.__Y[0][0] / self.__X[0][j]
        theta0 = np.array(self.__Y) - np.array(self.__X)[:, 1:].dot(np.array(self.__weights)[1:, :])
        self.__weights[0][0] = theta0.sum() / self.__m
        self.__weights = np.array(self.__weights)


    def train(self, epochs, optimizer="sgd", batch_size=1, regulariser=0):

        
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

        if optimizer == "sgd":
            self.__stochastic_gradient_descent(epochs, regulariser)

        elif optimizer == "bgd":
            self.__batch_gradient_descent(epochs, batch_size, regulariser)
            
        else:
            raise ValueError("invalid optimizer, use either 'sgd' or 'bgd'")


    def __stochastic_gradient_descent(self, epochs, regulariser):

        # Stochastic Gradient Descent

        self.__initialize_weights()
        
        epoch = 0
        same_error = 0
        prev_error = 0
        
        while epoch < epochs and same_error < 5:
            epoch += 1
            i = random.randint(0, self.__m - 1)

            x_ = self.__X[[i], :]
            y_ = self.__Y[[i], :]
            
            diff = np.dot(x_, self.__weights) - y_

            error = np.dot(diff.T, diff) / (2 * self.__m)

            if regulariser != 0:
                error = np.dot(diff.T, diff) / (2 * self.__m) + np.dot(self.__weights.T, self.__weights) * regulariser

            else:
                error = np.dot(diff.T, diff) / (2 * self.__m)

            for j in range(self.__n):
                self.__weights[j][0] -= (np.dot(diff.T, x_)[0][0] / self.__m) * self.learning_rate.lr_value

            print("Epoch {}     :       error   =    {}".format(epoch, error[0][0]))

            if prev_error == error:
                same_error += 1
            else:
                same_error = 0

            self.learning_rate.lr_value *= self.learning_rate.lr_increase


    def __batch_gradient_descent(self, epochs, batch_size, regulariser):

        # Batch Gradient Descent

        self.__initialize_weights()
        print(self.__weights)
        number_of_batches = (self.__m // batch_size) + 1

        x_in_batches = []
        y_in_batches = []

        for batch_number in range(1, number_of_batches):
            if batch_number != number_of_batches:
                x_in_batches.append(self.__X[((batch_number - 1) * batch_size):(batch_number * batch_size), :])
                y_in_batches.append(self.__Y[((batch_number - 1) * batch_size):(batch_number * batch_size), :])
            elif (batch_number - 1) * batch_size != self.__m:
                x_in_batches.append(self.__X[((batch_number - 1) * batch_size):self.__m, :])
                y_in_batches.append(self.__Y[((batch_number - 1) * batch_size):self.__m, :])

        epoch = 0
        same_error = 0
        prev_error = 0
        
        while epoch < epochs and same_error < 5:
            epoch += 1

            for batch in range(len(x_in_batches)):
                
                diff = np.dot(x_in_batches[batch], self.__weights) - y_in_batches[batch]

                error = np.dot(diff.T, diff) / (2 * self.__m)

                if regulariser != 0:
                    error = np.dot(diff.T, diff) / (2 * self.__m) + np.dot(self.__weights.T, self.__weights) * regulariser

                else:
                    error = np.dot(diff.T, diff) / (2 * self.__m)

                for j in range(self.__n):
                    self.__weights[j][0] -= (np.dot(diff.T, x_in_batches[batch][:,[j]])[0][0] / self.__m) * self.learning_rate.lr_value

            print("Epoch {}     :       error   =    {}".format(epoch, error[0][0]))

            if prev_error == error:
                same_error += 1
            else:
                same_error = 0

            self.learning_rate.lr_value *= self.learning_rate.lr_increase

    def normal_function(self):

        """
        Uses the normal funciton to optimize the weights.

        """

        x = np.array(self.__X)
        y = np.array(self.__Y)
        w = np.array(self.__weights)
        ans = np.linalg.inv((x.T).dot(x)).dot(x.T).dot(y)
        self.__weights = [list(j) for j in ans]

    def predict(self, value):

        """
        Predict a value.

        Args:
            value: (list) a list containing the values in the right order to the predicted

        Return:
            ans: (np.ndarray) predicted value
        """

        if isinstance(value, list) == True:
            if len(value) != self.__n - 1:
                raise ValueError("'value' should have " + str(self.__n - 1) +
                                    " elements within it")
            import copy
            v = copy.deepcopy(value)
            v.insert(0, 1)
            ans = np.array([v]).dot(np.array(self.__weights))
            ans = ans[0]
            
        return ans