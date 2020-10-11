import inspect
import numbers

import numpy as np
import scipy.odr as odr
import scipy.optimize as opt
from pycertainties import Val


def rows_to_list(string_data):
    return [row.split() for row in string_data.strip().split("\n")]


def rows_to_numpy(string_data, sep=","):
    if sep:
        data = [row.split(sep) for row in string_data.strip().split("\n")]
    else:
        data = [row.split() for row in string_data.strip().split("\n")]
    return np.array(data, np.float64)


def cols_to_numpy(string_data, sep=None):
    return rows_to_numpy(string_data, sep).transpose()


def pprint_matrix(matrix, column_lables=None, *, title=None, sep="|", width=20, fwidth=10):
    """
    A pretty printer for 2d arrays

    matrix: The 2d array
    column_labels: Labels for the columns while printing
    """
    if len(matrix.shape) != 2:
        raise ValueError

    rows, cols = matrix.shape
    if title:
        spaces = width + (width + 1) * (cols - 1)
        title_string = f"{{:^{spaces}}}"
        print(title_string.format(title))
    if column_lables:
        string = sep.join([f"{{:^{width}}}"] * cols)
        print(string.format(*column_lables))
    for row in range(rows):

        def fmt_str(val):
            return (
                f"{{:^{width}.{fwidth}g}}"
                if isinstance(val, numbers.Real) and not isinstance(val, int)
                else f"{{:^{width}}}"
            )

        strings = [fmt_str(val) for val in matrix[row]]
        string = sep.join(strings)
        print(string.format(*matrix[row]))


def _remove_zeros(xs, ys, dxs, dys):
    def filtered(values):
        if values is None:
            return values
        return [
            val for ind, val in enumerate(values) if (dxs is None or dxs[ind] != 0) and (dys is None or dys[ind] != 0)
        ]

    return filtered(xs), filtered(ys), filtered(dxs), filtered(dys)


def _fit_func(func, xs, ys, dxs=None, dys=None, guesses=None):
    if dxs is None:
        optimal, covarience = opt.curve_fit(func, xs, ys, sigma=dys, p0=guesses, maxfev=3000)
    else:
        xs, ys, dxs, dys = _remove_zeros(xs, ys, dxs, dys)
        data = odr.RealData(xs, ys, dxs, dys)
        new_func = lambda beta, x: func(x, *beta)
        sig = inspect.signature(func)
        options = len(sig.parameters) - 1
        model = odr.Model(new_func)
        odr_obj = odr.ODR(data, model, beta0=[1 for _ in range(options)] if guesses is None else guesses)
        res = odr_obj.run()
        optimal, covarience = res.beta, res.cov_beta

    stddev = np.sqrt(np.diag(covarience))
    return tuple(Val(value, uncertainty) for value, uncertainty in zip(optimal, stddev))


def fit_func(func, xs, ys, dxs=None, dys=None, limits=None, guesses=None):
    if limits is not None:
        trim = lambda values: values[limits] if values is not None else None
        values = [trim(values) for values in (xs, ys, dxs, dys)]
    else:
        values = (xs, ys, dxs, dys)
    return _fit_func(func, *values, guesses=guesses)


def r_squared(func, xs, ys, parameters):
    residuals = ys - func(xs, *parameters)
    residual_sum_of_squares = np.sum(residuals ** 2)
    total_sum_of_squares = np.sum((ys - np.mean(ys)) ** 2)
    return 1 - (residual_sum_of_squares / total_sum_of_squares)
