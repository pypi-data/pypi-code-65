# Fitting functions
# Derek Fujimoto
# Oct 2019

import numpy as np

def gaussian2D(x,y,x0,y0,sigmax,sigmay,amp,theta=0):
    """Gaussian in 2D - from wikipedia"""
    
    ct2 = np.cos(theta)**2
    st2 = np.sin(theta)**2
    s2t = np.sin(2*theta)
    
    sx = sigmax**2
    sy = sigmay**2
    
    a = 0.5*(ct2/sx + st2/sy)
    b = 0.25*s2t*(-1/sx + 1/sy)
    c = 0.5*(st2/sx + ct2/sy)
    
    return amp*np.exp(-(a*np.square(x-x0) + 2*b*(x-x0)*(y-y0) + c*np.square(y-y0)))

def disk2D(x,y,x0,y0,radius,amp):
    """2D Disk"""
    
    out = np.ones(x.shape)*amp
    
    idx = x0-radius < x
    idx *= x < x0+radius
    idx = y0-radius < y
    idx *= y < y0+radius
    
    out[idx] = 0
    return out

