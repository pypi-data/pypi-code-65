import numpy as np
from .learning_rate import *

class logistic_regression:

    def __init__(self, X, Y):
        if len(X) != len(Y):
            raise ValueError("examples and classifiers must have equal number of rows")

        for x in X:
            if len(x) != len(X[0]):
                raise ValueError("dimensions are not consistent in the first argument")

        self.__X = X
        self.__Y = Y
        self.__weights = [[(1/len(X[0])) * j] for j in range(len(X[0]) + 1)]
        self.learning_rate = learning_rate_class()

        self.__n = len(X[0]) + 1
        self.__m = len(X)
        self.__xavier_or_he_initialized = False

        for i in range(self.__m):
            self.__X[i].insert(0, 1)

    def __initialize_weights(self):
        if self.__m != 1:
            for j in range(1, self.__n):
                for i in range(1, self.__m):
                    base_difference = self.__X[i][j] - self.__X[i - 1][j]
                    if base_difference != 0:
                        self.__weights[j][0] += (self.__Y[i][0] - self.__Y[i - 1][0]) / base_difference
                self.__weights[j][0] /= self.__m - 1
        else:
            for j in range(1, self.__n):
                self.__weights[j][0] = self.__Y[0][0] / self.__X[0][j]
        theta0 = np.array(self.__Y) - np.array(self.__X)[:, 1:].dot(np.array(self.__weights)[1:, :])
        self.__weights[0][0] = theta0.sum() / self.__m

    def xavier_initialization(self):
        self.__xavier_or_he_initialized = True
        for j in range(self.__n):
            self.__weights[j][0] = np.random.normal(0, np.sqrt(1 / self.__n))

    def he_initialization(self):
        self.__xavier_or_he_initialized = True
        for j in range(self.__n):
            self.__weights[j][0] = np.random.normal(0, np.sqrt(2 / self.__n))

    def train(self, epochs, batch_size=1, regulariser=0):
        if batch_size < 1:
            raise ValueError("batch_size cannot be less than 1")

        if self.__xavier_or_he_initialized == False:
            self.__initialize_weights()

        x = np.array(self.__X)
        y = np.array(self.__Y)
        w = np.array(self.__weights)

        number_of_batches = (self.__m // batch_size) + 1

        x_in_batches = []
        y_in_batches = []

        for batch_number in range(1, number_of_batches):
            if batch_number != number_of_batches:
                x_in_batches.append(x[((batch_number - 1) * batch_size):(batch_number * batch_size), :])
                y_in_batches.append(y[((batch_number - 1) * batch_size):(batch_number * batch_size), :])
            elif (batch_number - 1) * batch_size != self.__m:
                x_in_batches.append(x[((batch_number - 1) * batch_size):self.__m, :])
                y_in_batches.append(y[((batch_number - 1) * batch_size):self.__m, :])

        epoch = 0
        same_error = 0
        prev_error = 0
        
        while epoch < epochs and same_error < 5:
            epoch += 1

            for batch in range(len(x_in_batches)):
                xb = x_in_batches[batch]
                yb = y_in_batches[batch]

                function_x = xb.dot(w)
                hypothesis_denominator = np.exp(np.multiply(function_x, -1)) + np.ones(function_x.shape)
                hypothesis = np.divide(np.ones(hypothesis_denominator.shape), hypothesis_denominator)

                error = (np.multiply((yb * (-1)), np.log10(hypothesis)) + np.multiply(((yb - 1) * (-1)), np.log10((hypothesis - 1) * (-1)))).sum() / self.__m
                
                diff = np.dot(x_in_batches[batch], w) - y_in_batches[batch]

                error = np.dot(diff.T, diff) / (2 * self.__m)

                if regulariser != 0:
                    error += np.dot(w.T, w) * regulariser

                for j in range(self.__n):

                    e_raised = np.exp(hypothesis * -1)

                    hypothesis_differentiation_divided_by_ln = (np.divide(e_raised, np.multiply((e_raised + 1), (e_raised + 1))) * w[j][0]) / np.log(10)
                    prefix1 = yb / hypothesis
                    prefix2 = ((yb - 1) * -1) / (hypothesis - 1)
                    diff_error_matrix = np.multiply(prefix1, hypothesis_differentiation_divided_by_ln) + np.multiply(prefix2, hypothesis_differentiation_divided_by_ln)

                    error_differentiated = (-1 / self.__m) * diff_error_matrix.sum()

                    w[j][0] -= error_differentiated * self.learning_rate.lr_value

            print("Epoch {}     :       error   =    {}".format(epoch, error[0][0]))

            if prev_error == error:
                same_error += 1
            else:
                same_error = 0

            self.learning_rate *= self.learning_rate.lr_increase

        self.__weights = [list(j) for j in w]

    def predict(self, value):
        if isinstance(value, list) == True:
            if len(value) != self.__n - 1:
                raise ValueError("'value' should have " + str(self.__n - 1) +
                                    " elements within it")
            import copy
            v = copy.deepcopy(value)
            function_x = np.array([v]).dot(np.array(self.__weights))
            ans = np.divide(1, (np.exp(function_x * (-1)) + 1))
        return ans[0]