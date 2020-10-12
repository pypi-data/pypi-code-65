from sklearn.metrics import mean_squared_error
from math import sqrt

def MeanSquaredError(y_predict, y_test):
    return sqrt(mean_squared_error(y_predict, y_test))

def abstract(val):
    return abs(val)

def arraylog(mainstr, arr):
    for obj in arr:
        print(mainstr, obj)

def square(num):
    return sqrt(num)        