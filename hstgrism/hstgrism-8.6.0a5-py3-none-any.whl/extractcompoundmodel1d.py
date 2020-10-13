from astropy.modeling import models,fitting
import pandas as pd
import numpy as np
from astropy.io import fits

class ExtractCompoundModel1D:
    """
    ExtractCompoundModel1D is a class to perform grism extraction using a 1D compound model from astropy.modeling. 
    ##########
    + Assumptions:
      - dispersion = x-axis
      - cross-dispersion = y-axis
      - grism_model, bkg_model, and fitter must be working in astropy.modeling framework. Use astropy.modeling.models and astropy.modeling.fitting. We recommend:
        > grism_model = astropy.modeling.models.Gaussian1D(amplitude,mean,stddev)
        > bkg_model = astropy.modeling.models.Polynomial1D(norder)
        > fitter = astropy.modeling.fitting.LevMarLSQFitter()
    ##########
    + Inputs:
      - image = 2D array of image
      - weigth = 2D array of weights
      - grism_model = 1D array parallel to x-axis with proper initialization.
      - bkg_model = 1D array parallel to x-axis with proper initialization.
        > During the fitting process, extraction_model = grism_model + bkg_model
      - fitter = a scalar of astropy.modeling.fitting.LevMarLSQFitter() by default.
    + Compute:
      - Use self.compute() after proper instantiation.
      - self.out_fit to access the outputs. It is 1D array parallel to x-axis.
      - self.out_table to access fit parameters in a table format
      - self.out_image_grism to access 2D image of grism component from the fit
      - self.out_image_bkg to access 2D image of bkg component from the fit
    + Save:
      - Use self.save(container) where container is hstgrism.container.Container object.
        > This will save extractcompoundmodel1d.csv as self.out_table.
        > This will save extractcompoundmodel1d.fits as self.out_image_grism and self.out_image.bkg in extension 1 and 2 respectively.
    """
    def __init__(self,image,weight,
                 grism_model,
                 bkg_model,
                 fitter = fitting.LevMarLSQFitter(),
                ):
        self.image = image
        self.weight = weight
        self.grism_model = grism_model
        self.bkg_model = bkg_model
        self.fitter = fitter
    def compute(self):
        ny,nx = self.image.shape
        tx = np.arange(ny)
        out_fit = []
        for i in np.arange(nx):
            values = self.image[:,i]
            weights = self.weight[:,i]
            kernel = self.grism_model[i] + self.bkg_model[i]
            t = self.fitter(kernel,tx,values,weights=weights)
            out_fit.append(t)
        self.out_fit = out_fit
        self.out_table = self._make_out_table()
        self.out_image_grism = self._make_out_image(component='grism')
        self.out_image_bkg = self._make_out_image(component='bkg')
    def _make_out_table(self):
        ##### Gaussian1D component #####
        table = {}
        amplitude = []
        mean = []
        stddev = []
        for ii,i in enumerate(self.out_fit):
            t = self.out_fit[ii][0]
            amplitude.append(t.amplitude.value)
            mean.append(t.mean.value)
            stddev.append(t.stddev.value)
        table['amplitude'] = amplitude
        table['mean'] = mean
        table['stddev'] = stddev
        ##### Polynomial1D component #####
        degree = []
        for ii,i in enumerate(self.out_fit): # get degree for each x
            t = self.out_fit[ii][1]
            degree.append(t.degree)
        table['degree'] = degree
        degree_max = max(degree) # get degree max
        for i in np.arange(degree_max+1): # preparing output template
            string = 'c{0}'.format(i)
            table[string] = []
        for ii,i in enumerate(self.out_fit): # construct output
            t = self.out_fit[ii][1]
            for j in np.arange(degree_max+1):
                string = 'c{0}'.format(j)
                try:
                    tt = t.__getattribute__(string).value
                except:
                    tt = 0.
                table[string].append(tt)
        ##### return #####
        return pd.DataFrame(table)
    def _make_out_image(self,component):
        if component=='grism':
            component_index = 0
        elif component=='bkg':
            component_index = 1
        new_image = np.full_like(self.image,np.nan,dtype=float)
        ny,nx = new_image.shape
        tx = np.arange(ny)
        for i in np.arange(nx):
            new_image[:,i] = self.out_fit[i][component_index](tx)
        return new_image
    def save(self,container=None):
        if container is None:
            raise ValueError('container must be specified. See hstgrism.container.Container')
        ##### out_table #####
        string = './{0}/{1}_extractcompoundmodel1d.csv'.format(container.data['savefolder'],container.data['saveprefix'])
        self.out_table.to_csv(string)
        print('Save {0}'.format(string))
        ##### out_image_grism and out_image_bkg #####
        string = './{0}/{1}_extractcompoundmodel1d.fits'.format(container.data['savefolder'],container.data['saveprefix'])
        phdu = fits.PrimaryHDU()
        ihdu1 = fits.ImageHDU()
        ihdu2 = fits.ImageHDU()
        hdul = fits.HDUList([phdu,ihdu1,ihdu2])
        hdul[1].data = self.out_image_grism
        hdul[2].data = self.out_image_bkg
        hdul.writeto(string,overwrite=True)
        print('Save {0}'.format(string))
        