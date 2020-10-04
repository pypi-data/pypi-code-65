#! /usr/bin/env python
# -*- coding: utf-8 -*-


""" very hight level module that handles spaxel extraction target/host and calibration """

import numpy as np
from astropy import coordinates, units

from . import astrometry, io, sedm
class CubeParser():

    def __init__(self, filename):
        """ """
        self.load(filename)
    # ============== #
    #  Method        #
    # ============== #
    # --------- #
    #  LOADER   #
    # --------- #
    def load(self, filename):
        """ """
        self._filename = filename
        self._cube = sedm.load_sedmcube(filename)
        self._target_radec = coordinates.SkyCoord(self.cube.header["OBJRA"],
                                                  self.cube.header["OBJDEC"],
                                                  unit=(units.hourangle, units.deg))
        self._wcsifu = astrometry.WCSIFU.from_filename(filename)

    def load_photoifu(self, mag=18):
        """ """
        from photoifu import hostparser
        self._photoifu = hostparser.HostParser([self._target_radec.ra.deg, self._target_radec.dec.deg], mag, self.cube.filename)
        self._load_subcubes_()
        
    def load_fluxcalibration(self, fluxcalfile=None):
        """ """
        if fluxcalfile is None:
            self._fluxcalfile = io.fetch_nearest_fluxcal(file = self.cube.filename)

        from .fluxcalibration import load_fluxcal_spectrum
        self._fluxcal = load_fluxcal_spectrum( self._fluxcalfile )

    def _load_subcubes_(self, buffer=8):
        """ """
        self._subcubes = {"host": self.cube.get_partial_cube( self.photoifu.ifuproject.get_spaxels_in("host"), np.arange( len((self.cube.lbda))) ),
                          "target": self.cube.get_partial_cube( self.photoifu.ifuproject.get_target_pixels(), np.arange( len((self.cube.lbda))) )}
        
    # --------- #
    #  GETTER   #
    # --------- #
    def extract_spectra(self, nofluxcal=False, **kwargs):
        """ """
        from pyifu import get_spectrum
        
        self.cube_target.extract_pointsource(**kwargs)
        es_star = self.cube_target.extractstar
        
        cube_bkgd = es_star.es_products["bkgdmodel"]
        self.spec_sky_raw = cube_bkgd.get_spectrum(cube_bkgd.get_faintest_spaxels(1))
        self.spec_sky = sedm.flux_calibrate_sedm(self.spec_sky_raw, fluxcalfile=self._fluxcalfile, nofluxcal=nofluxcal)
        
        self.spec_target_raw = es_star.es_products["spec"]
        self.spec_target = sedm.flux_calibrate_sedm(self.spec_target_raw, fluxcalfile=self._fluxcalfile, nofluxcal=nofluxcal)
        
        mean_host = self.cube_host.get_spectrum(np.arange( self.cube_host.nspaxels ))
        self.spec_host_raw = get_spectrum(mean_host.lbda, mean_host.data- self.spec_sky.data,
                                            variance=mean_host.variance, header=mean_host.header)
        self.spec_host = sedm.flux_calibrate_sedm(self.spec_host_raw, fluxcalfile=self._fluxcalfile, nofluxcal=nofluxcal)
        
        

    # ============== #
    #  Properties    #
    # ============== #
    @property
    def cube(self):
        """ """
        if not hasattr(self,"_cube"):
            self._cube = None
        return self._cube
    
    @property
    def fluxcalibration(self):
        """ """
        if not hasattr(self,"_fluxcal"):
            self.load_fluxcalibration()
        return self._fluxcal

    @property
    def fluxcalfile(self):
        """ """
        if not hasattr(self,"_fluxcalfile"):
            self.load_fluxcalibration()
        return self._fluxcalfile

    @property
    def cube_target(self):
        """ """
        if not hasattr(self,"_subcubes"):
            return None
        return self._subcubes["target"]
    
    @property
    def cube_host(self):
        """ """
        if not hasattr(self,"_subcubes"):
            return None
        return self._subcubes["host"]
    
    @property
    def wcsifu(self):
        """ """
        if not hasattr(self,"_wcsifu"):
            self._wcsifu = None
        return self._wcsifu

    @property
    def photoifu(self):
        """ """
        if not hasattr(self,"_photoifu"):
            self.load_photoifu()
        return self._photoifu

    
