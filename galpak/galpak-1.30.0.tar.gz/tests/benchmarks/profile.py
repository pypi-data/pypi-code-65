#!/usr/bin/python3.5

import galpak, sys
import pprofile

gk=galpak.GalPaK3D('data/input/GalPaK_cube_1101_from_paper.fits')
prof = pprofile.Profile()

with prof:
    gk.run_mcmc(max_iterations=5000,random_scale=2, verbose=False)

prof.annotate(sys.stdout)
