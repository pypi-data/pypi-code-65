import numpy as np

def ssp_vectorized(basis, positions):
    # Given a matrix of basis vectors, d by n (d = dimension of semantic pointer basis vectors, n = number of basis 
    # vectors, and a matrix of positions, N by n (N = number of points)
    # Return a matrix of N ssp vectors
    # Assuming the circular convolution defn for fractional binding
    positions = positions.reshape(-1,basis.shape[1])
    S_list = np.zeros((basis.shape[0],positions.shape[0]),dtype=complex)
    for i in np.arange(positions.shape[0]):
        S_list[:,i] = np.fft.ifft(np.prod(np.fft.fft(basis, axis=0)**positions[i,:], axis=1), axis=0)  
    return S_list


def rssp_vectorized(basis, positions, recursive_fun):
    # Given a matrix of basis vectors, d by n (d = dimension of semantic pointer basis vectors, n = number of basis 
    # vectors, and a matrix of positions, N by n (N = number of points)
    # Return a matrix of N ssp vectors
    # Assuming the circular convolution defn for fractional binding
    positions = positions.reshape(-1,basis.shape[1])
    S_list = np.zeros((basis.shape[0],positions.shape[0]),dtype=complex)
    for i in np.arange(positions.shape[0]):
        S_list[:,i] = np.fft.ifft(np.prod(np.fft.fft(recursive_fun(basis,positions[i,0],positions[i,1]), axis=0)**positions[i,:], axis=1), axis=0)  
    return S_list




# Path generating functions 
def circle_rw(n,r,x0,y0,sigma):
    pts = np.zeros((n,2))
    pts[0,:]=np.array([x0,y0])
    for i in np.arange(1,n):
        newpt = sigma*np.random.randn(2) 
        if (np.linalg.norm(pts[i-1,:]+newpt)>r):
            pts[i,:]=pts[i-1,:]-newpt
        else:
            pts[i,:]=pts[i-1,:]+newpt
            
    return(pts)

def random_path(radius, n_steps, dims, fac):
    walk = np.zeros((n_steps,dims))
    pt_old = np.zeros((1,dims))
    for i in np.arange(n_steps):
        walk[i,:] = pt_old
        step_vec = (np.random.rand(dims)-0.5)*fac
        pt_new = np.maximum(np.minimum(pt_old+step_vec, radius), -radius)
        pt_old = pt_new
    return walk

def generate_signal(T,dt,dims = 1, rms=0.5,limit=10, seed=1):
    np.random.seed(seed)             
    N = int(T/dt)
    dw = 2*np.pi/T
    
    # Don't get samples for outside limit, those coeffs will stay zero
    num_samples = max(1,min(N//2, int(2*np.pi*limit/dw)))
    
    x_freq = np.zeros((N,dims), dtype=complex)
    x_freq[0,:] = np.random.randn(dims) #zero-frequency coeffient
    x_freq[1:num_samples+1,:] = np.random.randn(num_samples,dims) + 1j*np.random.randn(num_samples,dims) #postive-frequency coeffients
    x_freq[-num_samples:,:] += np.flip(x_freq[1:num_samples+1,:].conjugate(),axis=0)  #negative-frequency coeffients
      
    x_time = np.fft.ifft(x_freq,n=N,axis=0)
    x_time = x_time.real # it is real, but in case of numerical error, make sure
    rescale = rms/np.sqrt(dt*np.sum(x_time**2)/T)
    x_time = rescale*x_time
    x_freq = rescale*x_freq
    
    x_freq = np.fft.fftshift(x_freq)    
    return(x_time,x_freq)

