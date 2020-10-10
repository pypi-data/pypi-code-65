import numpy

def fix_photoscan_nodata(im_data, im_profile):
    # Ox outputs GeoTiffs where nodata=0, but Photoscan defaults to nodata=MAX
    # see https://github.com/ceresimaging/ra/issues/518
    im_data[im_data == numpy.iinfo(im_data.dtype).max] = 0
    return im_data, im_profile
