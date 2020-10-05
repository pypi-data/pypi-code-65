"""
################################################################################

    Copyright (C) 2012-2020, Michele Cappellari
    E-mail: michele.cappellari_at_physics.ox.ac.uk

    Updated versions of the software are available from my web page
    http://purl.org/cappellari/software

    If you have found this software useful for your research,
    I would appreciate an acknowledgement to the use of the
    "adamet Python package of Cappellari et al. (2013), which implements
     the Adaptive Metropolis algorithm of Haario et al. (2001)".

    This software is provided as is without any warranty whatsoever.
    Permission to use, for non-commercial purposes is granted.
    Permission to modify for personal or internal use is granted,
    provided this copyright and disclaimer are included unchanged
    at the beginning of the file. All other rights are reserved.
    In particular, redistribution of the code is not allowed.

################################################################################

MODIFICATION HISTORY:
    V1.0.0: Michele Cappellari, Oxford, 27 January 2012
    V1.1.0: Implemented Adaptive Metropolis Algorithm. MC, Oxford, 10 February 2012
    V1.2.0: Add diagonal matrix to prevent possibly degenerate covariance matrix.
        MC, Oxford, 10 August 2012
    V1.2.1: Do not sort likelihood in output. MC, Oxford, 25 October 2012
    V2.0.0: Translated from IDL into Python . MC, Atlantic Ocean, 9 February 2014
    V2.0.1: Clip input parameters to bounds. MC, Oxford, 18 February 2015
    V2.0.2: Allow for both args and kwargs parameter to the user function.
        Dropped Python 2.7 support. Minor code refactoring.
        MC, Oxford, 13 October 2017
    V2.0.3: First released version. Organized into a package.
        MC, Oxford, 25 April 2018
    V2.0.4: Ensures the user function cannot affect the random chain.
        MC, Oxford, 27 April 2018
    V2.0.5: Some changes to the input format. MC, Oxford, 4 May 2018
    V2.0.6: Fixed clock DeprecationWarning in Python 3.7.
        MC, Oxford, 27 September 2018
    V2.0.7: Written complete docstring documentation.
        MC, Oxford, 4 March 2020

"""

import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter as clock

from adamet.corner_plot import corner_plot

###############################################################################

def _move(pars, sigpars, all_pars, prng):
    """
    Adaptive move

    """
    nu = np.unique(all_pars[:, 0]).size
    npars = pars.size

    # Accumulate at least as many *accepted* moves as the
    # elements of the covariance matrix before computing it.
    if nu > npars*(npars + 1.)/2.:

        eps = 0.01
        diag = np.diag((sigpars*eps)**2)
        cov = 2.38**2/npars*(np.cov(all_pars.T) + diag)
        pars = prng.multivariate_normal(pars, cov)

    else:

        pars = prng.normal(pars, sigpars)

    return pars

###############################################################################

def _metro(lnprob_fun, pars, bounds, lnprob, try_pars, prng, args, kwargs):
    """
    Metropolis step

    """
    # Moves out of bounds are rejected without function evaluation
    if np.all((try_pars >= bounds[0]) & (try_pars <= bounds[1])):

        try_lnprob = lnprob_fun(try_pars, *args, **kwargs)
        lnran = np.log(prng.uniform())
        lnratio = try_lnprob - lnprob

        if (try_lnprob > lnprob) or (lnran < lnratio):

            pars = try_pars   # Candidate point is accepted
            lnprob = try_lnprob

    return pars, lnprob

###############################################################################

def adamet(lnprob_fun, pars, sigpars, bounds, nstep,
           labels=None, nprint=100, quiet=False, fignum=None, plot=True,
           labels_scaling=1, seed=None, args=(), kwargs={}):
    """
    AdaMet Purpose
    --------------

    This is the implementation by
    `Cappellari et al. (2013) <https://ui.adsabs.harvard.edu/abs/2013MNRAS.432.1709C>`_
    of the Adaptive Metropolis algorithm by
    `Haario H., Saksman E., Tamminen J. (2001) <https://doi.org/10.2307/3318737>`_
    for Bayesian analysis.

    Usage Example
    -------------

    To learn how to use ``AdaMet`` run the example program in the
    ``adamet/examples`` directory, within the main package installation
    folder inside ``site-packages``, and read the detailed documentation
    in the docstring of the file ``adamet.py`` or on
    `PyPi <https://pypi.org/project/adamet/>`_.

    Note: For dimensions = 1 to 6, the optimal acceptance rates are
    `rate = [0.441, 0.352, 0.316, 0.279, 0.275, 0.266]`
    and the asymptotic value for many parameters is 23%

    Calling Sequence
    ----------------

    .. code-block:: python

        pars, lnprob = adamet(lnprob_fun, pars0, sigpars0, bounds, nstep,
           labels=None, nprint=100, quiet=False, fignum=None, plot=True,
           labels_scaling=1, seed=None, args=(), kwargs={})

    Input Parameters
    ----------------

    lnprob_fun: callable
        This function returns the natural logarithm of the conditional
        probability of the model, given the data::

            P(model | data) ~ P(data | model) P(model)

    pars0: array_like with shape (n,)
        vector with the mean of the multivariate Gaussian describing the
        proposal distribution from which samples are drawn.
        For maximum efficiency, this initial Gaussian should approximate the
        posterior distribution. This suggests adopting as `pars0` an initial
        guess for the model best-fitting parameters.
    sigpars0: array_like with shape (n,)
        vector with the dispersion `sigma` of the multivariate Gaussian
        describing the proposal distribution.
        For maximum efficiency, this initial Gaussian should approximate the
        posterior distribution. This suggests adopting as `sigpars` an initial
        guess of the uncertainty in the model parameters `pars`.
    bounds: 2-tuple of array_like
        Lower and upper bounds on independent variables. Each array must match
        the size of `pars`. The model probability is set to zero outside the
        bounds. This keyword is also used to define the plotting ranges.
    nsteps: integer
        Number of attempted moves in the chain. Typical numbers are a few
        thousands `nsteps`.


    Optional Keywords
    -----------------

    labels: array_like with shape (n,)
        String labels for each parameter to be used in the `corner_plot`
    nprint: integer
        Specifies the frequency for the intermediate plots, in moves.
        A typical value could be `nstep/10`.
    plot: boolean, optional
        Specifies whether to show a plot of the results or not.
    fignum: integer, optional
        Specifies the figure number for the plot.
    labels_scaling: float
        Relative scaling for the plotting labels.
    seed: integer
        Seed for the random generator. Specify this value for a repeatable
        random sequence.
    args, kwargs: tuple and dict, optional
        Additional arguments passed to `lnprob_fun`. Both empty by default.
        The calling signature is `lnprob_fun(x, *args, **kwargs)`.

    Output Parameters
    -----------------

    pars: array_like with shape (nsteps, n)
        Posterior distribution for the model parameters
    lnprob: array_like with shape (nsteps, n)
        Logarithm of the probbaility of the model, given the data, for each set
        of parameters in the posterior distribution `pars`.

    """

    pars = np.array(pars)  # Make copy to leave input unchanged
    sigpars = np.array(sigpars)
    bounds = np.array(bounds)

    assert pars.size == sigpars.size == bounds.shape[1], \
        "pars, sigpars, and bounds[1] must have the same size"

    if labels is not None:
        assert len(labels) == pars.size, "There must be one label per parameter"

    prng = np.random.RandomState(seed)  # Random stream independent of global one

    t = clock()

    pars = pars.clip(*bounds)  # clip parameters within bounds
    lnprob = lnprob_fun(pars, *args, **kwargs)
    all_pars = np.zeros((nstep, pars.size))
    all_lnprob = np.zeros(nstep)
    all_try_pars = np.zeros_like(all_pars)

    if plot:
        fig = corner_plot(all_pars, init=True, fignum=fignum)
        plt.pause(0.01)

    for j in range(nstep):

        try_pars = _move(pars, sigpars, all_pars[:j], prng)
        pars, lnprob = _metro(lnprob_fun, pars, bounds, lnprob, try_pars, prng, args, kwargs)

        all_pars[j] = pars  # Store only accepted moves or duplicates (when move is rejected)
        all_lnprob[j] = lnprob
        all_try_pars[j] = try_pars  # Store all attempted moves for plotting parameters coverage

        if ((j + 1) % nprint) == 0: # Just plotting/printing inside this block

            nu = np.unique(all_pars[:j, 0]).size
            if quiet is False:
                print('adamet: %0.1f %% done; %0.1f %% accepted' % 
                        (100.*(j + 1)/nstep, 100.*nu/(j + 1)))

            if plot and j > 1:
                corner_plot(all_pars[:j], all_lnprob[:j], xstry=all_try_pars[:j],
                            labels=labels, extents=bounds, fig=fig,
                            labels_scaling=labels_scaling)
                plt.pause(0.01)

    if quiet is False:
        print('adamet: done. Total time %0.2f seconds' % (clock() - t))

    return all_pars, all_lnprob

###############################################################################
