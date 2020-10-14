# -*- coding: utf-8 -*-
import nengo
import numpy as np
from nengo_ssp.vector_generation import HexagonalBasis, GridCellEncoders
#from nengo_ssp.utils import ssp_vectorized
    
class PathIntegrator(nengo.Network):
    def __init__(self, n_neurons, n_gridcells, scale_fac=1.0, basis=None,xy_rad=10, **kwargs):
        kwargs.setdefault("label", "PathIntegrator")
        super().__init__(**kwargs)
        
        
        if basis is None:
            X, Y, myK = HexagonalBasis(5,5)
            d = X.v.shape[0]
        else:
            X = basis[0]
            Y = basis[1]
            d = X.v.shape[0]
            myK = np.vstack([np.angle(np.fft.fftshift(np.fft.fft(X.v)))[0:d//2],
                             np.angle(np.fft.fftshift(np.fft.fft(Y.v)))[0:d//2]]).T
            
        n_oscs = d//2
        real_ids = np.arange(1,n_oscs*3,3)
        imag_ids = np.arange(2,n_oscs*3,3)
        S_ids = np.zeros(n_oscs*2 + 1, dtype=int)
        S_ids[0:d//2] = real_ids
        S_ids[d//2:(n_oscs*2)] = imag_ids
        S_ids[-1] = n_oscs*3 
        i_S_ids = np.argsort(S_ids)
        
        G_encoders,G_sorts = GridCellEncoders(n_gridcells, X,Y, xy_rad)

        taus = 0.1*np.ones(n_oscs)
            
        with self:
            to_SSP = self.get_to_SSP_mat(d)
            i_to_SSP = self.get_from_SSP_mat(d)

            
            self.input_vel = nengo.Node(size_in=2, label="input_vel")
            self.input_SSP = nengo.Node(size_in=d, label="input_initial_SSP")
            #self.input_FSSP = nengo.Node(size_in=d-1, label="input_initial_FSSP")
            #nengo.Node(self.input_SSP, self.input_FSSP, )
            
            self.output = nengo.Node(size_in=d, label="output")
            
            self.velocity = nengo.Ensemble(n_neurons, dimensions=2,label='velocity')
            zero_freq_term = nengo.Node([1,0,0])
            
            self.osc = nengo.networks.EnsembleArray(n_neurons, n_oscs + 1, 
                                                    ens_dimensions = 3,radius=np.sqrt(3), label="osc")
            self.osc.output.output = lambda t, x: x 
            self.grid_cells = nengo.Ensemble(n_gridcells, dimensions=d, encoders = G_encoders,
                                        radius=np.sqrt(2), label="grid_cells")
            
            def feedback(x, tau):
                w = x[0]/scale_fac
                r = np.maximum(np.sqrt(x[1]**2 + x[2]**2), 1e-5)
                dx1 = x[1]*(1-r**2)/r - x[2]*w 
                dx2 = x[2]*(1-r**2)/r + x[1]*w 
                return 0, tau*dx1 + x[1], tau*dx2 + x[2]
            

            nengo.Connection(self.input_vel, self.velocity, transform = scale_fac)
            for i in np.arange(n_oscs):
                nengo.Connection(self.velocity, self.osc.ea_ensembles[i][0], transform = myK[i,:].reshape(1,-1),  
                                 synapse=taus[i])
                
                S_back_mat = i_to_SSP[i_S_ids[2*i:(2*i+2)],:]

                
                nengo.Connection(self.input_SSP, self.osc.ea_ensembles[i][1:], transform=S_back_mat) #initialize
                
                nengo.Connection(self.osc.ea_ensembles[i], self.osc.ea_ensembles[i], 
                                 function= lambda x: feedback(x, taus[i]), 
                                 synapse=taus[i])

                #nengo.Connection(self.grid_cells, self.osc.ea_ensembles[i][1:], transform=S_back_mat, synapse=taus[i])
                
            nengo.Connection(zero_freq_term, self.osc.ea_ensembles[-1])
            nengo.Connection(self.osc.output[S_ids], self.grid_cells, transform = to_SSP, synapse=taus[0]) 

            #nengo.Connection(self.input_initial_SSP, self.grid_cells)
            
            nengo.Connection(self.grid_cells, self.output)
            
            

    
            
            
    def get_to_SSP_mat(self,D):
        W = np.fft.ifft(np.eye(D))
        W1 = W.real @ np.fft.ifftshift(np.eye(D),axes=0)
        W2 = W.imag @ np.fft.ifftshift(np.eye(D),axes=0)
        shiftmat1 = np.vstack([np.eye(D//2), np.zeros((1,D//2)), np.flip(np.eye(D//2), axis=0)])
        shiftmat2 = np.vstack([np.eye(D//2), np.zeros((1,D//2)), -np.flip(np.eye(D//2), axis=0)])
        shiftmat = np.vstack([ np.hstack([shiftmat1, np.zeros(shiftmat2.shape)]),
                              np.hstack([np.zeros(shiftmat2.shape), shiftmat2])])
        shiftmat = np.hstack([shiftmat, np.zeros((shiftmat.shape[0],1))])
        shiftmat[D//2,-1] = 1
        tr = np.hstack([W1, -W2]) @ shiftmat 

        return tr

    def get_from_SSP_mat(self,D):
        W = np.fft.fft(np.eye(D))
        W1 = np.fft.fftshift(np.eye(D),axes=0) @ W.real 
        W2 = np.fft.fftshift(np.eye(D),axes=0) @ W.imag 
        shiftmat1 = np.hstack([np.eye(D//2), np.zeros((D//2, 2*(D//2) + D//2 + 2))])
        shiftmat2 = np.hstack([np.zeros((D//2, 2*(D//2) + 1)), np.eye(D//2), np.zeros((D//2, D//2 + 1))])
        shiftmat = np.vstack([ shiftmat1,shiftmat2])
        tr = shiftmat @ np.vstack([W1, W2]) 
        return tr