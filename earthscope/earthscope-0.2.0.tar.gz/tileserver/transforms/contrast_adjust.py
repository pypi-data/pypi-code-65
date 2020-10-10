from numpy import swapaxes
import cv2
from functools import partial, update_wrapper

from improc.imops import imcalcs

def _is_grayscale(img):
    return img.ndim == 2 or (img.ndim >= 3 and img.shape[2] == 1)

def contrast_adjust(im_data, im_profile, method="optimized_linear", **kwargs):
    # Re-order axes for CV2
    im_data = swapaxes(swapaxes(im_data, 0, 1), 1, 2)

    input_is_grayscale = _is_grayscale(im_data)
    input_shape = im_data.shape
    if input_is_grayscale:
        im_data = cv2.cvtColor(im_data, cv2.COLOR_GRAY2BGR)

    im_data = imcalcs.contrast_adjust(im_data, method=method, **kwargs)

    if input_is_grayscale:
        im_data = cv2.cvtColor(im_data, cv2.COLOR_BGR2GRAY)
        im_data.shape = input_shape

    # Restore our axes order from CV2
    im_data = swapaxes(swapaxes(im_data, 1, 2), 0, 1)

    return im_data, im_profile

# Add clahe_adjust(), etc to the module
locals().update({ 
    method: update_wrapper(partial(contrast_adjust, method=method), contrast_adjust)
    for method in [
        "optimized_linear",
        "clahe_adjust",
        "bright_adjust",
        "linear"
    ] 
})
