import eqo
import itertools
import numpy as np

from time import sleep


if __name__ == '__main__':

    # create QUBO instance
    n   = 256
    # random parameter matrix (upper triangle)
    arr = np.triu(np.random.random((n, n)))
    Q   = eqo.qubo.fromMatrix(arr)

    with eqo.EQOCom(connection=('192.168.135.100', 10000), verbose=True) as fpga:

        # set random seed and initial parent
        fpga.randomize()
        fpga.timeout = 65535

        # print configuration info
        fpga.info()

        # load QUBO onto device
        fpga.loadQUBO(Q)

        # start optimization
        fpga.start()

        # wait for progress
        sleep(2)

        # stop optimization and get result
        fpga.reset() # soft reset
        
        status = fpga.status()
        solution, gen = status['solution'], status['impgen']

    print(f'\nSolution {eqo.bytesToDict(solution, crop=n)} found in generation {gen}')
