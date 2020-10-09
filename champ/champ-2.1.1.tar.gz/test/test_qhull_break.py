import numpy as np
from context import champ
import matplotlib.pyplot as plt
import os,sys,re


def main():
    part_ens = champ.PartitionEnsemble()
    part_ens.open('break_qhull.hdf5')
    print('maxpt=',part_ens.maxpt)
    print(len(part_ens.partitions))


    print(len(part_ens.ind2doms))
    part_ens.apply_CHAMP()
    print(len(part_ens.ind2doms))
    part_ens.apply_CHAMP()
    print(len(part_ens.ind2doms))
    part_ens.apply_CHAMP()
    print(len(part_ens.ind2doms))
    part_ens.apply_CHAMP()
    print(len(part_ens.ind2doms))

if __name__=='__main__':
    sys.exit(main())