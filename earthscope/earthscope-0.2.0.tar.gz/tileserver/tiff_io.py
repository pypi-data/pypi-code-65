import rasterio
import tempfile

def read_tiff(tiff_path):
    with rasterio.open(tiff_path, 'r') as im:
        im_data = im.read()
        im_profile = im.profile
        im_profile['count'] = len(im_data)
        return (im_data, im_profile)

def write_tiff(im_data, im_profile, source_tiff_path=None):
    outputTiff = tempfile.NamedTemporaryFile(suffix=".tiff")
    im_profile['count'] = len(im_data)

    with rasterio.open(outputTiff.name, 'w', **im_profile) as dst:
        dst.write(im_data)
    
    return outputTiff

def sniff_tiff(tiff_path, sniffing_func):
    with rasterio.open(tiff_path, 'r') as im:
        return sniffing_func(im)

def sniff_tiff_shape(tiff_path):
    return sniff_tiff(tiff_path, lambda im: im.shape)