# Fits image object
# Derek Fujimoto
# Nov 2019

import os
import numpy as np
import pandas as pd

from bccd.backend.functions import gaussian2D
from astropy.io import fits as astrofits

from scipy.optimize import curve_fit
from scipy.integrate import dblquad

from bccd.backend.PltTracker import PltTracker
from matplotlib.patches import Circle

import skimage as ski
from skimage import filters
from skimage.feature import canny
from skimage.transform import hough_circle,hough_circle_peaks
from skimage.transform import probabilistic_hough_line
from skimage.transform import rescale

plt_global = PltTracker()

# =========================================================================== #
class fits(object):
    """
        Data Fields: 
        
            black:          float, pixel value corresponding to black (zero)
            data:           2D numpy array, pixel values
            data_original:  numpy array, pixel values
            filename:       name of the file
            header:         dict, header information
            
            mask:           (x,y,r) specifying circle to mask on
            
            plt:            PltTracker object or None
            result_center:      (par,names) fitting results
            result_cm:          (par,names) center of mass results
            result_fit2D:       (par,cov) fitting results
            result_gaussian2D:  (par,cov,names) fitting results
            result_gaussian2D_overlap: float, overlap
            
        Colormaps: 
            Greys
            Purples
            Yellows
            Blues
            Oranges
            Reds
            Greens
            ...
                
            https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    """
    show_options = {'origin':'lower',
                    'interpolation':'nearest'}
    
    # ======================================================================= #
    def __init__(self,filename, plt=None, rescale_pixels=True):
        """
            Read the file
            self.plt: plot tracker
            rescale_pixels: if True, rescale image such that pixels are square
        """
        self.filename = filename
        self.read(filename,rescale_pixels=rescale_pixels)
        self.data_original = np.copy(self.data)
        self.set_mask(None)
        
        if plt is None:
            self.plt = plt_global
        else:
            self.plt = plt
            
    # ======================================================================= #
    def detect_lines(self,sigma=1,min_length=50,min_gap=3,theta=None,nlines=np.inf,
                     draw=True):
        """
            Detect lines in image
            
            nlines:     number of line s to find
            min_length: minimum length of lines to find
            min_gap:    minimum gap between pixels to avoid breaking the line    
            theta:      list of acceptable angles for the lines to point
            
            returns: list of points ((x0,y0),(x1,y1)) to identify the end points of 
                     the lines
        """
        
        # get raw data
        data = self.data
        
        # get edges
        edges = canny(data,sigma=sigma, low_threshold=0, high_threshold=1)
        
        # select lines
        lines = probabilistic_hough_line(edges,threshold=10,line_length=min_length,
                                         line_gap=min_gap,theta=theta)
        # draw
        if draw:
            self.plt.figure()
            self.plt.imshow(data,alpha=1,cmap='Greys_r',**self.show_options)
            edges = np.ma.masked_where(~edges,edges.astype(int))
            self.plt.imshow(edges,alpha=1,cmap='Reds_r',**self.show_options)
            
            for line in lines:
                self.plt.plot(*tuple(np.array(line).T))
                
        # return 
        return lines

    # ======================================================================= #
    def detect_hlines(self,sigma=1,min_length=50,min_gap=3,nlines=np.inf,
                   draw=True,**kwargs):
        """
            Detect horizontal lines in image
            
            nlines:     number of line s to find
            min_length: minimum length of lines to find
            min_gap:    minimum gap between pixels to avoid breaking the line    
            
            returns: list of y positions to identify each line
        """
        
        # make a set of ranges about pi/2
        theta = np.linspace(np.pi/2-0.01,np.pi/2+0.01,30)
        
        # get lines 
        lines = get_lines(sigma=sigma,
                          min_length=min_length,
                          min_gap=min_gap,
                          nlines=nlines,
                          draw=draw,
                          theta=theta,
                          **kwargs)
        
        # get y values of lines 
        return [l[0][1] for l in lines]
    
    # ======================================================================= #
    def detect_circles(self,rad_range,nlines=1,sigma=1,draw=True):
        """
            Detect circles in image
            
            rad_range:  specify raidus search range (lo,hi)
            alpha:      draw transparency
            nlines:     number of circles to find
            
            returns: (center_x,center_y,radius)
        """
        
        # get raw data
        data = np.copy(self.data)
        data[self.data.mask] = self.black
        
        # get edges
        edges = canny(data,sigma=sigma, low_threshold=0, high_threshold=1)
        
        # get radii
        hough_radii = np.arange(*rad_range, 2)
        hough_res = hough_circle(edges, hough_radii)
        
        # select cicles 
        accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii,
                                                    total_num_peaks=nlines)
        
        # draw
        if draw:
            self.plt.imshow(self.filename,data,alpha=1,cmap='Greys_r',**self.show_options)
            edges = np.ma.masked_where(~edges,edges.astype(int))
            self.plt.imshow(self.filename+'edges',edges,alpha=1,cmap='Reds_r',**self.show_options)
            
            for center_y, center_x, radius in zip(cy, cx, radii):
                circle = Circle((center_x,center_y),radius,
                            facecolor='none',linewidth=1,edgecolor='g')
                self.plt.gca().add_patch(circle)
                
        # return 
        return (cx,cy,radii)
    
    # ======================================================================= #
    def draw(self,black=None,alpha=1,cmap='Greys',imap=True):
        """
            Draw fits file to matplotlib figure
            
            black:      set black level
            alpha:      draw transparency
            cmap:       colormap
            imap:       invert the colour map
        """
        
        # get raw data
        if black is not None:
            self.set_black(black)
        data = self.data
        
        # color map 
        if imap: cmap+='_r'
        
        # draw
        self.plt.imshow(id=self.filename,X=data,alpha=alpha,cmap=cmap,**self.show_options)
    
    # ======================================================================= #    
    def draw_2Dfit(self,fn,*pars,levels=10,cmap='jet'):
        """
            Draw the fit function as contours
        
        """
        
        # get image shape
        shape = self.data.shape
        
        # get function image
        x = np.arange(shape[1])    
        y = np.arange(shape[0])    
        gauss = np.zeros((len(y),len(x)))
        for i in y:
            gauss[i-y[0],:] = fn(x,i,*pars)

        # draw image
        X,Y = np.meshgrid(x,y)
        ax = self.plt.gca()
        contours = ax.contour(X,Y,gauss,levels=levels,cmap=cmap)
        ax.clabel(contours,inline=True,fontsize='x-small',fmt='%g')
        
        self.contours = contours
        return contours

    # ======================================================================= #
    def draw_contour(self,nlevels=5,alpha=1,cmap='Greys',imap=True):
        """
            Draw contours of fits file to matplotlib figure
            
            nlevels:    number of contours to draw
            alpha:      draw transparency
            cmap:       colormap    
            imap:       invert the colour map
        """
        
        data = self.data
        
        # color map 
        if imap: cmap+='_r'
        
        # draw
        X,Y = np.meshgrid(*tuple(map(np.arange,data.shape[::-1])))
        ax = self.plt.gca()
        
        options = {k:val for k,val in self.show_options.items() if k != "interpolation"}
        self.plt.contour(self.filename,X,Y,data,levels=nlevels,cmap=cmap,**options)
    
    # ======================================================================= #
    def draw_edges(self,sigma=1,alpha=1,cmap='Greys',imap=True):
        """
            Draw fits file to matplotlib figure
            
            sigma:      Standard deviation of the Gaussian filter.
            alpha:      draw transparency
            cmap:       colormap
            imap:       invert the colour map
        """
        
        # get raw data
        data = self.data
        
        # get edges
        data2 = np.copy(data)
        data2[data.mask] = self.black
        edges = canny(data2,sigma=sigma,low_threshold=0, high_threshold=1)
        
        # color map
        if imap: cmap += '_r'
        
        # draw
        edges = np.ma.masked_where(~edges,edges.astype(int))
        self.plt.imshow(self.filename, edges, alpha=alpha, cmap=cmap, **self.show_options)
        
    # ======================================================================= #
    def draw_sobel(self,alpha=1,cmap='Greys',imap=False):
        """
            Draw fits file to matplotlib figure
            
            alpha:      draw transparency
            cmap:       colormap
            imap:       invert the colour map
        """
        
        # color map
        if imap: cmap += '_r'
        
        # draw
        data = np.copy(self.data)
        sbl = filters.sobel(data)
        sbl[self.data.mask]=0
        self.plt.imshow(self.filename, 
                        sbl,
                        alpha=alpha,
                        cmap=cmap,
                        **self.show_options)
    
        return sbl
        
    # ======================================================================= #
    def fit2D(self,function,**fitargs):
        """
            Fit general function to fits file
            
            function:   python function handle
            
            returns curve_fit output
        """
        
        # get data and trim the edges
        data = self.data[:300,:200]
        
        # flatten the image
        flat = np.ravel(data)
        
        # get number of fit parameters (first two are x,y)
        npar = function.__code__.co_argcount-2
        if 'p0' not in fitargs:
            fitargs['p0'] = np.ones(npar)
            
        # get zero
        zero = np.min(flat)
        flat -= zero
        
        # normalize
        flat /= np.max(flat)
        
        # flatten the funtion 
        def fitfn(xy,*pars):    
            output = function(*xy,*pars)
            return np.ravel(output)
        
        # fit
        x = np.indices(data.shape)[::-1]
        par,cov = curve_fit(fitfn,x,flat,**fitargs)
        
        self.result_fit2D = (par,cov)
        return (par,cov)
    
    # ======================================================================= #    
    def fit_gaussian2D(self,draw=True,**fitargs):
        """
            Fit 2D gaussian to image
            
            draw:       draw the output
        """
        
        # get data 
        data = self.data
        
        # estimate moments https://scipy-cookbook.readthedocs.io/items/FittingData.html
        total = data.sum()
        X, Y = np.indices(data.shape)
        x = (X*data).sum()/total
        y = (Y*data).sum()/total
        col = data[:, int(y)]
        width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
        row = data[int(x), :]
        width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum()) 
        
        # fit 
        p0 = (x,y,width_x,width_y,1,0)
        par,cov = self.fit2D(gaussian2D,p0=p0)
        std = np.diag(cov)**0.5
        
        # make output
        df = pd.DataFrame({"result":par,"error":std},
                            index=('x0','y0','sigmax','sigmay','amp','theta'))
        
        # draw output
        if draw:
            self.plt.figure()    
            self.draw()
            contours = self.draw_2Dfit(gaussian2D,*par[:4],1,0,**fitargs)
            
            self.plt.xlim((par[0]-4*par[2],par[0]+4*par[2]))
            self.plt.ylim((par[1]-4*par[3],par[1]+4*par[3]))
            self.plt.gca().clabel(contours,inline=True,fontsize='x-small',fmt='%g')
    
        self.result_gaussian2D = df
        
        return df
    
    # ======================================================================= #    
    def get_center(self,draw=True):
        """
            Get image center of mass
            
            draw:       if true, draw the output
            returns:    x0,y0,sigx,sigy
        """
        
        # get raw data
        data = self.data
        black = max(self.black,self.header['BZERO'])
            
        # compress
        sumx = np.ma.mean(data,axis=0)
        sumy = np.ma.mean(data,axis=1)
        
        # shift baseline
        sumx -= black
        sumy -= black
        
        # normalize
        normx = np.ma.max(sumx)
        normy = np.ma.max(sumy)
        
        sumx /= normx
        sumy /= normy
        
        # fit with gaussian
        gaus = lambda x,x0,sig,amp,base : amp*np.exp(-((x-x0)/(2*sig))**2)+base
        
        parx,cov = curve_fit(gaus,np.arange(len(sumx)),sumx,p0=(180,10,1,0),
                                bounds=((0,0,0,-np.inf),np.inf))
        stdx = np.diag(cov)**0.5
        
        pary,cov = curve_fit(gaus,np.arange(len(sumy)),sumy,p0=(260,10,1,0),
                                bounds=((0,0,0,-np.inf),np.inf))
        stdy = np.diag(cov)**0.5               
        
        # draw
        if draw:
            self.plt.figure()
            self.plt.plot(sumx*normx,label='x')
            self.plt.plot(sumy*normy,label='y')
            
            fitx = np.linspace(0,max(len(sumx),len(sumy)),5000)
            self.plt.plot(fitx,gaus(fitx,*parx)*normx,color='k')
            self.plt.plot(fitx,gaus(fitx,*pary)*normy,color='k')     
            self.plt.legend()
            
            self.plt.figure()
            self.plt.imshow(self.filename,data,cmap='Greys_r',**self.show_options)
            self.plt.errorbar(parx[0],pary[0],xerr=2*parx[1],yerr=2*pary[1],fmt='o',
                          fillstyle='none',markersize=9)
                          
            if pary[1] > 2 and parx[1] > 2:
                self.plt.ylim(pary[0]-pary[1]*6,pary[0]+pary[1]*6)   
                self.plt.xlim(parx[0]-parx[1]*6,parx[0]+parx[1]*6)
                
                
        self.result_center = ((parx[0],pary[0],parx[1],pary[1]),
                              ('x0','y0','sigx','sigy'))
                
        # return 
        return (parx[0],pary[0],parx[1],pary[1])

    # ======================================================================= #
    def get_cm(self,draw=True):
        """
            Get image center of mass
            
            draw:       if true, draw the output
        """
        
        # get raw data
        data = self.data
        
        # compress
        sumx = np.ma.mean(data,axis=0)
        sumy = np.ma.mean(data,axis=1)
        
        # estimate center with weighted average
        sumx -= np.ma.min(sumx)
        sumy -= np.ma.min(sumy)
        
        nsumx = len(sumx)
        nsumy = len(sumy)
        
        cx = np.ma.average(np.arange(nsumx),weights=sumx)
        cy = np.ma.average(np.arange(nsumy),weights=sumy)

        # draw
        if draw:
            self.plt.figure()
            self.plt.imshow(self.filename,data,cmap='Greys_r',**self.show_options)
            self.plt.plot(cx,cy,'x')
                
        self.result_cm = ((cx,cy),('x0','y0'))
        
        # return 
        return (cx,cy)

    # ======================================================================= #
    def get_gaussian2D_overlap(self,ylo,yhi,xlo,xhi):
        """
            Get integral of gaussian2D PDF within some interval, normalized to the 
            area such that the returned overlap is the event probability within the 
            range. 
            
            ylo:    lower integration bound [outer] (float)
            yhi:    upper integration bound [outer] (float)
            xlo:    lower integration bound [inner] (lambda function)
            xlhi:   upper integration bound [inner] (lambda function)
            
                integration is: 
                    
                    int_y int_x G(x,y) dx dy
            
            
            returns overlap as given by dblquad
        """
        
        # get fitting results 
        x0,y0,sx,sy,amp,theta = self.result_gaussian2D['result']
        
        # get normalized amplitude
        # https://en.wikipedia.org/wiki/Gaussian_function
        a = 0.5*(np.cos(theta)/sx)**2 + 0.5*(np.sin(theta)/sy)**2
        b = 0.25*-(np.sin(theta)/sx)**2 + 0.25*(np.sin(theta)/sy)**2
        c = 0.5*(np.sin(theta)/sx)**2 + 0.5*(np.cos(theta)/sy)**2
        amp = np.sqrt(a*c-b**2)/np.pi
        
        # make PDF
        gaus = lambda x,y: self.gaussian2D(x,y,x0,y0,sx,sy,amp,theta)
        
        # integrate: fraction of beam overlap
        overlap =  dblquad(gaus,ylo,yhi,xlo,xhi)[0]
        
        self.result_gaussian2D_overlap = overlap
        return overlap
        
    # ======================================================================= #
    def read(self,filename,rescale_pixels=True):
        """
            Get xy data from fits file. Values are brightness of pixel. 
            
            filename:       name of file to open
            rescale_pixels: if True, rescale image such that pixels are square
        """
        
        # open the file
        filename = os.path.join(os.getcwd(),filename)
        fid = astrofits.open(filename)[0]
        
        # read the header
        self.header = fid.header
        
        # get the data
        data = fid.data

        # fix bad pixels: set to max
        data[data<self.header['BZERO']] = np.max(data)
        self.black = self.header['BZERO']
        
        # rescale image to correct pixel size asymmetry
        if rescale_pixels:
            aspect = self.header['YPIXSZ']/self.header['XPIXSZ']
            
            # always enlarge image, never make it smaller
            if aspect > 1:      resc = (aspect,1)
            else:               resc = (1,1/aspect)
            
            data = rescale(data,resc,order=3,multichannel=False,preserve_range=True) 
        
        self.data = data
        
    # ======================================================================= #
    def set_black(self,black):
        """
            Clean, remove lowest values
            
            black:  value to set to black, all pixels of lower value raised to 
                    this level
        """
        
        # set the black input
        self.black = black
        
        # apply black input and mask settings
        self.set_mask(self.mask)
        
    # ======================================================================= #
    def set_mask(self,mask):
        """
            Mask image data
            mask:       (x,y,r) specifying center and radius of circle to mask on
        """
        
        # set the mask input
        self.mask = mask
        
        # reset blacklevel
        data = np.copy(self.data_original)
        data[data<self.black] = self.black
        
        # masking
        if mask is not None:     
            window = np.ones(self.data.shape)
            rr,cc = ski.draw.disk((mask[1],mask[0]),mask[2],shape=data.shape)
            window[rr,cc] = 0
            data = np.ma.array(data,mask=window)
        
        # make as a masked array
        else:
            data = np.ma.asarray(data)
        
        self.data = data
        
