

import os
from astropy.io import fits


galdiff_path = os.path.join(os.path.expandvars('$FERMI_DIFFUSE_DIR'), 'gll_iem_v07.fits')
hdulist = fits.open(galdiff_path)

