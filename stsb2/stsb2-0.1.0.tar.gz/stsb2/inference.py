
import abc
import collections

import numpy as np
from scipy import stats

from . import util
from . import effects


def gen_str_param_names(root):
    """Generates string parameter names.

    This is mainly useful for plotting or downstream work in other libraries.

    Args:
        root (Block): a block. Parameter names will be generated for this nodes and all of
            its predecessors in the compute graph.

    Returns:
        names (list[string]): list of parameter names
    """
    blocks, params, bounds = util.get_free_parameters_from_root(
        root
    )
    names = [[x.uid + '-' + p for p in param] for x, param in zip(blocks, params)]
    return names


def dist_suggestion(bound):
    """Suggests proposal / guide distribution given a Bound.

    This is very basic. Suggests a Normal for infinite support, LogNormal for 
    half-infinite (positive half-line) support, and Beta distribution for support
    on [0, 1]. Returns `None` otherwise.

    Args:
        bound (Bound): the bound for which a distribution is desired

    Returns:
        distribution (Distribution1D): a distribution class
    """
    if type(bound) is RealLine:
        return NormalDistribution1D
    if type(bound) is PositiveReal:
        return LogNormalDistribution1D
    if type(bound) is Interval:
        if (bound.lower == 0.0) and (bound.upper == 1.0):
            return BetaDistribution1D
        return None


class Bound1D:
    """Object describing the support of a univariate distribution. 

    Bounds must implement __call__, yielding a (lower, upper) tuple, and 
    __contains__(...), returning True if lower < ... < upper. Bound1D is
    designed to be subclassed.
    """

    def __init__(self,):
        self.upper = None
        self.lower = None

    def __repr__(self,):
        return f"Bound1D({self.lower}, {self.upper})"

    def __call__(self,):
        return (self.lower, self.upper)

    def __contains__(self, item):
        return (item >= self.lower) and (item <= self.upper)


class RealLine(Bound1D):
    """See documentation of Bound1D.

    (-infinity, infinity)
    """

    def __init__(self,):
        super().__init__()
        self.lower = -np.inf
        self.upper = np.inf

    def __repr__(self,):
        return f"RealLine()"


class PositiveReal(Bound1D):
    """See documentation of Bound1D.

    (0, infinity)
    """

    def __init__(self,):
        super().__init__()
        self.lower = 0.0
        self.upper = np.inf

    def __repr__(self,):
        return f"PositiveReal()"


class Interval(Bound1D):
    """See documentation of Bound1D.

    (lower, upper)
    """

    def __init__(self, lower, upper):
        super().__init__()
        self.lower = lower
        self.upper = upper

    def __repr__(self,):
        return f"Interval({self.lower}, {self.upper})"


class Distribution1D: 
    """A 1d probability distribution. 

    This essentially provides an interface to scipy.stats.<distribution_name> and adds 
    the ability to update parameters (useful for, e.g., variational inference).
    """

    def __init__(self,):
        ...

    def __call__(self, size=1):
        return self.sample(size=size)

    def update_parameters(self, **kwargs):
        """Updates the parameters of the distribution. 

        Args:
            kwargs (dict, optional): {param_name: param_value, ...}
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
            self._init_dist()

    @abc.abstractmethod
    def _init_dist(self,):
        ...

    @abc.abstractmethod
    def sample(self, size=1):
        """Returns a sample from the distribution. 

        Sample is of shape (size,)

        Args:
            size (int >= 1): number of samples to return

        Returns:
            sample (float || numpy.ndarray): a sample from the distribution
        """
        ...

    @abc.abstractmethod
    def lpdf(self, x):
        """Returns the log probability of `x` under the distribution. 

        Args:
            x (float || numpy.ndarray): a value to score

        Returns:
            lpdf (float || numpy.ndarray): the log probability of the value
        """
        ...


class ProductDistribution1D(Distribution1D):
    """See documentation of Distribution1D.

    A factorization q(z) = \prod_n q_n(z_n). 

    Args:
        distributions (iterable[Distribution1D]): the 1d distributions
    """

    def __init__(self, *distributions):
        super().__init__()
        self.distributions = distributions

    def _init_dist(self,):
        for dist in self.distributions:
            dist._init_dist()

    def sample(self, size=1):
        """See doocumentation of Distribution1D.

        Returns:
            sample (numpy.ndarray): shape is (size, len(distributions))
        """
        return np.stack([
            dist(size=size) for dist in self.distributions
        ], axis=-1)
    
    def lpdf(self, x):
        """See documentation of Distribution 1D.

        log q(z) = \sum_n log q_n(z_n).
        """
        return sum(
            [dist.lpdf(x[..., i]) for i, dist in enumerate(self.distributions)]
        )


class NormalDistribution1D(Distribution1D):
    """See documentation of Distribution1D.

    A normal distribution. 

    Args:
        loc (float || numpy.ndarray): the mean of the distribution
        log_scale (float || numpy.ndarray): the log standard deviation of the distribution
    """

    def __init__(self, loc=0.0, log_scale=0.0):
        super().__init__()
        self.loc = loc
        self.log_scale = log_scale
        
        self._init_dist()
        
    def _init_dist(self,):
        self.dist_object = stats.norm(self.loc, np.exp(self.log_scale))
    
    def sample(self, size=1):
        """See doocumentation of Distribution1D.

        Returns:
            sample (numpy.ndarray): shape is (size, len(distributions))
        """
        return self.dist_object.rvs(size=size)

    def lpdf(self, x):
        """See documentation of Distribution1D. 
        """
        return self.dist_object.logpdf(x)


class LogNormalDistribution1D(Distribution1D):
    """See documentation of Distribution1D.

    A log-normal distribution. 

    Args:
        loc (float || numpy.ndarray): the mean of the underlying normal distribution
        log_scale (float || numpy.ndarray): the log standard deviation of the underlying 
        normal distribution
    """

    def __init__(self, loc=0.0, log_scale=0.0):
        super().__init__()
        self.loc = loc
        self.log_scale = log_scale
        
        self._init_dist()

    def _init_dist(self,):
        self.dist_object = stats.lognorm(np.exp(self.log_scale), scale=np.exp(self.loc))
    
    def sample(self, size=1):
        """See doocumentation of Distribution1D.

        Returns:
            sample (numpy.ndarray): shape is (size, len(distributions))
        """
        return self.dist_object.rvs(size=size)

    def lpdf(self, x):
        """See documentation of Distribution1D. 
        """
        return self.dist_object.logpdf(x)


class BetaDistribution1D(Distribution1D):
    """See documentation of Distribution1D.

    A beta distribution. 

    Args:
        log_alpha (float): the log of the alpha parameter of the beta distribution
        log_beta (float): the log of the beta parameter of the beta distribution
    """

    def __init__(self, log_alpha=0.0, log_beta=0.0):
        super().__init__()
        self.log_alpha = log_alpha 
        self.log_beta = log_beta

        self._init_dist()

    def _init_dist(self,):
        self.dist_object = stats.beta(
            np.exp(self.log_alpha), np.exp(self.log_beta)
        )

    def sample(self, size=1):
        """See doocumentation of Distribution1D.

        Returns:
            sample (numpy.ndarray): shape is (size, len(distributions))
        """

        return self.dist_object.rvs(size=size)

    def lpdf(self, x):
        """See documentation of Distribution1D. 
        """
        return self.dist_object.logpdf(x)


class Guide:
    """A `Guide` is a collection of distributions that knows something 
    about an underlying graph of blocks. 

    It can be used as a prior or as a variational posterior (which is where the name Guide 
    comes from, c.f. the Pyro language). `Guide`s contain a collection of `Distribution1D`s
    and track the behavior of all `Block`s and free parameters in the compute graph.

    Args:
        root (Block): a block. Will be treated as the root of a graph and all predecessor 
            nodes in the graph will be tracked.
    """

    def __init__(self, root):
        self.root = root
        free_blocks, free_parameters, free_bounds = util.get_free_parameters_from_root(self.root)
        self.free_blocks = free_blocks
        self.free_parameters = free_parameters
        self.free_bounds = free_bounds 

        self.distributions = dict()
        

class AutoGuide(Guide):
    """A `Guide` that attempts to automate the definition of distributions. 

    `AutoGuide` tries to define a distribution for each free parameter in the graph it's
    tracking. If it's unable to do this, it tags that parameter as unmodeled for later
    custom modeling.

    Args:
        root (Block): a block. Will be treated as the root of a graph and all predecessor 
            nodes in the graph will be tracked.
    """

    def __init__(self, root):
        super().__init__(root)

        self.unmodeled = dict()

        for block, parameters, bounds in zip(
            self.free_blocks,
            self.free_parameters,
            self.free_bounds,
        ):
            self.distributions[block] = dict()
            self.unmodeled[block] = list()

            for param, bound in zip(parameters, bounds):
                suggested_dist = dist_suggestion(bound)
                if suggested_dist is not None:
                    self.distributions[block][param] = suggested_dist()
                else:
                    self.unmodeled[block].append(param)
            if self.distributions[block] == dict():
                del self.distributions[block]

    def sample(self, size=1):
        """See documentation of ProductDistribution.sample(...)

        Args:
            size (int >= 1): number of draws to sample
        """
        rv = list()
        for block, params in self.distributions.items():
            for param, dist in params.items():
                draw = dist.sample(size=size)
                rv.append(draw)
        return np.array(rv)

    def set_model_rvs(self, draw):
        """Sets free parameter values of the underlying STS graph. 

        Args:
            draw (numpy.ndarray): a draw from the `Guide`
        """
        i = 0
        for block, params in self.distributions.items():
            for param, dist in params.items():
                setattr(block, param, draw[i])
                i += 1

    def lpdf(self, draw):
        """See documentation of Distribution1D.lpdf(...)

        log p = \sum_n \log p_n, where the sum runs over all free
        parameters of the underlying STS graph.

        Args:
            draw (numpy.ndarray): a draw from the `Guide`
        """
        log_prob_sum = 0.0
        i = 0
        for block, params in self.distributions.items():
            for param, dist in params.items():
                lpdf = dist.lpdf(draw[i])
                log_prob_sum += lpdf
                i += 1
        return log_prob_sum


class QuasiLikelihood:
    """A callable that can be treated as the data likelihood function

    The idea of a quasilikelihood is that, even though we don't actually know what 
    the data likelihood is, we can manufacture a function that is plausible. 
    For example, if we observe an unbounded time series, we could conjecture a
    noisy observation model that we parameterize as a Gaussian state space model.
    All `QuasiLikelihood`s must implement lpdf, which returns the (quasi)likelihood of
    draws given the observed data, and `__call__`, which calls `lpdf`.

    Args:
        data (numpy.ndarray): observed data
    """
    
    def __init__(
        self,
        data,
    ):
        self.data = data
        
    @abc.abstractmethod
    def lpdf(self, draws,):
        ...
        
    def __call__(self, draws,):
        return self.lpdf(draws,)


class GaussianQuasiLikelihood(QuasiLikelihood):
    """See documentation of QuasiLikelihood. 

    A gaussian state space quasilikelihood. 

    Args:
        data (numpy.ndarray): observed data
        std_mode (string): one of 'rolling', 'constant'. If 'rolling', will be computed 
            using a windowed rolling standard deviation of the differences of the 
            observed data. If 'constant', will be equal to the standard deviation of the 
            observed data.
    """
    
    def __init__(
        self,
        data,
        std_mode='rolling',
    ):
        super().__init__(data,)
        if len(self.data.shape) == 1:
            self.data = self.data.reshape((1, -1))
        if std_mode == 'constant':
            self.sigma = util._constant_std(data.flatten()) \
                * np.ones(data.shape[-1])
        elif std_mode == 'rolling':
            try:
                self.sigma = util._rolling_std(data)
            except ValueError:
                raise NotImplementedError(
                    'Currently only 1d time series are supported'
                    ' Try calling .flatten()'
                )
        else:
            raise ValueError(
                'std must be one of "constant" or "rolling"'
            )
        self.prec = np.linalg.pinv(np.diag(self.sigma ** 2.0))        
        
    def lpdf(self, draws, reduce_=True):
        """See documentation of QuasiLikelihood.lpdf(...).

        Args:
            draws (numpy.ndarray): draws from a model
            reduce_ (bool): if reduce_, returns the average lpdf
        """
        diff = self.data - draws
        lpdfs = np.apply_along_axis(
            lambda x: x.T.dot(self.prec).dot(x),
            1,
            diff
        )
        
        if reduce_:
            return -0.5 * lpdfs.mean()
        return -0.5 * lpdfs


class EpsilonStrategy:
    """The strategy for setting the tolerance in ABC.

    All `EpsilonStrategy` must implement `__call__`, which returns 
    the current epsilon value. 
    """

    def __init__(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class ConstantEpsilon(EpsilonStrategy):
    """See documentation for EpsilonStrategy. 

    A fixed, constant epsilon value.

    Args:
        eps (float >= 0.0): the acceptance threshold
    """

    def __init__(self, eps=0.0):
        self.eps = eps

    def __call__(self, iteration,):
        return self.eps


class ABCDistanceMetric:
    """A distance metric for use in approximate sampling.

    All `ABCDistanceMetric` must implement `accept(...)`, which returns 
    an array of indices of the sample that should be accepted.

    Args:
        eps (EpsilonStrategy): the threshold class
        eps_kwargs (dict): keyword arguments to pass to the EpsilonStrategy
    """

    def __init__(
        self,
        *args,
        eps=ConstantEpsilon,
        eps_kwargs=dict()
    ):
        self.eps = eps(**eps_kwargs)

    @abc.abstractmethod
    def accept(self, *args, **kwargs):
        ...


class MSEDistanceMetric(ABCDistanceMetric):
    """See documentation of ABCDistanceMetric

    (x, y) -> ((x - y) ** 2.0).mean() is the distance function.

    Args:
        eps (EpsilonStrategy): the threshold class
        eps_kwargs (dict): keyword arguments to pass to the EpsilonStrategy

    """

    def accept(self, data, draws, iteration):
        """Whether to accept the draws given the data. 

        Args:
            data (numpy.ndarray): observed data
            draws (numpy.ndarray): draws from a model
            iteration (int >= 0): iteration of sampling

        Returns:
            accept (numpy.ndarray): an array of indices of the sample that should be
                accepted
        """
        score = ((data - draws) ** 2.0).mean()
        return np.where(score < self.eps(iteration))


class GaussianDistanceMetric(
    GaussianQuasiLikelihood, ABCDistanceMetric
):
    """See documentation of ABCDistanceMetric

    (x, y) -> log MultivariateNormalLikelihood(x, y; cov) is the distance function.

    Args:
        data (numpy.ndarray): observed data
        eps (EpsilonStrategy): the threshold class
        eps_kwargs (dict): keyword arguments to pass to the EpsilonStrategy
    """

    def __init__(
        self,
        data, 
        eps=ConstantEpsilon,
        eps_kwargs=dict(),
    ):
        GaussianQuasiLikelihood.__init__(self, data)
        ABCDistanceMetric.__init__(self, eps=eps, eps_kwargs=eps_kwargs)

    def accept(self, draws, iteration,):
        """Whether to accept the draws given the data. 

        Args:
            draws (numpy.ndarray): draws from a model
            iteration (int >= 0): iteration of sampling

        Returns:
            accept (numpy.ndarray): an array of indices of the sample that should be
                accepted

        """
        score = self.lpdf(draws, reduce_=False)
        return np.where(-score < self.eps(iteration))


class Sampler:
    """Base class for all samplers.

    Args:
        niter (int >=0 || None): number of iterations to run the sampler
        nsample (int >= 0 || None): number of draws from the (approximate) posterior
        verbosity (float >=0): status messages are printed `verbosity` fraction of
            the time
    """

    def __init__(
        self, *args, **kwargs
    ):
        self.niter = kwargs.get('niter', None)
        self.nsample = kwargs.get('nsample', None)
        self.verbosity = kwargs.get('verbosity', 0.01)
        
        self.prior_samples = list()
        self.likelihood_samples = list()
        self.posterior_samples = list()

    @abc.abstractmethod
    def sample(self, *args, **kwargs):
        ...
    
    def _empirical_joint(self,):
        return self.prior_samples, self.likelihood_samples


class ABCSampler(Sampler):
    """See the documentation of Sampler.

    Uses approximate Bayesian computation rejection sampling to sample from the 
    approximate posterior / posterior predictive distributions. Should only be used
    when data is already observed since draws from the prior can be made with calls
    to `series(...)`.

    Args:
        series (Block): the root of the DGP
        data (numpy.ndarray): the observed data
        guide (Guide): the proposal distribution
        metric (Metric): initialized acceptance metric object
        niter (int >= 0 || None): number of iterations for which to run sampler
        nsample (int >=0 || None): number of draws to make. If this argument is
            not None, then `niter` is not used
        verbosity (float >= 0): status messages are printed `verbosity` fraction
            of the time
    """

    def __init__(
        self,
        series,
        data=None,
        guide=None,
        metric=None,
        niter=None,
        nsample=100,
        verbosity=0.01,
    ):
        super().__init__(
            niter=niter,
            nsample=nsample,
            verbosity=verbosity
        )

        self.series = series
        self.data = data

        if (guide is None) and (data is not None):
            guide = AutoGuide(self.series)
        self.guide = guide

        if (metric is None) and (data is not None):
            metric = MSEDistanceMetric(
                eps_kwargs={
                    'eps': 0.5 * np.var(self.data)
                }
            )
        self.metric = metric

        nodes, params, bounds = util.get_free_parameters_from_root(self.series)
        self.nodes = nodes
        self.params = params
        self.bounds = bounds

        self.iverbose = int(1.0 / verbosity)

    def _mc_sample(self, niter):
        posterior = list()
        ppd = list()
        
        for n in range(niter):
            with effects.ProposalEffect(self.series):
                draw = self.guide.sample()
                util.set_all_values(draw, self.nodes, self.params)
                sample = self.series.sample(size=1)
                accept = self.metric.accept(self.data, sample.flatten(), n)[0]
                
                if len(accept) > 0:
                    posterior.append(draw.flatten())
                    ppd.append(sample.flatten())
                    
            if n % self.iverbose == 0:
                print(f"On iteration {n}, so far {len(ppd)} samples")
                    
        return np.array(posterior), np.array(ppd)

    def _lv_sample(self, nsample):
        posterior = list()
        ppd = list()
        
        n_total = 0
        n = 0
        while n_total < nsample:
            with effects.ProposalEffect(self.series):
                draw = self.guide.sample()
                util.set_all_values(draw, self.nodes, self.params)
                sample = self.series.sample(size=1)
                accept = self.metric.accept(self.data, sample.flatten(), n)[0]
                
                if len(accept) > 0:
                    posterior.append(draw.flatten())
                    ppd.append(sample.flatten())
                    n_total += 1
                    
            n += 1
            if n % self.iverbose == 0:
                print(f"On iteration {n}, so far {len(ppd)} samples")
                    
        return np.array(posterior), np.array(ppd)

    def sample(self, nsample=None, niter=None):
        """Samples from the approximate posterior. 

        If `nsample` is passed, then a las vegas sampling algorithm is used
        (the sampler will return `nsample` draws, but there is no time bound
        on how long this will take). If `nsample` is None and `niter` is an 
        integer, then a monte carlo sampling algorithm is used (the sampler
        will run for only `niter` iterations and a random number >= 0 samples
        will be returned)

        Args:
            nsample (int >= 0 || None): number of samples to draw
            niter (int >= 0 || None): number of iterations to run the sampler
        """
        if self.data is None:
            raise ValueError("To sample from prior, just call series.sample(...)")

        if niter is None:
            if nsample is None:
                nsample = self.nsample
            return self._lv_sample(nsample)
        else:
            if niter is None:
                niter =  self.niter
            return self._mc_sample(niter)
        
