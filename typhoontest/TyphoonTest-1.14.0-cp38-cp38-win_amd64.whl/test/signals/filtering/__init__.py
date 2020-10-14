"""
This package contains function relevant to signal filtering
"""
from . import impl as _impl

def moving_average(signal, window_length, assume_previous_data=False):
    """
    Calculates average value of the provided signal by using moving window technique, similar to
    'typhoon.test.rms.window_rms' function. User is specifying the size of the moving window in seconds with
    'window_length' argument. To get valid rms value, window size should represent whole number of signal periods.
    If "assume_previous_data" is set to True, the function will assume signal values before the provided ones; In this
    way, rms result will not have transient period during the first "window_length" seconds; rms result will have
    expected values from beginning. Otherwise, initial transient will be present during that period.

    Parameters
    ----------
    signal: pandas.Series
        pandas.Series which represents the signal which average value should be calculated.
    window_length: float
        Length of the moving window for average calculation, in seconds.
    assume_previous_data: bool - default True
        If set, the resulting average signal will have valid values from beginning of function analysis. This is
        achieved by assuming that the signal in previous "window_length" seconds behaved exactly the same as in the
        first provided "window_length" seconds.

    Returns
    -------
    result: pandas.Series
        The resulting signal which represents the instantaneous average of the provided one. The time indices of the
        input and output signals are identical.

    Examples
    --------
    >>> from typhoon.test.signals.filtering import moving_average
    >>> from typhoon.test.signals. import pandas_sine
    >>> # calculate average signal for the pure sine - the result will give zero signal
    >>> sine = pandas_sine(amplitude=100, frequency=50, Ts=1e-6)
    >>> average1 = moving_average(sine, window_length=1/50)
    >>> # create sine signal with some offset - moving_average detects that offset as average value
    >>> sine_offset = sine + 100
    >>> average2 = moving_average(sine_offset, window_length=1/50)

    See Also
    --------
    typhoon.test.rms.window_rms
    """
    return _impl.moving_average(signal, window_length, assume_previous_data)