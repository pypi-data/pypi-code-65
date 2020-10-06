from numbers import *
import numpy as np
import math

def rint(num):
    if isinstance(num, int):
        return nun
    elif str(num).__contains__('.'):
        int_down = math.floor(num)
        int_up = math.ceil(num)
        if int_down == int_up:
            return int_down
        elif num < (int_down + 0.5):
            return int_down
        else:
            return int_up
    else:
        return int(num)


def convert_to_int(num):
    if isinstance(num, int):
        return num
    elif str(num).__contains__('.'):
        return rint(num)
    else:
        return int(num)


def convert_to_int_or_float(num):
    if isinstance(num, int):
        return num
    else:
        str_num = str(num)
        list_num = str_num.split('.')
        len_num = len(list_num)
        if len_num == 1:
            return int(num)
        elif len_num == 2:
            list_decimal = list_num[1].split('e')
            len_decimal = len(list_decimal)
            if len_decimal == 1:
                if int(list_num[1]) == 0:
                    return int(num)
                elif isinstance(num, float):
                    return num
                else:
                    return float(num)
            elif int(list_decimal[1]) < 0:
                if isinstance(num, float):
                    return num
                else:
                    return float(num)
            elif int(list_decimal[1]) > 0:
                return rint(num)

        else:
            raise TypeError('num')

    return num_converted


def if_its_str_contains_a_dot_convert_to_float_else_int(num):

    if isinstance(num, int):
        num_converted = num
    elif str(num).__contains__('.'):
        if isinstance(num, float):
            num_converted = num
        else:
            num_converted = float(num)
    else:
        num_converted = int(num)

    return num_converted


def if_equal_to_the_nearest_int_convert_to_int_else_float(num):
    if isinstance(num, int):
        num_converted = num
    else:

        num_rounded = rint(num)
        if num_rounded == num:
            if isinstance(num_rounded, int):
                num_converted = num_rounded
            else:
                num_converted = int(num_rounded)
        else:
            num_converted = float(num)

    return num_converted


def factors_of_x(x, y=1):
    type_x = type(x)
    type_y = type(y)

    x_is_integer = isinstance(x, Integral)

    # The Numeric abstract base classes:
    # numbers.Complex
    # numbers.Real
    # numbers.Integral
    # numbers.Number

    if not x_is_integer:
        raise Exception('x must be ab integer. Now, type_x = {}'.format(type_x))

    y_is_integer = isinstance(y, Integral)
    if not y_is_integer:
        raise Exception('y must be ab integer. Now, type_y = {}'.format(type_y))

    factors = np.empty(0, int)

    for i in range(y, x + 1):
        if x % i == 0:
            factors = np.append(factors, i)

    return factors


def gamma(z):
    
    print('scipy.special.gamma(z) is more efficient')
    
    pos_inf = 100
    n_dx = 10000000
    dx = pos_inf / n_dx

    if not isinstance(z, np.ndarray):
        z = np.asarray(z)

    n_axes_z = len(z.shape)
    n_axes_x = n_axes_z + 1
    axis_delta = n_axes_x - 1
    x = np.arange(0, pos_inf, dx)
    while len(x.shape) < n_axes_x:
        x = np.expand_dims(x, axis=0)

    if n_axes_z > 0:
        z = np.expand_dims(z, axis_delta)

    with np.errstate(divide='ignore'):
        return np.sum(
            np.power(x, z - 1) * np.power(math.e, -x) * dx, axis=axis_delta)
