from tileserver.transforms import convert_to_8bit, convert_to_rgb
from tileserver.transforms.contrast_adjust import optimized_linear, clahe_adjust, bright_adjust, linear

from tileserver.tiff_transform_cache import transform_if_needed

def all_bands_uint8(im):
    if all(dtype == 'uint8' for dtype in im.dtypes):
        return True
    elif all(dtype == 'uint16' for dtype in im.dtypes):
        return False
    else:
        raise Exception(f"Not sure how to convert TIFF with channels of type: {im.dtypes}")

def convert_to_rgb_8bit_if_needed(tiff_path, adjust_contrast=True):
    transform_chain = (
        convert_to_rgb,
        convert_to_8bit,
    )

    if adjust_contrast:
        transform_chain += (optimized_linear,)
        # transform_chain += (linear, clahe_adjust)

        # transform_chain += (linear,)
        # transform_chain += (bright_adjust,)

    return transform_if_needed(
        tiff_path,
        transform_chain=transform_chain,
        skip_transform_if=all_bands_uint8
    )
