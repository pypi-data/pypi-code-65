from typing import Union

import numpy
from scipy.stats import bernoulli, norm


class ControlledProcess:
    """
    A standard, in-control process with no disturbances. In the theoretical model, this is a process with
    :math:`d_t = 0`

    .. plot::
       :include-source:

        from conch_pattern import ControlledProcess
        import numpy
        import matplotlib.pyplot as plt

        sample = ControlledProcess().generate(100, seed=3)

        plt.plot(sample)
        plt.show()

    """

    def __init__(self, autocorr=0, distribution=norm(loc=0, scale=1)):
        """
        :param autocorr: This is the autoregressive coefficient :math:`−1 < \\phi < 1`. It controls the degree of
            autocorrelation in the process, ie the extent to which new points depend on the previous points.
            :code:`autocorr=0` indicates no autocorrelation, while :code:`autocorr=1` indicates total autocorrelation.
        :param distribution: The distribution that the process follows. This should be a subclass of
            :code:`scipy.stats.rv_continuous` or :code:`scipy.stats.rv_discrete`. By default this is a standard normal
            distribution
        """
        self.distribution = distribution
        self.autocorr = autocorr

    @property
    def accumulator(self) -> numpy.ufunc:
        """
        Returns a numpy ufunc that can be used to implement accumulation. This can be overridden by a child class, but
        this isn't recommended.
        """
        return numpy.frompyfunc(lambda prev, curr: prev * self.autocorr + curr, 2, 1)

    def generate(self, n: int, seed: int = None):
        """
        Generate a series of points from the process

        :param n: The number of points to generate
        :param seed: An optional random seed, for example to allow for reproducible sampling
        """
        noise = self.distribution.rvs(n, random_state=seed)
        in_control = self.accumulator.accumulate(noise, dtype=numpy.object)
        return in_control + self.disturbance(n)

    def disturbance(self, n: int) -> Union[numpy.ndarray, int]:
        """
        Returns the disturbance value :math:`d_t` for a sample of n points. This is designed to be overridden by child
        classes

        :param n: The length of the sample to generate the disturbance for. This should match the length of the returned
            array, or the return value should be able to be broadcast to this length.
        """
        return 0


class TrendProcess(ControlledProcess):
    """
    A process subject to a trend disturbance. In the theoretical model, this is a process with
    :math:`d_t = d \\times t` at time :math:`t`.

    .. plot::
       :include-source:

        from conch_pattern import ControlledProcess, TrendProcess
        import numpy
        import matplotlib.pyplot as plt

        sample = numpy.append(
            ControlledProcess().generate(50, seed=3),
            TrendProcess(slope=0.1).generate(50, seed=1)
        )

        plt.plot(sample)
        plt.axvline(x=50, linestyle='--', c='C3')
        plt.show()
    """

    def __init__(self, slope=1, **kwargs):
        """
        :param slope: This is the slope of the trend, ie :math:`d`. A positive value indicates an upwards trend while a
            negative value indicates a downwards trend
        """
        super().__init__(**kwargs)
        self.slope = slope

    def disturbance(self, n: int) -> Union[numpy.ndarray, int]:
        return numpy.arange(n) * self.slope


class ShiftProcess(ControlledProcess):
    """
    A process subject to a shift disturbance, ie the addition of a constant to the distribution.
    In the theoretical model, this is a process with :math:`d_t = u \\times s`
    where :math:`u` is 1 when the shift is active, or 0 otherwise. For this implementation, :math:`u` is assumed to be 1
    always, since you can switch to an in-control process if you want to disable the shift.

    .. plot::
       :include-source:

        from conch_pattern import ControlledProcess, ShiftProcess
        import numpy
        import matplotlib.pyplot as plt

        sample = numpy.append(
            ControlledProcess().generate(50, seed=3),
            ShiftProcess(magnitude=3).generate(50, seed=1)
        )

        plt.plot(sample)
        plt.axvline(x=50, linestyle='--', c='C3')
        plt.show()
    """

    def __init__(self, magnitude=1, **kwargs):
        """
        :param magnitude: The magnitude of the shift (in terms of the standard deviation of the distribution), ie
            :math:`s` in the theoretical model.
        """
        super().__init__(**kwargs)
        self.magnitude = magnitude

    def disturbance(self, n: int) -> Union[numpy.ndarray, int]:
        return self.magnitude


class CycleProcess(ControlledProcess):
    """
    A process subject to a cycle disturbance, ie the addition of a sine function to the outputs.
    In the theoretical model, this is a process with
    :math:`d_t = a \\times sin \\left( \\frac{2 \\pi t}{\\Omega} \\right)`, where :math:`t` is time.

    .. plot::
       :include-source:

        from conch_pattern import ControlledProcess, CycleProcess
        import numpy
        import matplotlib.pyplot as plt

        sample = numpy.append(
            ControlledProcess().generate(50, seed=3),
            CycleProcess(amplitude=3).generate(50, seed=1)
        )

        plt.plot(sample)
        plt.axvline(x=50, linestyle='--', c='C3')
        plt.show()
    """

    def __init__(self, amplitude=1, period=8, **kwargs):
        """
        :param amplitude: The amplitude of the cycle in (in terms of the process standard deviation), in the formula
            above, this is :math:`a` .
        :param period: Number of data points per cycle. In the formula above, this is :math:`\\Omega`.
        """
        super().__init__(**kwargs)
        self.amplitude = amplitude
        self.period = period

    def disturbance(self, n: int) -> Union[numpy.ndarray, int]:
        const = (2 * numpy.pi) / self.period
        times = numpy.arange(0, n) * const
        sine = numpy.sin(times)
        return self.amplitude * sine


class SystematicProcess(ControlledProcess):
    """
    A process subject to a systematic disturbance. In the theoretical model, this is a process with
    :math:`d_t = g \\times (-1)^t`, where :math:`t` is time. In other words, we alternate between adding and
    subtracting a constant from the process.

    .. plot::
       :include-source:

        from conch_pattern import ControlledProcess, SystematicProcess
        import numpy
        import matplotlib.pyplot as plt

        sample = numpy.append(
            ControlledProcess().generate(50, seed=3),
            SystematicProcess().generate(50, seed=1)
        )

        plt.plot(sample)
        plt.axvline(x=50, linestyle='--', c='C3')
        plt.show()
    """

    def __init__(self, magnitude=1, **kwargs):
        """
        :param magnitude: The magnitude of the systematic shift. This is :math:`g` in the above formula.
        """
        super().__init__(**kwargs)
        self.magnitude = magnitude

    def disturbance(self, n: int) -> Union[numpy.ndarray, int]:
        arr = numpy.arange(n)
        alternating = (-1) ** arr
        return self.magnitude * alternating


class MixtureProcess(ControlledProcess):
    """
    A process subject to a systematic disturbance. In the theoretical model, this is a process with
    :math:`d_t = r \\times (-1)^h`. In the original simulator presented by [Guh2008]_, :math:`h` is :math:`0` if
    :math:`p < rp`, otherwise :math:`1`, where :math:`0 < p < 1` is a random number, and :math:`rp` is a fixed value
    for the process. However assuming we can determine the CDF of :math:`p`, this can be simplified to
    :math:`h \\sim Bernoulli(p^*)`. This is the model that
    is used here, and it has a more intuitive explanation: the disturbance is "active" with probability :math:`p^*`,
    otherwise it is inactive.

    .. plot::
       :include-source:

        from conch_pattern import ControlledProcess, MixtureProcess
        import numpy
        import matplotlib.pyplot as plt

        sample = numpy.append(
            ControlledProcess().generate(50, seed=3),
            MixtureProcess().generate(50, seed=1)
        )

        plt.plot(sample)
        plt.axvline(x=50, linestyle='--', c='C3')
        plt.show()
    """

    def __init__(self, magnitude=1, switch=0.5, **kwargs):
        """
        :param magnitude: The magnitude of the shift that should occur when the disturbance is active. In the formula
            above, this corresponds to :math:`r`
        :param switch: The probability of enabling the mixture disturbance. This corresponds to :math:`p^*` in the above
            simplified formula
        """
        super().__init__(**kwargs)
        self.magnitude = magnitude
        self.switch = switch

    def disturbance(self, n: int) -> Union[numpy.ndarray, int]:
        switch = bernoulli(self.switch).rvs(n)
        return self.magnitude * (-1) ** switch
