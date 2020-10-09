import modbp
from context import champ
import numpy as np

import os,re,sys

import network_tools as nt
import graph_tool as gt
import graph_tool.draw as gtd
import graph_tool.collection as gtc
import matplotlib.pyplot as plt
import seaborn as sbn

import h5py
from time import time
import seaborn as sbn

def test():
    karate = gt.collection.data["karate"]

    karate_ig = nt.convert_graph_tool_to_igraph(karate)
    part_ens = champ.parallel_leiden(karate_ig, start=0, fin=2, numruns=200, progress=True)

def main():
    dir='/Users/whweir/Documents/UNC_SOM_docs/Mucha_Lab/thesis/notebooks'
    # part_file1=os.path.join(dir,'reactome_champ_20k_lower_gamma.hdf5')
    # part_file2=os.path.join(dir,'reactome_champ_20k.hdf5')
    part_file1=os.path.join(dir,'reactome_champ_50_lower.hdf5')
    part_file2=os.path.join(dir,'reactome_champ_100.hdf5')

    part_ens=champ.PartitionEnsemble()
    part_ens.load(part_file1)
    part_ens2=champ.PartitionEnsemble()
    part_ens2.load(part_file2)

    print('part1',len(part_ens.ind2doms),
          'part2',len(part_ens2.ind2doms))

    part_ens=part_ens.merge_ensemble(new=False,otherEnsemble=part_ens2)

    print('part1',len(part_ens.ind2doms),
          'part2',len(part_ens2.ind2doms))


    return 0

if __name__=='__main__':
    # sys.exit(main())
    sys.exit(test())