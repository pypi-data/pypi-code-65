from scipy.interpolate import RegularGridInterpolator
import numpy as np
from astropy.io import fits
import pandas as pd

class Resampling:
    """
    Resampling does SOMETHING.
    ##########
    - Inputs:
      - image = 2D array of original image
      - trace_x = 1D array of pixel X locations of trace
      - trace_y = 1D array of pixel Y locations of trace, running parallel to trace_x
      - trace_dx = 1D array of pixel dx directions given each trace (x,y) location, running parallel to trace_x
      - trace_dy = 1D array of pixel dy directions given each trace (x,y) location, running parallel to trace_x
      - aperture_size = int as size in pixels of the new resampling grids.
    - Notes:
      - hstgrism.aperturedirection.ApertureDirection can construct (dx,dy).
      - Resampling will produce a new image with nrow = 2 * aperture_size + 1, and ncol = len(trace_x).
      - The resampling grid assumes radius from np.arange(-aperture_size, aperture_size + 1) centered at trace given direction (dx,dy).
    - Compute:
      - Use self.compute(params_regulargridinterpolator) after properly instantiated
      - params_regulargridinterpolator = dict with keywords to specify scipy.interpolate.RegularGridInterpolator(**params_regulargridinterpolator)
        - if None, params_regulargridinterpolator = {'method':'linear','bounds_error':True,'fill_value':np.nan} is assigned.
      - self.image_interpolator = access image interpolator with the original image as the template. To use, self.image_interpolator((row,col))
      - self.resampling = dict with keywords as index parallel to self.trace_x, and values as another dict composing of:
        - self.resampling[index]['xcut'] = 1D array of pixel X at the resampling locations w.r.t. the original image
        - self.resampling[index]['ycut'] = 1D array of pixel Y at the resampling locations w.r.t. the original image
        - self.resampling[index]['value'] = 1D array of values at the resampling locations w.r.t. the original image
        - self.image_resampling = 2D image of the resampling.
          - trace would be centered at row index = aperture_size (using 0 indexing), and dispersed along columns
          - columns map directly the self.trace_x, running parallelly.
    - Save:
      - Use self.save(trace_ww,container) to save the computation. This will overwrite existing files if any.
        - container = Container class. See hstgrism.container.Container.
        - trace_ww = 1D array of wavelength running parallel to pixel X on the resampling image (i.e., running parallel to self.trace_x in the original image)
        - ./savefolder/saveprefix_resampling.fits = resampling image in extension 1 (extension 0 as empty primaryHDU)
        - ./savefolder/saveprefix_resampling.csv = csv table of trace/wavelength w.r.t. the resampling image
        - savefolder and saveprefix are specified by container.
    """
    def __init__(self,image,trace_x,trace_y,trace_dx,trace_dy,aperture_size):
        self.image = image
        self.trace_x = trace_x
        self.trace_y = trace_y
        self.trace_dx = trace_dx
        self.trace_dy = trace_dy
        self.aperture_size = aperture_size
    def compute(self,params_regulargridinterpolator=None):
        if params_regulargridinterpolator is None:
            params_regulargridinterpolator = {'method':'linear','bounds_error':True,'fill_value':np.nan}
        nrow,ncol = self.image.shape
        self.image_interpolator = RegularGridInterpolator((np.arange(nrow),np.arange(ncol)),self.image,**params_regulargridinterpolator)
        aperture_size_array = np.arange(-self.aperture_size,self.aperture_size+1)
        ##### prepare new sampling locations #####
        ##### use interpolator to get new values #####
        self.resampling = {}
        for ii,i in enumerate(self.trace_x):
            tx,ty = self.trace_x[ii],self.trace_y[ii]
            tdx,tdy = aperture_size_array * self.trace_dx[ii], aperture_size_array * self.trace_dy[ii]
            tx,ty = tx+tdx,ty+tdy
            t = np.array(tuple(zip(ty,tx)))
            tv = self.image_interpolator(t)
            self.resampling[ii] = {'xcut':tx,'ycut':ty,'value':tv}
        ##### make new image #####
        ncol_resampling, = self.trace_x.shape
        nrow_resampling = self.aperture_size * 2 + 1
        self.image_resampling = np.empty((nrow_resampling,ncol_resampling))
        for ii,i in enumerate(self.resampling):
            self.image_resampling[:,ii] = self.resampling[i]['value']
    def save(self,trace_ww=None,container=None):
        if container is None:
            raise ValueError('container must be specified. Use hstgrism.container.Container')
        ##### resampling.fits #####
        phdu = fits.PrimaryHDU()
        ihdu = fits.ImageHDU(self.image_resampling)
        hdul = fits.HDUList([phdu,ihdu])
        string = './{0}/{1}_resampling.fits'.format(container.data['savefolder'],container.data['saveprefix'])
        hdul.writeto(string,overwrite=True)
        print('Save {0}'.format(string))
        ##### resampling.csv #####
        ncol_resampling, = self.trace_x.shape
        tx = np.arange(ncol_resampling)
        ty = np.full_like(tx,self.aperture_size,dtype=float)
        if trace_ww is None:
            tw = np.full_like(tx,None,dtype=object)
        else:
            tw = trace_ww
        csv_table = {'x':tx,'y':ty,'ww':tw}
        string = './{0}/{1}_resampling.csv'.format(container.data['savefolder'],container.data['saveprefix'])
        pd.DataFrame(csv_table).to_csv(string)
        print('Save {0}'.format(string))
        