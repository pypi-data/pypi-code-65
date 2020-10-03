import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':

    N, M, nc = 64, 128, 4
    kspace = np.ones((N, M, nc), dtype=bool)

    kspace[2::3, ...] = 0
    kspace[1::3, ...] = 0

    # calibration square in the center
    ctr = (N // 2, M // 2)
    pd0 = 10
    pd1 = 5
    kspace[ctr[0]-pd0:ctr[0]+pd0, ctr[1]-pd1:ctr[1]+pd1, :] = 1

    mask = np.abs(kspace[..., 0]) > 0

    # Start by finding the largest hypercube
    ctrs = [d // 2 for d in mask.shape]
    slices = [[c, c+1] for c in ctrs]
    while np.all(mask[tuple([slice(l-1, r+1) for l, r in slices])]):
        slices = [[l-1, r+1] for l, r in slices]

    # Stretch left/right in each dimension
    for dim in range(mask.ndim):
        # left: only check left condition on the current dimension
        while np.all(mask[tuple([slice(l-(dim == ii), r) for ii, (l, r) in enumerate(slices)])]):
            slices[dim][0] -= 1
        # right: only check right condition on the current dimension
        while np.all(mask[tuple([slice(l, r+(dim == ii)) for ii, (l, r) in enumerate(slices)])]):
            slices[dim][1] += 1

    region = np.zeros(mask.shape, dtype=bool)
    region[tuple([slice(l, r) for l, r in slices])] = True
    plt.imshow(region)
    plt.show()

    # # Make the largest square we can muster
    # left = ctr[0]
    # right = ctr[0]
    # top = ctr[1]
    # bottom = ctr[1]
    # while np.all(mask[left-1:right+1, top-1:bottom+1]):
    #     top -= 1
    #     bottom += 1
    #     left -= 1
    #     right += 1

    # # Extend the rectangle in all directions
    # while np.all(mask[left-1:right, top:bottom]):
    #     left -= 1
    # while np.all(mask[left:right+1, top:bottom]):
    #     right += 1
    # while np.all(mask[left:right, top-1:bottom]):
    #     top -= 1
    # while np.all(mask[left:right, top:bottom+1]):
    #     bottom += 1

    # region = np.zeros(mask.shape, dtype=bool)
    # region[left:right, top:bottom] = True

    plt.imshow(region)
    plt.show()

    plt.imshow(mask.astype(int) - 2*region)
    plt.show()
