#tutorial file
import os
import sys
from astro_ghost.PS1QueryFunctions import getAllPostageStamps
from astro_ghost.TNSQueryFunctions import getTNSSpectra, clean_spectra
from astro_ghost.NEDQueryFunctions import getNEDSpectra
from astro_ghost.ghostHelperFunctions import getTransientHosts, getGHOST
from astropy.coordinates import SkyCoord
from astropy import units as u
import pandas as pd

verbose = 1
#download the database from ghost.ncsa.illinois.edu
getGHOST(real=False, verbose=verbose)

#getdummyGHOST()
snName = ['SN 2012dt', 'SN 1998bn', 'SN 1957B']
snCoord = [SkyCoord(14.162*u.deg, -9.90253*u.deg, frame='icrs'), SkyCoord(187.32867*u.deg, -23.16367*u.deg, frame='icrs'), SkyCoord(186.26125*u.deg, +12.899444*u.deg, frame='icrs')]
snClass = ['SN IIP', 'SN', 'SN Ia']

hosts = getTransientHosts(snName, snCoord, snClass, verbose=verbose, starcut='aggressive')

hSpecPath = "./hostSpectra/"
tSpecPath = "./SNspectra/"
psPath = "./hostPostageStamps/"
paths = [hSpecPath, tSpecPath, psPath]
for tempPath in paths:
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

hosts = pd.read_csv("./transients_20201012//tables/FinalAssociationTable.csv")
transients = pd.read_csv("./transients_20201012/tables/transients_20201012.csv")
getAllPostageStamps(hosts, 120, psPath, verbose)
getNEDSpectra(hosts, hSpecPath, verbose)
getTNSSpectra(transients, tSpecPath, verbose)

clean_spectra(tSpecPath)

from datetime import datetime
import pandas as pd
import numpy as np
import pickle
from collections import Counter
from astro_ghost.ghostHelperFunctions import fullData
