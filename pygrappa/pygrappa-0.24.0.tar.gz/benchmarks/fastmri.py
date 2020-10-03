import random
from time import time

import h5py
import numpy as np
import matplotlib.pyplot as plt
from pygrappa import mdgrappa as grappa_fun


def gen_mask_equidistant(kspace, accel_factor=4):
    # inspired by https://github.com/facebookresearch/fastMRI/blob/master/common/subsample.py
    shape = kspace.shape
    num_cols = shape[-1]

    center_fraction = (32 // accel_factor) / 100

    # Create the mask
    num_low_freqs = int(round(num_cols * center_fraction))
    num_high_freqs = num_cols // accel_factor - num_low_freqs
    high_freqs_spacing = (num_cols - num_low_freqs) // num_high_freqs
    acs_lim = (num_cols - num_low_freqs + 1) // 2
    mask_offset = random.randrange(high_freqs_spacing)
    high_freqs_location = np.arange(mask_offset, num_cols, high_freqs_spacing)
    low_freqs_location = np.arange(acs_lim, acs_lim + num_low_freqs)
    mask_locations = np.concatenate([high_freqs_location, low_freqs_location])
    mask = np.zeros((num_cols,))
    mask[mask_locations] = True

    # Reshape the mask
    mask_shape = [1 for _ in shape]
    mask_shape[-1] = num_cols
    mask = mask.reshape(*mask_shape)
    return mask


def load_kspace(filename):
    with h5py.File(filename, 'r') as h5_obj:
        kspace = h5_obj['kspace'][()]
        return kspace

if __name__ == '__main__':

    t0 = time()
    gt_kspace = load_kspace('data/file1000000.h5')
    print(f'Took {time() - t0} seconds to load data')

    # Just look at a singleslice
    sl = 21
    gt_kspace = gt_kspace[sl, ...]
    imspace = np.fft.fftshift(np.fft.fft2(gt_kspace, axes=(-1, -2)), axes=(-1, -2))

    mask = gen_mask_equidistant(gt_kspace, accel_factor=3)
    kspace = mask*gt_kspace
    # kspace = gt_kspace.copy()
    # kspace[..., 3::4] = 0
    # kspace[..., 0::4] = 0
    # kspace[..., 2::4] = 0
    u_imspace = np.fft.fftshift(np.fft.fft2(kspace, axes=(-1, -2)), axes=(-1, -2))

    # Look at mask
    plt.imshow(np.abs(kspace[0, ...]) > 0)
    plt.show()

    sy = kspace.shape[-1]
    ctr = sy // 2
    pd = (198 - 169) // 2
    calib = gt_kspace[..., ctr-pd:ctr+pd].copy()

    t0 = time()
    recon = grappa_fun(kspace, calib, coil_axis=0, kernel_size=(5, 5), lamda=20)#, niter=3, silent=False)
    print(f'Took {time() - t0} to run grappa')

    # mask = mask.squeeze() == True
    # print(np.average(np.abs(recon[..., mask]).flatten())/np.average(np.abs(recon[..., ~mask]).flatten()))


    # plt.imshow(np.log(np.abs(recon[0, ...])))
    # plt.show()

    recon = np.fft.fftshift(np.fft.fft2(recon, axes=(-1, -2)), axes=(-1, -2))

    plt.subplot(1, 2, 1)
    plt.imshow(np.sqrt(np.sum(np.abs(recon**2), axis=0)))

    plt.subplot(1, 2, 2)
    plt.imshow(np.sqrt(np.sum(np.abs(imspace**2), axis=0)))
    plt.show()
