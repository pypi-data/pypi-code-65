# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from photonpy import Context, PostProcessMethods, Gaussian, Estimator
import numpy as np
from photonpy.smlm.frc import FRC
from photonpy.smlm.drift_estimate import minEntropy,rcc
import tqdm
from scipy.interpolate import InterpolatedUnivariateSpline
from photonpy.utils.multipart_tiff import MultipartTiffSaver

import h5py 
import yaml

class Dataset:
    """
    Keep a localization dataset using numpy structured array
    """
    def __init__(self, length, dims, imgshape=None, data=None,origin=None, config=None, haveSigma=False, **kwargs):

        self.createDTypes(dims, len(imgshape), haveSigma)
        
        self.imgshape = imgshape 
        if data is not None:
            self.data = data
        else:
            self.data = np.recarray(length, dtype=self.dtypeLoc)
            self.data.fill(0)

        self.sigma = np.zeros(dims)
        self.config = config if config is not None else {}
        
        if kwargs is not None:
            self.config = {**self.config, **kwargs}
                
        
    def __getitem__(self,idx):
        if type(idx) == str:
            return self.config[idx]
        else:
            indices = idx
            return type(self)(0, self.dims, self.imgshape, self.data[indices], config=self.config)

    def __setitem__(self, idx, val):
        self.config[idx]=val

    def copy(self):
        return self[np.arange(len(self))]
            
    def createDTypes(self,dims, imgdims, includeGaussSigma):
        """
        Can be overriden to add columns
        """
        dtypeEstim = [
            ('pos', np.float32, (dims,)),
            ('photons', np.float32),
            ('bg', np.float32)]
        
        if includeGaussSigma:
            dtypeEstim.append(
                ('sigma', np.float32, (2,))
            )
        
        self.dtypeEstim = np.dtype(dtypeEstim)
        
        self.dtypeLoc = np.dtype([
            ('roi_id', np.int32),  # typically used as the original ROI index in an unfiltered dataset
            ('frame', np.int32),
            ('estim', self.dtypeEstim),
            ('crlb', self.dtypeEstim),
            ('chisq', np.float32),
            ('group', np.int32),
            ('roipos', np.int32, (imgdims,))
            ])

            
    def filter(self, indices):
        """
        Keep only the selected indices, filtering in-place. An alternative is doing a copy: ds2 = ds[indices]
        """
        prevcount = len(self)
        self.data = self.data[indices]
        
        print(f"Keeping {len(self.data)}/{prevcount} spots")
    
    
    
    @property
    def numFrames(self):
        return np.max(self.data.frame)+1
            
    def indicesPerFrame(self):
        frame_indices = self.data.frame
        if len(frame_indices) == 0: 
            numFrames = 0
        else:
            numFrames = np.max(frame_indices)+1
        frames = [[] for i in range(numFrames)]
        for k in range(len(self.data)):
            frames[frame_indices[k]].append(k)
        for f in range(numFrames):
            frames[f] = np.array(frames[f], dtype=int)
        return frames
            
    def __len__(self):
        return len(self.data)
    
    @property
    def dims(self):
        return self.data.estim.pos.shape[1]
    
    @property
    def pos(self):
        return self.data.estim.pos
    
    @pos.setter
    def pos(self, val):
        self.data.estim.pos = val
    
    @property
    def crlb(self):
        return self.data.crlb
    
    @property
    def photons(self):
        return self.data.estim.photons

    @photons.setter
    def photons(self, val):
        self.data.estim.photons = val
    
    @property
    def background(self):
        return self.data.estim.bg
    
    @property
    def framenum(self):
        return self.data.frame
    
    @property
    def chisq(self):
        return self.data.chisq
    
    @property
    def roi_id(self):
        return self.data.roi_id
    
    @property
    def local_pos(self):
        """
        Localization position within ROI.
        """
        lpos = self.pos*1
        lpos[:,0] -= self.data.roipos[:,-1]
        lpos[:,1] -= self.data.roipos[:,-2]
        return lpos
        
    def __repr__(self):
        return f'Dataset with {len(self)} {self.dims}D localizations.'
    
    def FRC2D(self, zoom=10, display=True,pixelsize=None):
        return FRC(self.pos, self.photons, zoom, self.imgshape, pixelsize, display=display)

    def estimateDriftMinEntropy(self, framesPerBin=10,maxdrift=3, **kwargs):
        sigma = np.mean(self.data.crlb.pos, 0)
        
        drift, _, est_precision = minEntropy(self.data.estim.pos, 
                   self.data.frame, 
                   self.data.crlb.pos, framesperbin=framesPerBin, maxdrift=maxdrift,
                   imgshape=self.imgshape, sigmaPrecise=sigma, pixelsize=self['pixelsize'], **kwargs)

        return drift, est_precision
        
    def applyDrift(self, drift):
        self.data.estim.pos -= drift[self.data.frame]
        
    def _xyI(ds):
        r=np.zeros((len(ds),3))
        r[:,:2] = ds.pos[:,:2]
        r[:,2] = ds.photons
        return r

    
    def estimateDriftRCC(self, framesPerBin=500, zoom=1, maxdrift=3):
        drift = rcc(self._xyI(), self.framenum, int(self.numFrames/framesPerBin), 
            np.max(self.imgshape), maxdrift=maxdrift, zoom=zoom)[0]
        return drift
        
    def estimateDriftFiducialMarkers(self, marker_indices):
        """
        Marker indices is a list of lists with indices
        """
        drift = np.zeros((self.numFrames,self.dims))
        for marker in marker_indices:
            sortedidx = np.sort(marker)
            t = (self.data.frame[sortedidx]+0.5)
            for d in range(self.dims):
                spl = InterpolatedUnivariateSpline(t, self.pos[sortedidx][:,d], k=2)
                trace = spl(np.arange(self.numFrames))
                drift[:,d] += trace - np.mean(trace)
        drift /= len(marker_indices)
        
        # Compute the combined variance of the beads
        combined_var = 1 / np.sum(
            [ 1 / (self.crlb.pos[marker]**2).mean(0) for marker in marker_indices ], 0)
        combined_crlb = np.sqrt(combined_var)

        print(f"CRLB of combined bead localizations: {combined_crlb}. ({combined_crlb*self.pixelsize} nm)")
        
        return drift
    
        
    def align(self, other):
        xyI = np.concatenate([self._xyI(), other._xyI()])
        framenum = np.concatenate([np.zeros(len(self),dtype=np.int32), np.ones(len(other),dtype=np.int32)])
        
        return rcc(xyI, framenum, 2, np.max(self.imgshape), maxdrift=10,RCC=False)[0][1]

    @property
    def fields(self):
        return self.data.dtype.fields

    
    def renderGaussianSpots(self, zoom, sigma=None):
        imgshape = np.array(self.imgshape)*zoom
        with Context() as ctx:

            img = np.zeros(imgshape,dtype=np.float64)
            if sigma is None:
                sigma = np.mean(self.crlb.pos[:2])
            
            spots = np.zeros((len(self), 5), dtype=np.float32)
            spots[:, 0] = self.pos[:,0] * zoom
            spots[:, 1] = self.pos[:,1] * zoom
            spots[:, 2] = sigma
            spots[:, 3] = sigma
            spots[:, 4] = self.photons

            return Gaussian(ctx).Draw(img, spots)
        
    
    def pick(self, centers, distance, debugMode=False):
        with Context(debugMode=debugMode) as ctx:
            counts, indices = PostProcessMethods(ctx).FindNeighbors(centers, self.pos, distance)

        idxlist = []
        pos = 0
        for count in counts:
            idxlist.append( indices[pos:pos+count] )
            pos += count
            
        return idxlist
        

    def cluster(self, maxDistance, debugMode=False):
        with Context(debugMode=debugMode) as ctx:
                        
            def callback(startidx, counts, indices):
                print(f"Callback: {startidx}. counts:{len(counts)} indices:{len(indices)}")
                                                        
            clusterPos, clusterCrlb, mapping = PostProcessMethods(ctx).ClusterLocs(
                self.pos, self.crlb.pos, maxDistance)
                    
        print(f"Computing cluster properties")
        
        counts = np.bincount(mapping)
        def getClusterData(org):
            r = np.recarray( len(counts), dtype=self.dtypeEstim)
            r.photons = np.bincount(mapping, org.photons) / counts
            r.bg = np.bincount(mapping, org.bg) / counts
            for k in range(self.dims):
                r.pos[:,k] = np.bincount(mapping, org.pos[:,k]) / counts
            return r
                
        clusterEstim = getClusterData(self.data.estim)
        clusterCrlb = getClusterData(self.data.crlb)
        
        ds = Dataset(len(clusterPos), self.dims, self.imgshape, config=self.config)
        ds.data.estim = clusterEstim
        ds.data.crlb = clusterCrlb
        ds.sigma = np.ones(self.dims)*maxDistance
        
        clusters = [[] for i in range(len(ds))]
        for i in range(len(mapping)):
            clusters[mapping[i]].append(i)
        for i in range(len(clusters)):
            clusters[i] = np.array(clusters[i])
        
        return ds, mapping, clusters#clusterPos, clusterCrlb, mapping 
    
    def save(self,fn):
        ext = os.path.splitext(fn)[1]
        if ext == '.hdf5':
            self.save_hdf5(fn)
        else:
            raise ValueError('unknown extension')
            
    def save_hdf5(self,fn):
        print(f"Saving hdf5 to {fn}")
    
        with h5py.File(fn, 'w') as f:
            dtype = [('frame', '<u4'), 
                     ('x', '<f4'), ('y', '<f4'),
                     ('photons', '<f4'), 
                     ('sx', '<f4'), ('sy', '<f4'), 
                     ('bg', '<f4'), 
                     ('lpx', '<f4'), ('lpy', '<f4'), 
                     ('lI', '<f4'), ('lbg', '<f4'), 
                     ('ellipticity', '<f4'), 
                     ('net_gradient', '<f4')]

            if 'sigma' in self.data.estim.dtype.fields:
                dtype.append(('lsx', '<f4'))
                dtype.append(('lsy', '<f4'))
            
            if self.dims==3:
                for fld in [('z', '<f4'), ('lpz', '<f4')]:
                    dtype.append(fld)
            
            locs = f.create_dataset('locs', shape=(len(self),), dtype=dtype)
            locs['frame'] = self.framenum
            locs['x'] = self.pos[:,0]
            locs['y'] = self.pos[:,1]
            locs['lpx'] = self.crlb.pos[:,0]
            locs['lpy'] = self.crlb.pos[:,1]

            if self.dims==3:
                locs['z'] = self.pos[:,2]
                locs['lpz'] = self.crlb.pos[:,2]
                        
            locs['photons'] = self.photons
            locs['bg'] = self.background
            if 'sigma' in self.data.estim.dtype.fields:
                locs['sx'] = self.data.estim.sigma[:,0]
                locs['sy'] = self.data.estim.sigma[:,1]
                locs['lsx'] = self.crlb.sigma[:,0]
                locs['lsy'] = self.crlb.sigma[:,1]
            locs['lI'] = self.crlb.photons,
            locs['lbg'] = self.crlb.bg
            locs['net_gradient'] = 0
                                
            info =  {'Byte Order': '<',
                     'Camera': 'Dont know' ,
                     'Data Type': 'uint16',
                     'File': fn,
                     'Frames': int(np.max(self.framenum)+1 if len(self.framenum)>0 else 0),
                     'Width': int(self.imgshape[1]),
                     'Height': int(self.imgshape[0])
                     }
            
            info_fn = os.path.splitext(fn)[0] + ".yaml" 
            with open(info_fn, "w") as file:
                yaml.dump(info, file, default_flow_style=False) 
    
    @staticmethod
    def load_hdf5(fn):
        
        with h5py.File(fn, 'r') as f:
            locs = f['locs']
            
            info_fn = os.path.splitext(fn)[0] + ".yaml" 
            with open(info_fn, "r") as file:
                if hasattr(yaml, 'unsafe_load'):
                    obj = yaml.unsafe_load_all(file)
                else:
                    obj = yaml.load_all(file)
                obj=list(obj)[0]
                imgshape=np.array([obj['Height'],obj['Width']])

            if 'z' in locs:
                dims = 3
            else:
                dims = 2

            ds = Dataset(len(locs), dims, imgshape)
            ds.photons[:] = locs['photons']
            ds.background[:] = locs['bg']
            ds.pos[:,0] = locs['x']
            ds.pos[:,1] = locs['y']
            if dims==3: 
                ds.pos[:,2] = locs['z']
                ds.crlb.pos[:,2] = locs['lpz']

            ds.crlb.pos[:,0] = locs['lpx']
            ds.crlb.pos[:,1] = locs['lpy']
            ds.crlb.photons = locs['lI']
            ds.crlb.bg = locs['lbg']

            sx = np.array(locs['sx'])
            sy = np.array(locs['sy'])
            
            if 'lsx' in locs: # picasso doesnt save crlb for the sigma fits
                ds.crlb.sigma[:,0] = locs['lsx']
                ds.crlb.sigma[:,1] = locs['lsy']
            
            ds.data.estim.sigma[:,0] = locs['sx']
            ds.data.estim.sigma[:,1] = locs['sy']
            
            ds.framenum[:] = locs['frame']
            
            if 'group' in locs:
                ds.data.group = locs['group']
            
        return ds

    @staticmethod
    def load(fn, **kwargs):
        ext = os.path.splitext(fn)[1]
        if ext == '.hdf5':
            return Dataset.load_hdf5(fn)
        else:
            raise ValueError('unknown extension')
    
    @staticmethod
    def fromEstimates(estim, colnames, framenum, imgshape, crlb=None, chisq=None, roipos=None, addroipos=True, **kwargs):
        
        is3D = 'z' in colnames
        haveSigma = 'sx' in colnames
        if haveSigma:
            sx = colnames.index('sx')
            sy = colnames.index('sy')
        else:
            sx=sy=None
            
        dims = 3 if is3D else 2
        I_idx = colnames.index('I')
        bg_idx = colnames.index('bg')
        
        ds = Dataset(len(estim), dims, imgshape, haveSigma=haveSigma, **kwargs)
        ds.data.roi_id = np.arange(len(estim))
        
        if estim is not None:
            if addroipos and roipos is not None:
                estim = estim*1
                estim[:,[0,1]] += roipos[:,[1,0]]

            if np.can_cast(estim.dtype, ds.dtypeEstim):
                ds.data.estim = estim
            else:
                # Assuming X,Y,[Z,]I,bg
                ds.data.estim.pos = estim[:,:dims]
                ds.data.estim.photons = estim[:,I_idx]
                ds.data.estim.bg = estim[:,bg_idx]
                
                if haveSigma:
                    ds.data.estim.sigma = estim[:,[sx,sy]]
                    ds.sigma = np.median(ds.data.estim.sigma,0)
            
        if crlb is not None:
            if np.can_cast(crlb.dtype, ds.dtypeEstim):
                ds.data.crlb = crlb
            else:
                ds.data.crlb.pos = crlb[:,:dims]
                ds.data.crlb.photons = crlb[:,I_idx]
                ds.data.crlb.bg = crlb[:,bg_idx]

                if haveSigma:
                    ds.data.crlb.sigma = crlb[:,[sx,sy]]
            
        if chisq is not None:
            ds.data.chisq = chisq
        
        if framenum is not None:
            ds.data.frame = framenum
            
        if roipos is not None:
            ds.data.roipos = roipos
            
        return ds
    
    def info(self):
        m_crlb_x = np.median(self.crlb.pos[:,0])
        m_bg= np.median(self.background)
        m_I=np.median(self.photons)
        return f"#Spots: {len(self)}. Imgsize:{self.imgshape[0]}x{self.imgshape[1]} pixels. Median CRLB X: {m_crlb_x:.2f} [pixels], bg:{m_bg:.1f}. I:{m_I:.1f}"
        
    
    def simulateMovie(self, psf : Estimator, tiff_fn, numframes, ontimes_generator, background=5, drift=None):
        if len(psf.sampleshape) != 2:
            raise ValueError('Expecting a 2D PSF')
            
        with MultipartTiffSaver(tiff_fn) as tifwriter:
            
            for f,ontimes in enumerate(tqdm.tqdm(ontimes_generator, total=numframes)):
                
                idx = np.where(ontimes>0)[0]
                
                params = np.zeros((len(idx),2+self.dims))
                params[:,:self.dims] = self.pos[idx]
                if drift is not None:
                    params[:,:self.dims] += drift[f,None]
                params[:,self.dims] = ontimes[idx]*self.photons[idx]
                roisize = np.array(psf.sampleshape)
                roipos = (params[:,[1,0]] - roisize//2).astype(np.int32)
                params[:,[1,0]] -= roipos
                
                rois = psf.ExpectedValue(params)
                img = psf.ctx.smlm.DrawROIs(self.imgshape, rois, roipos)
                img += background
                smp = np.random.poisson(img)
                tifwriter.save(smp)
                
        
    
    @staticmethod
    def fromQueueResults(qr, imgshape, **kwargs) -> Dataset:
        return Dataset.fromEstimates(qr.estim,  qr.colnames, qr.ids, imgshape, qr.crlb, qr.chisq, roipos=qr.roipos, **kwargs)
    