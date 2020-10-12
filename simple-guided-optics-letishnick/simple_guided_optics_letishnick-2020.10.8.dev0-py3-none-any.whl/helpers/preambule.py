    # General default libraries

import numpy as np
import scipy as sp

    # Some signal treatment routines
#TODO add the methods that unitilise these functions
#TODO (needed for pulse propagation)
from scipy.signal import convolve, gausspulse, chirp

    # Curve treatment, do not import for now
#TODO add the methods that unitilise these functions
#TODO (needed for my latest paper to treat the reflectogram)
#TODO (don't see a necessity to keep in any more)
# from lmfit import Minimizer, Parameters, report_fit, Model

import warnings

        ## Constants
from scipy.constants import c
from scipy.constants import pi
from scipy.constants import epsilon_0
from scipy.constants import mu_0

    # aliases
e = sp.exp(1)

eps0 = epsilon_0
mu0 = mu_0

eps0_umps = epsilon_0*1e30
mu0_umps = mu_0*1e-18

    # normalisation speeds of light
c_nmps = 1e-3 /sp.sqrt(eps0*mu0)
c_umps = 1e-6 /sp.sqrt(eps0*mu0)
c_mps  = 1e-12/sp.sqrt(eps0*mu0)
c_kmps = 1e-15/sp.sqrt(eps0*mu0)


        ## General mathematical functions
from numpy import sin, cos, sinh, cosh, tan, exp, sinc, absolute, log, log10, \
                  arctan, arctan2, conjugate
from scipy.special import jv, kv, jvp, kvp, factorial
from scipy.optimize import root, brentq


    # Additional useful unctions 
    # general math
def cot(x):
    return tan(x)**-1
def sec(x):
    return 1/cos(x)
def csc(x):
    return 1/sin(x) 
    
    # these are traditional russian acronyms, can't live without them sometimes
sqrt=sp.emath.sqrt
ln=log
lg=log10
arctg=arctan

    # log10 values math
def cmp2dB(x):
    return 20 * np.log10(absolute(x)**2)
def cmp2dB_pwr(x):
    return 10 * np.log10(absolute(x)**2)
def dB2lin(x):
    return 10 ** (0.1*x)
def normalise_cmp(x):
    return absolute(x)**2/np.max(absolute(x))**2
def normalized(x):
    return x/np.max(x)

    # find nearest above = fna.
''' Ceci cherche l'indice du my_array qui correspond au valeur "target" '''
''' This one looks for an index of my_array corresponding to a target value,
    borrowed from stackexchange'''
def fna(my_array, target):
    diff = my_array - target
    mask = np.ma.less_equal(diff, 0)
    if np.all(mask):
        return None # returns None if target is greater than any value
    masked_diff = np.ma.masked_array(diff, mask)
    return masked_diff.argmin()



''' '''


        ## Fourier
    #TODO necessary for pulse propagation
import scipy.fftpack as fft

    # Transformation de Fourier améliorée
def FFT_t(A,n=None,ax=0):
    return fft.ifftshift(fft.ifft(fft.fftshift(A,axes=(ax,)),n,axis=ax),axes=(ax,))
def IFFT_t(A,n=None,ax=0):
    return fft.ifftshift(fft.fft(fft.fftshift(A,axes=(ax,)),n,axis=ax),axes=(ax,))

    # A partial Fourier transform
def IFFT_partial(f, Hw, fs=None,
                 window=np.kaiser, N=12,
                 fft_pts=2**12):
    ''' The function mimics the VNA time-domain analysis algorythm'''
    '''

    f --- the array of frequencies of H(w) between f1 and f2 ;
    Hw --- the system frequency response
    fs --- sampling frequency. Defaults in f2.
        by increasing fs it is possible to bet a better time resolution
    window --- the apodization window. Default is Kaiser
    N --- the window order, defaults in 12
    fft_pts --- number of desired fft points
    '''

    #TODO
    ''' Sometimes the function varies a lot in the frequency region, like, for
        exemple, the amplitude transmission of a ring resonator.
        Thus, the frequency response have to be truncated to make the prominent
        H(w) characterictics appear.


    '''

    #TODO
    ''' Backward transform
    '''
    f1 = f[0]; f2 = f[-1]
        # new frequency centre
    fcentre = (f2 + f1)/2
        # the new f2
    f3 = f2 - fcentre

        # setting FFT grids
    if fs==None:
        fs = f2

    window_ps = fft_pts/(fs)
    # fft_freqs = fft.fftshift(fft.fftfreq(fft_pts, d = 1/fs))
    t_ps = np.linspace(-window_ps/2, window_ps/2, fft_pts, endpoint=False)

    ''' we can set the sampling frequency to be greater than f2,
        in this case we have to zero pad'''
    if fs > f2:
        # Hw = both_side_padded(Hw)

        # new freq array and the number of points to pad
        pad_left = len(fft_freqs[0:fna(fft_freqs, -f3)])

        pad_right = pad_left - 1

            # interpolating to usual frequencies
            # the number of interp points is that what's left
        interp_points=len(fft_freqs[fna(fft_freqs, -f3):fna(fft_freqs,  f3)])
        interpolator_re=InterpolatedUnivariateSpline(filtre_freq_array, filtre_Hw.real)
        interpolator_im=InterpolatedUnivariateSpline(filtre_freq_array, filtre_Hw.imag)
        freqs_interp=np.linspace(filtre_freq_array[0],
                                 filtre_freq_array[-1], interp_points)
        filtre_Hw_interp=interpolator_re(freqs_interp)+1j*interpolator_im(freqs_interp)

            # padding
        Hw_pad=np.pad(filtre_Hw_interp, \
                    (pad_left,pad_right), 'constant', constant_values=(0, 0))

    else:
        Hw = interp_xypts(f, Hw, fft_pts)

        # windowing
    window_apod = np.kaiser(fft_pts, N)

        # iFFTing
    Ht = IFFT_t(Hw*window_apod)

        # IF NEEDED, MAYBE NOT 
        # The centre displacement of the straight fft
    # exp(-1j*2*pi*f3)*

    return np.array([t_ps, Ht])



''' '''



        ## Interpolation helper routines
from scipy.interpolate import InterpolatedUnivariateSpline

    # Interponation of x and y in N points
def interp_xypts(x_array, y_array, points, return_x=False):

    ''' The envelope function that computes an interpolated array from the two
        arrays. The ordinate and the abscissae are of the same size. 
        Due to the restrictions of InterpolatedUnivariateSpline y have to increase
    '''

        # the array of new abscissae by the intended endpoints
    x_new = np.linspace(x_array[0], x_array[-1], points)

        # checking if there are any complex numbers
    if np.any(y_array.imag) !=0:
        interpolator_re = InterpolatedUnivariateSpline(x_array, y_array.real)
        interpolator_im = InterpolatedUnivariateSpline(x_array, y_array.imag)
        y_new = interpolator_re(x_new) + 1j*interpolator_im(x_new)
    else:
        interpolator = InterpolatedUnivariateSpline(x_array, y_array)
        y_new = interpolator(x_new)

    if return_x:
        return np.array([x_new,y_new])
    else:
        return y_new

    # Interponation to a new x
def interp_tonew_x(x_old, x_intended, y_array, points, return_x=False):

    ''' The envelope function that computes an interpolated array from two
        arrays. One of them has been calculated in the different abscissae
    '''

        # the array of new abscissae by the intended endpoints
    x_new = np.linspace(x_intended[0], x_intended[-1], points)

        # if the array is complex one need to separate Re and Im parts
    if np.any(y_array.imag) !=0:
        interpolator_re = InterpolatedUnivariateSpline(x_old, y_array.real)
        interpolator_im = InterpolatedUnivariateSpline(x_old, y_array.imag)
        y_new = interpolator_re(x_new) + 1j*interpolator_im(x_new)
    else:
        interpolator = InterpolatedUnivariateSpline(x_old, y_array)
        interpolator = InterpolatedUnivariateSpline(x_old, y_array)
        y_new = interpolator(x_new)

        # returning the intended abscissae array
    if return_x:
        return np.array([x_new,y_new])
    else:
        return y_new



''' '''

        ## Point of array output
def point_or_array_output(input_array,
                        returned_points, interp_points,
                        input_lam, input_freq, input_V,
                        simulation_units, internal = False,
                        wavelength_point = None, frequency_point = None, V_point = None):
    '''
    The function that outputs either an array of calculated waveguide properties
    or a value on a calculated point. There is a lot of ifs so the code looks bulky
    As long as there is a comparison procedure, the function has to be provided
    with abscissae arrays: interp_lam, interp_freq, interp_V
    '''
    warned = False

        # interpolating
    interp_lam  = np.linspace(input_lam[0],  input_lam[-1],  interp_points)
    interp_V    = np.linspace(input_V[0],    input_V[-1],    interp_points)
    interp_freq = np.linspace(input_freq[0], input_freq[-1], interp_points)

        # Values to output on particular points
    if wavelength_point != None:
        if (np.min(interp_lam) <= wavelength_point <= np.max(interp_lam)):
            returned_array = input_array[fna(interp_lam, wavelength_point)]
        else:
            warnings.warn("The wavelength has to be within the sim range")
            warned = True

    elif frequency_point != None:
        if (np.min(interp_freq) <= frequency_point <= np.max(interp_freq)):
            returned_array = input_array[fna(interp_freq, frequency_point)]
        else:
            warnings.warn("The frequency has to be within the sim range")
            warned = True

    elif V_point != None:
        if (np.min(interp_V) <= V_point <= np.max(interp_V)):
            returned_array = input_array[fna(interp_V, V_point)]
        else:
            warnings.warn("The V number has to be within the sim range")
            warned = True

            # outputting an entire array interpolated back to sim points
    if wavelength_point==None and frequency_point==None and V_point==None:

            # output wavelength
        if simulation_units=='wavelength':
            returned_array = interp_tonew_x(
                              interp_lam, input_lam, input_array, returned_points)

        if simulation_units=='frequency':
            returned_array = interp_tonew_x(
                              interp_freq, input_freq, input_array, returned_points)

        if simulation_units=='V-number':
            returned_array = interp_tonew_x(
                              interp_V, input_V, input_array, returned_points)

        # for it is better to return nothing more that a warning
    if warned: return None
        # the interpolated neff for subsequent internal usage
    elif internal: return input_array
    else: return returned_array


''' '''


        ## Basiline removal
#TODO useless for now, used once in the reflectogram treatment
# newertheless, this is a cool procedure
from scipy import sparse
from scipy.sparse.linalg import spsolve

def baseline_als(y, lam, p, niter=10):
  L = len(y)
  D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
  w = np.ones(L)
  for i in range(niter):
    W = sparse.spdiags(w, 0, L, L)
    Z = W + lam * D.dot(D.transpose())
    z = spsolve(Z, w*y)
    w = p * (y > z) + (1-p) * (y < z)
  return z
