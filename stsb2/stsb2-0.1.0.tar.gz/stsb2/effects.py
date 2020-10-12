
from . import util


def _effect_call(obj, fn):
    """Turns an effect handler defined as a context manager into a callable.

    Args:
        obj (Effect): an effect
        fn (callable): a callable
    """
    def wrapper(*args, **kwargs):
        obj.__enter__()
        result = fn(*args, **kwargs)
        obj.__exit__(None, None, None)  # NOTE: useless traceback etc.
        return result
    return wrapper


def effect(obj):
    """Convert an Effect object into a function decorator.

    Args:
        obj (Effect): an effect handler

    Returns:
        effect (callable): a decorator
    """
    return lambda x: _effect_call(obj, x)


def _forecast_on(obj, Nt):
    """Fast-forwards a Block-like object from sample to forecast mode.

    This does three things:
    1. t0 -> t1
    2. t1 -> t1 + Nt
    3. ic -> final condition (last value of cached draw)
    """
    setattr(obj, 't0', obj.t1 + 1)
    setattr(obj, 't1', obj.t1 + Nt + 1)

    if hasattr(obj, 'ic'):
        # TODO: should we draw a new sample?
        # this would involve drawing a new global sample and caching the old cache...
        setattr(obj, 'ic', obj.cache[-1][..., -1])


def _forecast_off(obj, t0, t1, ic):
    """Reverses a Block-like object from forecast to sample mode.

    This does three things:
    1. t1 -> t0
    2. t0 -> old t0
    3. ic -> old ic
    """

    setattr(obj, 't0', t0)
    setattr(obj, 't1', t1)

    if hasattr(obj, 'ic'):
        setattr(obj, 'ic', ic)


class Effect:
    """A context manager that changes the interpretation of an STS call.
    """

    def __init__(self, *args, **kwargs):
        ...

    def __call__(self, fn):
        return _effect_call(self, fn)


class ForecastEffect(Effect):
    """Effect handler for forecasting tasks.

    From start to finish, the forecast operation consists of 
    + turning off caching
    + fast-forwarding time
    + (possibly) intervening on all free parameters
    + calling sample
    + (possibly) reverting free parameter values
    + reversing time
    + resuming caching

    Args:
        root (block): the root of the STS graph
        Nt (int >= 1): number of timesteps to forecast
    """

    def __init__(self, root, Nt=1):
        self.root = root
        self.Nt = Nt

        self.nodes = util.get_nodes_from_root(self.root)
        self.ics = [k.ic if hasattr(k, 'ic') else None for k in self.nodes]
        self.t0s = list()
        self.t1s = list()

    def __enter__(self,):
        for node in self.nodes:
            self.t0s.append(node.t0)
            self.t1s.append(node.t1)
            _forecast_on(node, self.Nt)
        util.set_cache_mode(self.root, False)

    def __exit__(self, type, value, traceback):
        for node, t0, t1, ic in zip(
            self.nodes, self.t0s, self.t1s, self.ics,
        ):
            _forecast_off(node, t0, t1, ic)
        util.set_cache_mode(self.root, True)


class ProposalEffect(Effect):
    """Effect handler for evaluating proposals.

    From start to finish, the proposal operation consists of
    + intervening on each free parameter
    + turning off caching
    + <sampling and other operations>
    + turning on caching
    + replacing old parameter values

    Args:
        root (Block): the root of the STS graph
    """

    def __init__(self, root,):
        self.root = root
        nodes, params, bounds = util.get_free_parameters_from_root(self.root)
        self.nodes = nodes
        self.params = params
        self.bounds = bounds

        self.old_params = dict()

    def __enter__(self,):
        for node, param in zip(self.nodes, self.params):
            self.old_params[node] = [getattr(node, p) for p in param]
        util.set_cache_mode(self.root, False)
    
    def __exit__(self, type, value, traceback):
        for node, param in zip(self.nodes, self.params):
            for i, p in enumerate(param):
                setattr(node, p, self.old_params[node][i])
        util.set_cache_mode(self.root, True)


class __ForecastEffect(Effect):
    """DEPRECATED
    Effect handler for forecasting-like tasks

    Temporarily turns off caching and intervenes on the `root.<param>` with 
    the passed `<param>` value. Turns caching back on upon exit.

    Args:
        root (stsb.Block): the root block
        ic (numpy.ndarray): value of the initial condition from which to start forecasting
    """

    def __init__(self, root, **kwargs):
        super().__init__()
        self.root = root
        self.new_kwargs = kwargs

        self.old_kwargs = dict()

    def __enter__(self,):
        for k, v in self.new_kwargs.items():
            if v is not None:
                self.old_kwargs[k] = getattr(self.root, k)
                setattr(self.root, k, v)
        util.set_cache_mode(self.root, False)

    def __exit__(self, type, value, traceback):
        for k, v in self.old_kwargs.items():
            setattr(self.root, k, v)
        util.set_cache_mode(self.root, True)


class InterveneEffect(Effect):
    """Effect handler for intervening on a single STS node.

    + Replace the node's free parameters with kwargs
    + <perform some operations>
    + Reset to original free parameter values

    Args:
        node (Block): node on which to intervene
        kwargs (dict): {param_name: new_param_val, ...}
    """

    def __init__(self, node, **kwargs):
        super().__init__()
        self.node = node
        self.kwargs = kwargs

        self.old_kwargs = dict()

    def __enter__(self,):
        for k, v in self.kwargs.items():
            self.old_kwargs[k] = getattr(self.node, k)
            if v == 'cache':
                setattr(self.node, k, self.node.cache[0][..., -1])
            else:
                setattr(self.node, k, v)

    def __exit__(self, type, value, traceback):
        for k, v in self.old_kwargs.items():
            setattr(self.node, k, v)
