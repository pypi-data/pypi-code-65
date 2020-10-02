"""Ref: Improving the Uncertainty Quantifcation of Sliced Normal
Distributions by Scaling the Covariance matrix Colbert et al 2020

This module enables the creation of sliced normal distributions, which are
approximations of probabilistic data distributions. They are capable of
modelling complex dependence structures at high dimensions, and require only a
specified degree of freedom and, in the case of the scaled sliced normal, a
number of samples to draw from across the support.

Samples are monomially expanded from physical space into into a feature space,
and the mean snd covariance of the resulting distribution is estimated as
approximately Gaussian. The density in feature space can then be collapsed back
into physical space if required by estimating the normalisation constant of the
feature space Gaussian.

basic_sn returns the feature space mean and covariance. This is efficient but
often lacks accuracy.

scaled_sn scales the covariance by a scalar gamma, determined through an
optimisation procedure using the normalisation constant estimator. This
produces a much better fit but is computationally expensive.

sn_phi will return a map of the unnormalised feature space density for points
on the support.

phi returns the physical space density of a data point which has had the mean
subtracted from it.

nearest_psd finds a positive semi-definite matrix which is clsoe to the
provided matrix. This is necessary to get around computational issues when
dealing with a large matrix, but introduces some computational cost.

z_expand returns a map of the feature space equivalents of physical space
points.

"""
from itertools import combinations_with_replacement as cwr
from itertools import chain
from functools import reduce
from operator import mul, sub, neg
from scipy.optimize import minimize as scimin
import numpy as np
from slicednormals import hyper_ellipse as he


class basic_sn():
    """Returns the feature space mean and covariance. This is efficient but often lacks accuracy."""
    def __init__(self, data, dof):
        if isinstance(data[0], (int, float)):
            self.data = [[d] for d in data]
        else:
            self.data = data
        self.dof = dof
        self.mu = None
        self.sigma = None
        self.z_data = np.array(z_expand(self.data, self.dof))
        self.mu = np.mean(self.z_data, 0)
        self.sigma = nearest_psd(np.cov(self.z_data, ddof=1, rowvar=False))

    def sn_phi(self, data, mapped=False):
        """ Returns the unnormalised feature space log density of a
        given point in physical space."""
        if isinstance(data, (int, float)):
            data = [[data]]
        elif (
            isinstance(data, (np.ndarray, list)) and
            isinstance(data[0], (int, float))):
                if len(self.data[0]) > 1:
                    data = [data]
                else:
                    data = [[d] for d in data]
        assert len(data[0]) == len(self.data[0]), 'Incorrect dimensions'
        dlen = len(data)

        z_data = z_expand(data, self.dof, mapped=True)
        if mapped:
            return map(phi, map(sub, z_data, [self.mu]*dlen), [self.sigma]*dlen)
        else:
            return list(map(phi, map(sub, z_data, [self.mu]*dlen), [self.sigma]*dlen))

class scaled_sn(basic_sn):
    """ Sliced normal with a scaled covariance, optimised using an estimate of
    the normalisation constant. Increasing no_supp_samples improves this
    estimation, but each point must be expanded and evaluated for density, so
    this increases computational cost quite significantly."""
    def __init__(self, data, dof, no_supp_samples, retain_supp_samples=False):
        super().__init__(data, dof)
        if retain_supp_samples:
            if isinstance(data[0], (float, int)):
                self.supp_samples = [[d] for d in (
                    np.random.rand(no_supp_samples)*(max(data)-min(data))*1.5
                    )+1.25*min(data)-0.25*max(data)]
            else:
                self.hyper_ellipse = he(data=self.data)
                self.supp_samples = self.hyper_ellipse.sample(no_supp_samples)
            self.z_supp_samples = map(
                sub,
                z_expand(self.supp_samples, self.dof, mapped=True),
                [self.mu]*no_supp_samples
                )
            self.z_supp_phi = np.array(
                list(
                    map(phi,
                        self.z_supp_samples,
                        [self.sigma]*no_supp_samples)
                    )
                )
            self.z_data_phi_sum = sum(
                map(phi, self.z_data - self.mu, [self.sigma]*len(data))
                )
            objfun = lambda gamma: (
                    len(self.data) *
                    np.log(sum(np.exp(self.z_supp_phi * -1 *  gamma)))
                ) + gamma * self.z_data_phi_sum
        else:
            if isinstance(data[0], (float, int)):
                supp_samples = [[d] for d in (
                    np.random.rand(no_supp_samples)*(max(data)-min(data))*1.5
                    )+1.25*min(data)-0.25*max(data)]
            else:
                hyper_ellipse = he(data=self.data)
                supp_samples = hyper_ellipse.sample(no_supp_samples)
            z_supp_samples = map(
                sub,
                z_expand(supp_samples, self.dof, mapped=True),
                [self.mu]*no_supp_samples
                )
            z_supp_phi = np.array(
                list(map(phi, z_supp_samples, [self.sigma]*no_supp_samples))
                )
            z_data_phi_sum = sum(
                map(phi, self.z_data - self.mu, [self.sigma]*len(data))
                )
            objfun = lambda gamma: (
                    len(self.data) *
                    np.log(sum(np.exp(z_supp_phi * -1 * gamma)))
                ) + gamma * z_data_phi_sum
        self.gamma = scimin(objfun, 1e-9, bounds=((0, None),)).x
        self.sigma = self.sigma/self.gamma
        if retain_supp_samples:
            self.z_supp_phi *= self.gamma
            self.norm_est = sum(map(np.exp, -1 * self.z_supp_phi))

def phi(d_mu, sigma):
    """ Returns unnormalised log density of data point which has had its mean
    subtracted from it."""
    # Unnormalised log-likelihood
    # Dmu = data - mu
    return sum((d_mu)*np.linalg.solve(sigma, (d_mu)))/2

def nearest_psd(mat):
    """ Finds a positive semi-definite matrix which is clsoe to the provided
    matrix. This is necessary to get around computational issues when dealing
    with a large matrix, but introduces some computational cost."""
    try:
        np.linalg.cholesky(mat)
        return mat
    except np.linalg.LinAlgError:
        symm = (mat + mat.T)/2
    [_, s, v] = np.linalg.svd(symm)
    symm_pf = np.dot(v, np.dot(s, v.T))
    mat_star = (mat + symm_pf)/2
    mat_star = (mat_star + mat_star.T)/2
    k = 0
    while True:
        if k>1000: 
            raise Exception('Matrix cannot be bent into positive semi-definite')
        try:
            np.linalg.cholesky(mat_star)
            break
        except np.linalg.LinAlgError:
            k += 1
        e_min = np.min(
            np.real(np.linalg.eig(mat_star)[0])
            )
        mat_star += (
            (-e_min * k ** 2 + np.spacing(1)) *
            np.eye(np.shape(mat_star)[0])
        )
    return mat_star

def z_expand(p_data, dof=1, mapped=False):
    """ Returns a map of the feature space equivalents of the physical space
    dataset. """
    if isinstance(p_data[0], (list, np.ndarray)):
        dlen = len(p_data)
        if len(p_data[0]) == 1:
            zfun = lambda x, dof: [*map(pow, [x[0]]*dof, range(1,dof+1))]
        else:
            zfun = z_expand_func
    elif isinstance(p_data[0], (int, float)):
        dlen = 1
        p_data = [p_data]
        zfun = z_expand_func
    if mapped:
        return map(zfun, p_data, [dof]*dlen)
    else:
        return [*map(zfun, p_data, [dof]*dlen)]

def z_expand_func(data, dof):
    """ Expansion function, defined to make mapping easier. """
    return [
        reduce(mul, c) for c in
        chain.from_iterable([cwr(data, d) for d in range(1, dof + 1)])
        ]
