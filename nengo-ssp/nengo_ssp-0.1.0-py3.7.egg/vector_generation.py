import numpy as np
#import nengolib
from nengo_ssp.spatial_semantic_pointer import SpatialSemanticPointer
from nengo_ssp.hrr_algebra import HrrAlgebra

def PlaneWaveBasis(K):
    # Create the bases vectors X,Y as described in the paper with the wavevectors 
    # (k_i = (u_i,v_i)) given in a matrix K. To get hexganal patterns use 3 K vectors 120 degs apart
    # To get mulit-scales/orientation, give many such sets of 3 K vectors 
    # K is _ by 2 
    d = K.shape[0]
    n = K.shape[1]
    
    Bases = []
    for i in range(n):
        F = np.ones((d*2 + 1,), dtype="complex")
        F[0:d] = np.exp(1.j*K[:,i])
        F[-d:] = np.flip(np.conj(F[0:d]))
        F = np.fft.ifftshift(F)
        Basis = SpatialSemanticPointer(data=np.fft.ifft(F), algebra=HrrAlgebra())
        Bases.append(Basis)
    return Bases

def WeightedPlaneWaveBasis(K,W):
    # Create the bases vectors X,Y as described in the paper with the wavevectors 
    # (k_i = (u_i,v_i)) given in a matrix K. To get hexganal patterns use 3 K vectors 120 degs apart
    # To get mulit-scales/orientation, give many such sets of 3 K vectors 
    # K is _ by 2 
    d = K.shape[0]
    n = K.shape[1]
    
    Bases = []
    for i in range(n):
        F = np.ones((d*2 + 1,), dtype="complex")
        F[0:d] = W*np.exp(1.j*K[:,i])
        F[-d:] = np.flip(W*np.conj(F[0:d]))
        Basis = SpatialSemanticPointer(data=np.fft.ifft(F), algebra=HrrAlgebra())
        Bases.append(Basis)
    return Bases

def HexagonalBasis(n_rotates=8,n_scales=8,scale_min=0.8, scale_max=3):
    # Create bases vectors X,Y consisting of mulitple sets of hexagonal bases
    K_hex = np.array([[0,1], [np.sqrt(3)/2,-0.5], [-np.sqrt(3)/2,-0.5]])

    scales = np.linspace(scale_min,scale_max,n_scales)
    K_scales = np.vstack([K_hex*i for i in scales])
    thetas = np.arange(0,n_rotates)*np.pi/(n_rotates) #***
    R_mats = np.stack([np.stack([np.cos(thetas), -np.sin(thetas)],axis=1),
           np.stack([np.sin(thetas), np.cos(thetas)], axis=1)], axis=1)
    K_scale_rotates = (R_mats @ K_scales.T).transpose(1,2,0).T.reshape(-1,2)
    X, Y = PlaneWaveBasis(K_scale_rotates)
    return X, Y, K_scale_rotates

def RectangularBasis(n_rotates=8,n_scales=8,scale_min=0.8, scale_max=3):
    # Create bases vectors X,Y consisting of mulitple sets of hexagonal bases
    K_rec = np.array([[0,1], [1,0]])

    scales = np.linspace(scale_min,scale_max,n_scales)
    K_scales = np.vstack([K_rec*i for i in scales])
    thetas = np.arange(0,n_rotates)*np.pi/(n_rotates) #***
    R_mats = np.stack([np.stack([np.cos(thetas), -np.sin(thetas)],axis=1),
           np.stack([np.sin(thetas), np.cos(thetas)], axis=1)], axis=1)
    K_scale_rotates = (R_mats @ K_scales.T).transpose(1,2,0).T.reshape(-1,2)
    X, Y = PlaneWaveBasis(K_scale_rotates)
    return X, Y, K_scale_rotates

def RecursiveBasisFun(K):
    def _recursive_fun(A,x,y):
        plane_wave = np.exp(1.j*(K[:,0]*x + K[:,1]*y))
        h = np.sum((plane_wave + np.conj(plane_wave)).real,axis=0)
        #h = np.sum(plane_wave,axis=0)
        return np.fft.ifft(np.fft.fft(A, axis=0)**(np.abs(h)/3 + 2), axis=0) 
    return _recursive_fun


def GridCellEncoders(n_G,X,Y, radius=10):
    d = len(X.v)
    N = (d-1)//6
    #G_pos_dist = nengolib.stats.Rd()
    #G_pos = G_pos_dist.sample(n_G,2)*2*radius - radius    
    G_pos = np.random.rand(n_G,2)*2*radius - radius
    if N < n_G:
        G_sorts = np.hstack([np.arange(N), np.random.randint(0, N - 1, size = n_G - N)])
    else:
        G_sorts = np.arange(n_G)
    G_encoders = np.zeros((n_G,d))
    for i in np.arange(n_G):
        sub_mat = _get_sub_SSP(G_sorts[i],N)
        proj_mat = _proj_sub_SSP(G_sorts[i],N)
        Xi = SpatialSemanticPointer(data = sub_mat @ X.v)
        Yi = SpatialSemanticPointer(data = sub_mat @ Y.v)
        G_encoders[i,:] = N * proj_mat @ ((Xi**G_pos[i,0])*(Yi**G_pos[i,1])).v
    return G_encoders, G_sorts
        
        
def UnitaryVectors(D, eps=1e-3, rng=np.random):
    a = rng.rand((D - 1) // 2)
    sign = rng.choice((-1, +1), len(a))
    phi = sign * np.pi * (eps + a * (1 - 2 * eps))
    assert np.all(np.abs(phi) >= np.pi * eps)
    assert np.all(np.abs(phi) <= np.pi * (1 - eps))

    fv = np.zeros(D, dtype='complex64')
    fv[0] = 1
    fv[1:(D + 1) // 2] = np.cos(phi) + 1j * np.sin(phi)
    fv[-1:D // 2:-1] = np.conj(fv[1:(D + 1) // 2])
    if D % 2 == 0:
        fv[D // 2] = 1

    assert np.allclose(np.abs(fv), 1)
    v = np.fft.ifft(fv)
    v = v.real
    return SpatialSemanticPointer(v)
        
        
        
        
        
        
def _get_sub_FourierSSP(n, N, sublen=3):
    # Return a matrix, \bar{A}_n
    # Consider the multi scale representation (S_{total}) and sub vectors (S_n) described in the paper 
    # Then
    # \bar{A}_n F{S_{total}} = F{S_n}
    # i.e. pick out the sub vector in the Fourier domain
    tot_len = 2*sublen*N + 1
    FA = np.zeros((2*sublen + 1, tot_len))
    FA[0:sublen, sublen*n:sublen*(n+1)] = np.eye(sublen)
    FA[sublen, sublen*N] = 1
    FA[sublen+1:, tot_len - np.arange(sublen*(n+1),sublen*n,-1)] = np.eye(sublen)
    return FA

def _get_sub_SSP(n,N,sublen=3):
    # Return a matrix, A_n
    # Consider the multi scale representation (S_{total}) and sub vectors (S_n) described in the paper 
    # Then
    # A_n S_{total} = S_n
    # i.e. pick out the sub vector in the time domain
    tot_len = 2*sublen*N + 1
    FA = _get_sub_FourierSSP(n,N,sublen=sublen)
    W = np.fft.fft(np.eye(tot_len))
    invW = np.fft.ifft(np.eye(2*sublen + 1))
    A = invW @ np.fft.ifftshift(FA) @ W
    return A.real

def _proj_sub_FourierSSP(n,N,sublen=3):
    # Return a matrix, \bar{B}_n
    # Consider the multi scale representation (S_{total}) and sub vectors (S_n) described in the paper 
    # Then
    # \sum_n \bar{B}_n F{S_{n}} = F{S_{total}}
    # i.e. project the sub vector in the Fourier domain such that summing all such projections gives the full vector in Fourier domain
    tot_len = 2*sublen*N + 1
    FB = np.zeros((2*sublen + 1, tot_len))
    FB[0:sublen, sublen*n:sublen*(n+1)] = np.eye(sublen)
    FB[sublen, sublen*N] = 1/N # all sub vectors have a "1" zero freq term so scale it so full vector will have 1 
    FB[sublen+1:, tot_len - np.arange(sublen*(n+1),sublen*n,-1)] = np.eye(sublen)
    return FB.T

def _proj_sub_SSP(n,N,sublen=3):
    # Return a matrix, B_n
    # Consider the multi scale representation (S_{total}) and sub vectors (S_n) described in the paper 
    # Then
    # \sum_n B_n S_{n} = S_{total}
    # i.e. project the sub vector in the time domain such that summing all such projections gives the full vector
    tot_len = 2*sublen*N + 1
    FB = _proj_sub_FourierSSP(n,N,sublen=sublen)
    invW = np.fft.ifft(np.eye(tot_len))
    W = np.fft.fft(np.eye(2*sublen + 1))
    B = invW @ np.fft.ifftshift(FB) @ W
    return B.real

def _planewave_mat(K, xx, yy, x0=0, y0=0):
    # Sum all plane waves to get inference pattern.
    # If you make SSPs with basis vectors from ssp_plane_basis(K) and call 
    # sim_dots, _ = similarity_plot(X, Y, xs, ys, x0, y0) 
    # then sim_dots should be the same as whats returned here. This is a check/quicker way to try out patterns
    mat = np.zeros(xx.shape)
    for i in np.arange(K.shape[0]):
        plane_wave = np.exp(1.j*(K[i,0]*(xx-x0) + K[i,1]*(yy-y0)))
        mat += (plane_wave + np.conj(plane_wave)).real
    return mat