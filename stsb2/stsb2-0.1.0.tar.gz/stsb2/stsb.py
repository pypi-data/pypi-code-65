
import abc

import numpy as np
from scipy import stats

from . import inference
from . import effects


APPLY_FUNCS = {
    'log': np.log,
    'exp': np.exp,
    'tanh': np.tanh,
    'invtanh': np.arctanh,
    'invlogit': lambda x: 1./(1. + np.exp(-1. * x)),
    'logit': lambda x: np.log(x / (1. - x)),
    'floor': np.floor,
    'sin': np.sin,
    'cos': np.cos,
    'softplus': lambda x, limit=30.0: np.where(
            x < limit,
            np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0.0),
            x
        ),
    'diff': lambda x: x[..., 1:] - x[..., :-1],
    'logdiff': lambda x: np.log(x[..., 1:]) - np.log(x[..., :-1]),
}
APPLY_FUNC_NAMES = {v: k for k, v in APPLY_FUNCS.items()}


def _make_2d(obj, size, timesteps):
    if type(obj) is float:
        obj = np.array([obj]).reshape((-1, 1))
    else:
        obj = obj.reshape((-1, 1))
    obj = obj * np.ones((size, timesteps))
    return obj


def _make_1d(obj, size):
    if type(obj) is float:
        obj = np.array([obj]).flatten()
    return obj.flatten()


def _add_fns_to_repr(obj, string):
    if obj.apply_funcs != list():
        for fn in obj.apply_funcs:
            string = f"{APPLY_FUNC_NAMES[fn]}({string})"
    return string


def _apply_fns(obj, draws):
    for fn in obj.apply_funcs:
        draws = fn(draws)
    return draws


def _is_block(obj):
    return issubclass(type(obj), Block)


def get_id(obj):
    """Assign the uid of a Block.

    Args:
        obj (Block): block to which you want to assign a uid.

    Returns:
        id_ (string): the block's uid
    """
    id_ = str(type(obj)) + str(type(obj).num)
    type(obj).num += 1
    return id_


def get_timesteps(obj):
    """Get the number of timesteps over which the block is defined.

    Args:
        obj (Block): block from which you want the number of timesteps

    Returns:
        timesteps (int > 0): number of timesteps over which the block is defined
    """
    return obj.t1 - obj.t0


def set_time_endpoints(obj, t0, t1):
    """Set time endpoints of block. 

    Args:
        obj (Block): block for which you want to set timepoints
        t0 (int): initial time
        t1 (int): end time
    """
    if t0 is not None:
        obj.t0 = t0
    if t1 is not None:
        obj.t1 = t1


def changepoint(left, right, frac=0.5):
    """Functional endpoint to changepoint block creation. 

    Args:
        left (Block): the left block in the changepoint
        right (Block): the right block in the changepoint
        frac (float, 0 < frac < 1): where the changepoint is on interval (t0, t1)

    Returns:
        ChangepointBlock(left, right, frac=frac)
    """
    return ChangepointBlock(left, right, frac=frac)


class Block:
    """Base class for all STS blocks.

    Args:
        t0 (int): start timepoint
        t1 (int): end timepoint
        is_cached (str): whether to give sampling a cached interpretation.
            If `is_cached`, subsequent calls to `.sample(...)` after the first
            will replay the result of the first call. This behavior will
            occur until the cache is reset (with `util.clear_cache(...)` or
            `self.clear_cache(...)`)
    """

    num = 0

    def __init__(self, t0=0, t1=2, is_cached=False, **kwargs):
        self.uid = get_id(self)
        self.t0 = t0
        self.t1 = t1

        self.timesteps = get_timesteps(self)
        self.parameters = list()
        self.parameter_bounds = list()
        self.apply_funcs = list()
        self._prec = list()
        self._succ = list()

        # replay / memoization
        self.is_cached = is_cached
        self.cache = list()

    def __add__(self, right):
        return AddedBlock(self, right)

    def __call__(self, size=1,):
        return self.sample(size=size)

    def clear_cache(self,):
        """Clears the block cache.

        This method does *not* alter the cache mode.
        """
        self.cache = list()

    def _transform(self, arg, *args):
        """Defines a transform from a string argument.

        Currently the following string arguments are supported:
            + exp
            + log
            + logit
            + invlogit
            + tanh
            + arctanh
            + invlogit
            + logit
            + floor
            + sin
            + cos
            + softplus
            + diff (lowers time dimemsion by 1)
            + logdiff (lowers time dimension by 1)

        The resulting transform will be added to the transform stack iff
        it is not already at the top of the stack.

        Args:
            arg (str): one of the above strings corresponding to function

        Returns:
            self (stsb.Block)
        """
        func = APPLY_FUNCS[arg] 
        if func in self.apply_funcs:
            if func != self.apply_funcs[-1]:
                self.apply_funcs.append(func)
        else:
            self.apply_funcs.append(func)
        return self

    def _maybe_add_blocks(self, *args):
        """Adds parameters to prec and succ if they subclass Block.

        Args:
            *args: iterable of (name, parameter, bound) 
        """
        for name, arg, bound in args:
            if _is_block(arg):
                self._prec.append(arg)
                arg._succ.append(self)
            else:
                self.parameters.append(name)
                self.parameter_bounds.append(bound)

    def log(self):
        """x -> log x 

        Block paths must be positive for valid output.
        """
        return self._transform('log')

    def exp(self):
        """x -> exp(x)
        """
        return self._transform('exp')

    def tanh(self):
        """x -> tanh(x), i.e. x -> (exp(x) - exp(-x)) / (exp(x) + exp(-x))
        """
        return self._transform('tanh')

    def arctanh(self):
        """x -> arctanh(x), i.e. x -> 0.5 log ((1 + x) / (1 - x))
        """
        return self._transform('arctanh')

    def invlogit(self):
        """x -> 1 / (1 + exp(-x))
        """
        return self._transform('invlogit')

    def logit(self):
        """x -> log(x / (1 - x))
        """
        return self._transform('logit')

    def floor(self):
        """x -> x - [[x]], where [[.]] is the fractional part operator
        """
        return self._transform('floor')

    def sin(self):
        """x -> sin x
        """
        return self._transform('sin')

    def cos(self):
        """x -> cos x
        """
        return self._transform('cos')

    def softplus(self):
        """x -> log(1 + exp(x))
        """
        return self._transform('softplus')

    def diff(self):
        """x -> x[1:] - x[:-1]

        Note that this lowers the time dimension from T to T - 1.
        """
        return self._transform('diff')

    def logdiff(self):
        """x -> log x[1:] - log x[:-1]

        NOte that this lowers the time dimension from T to T - 1.
        """
        return self._transform('logdiff')

    @abc.abstractmethod
    def _sample(self, size=1):
        ...

    def forecast_many(self, size=1, Nt=1, ic=None, **kwargs):
        """Draw many forecast paths.

        Args:
            size (int >= 1): number of forecast paths
            Nt (int >= 1): number of timesteps forward to forecast
            ic (float || numpy.ndarray): initial condition, optional. If not set,
                will be set to the last observed / simulated value of the block.

        Returns: (numpy.ndarray) array of shape (size, ic.shape[0], t1 - t0)
            
        """
        return np.array([
            self.forecast(size=None, Nt=Nt, ic=ic, **kwargs)
            for _ in range(size)
        ])

    def forecast(self, size=None, Nt=1, **kwargs):
        """Forecasts the block forward in time. 

        Forecasting is equivalent to fast-forwarding time, using possibly-updated parameter estimates,
        and calling sample(...).

        Args:
            size (int >= 1): number of forecast paths
            Nt (int >= 1): number of timesteps forward to forecast
        """
        if not self.is_cached:
            raise ValueError('Need to enable cache for forecasting')
        if len(self.cache) == 0:
            raise ValueError('Cache is empty, cannot forecast')
        if size is not None:
            if size != self.cache[0].shape[0]:
                raise ValueError('Passed size = {size}, but cache size = (self.cache[0].shape[0])')
        return self._forecast(size=size, Nt=Nt, **kwargs)

    def _forecast(self, size=None, Nt=1,):
        """See documentation of `forecast(...)` and `effects.ForecastEffect`.
        """
        if size is None:
            size = self.cache[0].shape[0]

        with effects.ForecastEffect(self, Nt=Nt):
            paths = self.sample(size=size)
        return paths

    def sample(self, size=1):
        """Draws a batch of `size` samples from the block.
        
        Args:
            size (int): batch size

        Returns:
            draws (numpy.ndarray) sampled values from the block
        """
        if self.is_cached:
            if len(self.cache) < 1:
                draws = self._sample(size=size)
                self.cache.append(draws)  # cache in untransformed space
                return _apply_fns(self, draws)
            return _apply_fns(self, self.cache[-1])
        return _apply_fns(self, self._sample(size=size))

    def parameter_update(self, **kwargs):
        """Updates the parameters of the block.

        This method should be used with caution as it can change the type, dimension, etc
        of any parameter that is passed and does not perform any safety checks.
        Passed values can be 
            + numeric types
            + `numpy.ndarray`s
            + `stsb.Block`s

        Args:
            **kwargs: `parameter_1_name=parameter_1_value, ...`
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def prec(self):
        """Returns the predecessor nodes of `self` in the (implicit) compute graph

        Returns:
            _prec (list): list of predecessor nodes
        """
        return self._prec

    def succ(self):
        """Returns the successor nodes of `self` in the (implicit) compute graph

        Returns:
            _succ (list): list of successor nodes
        """
        return self._succ


class NonMarkovBlock(Block):
    """Block that depends on its sample history. 

    This block should be subclassed and is nonfunctional on its own.

    Args:
        t0 (int): start timepoint
        t1 (int): end timepoint
        is_cached (str): whether to give sampling a cached interpretation.
            If `is_cached`, subsequent calls to `.sample(...)` after the first
            will replay the result of the first call. This behavior will
            occur until the cache is reset (with `util.clear_cache(...)` or
            `self.clear_cache(...)`)
    """

    num = 0

    def __init__(
        self,
        t0=0,
        t1=2,
        *args,
        **kwargs,
    ):
        super().__init__(t0=t0, t1=t1)
        self.history = None

    def _sample(self, size=1):
        raise NotImplementedError('NonMarkovBlock is intended only for subclassing')


class AddedBlock(Block):
    """The result of adding two blocks together.

    If `x` and `y` are two `stsb.Block`s, then `z = x + y` means that `z` is an `AddedBlock`.
    A call to `z.sample(...)` returns the result of `left.sample(...) + right.sample(...)`.

    Args:
        left (Block): the left addend
        right (Block): the right addend
    """
    
    num = 0
    
    def __init__(
        self,
        left,
        right,
    ):
        self.uid = get_id(self)
        self.left = left
        self.right = right
        self.t0 = self.left.t0
        self.t1 = self.right.t1
        super().__init__(t0=self.t0, t1=self.t1)
        
        self._maybe_add_blocks(
                ('left', self.left, inference.RealLine()),
                ('right', self.right, inference.RealLine()),
        )
        
    def __repr__(self,):
        string = f'Add({str(self.left)}, {str(self.right)})'
        return _add_fns_to_repr(self, string)
        
    def _sample(self, size=1):
        return self.left.sample(size=size,) + self.right.sample(size=size,)


class ChangepointBlock(Block):
    """Generates a single block combining two distinct block behaviors with a changepoint

    Suppose `u` and `v` are two blocks and `w = ChangepointBlock(u, v)`.
    Then this is equivalent to sampling from `u` from `t0` to `t^*`, sampling from `v` 
    from `t^*` to `t1`, and concatenating the result into a single array.
    The changepoint `t^*` is a free parameter to be set.
    It is set by the continuous parameter `frac` which must be bounded between 0 and 1.
    The changepoint is defined by `t^* = int(frac * (t1 - t0))`. A call to `forecast(...)` 
    is equivalent to calling `right.forecast(...)`.

    Args:
        left (Block): the left block in the changepoint, values of this before `t^*` will be used
        right (Block): the right block in the changepoint, values of this after `t^*` will be used
        frac (float, optional): the fractional position of the changepoint
    """

    num = 0

    def __init__(
        self,
        left,
        right,
        frac=None
    ):
        self.uid = get_id(self)
        self.left = left
        self.right = right
        self.frac = frac
        self.t0 = self.left.t0
        self.t1 = self.right.t1

        super().__init__(t0=self.t0, t1=self.t1)

        self._maybe_add_blocks(
            ('left', self.left, inference.RealLine()),
            ('right', self.right, inference.RealLine()),
            ('frac', self.frac, inference.Interval(0.0, 1.0)),
        )

    def __repr__(self):
        string = f"({str(self.left)} ~cp~ {self.right})"
        return _add_fns_to_repr(self, string)

    def _sample(self, size=1):
        left = self.left.sample(size=size)
        right = self.right.sample(size=size)

        if self.frac is None:
            frac = _make_1d(np.random.random(), size)
        else:
            frac = _make_1d(self.frac, size)
        
        # NOTE: this broadcasts so a vector changepoint distribution is possible
        changepoint = (frac * (self.t1 - self.t0)).astype(int)

        if changepoint.shape[0] == 1:
            return np.concatenate((
                left[:, :changepoint[0]], right[:, changepoint[0]:],
            ), axis=-1)
        
        # TODO: this is hideous. Can we clean this up somehow?
        cuts = np.empty((size, self.timesteps))
        for idx, cpt in enumerate(changepoint):
            cuts[idx] = np.concatenate((
                left[idx, :cpt], right[idx, cpt:],
            ), axis=-1)
        return cuts

    def _forecast(self, size=None, Nt=1,):
        if size is None:
            size = self.cache[0].shape[0]

        with effects.ForecastEffect(self, Nt=Nt):
            paths = self.right.sample(size=size)  # changepoint is fixed in the past
        return paths


class RandomWalk(Block):
    """Implements a random walk with drift. 

    The DGP of RandomWalk is `f(t) = f(t - 1) + loc + scale * w(t), f(0) = ic`, where
    `w` is standard normal distributed. Both loc and scale can be univariate parameters,
    vector parameters, or `Block`s to implement composition.

    Args:
        t0 (int): start timepoint
        t1 (int): end timepoint
        loc (None || Block || float || numpy.ndarray): if None, loc will be drawn from a standard normal
        scale (None || Block || float || numpy.ndarray): if None, scale will be drawn from a standard
            lognormal
        ic (None || float || numpy.ndarray): the initial condition. 
    """

    num = 0

    def __init__(
        self,
        t0=0,
        t1=2,
        loc=None,
        scale=None,
        ic=None,
    ):
        super().__init__(t0=t0, t1=t1)
        self.uid = get_id(self)
        self.loc = loc
        self.scale = scale
        self.ic = ic

        self._maybe_add_blocks(
            ('loc', self.loc, inference.RealLine()),
            ('scale', self.scale, inference.PositiveReal()),
            ('ic', self.ic, inference.RealLine()),
        )

    def __repr__(self,):
        string = f"RandomWalk({self.loc}, {self.scale}, {self.ic})"
        return _add_fns_to_repr(self, string)

    def _sample(self, size=1):
        these_timesteps = get_timesteps(self)
        if issubclass(type(self.loc), Block):
            loc = self.loc.sample(size=size)
        elif self.loc is None:
            loc = np.random.randn(size).reshape((-1, 1))
        else:
            loc = _make_2d(self.loc, size, these_timesteps)

        if issubclass(type(self.scale), Block):
            scale = self.scale.sample(size=size)
        elif self.scale is None:
            scale = np.exp(np.random.randn(size)).reshape((-1, 1))
        else:
            scale = _make_2d(self.scale, size, these_timesteps)

        if self.ic is None:
            ic = _make_1d(0.0, size)
        else:
            ic = _make_1d(self.ic, size)
        
        noise = loc + scale * np.random.randn(size, these_timesteps)
        return np.cumsum(noise, axis=-1) + ic.reshape((-1, 1))


class GlobalTrend(Block):
    """Implements a global trend model.

    The DGP of GlobalTrend is `f(t) = a + b * t`. Both `a` and `b` can be univariate parameters,
    multivariate parameters, or `Block`s. 

    Args:
        t0 (int): start timepoint
        t1 (int): end timepoint
        a (None || Block || float || numpy.ndarray): if None, a is drawn from a standard normal.
        b (None || Block || float || numpy.ndarray): if None, b is drawn from a standard normal.
    """

    num = 0

    def __init__(
        self,
        t0=0,
        t1=2,
        a=None,
        b=None,
    ):
        super().__init__(t0=t0, t1=t1)
        self.uid = get_id(self)
        self.a = a
        self.b = b

        self._maybe_add_blocks(
            ('a', self.a, inference.RealLine()),
            ('b', self.b, inference.RealLine()),
        )

    def __repr__(self,):
        string = f"GlobalTrend({self.a}, {self.b})"
        return _add_fns_to_repr(self, string)

    def _sample(self, size=1):
        these_timesteps = get_timesteps(self)
        if issubclass(type(self.a), Block):
            a = self.a.sample(size=size)
        elif self.a is None:
            a = np.random.randn(size).reshape((-1, 1))
        else:
            a = _make_2d(self.a, size, these_timesteps)

        if issubclass(type(self.b), Block):
            b = self.b.sample(size=size)
        elif self.b is None:
            b = np.random.randn(size).reshape((-1, 1))
        else:
            b = _make_2d(self.b, size, these_timesteps)

        time = np.linspace(self.t0, self.t1, these_timesteps)
        return a + b * time


class MA1(Block):
    """A moving average of order 1.

    The DGP for MA1 is `f(t) = loc + e[t] + theta * e[t - 1]`, where `e ~ Normal(0, scale^2)`. 
    Each of loc, scale, and theta can be univariate parameters, multivariate parameters, or `Block`s.

    Args:
        t0 (int): start timepoint
        t1 (int): end timepoint
        loc (None || Block || float || numpy.ndarray): if None, loc is distributed standard normal.
        scale (None || Block || float || numpy.ndarray): if None, scale is distributed standard 
            lognormal.
        theta (None || Block || float || numpy.ndarray): if None, theta is distributed standard normal.
    """

    num = 0

    def __init__(
        self,
        t0=0,
        t1=2,
        loc=None,
        scale=None,
        theta=None,
    ):
        super().__init__(t0=t0, t1=t1)
        self.uid = get_id(self)
        self.loc = loc
        self.scale = scale
        self.theta = theta

        self._maybe_add_blocks(
            ('loc', self.loc, inference.RealLine()),
            ('scale', self.scale, inference.PositiveReal()),
            ('theta', self.theta, inference.RealLine()),
        )

    def __repr__(self,):
        string = f"MA1({self.loc}, {self.scale}, {self.theta})"
        return _add_fns_to_repr(self, string)

    def _sample(self, size=1):
        these_timesteps = get_timesteps(self)
        if issubclass(type(self.loc), Block):
            loc = self.loc.sample(size=size)
        elif self.loc is None:
            loc = np.random.random(size=size).reshape((-1, 1)) \
                * np.ones((size, these_timesteps))
        else:
            loc = _make_2d(self.loc, size, these_timesteps)

        if issubclass(type(self.scale), Block):
            scale = self.scale.sample(size=size)
        elif self.scale is None:
            scale = np.exp(np.random.randn(size)).reshape((-1, 1)) \
                * np.ones((size, these_timesteps))
        else:
            scale = _make_2d(self.scale, size, these_timesteps)

        if issubclass(type(self.theta), Block):
            theta = self.theta.sample(size=size)
        elif self.theta is None:
            theta = np.random.random(size=size).reshape((-1, 1)) \
                * np.ones((size, these_timesteps))
        else:
            theta = _make_2d(self.theta, size, these_timesteps)

        noise = scale * np.random.randn(size, these_timesteps)
        front_noise = scale[..., 0].reshape((-1, 1)) * np.random.randn(size, 1)
        noise = np.concatenate((front_noise, noise), axis=-1)
        return loc + noise[..., 1:] + theta * noise[..., :-1]


class AR1(Block):
    """An autoregressive process of order 1.

    The DGP for AR1 is `f(t) = beta * f(t - 1) + scale * e(t), f(0) = ic`, 
    where `e` is a standard normal distributed vector. Both beta and scale can be 
    univariate parameters, multivariate parameters, or `Block`s.

    Args:
        t0 (int): start timepoint
        t1 (int): end timepoint
        beta (None || Block || float || numpy.ndarray): if None, beta is distributed standard normal
        scale (None || Block || float || numpy.ndarray): if None, scale is distributed standard 
            lognormal.
        ic (None || float || numpy.ndarray): if None, ic is distributed standard normal

    """

    num = 0

    def __init__(
        self,
        t0=0,
        t1=2,
        beta=None,
        scale=None,
        ic=None,
    ):
        super().__init__(t0=t0, t1=t1)
        self.uid = get_id(self)
        self.beta = beta
        self.scale = scale
        self.ic = ic
        
        self._maybe_add_blocks(
            ('beta', self.beta, inference.RealLine()),  # TODO: change this? 
            ('scale', self.scale, inference.PositiveReal()),
            ('ic', self.ic, inference.RealLine()),
        )

    def __repr__(self,):
        string = f"AR1({self.beta}, {self.scale}, {self.ic})"
        return _add_fns_to_repr(self, string)

    def _sample(self, size=1):
        these_timesteps = get_timesteps(self)
        if issubclass(type(self.beta), Block):
            beta = self.beta.sample(size=size)
        elif self.beta is None:
            beta = np.random.random(size=size).reshape((-1, 1)) \
                * np.ones((size, these_timesteps))
        else:
            beta = _make_2d(self.beta, size, these_timesteps)

        if issubclass(type(self.scale), Block):
            scale = self.scale.sample(size=size)
        elif self.scale is None:
            scale = np.exp(np.random.randn(size)).reshape((-1, 1)) \
                * np.ones((size, these_timesteps))
        else:
            scale = _make_2d(self.scale, size, these_timesteps)

        if self.ic is None:
            ic = _make_1d(0.0, size)
        else:
            ic = _make_1d(self.ic, size)

        paths = np.empty((size, these_timesteps))
        noise = scale * np.random.randn(size, these_timesteps)
        paths[:, 0] = ic + noise[:, 0]

        for t in range(1, these_timesteps):
            paths[:, t] = paths[:, t - 1] * beta[:, t] + noise[:, t]
        return paths
