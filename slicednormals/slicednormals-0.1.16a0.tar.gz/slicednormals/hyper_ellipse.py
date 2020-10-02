"""
Takes a data set and finds an ellipse which encloses it. Sampels can then be
drawn uniformly across this ellipse using the Dezert Musso algorithm. This is
more efficient in many cases than simple sampling from an enclosing cube.

Based on the procedure described in Improving the Uncertainty Quantifcation of
Sliced Normal Distributions by Scaling the Covariance matrix Colbert et al 2020
"""

import numpy as np
from scipy.optimize import minimize as scimin
from scipy.special import gamma
from numpy.random import default_rng


class hyper_ellipse():
    """ Finds a hyper ellipse which bounds the provided data, and inflates it
    slightly to allow for small data sets. This inflation if naive at present,
    and will be improved in later updates."""
    def __init__(self, data=None):
        self.data = data
        if not self.data is None:
            self.fit_hyper_ellipse()

    def fit_hyper_ellipse(self, data=None):
        """ Calculates hyper-ellipse parameters following following "Improving
        the Uncertainty quantification of Sliced Normal Distributions by Scaling
        the Covariance matrix" Colbert et al 2020 Appendix A. """
        if not data is None:
            self.data = data
        mu = np.mean(self.data, 0)
        sigma = nearest_psd(np.cov(self.data.T, ddof=1))
        l = np.linalg.cholesky(sigma)
        temp_q = np.linalg.solve(sigma, mu.T)
        q_0 = nearest_psd(
            np.vstack((
                np.hstack(
                    (mu @ temp_q, -(temp_q))
                    ),
                np.vstack((
                    -temp_q,
                    np.linalg.solve(
                        l, np.linalg.solve(l.T, np.eye(np.shape(l)[0]))
                        )
                    )).T
                ))
            )
        q_0 = np.linalg.cholesky(q_0)
        he_q = scimin(self.he_obj_fun, q_0).x
        l = int(len(he_q) ** 0.5)
        he_q = np.reshape(he_q, (l, l))
        self.q = (he_q @ he_q.T).T

        self.p_matrix = self.q[1:, 1:]
        self.chol_p_matrix = np.linalg.cholesky(nearest_psd(self.p_matrix))
        self.sigma = np.linalg.solve(
            self.chol_p_matrix,
            np.linalg.solve(
                self.chol_p_matrix.T,
                np.eye(np.shape(self.chol_p_matrix)[0])
            ))

        #self.sigma = np.linalg.inv(self.p_matrix)
        self.mu = self.sigma@self.q[1:, 0]
        self.mu = mu
        self.beta = self.f_beta(self.q)
        self.dims = np.shape(self.data)[1]
        d_mu = self.data[
            np.argmax(np.linalg.norm(self.data-self.mu, axis=1)),
            :] - self.mu
        self.threshold = np.min(
            np.sum(d_mu.T * (np.linalg.solve(self.sigma, d_mu.T)), 0)
            )*(1+1/np.sqrt(len(self.data)))
        self.volume = (
            np.pi ** (self.dims / 2) / gamma(1+self.dims/2)
            )*(np.linalg.det(self.sigma)**0.5)*(self.threshold**(self.dims/2))

    def he_obj_fun(self, q):
        """ Objective optimisation function used to find minimum bounding
        ellipse. Ellipse parameters are described in one matrix. """
        l = int(len(q)**0.5)
        q = np.reshape(q, (l, l))
        q = q@q.T 
        return -np.log(np.linalg.det(q))-self.f_beta(q)

    def f_beta(self, q):
        " Finds the minimum unnormalised log density."
        beta = 1
        data1 = np.column_stack([np.ones(np.shape(self.data)[0]), self.data])
        beta = np.min(-np.diag(data1@q@data1.T))
        return beta

    def sample(self, no_samples=None):
        """ Returns samples drawn from the hyper ellipse."""
        return dezert_musso(self.threshold, self.sigma, self.mu, no_samples)

def dezert_musso(threshold, sigma, mu, no_samples):
    """ Algorithm for uniformly sampling from a hyper ellipse. """
    rng = default_rng()
    dims = np.shape(sigma)[0]

    h_sphere = rng.standard_normal(size=(no_samples, dims))
    h_sphere = h_sphere.T/np.sqrt(np.sum(h_sphere**2, 1))

    counter = rng.random(size=no_samples)**(1/dims)
    unif_sph = counter*h_sphere
    chol_s = np.linalg.cholesky(sigma)
    unif_ell = chol_s.T @ unif_sph
    return (unif_ell*np.sqrt(threshold)+np.array([mu]).T).T

def nearest_psd(mat):
    """ Finds a positive semi-definite matrix which is close to the provided
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
