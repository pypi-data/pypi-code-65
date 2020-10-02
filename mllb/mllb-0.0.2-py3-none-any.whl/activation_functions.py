# Neural network activation function with NumPy. These two functions
# calculate and output the activation funcitons for two dimensional 
# NumPy arrays.

def activate(arr, activator):

    # Args:
    #       arr: (numpy.ndarray) NumPy array
    #
    #       activator: (str) string that indicates the kind of activation
    #                  to be performed on the array
    #
    # Return:
    #       ans: (numpy.ndarray) NumPy array

    import numpy as np

    if activator == "sigmoid":

        denominator = np.array(1) + np.exp(-arr)
        ans = np.divide(1, denominator)

    elif activator == "relu":

        ans = np.maximum(arr, 0)

    elif activator == "tanh":

        ans = np.tanh(arr)

    elif activator == "softplus":

        added = np.add(1, arr)
        ans = np.log(added)

    elif activator == "leakyrelu":

        ans = 0.01 * np.maximum(arr, 0)

    elif activator == "softmax":

        exped = np.exp(arr)
        normalizer = np.sum(exped)
        ans = np.divide(exped, normalizer)

    elif activator == "none":
        ans = arr

    else:
        raise ValueError("Invalid activator.")

    return ans


def activate_prime(arr, type):

    # Derivative of an activation function

    # Args:
    #       arr: (numpy.ndarray) NumPy array
    #
    #       type: (str) string that indicates the kind of activation
    #             derivative to be performed on the array
    #
    # Return:
    #       ans: (numpy.ndarray) NumPy array

    import numpy as np

    if type == "sigmoid":

        ans = np.multiply(arr, np.subtract(1, arr))

    elif type == "relu":

        ans = arr
        arr[ans<=0] = 0
        arr[ans>0] = 1

    elif type == "tanh":

        numerator = np.subtract(np.exp(arr), 1)
        ans = np.divide(numerator, np.exp(arr))

    elif type == "leakyrelu":

        ans = arr
        arr[ans<=0] = 0
        arr[ans>0] = 0.01

    elif type == "softmax":

        ans = arr - np.power(arr, 2)

    elif type == "none":
        ans = arr

    else:
        raise ValueError("Invalid activator.")