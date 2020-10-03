'''Run GRAPPA on 7T knee data.'''

from time import time

import numpy as np
import matplotlib.pyplot as plt

from pygrappa import mdgrappa as grappa


def ifft2(x, ax=(0, 1)):
    '''centered 2D iFFT'''
    return np.fft.fftshift(
        np.fft.ifft2(
            np.fft.ifftshift(x, axes=ax), axes=ax), axes=ax)


def sos(x, ax=-1):
    '''sum of squares'''
    return np.sqrt(np.sum(np.abs(x)**2, axis=ax))


if __name__ == '__main__':

    # Load data
    print('Start loading data...')
    t0 = time()
    sl = np.load('/home/nicholas/Documents/pygrappa/data/slice.npy')
    print('Loading data took %g seconds' % (time() - t0))

    # Remove some coils
    sl = sl[..., ::2]

    t0 = time()
    res = grappa(sl)
    print(f'Took {time() - t0} seconds to recon')

    plt.imshow(np.log(sos(res)))
    plt.show()

    plt.imshow(sos(ifft2(res)), cmap='gray')
    plt.show()
