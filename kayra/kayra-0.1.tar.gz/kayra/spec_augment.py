import random
import numpy as np
import tensorflow as tf
# from tensorflow_addons.image import sparse_image_warp
from kayra.sparse_image_warp import sparse_image_warp



def spec_augment(spec: np.ndarray, num_masks=1, F=30, T=80, W=80, mask_type='mean', freq_mask=True, time_mask=True, time_warp=True):
    """ Implementation of the Spec Augment method, which consists of applying 3 transformations
        to a spectrogram of an audio waveform.

        SpecAgument time-warps the spectrogram, masks blocks of frequency channels and masks 
        blocks of utterances of time. 

        The aproach consists of randomly selecting the position on the spectrogram to conduct 
        these operations and subsequentely randomly selecting the number of frequency channels
        and time bins to mask and warp from a range

        The method is best describe here: https://arxiv.org/abs/1904.08779

        Arguments:
            spec {np.ndarray} -- The spectrogram
            num_masks {int} -- Number of masks that will be created in each axis (default: {1})
            F {int} -- Maximum number of frequency channels to be masked in each masking operation (default: {30})
            T {int} -- Maximum number of utterances of time to be masked in each masking operation (default: {80})
            W {int} -- Maximum number of utterances of time that will be warped (default: {80})
            mask_type {str} -- Type of masking. Valid values are 'mean', 'zero', 'min' or 'max' (default: {'mean'})
            freq_mask {bool} -- Toggles frequency masking (default: {True})
            time_mask {bool} -- Toggles time bins masking (default: {True})
            time_warp {bool} -- Toggles time warping (default: {True})

        Returns:
            np.ndarray -- The modified Spectrogram
    """
    mask_types = ['mean', 'zero', 'min', 'max']

    assert mask_type in mask_types, "invalid mask option, possible choices are { 'mean', 'zero', 'min', 'max' }"
    spec = spec.copy()
    mask_dict = {
        'mean': spec.mean(),
        'zero': 0,
        'min': spec.min(),
        'max': spec.max()
    }

    num_freq_channels = spec.shape[1]
    num_time_steps = spec.shape[0]

    #time warping
    if time_warp:
        assert W > 0, "W must be > 0"
        freq_center = num_freq_channels // 2

        point_to_warp = random.randrange(W, num_time_steps - W)
        w = random.randrange(-W, W)

        scr_pts = tf.convert_to_tensor([[[point_to_warp, freq_center]]], dtype=tf.float32)
        dest_pts = tf.convert_to_tensor([[[point_to_warp + w, freq_center]]], dtype=tf.float32)

        tensor_img = tf.convert_to_tensor([spec], dtype=tf.float32)
        tensor_img = tf.expand_dims(tensor_img, 3)

        spec = sparse_image_warp(tensor_img, scr_pts, dest_pts, num_boundary_points=2)[0].numpy()
        spec = spec.reshape(num_time_steps, num_freq_channels)

    for i in range(num_masks):
        #freq_mask
        if freq_mask:
            assert F > 0, "F must be > 0"
            f = random.randrange(0, F) # f will be the number of masked frequency bins
            f0 = random.randrange(0, num_freq_channels - f)
            spec[:, f0:f0+f] = mask_dict[mask_type]

        #time mask
        if time_mask:
            assert T > 0, "T must be > 0"
            t = random.randrange(0, T) # t will be the number of masked time steps
            t0 = random.randrange(0, num_time_steps - t)
            spec[t0:t0+t, :] = mask_dict[mask_type]

    return spec
