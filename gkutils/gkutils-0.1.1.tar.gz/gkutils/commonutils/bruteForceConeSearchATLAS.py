#!/usr/bin/env python
"""Is object in the list of ATLAS exposures?

Usage:
  %s <atlasCentresFile> <inputCoordsFile> [--searchradius=<searchradius>] [--footprints] [--red]
  %s (-h | --help)
  %s --version

Options:
  -h --help                      Show this screen.
  --version                      Show version.
  --searchradius=<searchradius>  Cone search radius in degrees. [default: 3.86]
  --footprints                   Give me the ATLAS footprints that overlap this RA and Dec. (Otherwise do a cone search.)
  --red                          Give me the full ATLAS reduced file locations.


Example:
   %s atlas_coordinates.tst test_coordinates.tst

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, shutil, re
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile, coords_sex_to_dec, bruteForceGenericConeSearch, isObjectInsideATLASFootprint

atlas_regex = '(0[12]a)([56][0-9]{4})o([0-9]{4})([A-Za-z])'
atlas_regex_compiled = re.compile(atlas_regex)

def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)

    atlasCentres = readGenericDataFile(options.atlasCentresFile, delimiter='\t')
    inputCoords = readGenericDataFile(options.inputCoordsFile, delimiter=',')

    radius = 3.86
    try:
        radius = float(options.searchradius)

    except ValueError as e:
        pass

    if options.footprints:
        for row in inputCoords:
            try:
                ra = float(row['ra'])
                dec = float(row['dec'])
            except ValueError as e:
                ra, dec = coords_sex_to_dec(row['ra'], row['dec'])

            for r in atlasCentres:
                if isObjectInsideATLASFootprint(ra, dec, float(r['ra_deg']), float(r['dec_deg'])):
                    reSearch = atlas_regex_compiled.search(r['expname'])
                    if reSearch:
                        camera = reSearch.group(1)
                        mjd = reSearch.group(2)
                        expno = reSearch.group(3)
                        filt = reSearch.group(4)
                        red = ''
                        if options.red:
                            red = '/atlas/red/' + camera + '/' + mjd + '/' + r['expname'] + '.fits.fz'
                        print(row['name'], red)
                    else:
                        print(row['name'], r['expname'])

    else:
        for row in inputCoords:
            try:
                ra = float(row['ra'])
                dec = float(row['dec'])
            except ValueError as e:
                ra, dec = coords_sex_to_dec(row['ra'], row['dec'])

            header, results = bruteForceGenericConeSearch(options.atlasCentresFile, [[ra, dec]], radius*3600.0, raIndex = 'ra_deg', decIndex = 'dec_deg')
            for r in results:
                exps = r.split()
                reSearch = atlas_regex_compiled.search(exps[1])
                if reSearch:
                    camera = reSearch.group(1)
                    mjd = reSearch.group(2)
                    expno = reSearch.group(3)
                    filt = reSearch.group(4)
                    red = ''
                    if options.red:
                        red = '/atlas/red/' + camera + '/' + mjd + '/' + exps[1] + '.fits.fz'
                        print (row['name'], red, "%.2f" % (float(exps[5])/3600.0))
                    else:
                        print (row['name'], exps[1], "%.2f" % (float(exps[5])/3600.0))
                else:
                    print (row['name'], exps[1], "%.2f" % (float(exps[5])/3600.0))



        


if __name__=='__main__':
    main()
    
