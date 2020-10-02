import pickle

import mdtraj
import numpy as np
from simtk.openmm import unit
from shutil import copyfile


import random

from .utils import select_atoms, find_flat_bottom_radius

import re
import os

from .ommtk import MetadynamicSimulation


class SegmentMappingSim(MetadynamicSimulation):
    """
    This is a specialized version of the metaD simulation that runs a short run with a high bias,
    saves the coordinates and CV values and uses them to seed a forced sampling of the unbinding pathway
    (without previous knowledge of needed restraints. It begins a run with scan bias, and continues in .5ns
    intervals until the distance CV has reached the value of the unbound_distance variable.

    Once the distance is reached, suitable (equidistant in CV distance space) frames are chosen to represent the
    unbinding pathway and used as seeds for a sequential multiple walkers metaD run.

    Params

    num_segs int
        number of segments along the unbinding pathway to seed
    seg_sim_time unit.Quantity
        length of simulation time to spend in each segment
    scan_bias int
        initial bias_factor for scan portion of the protocol
    scan_time unit.Quantity
        time to run the initial scan
    unbound_distance unit.quantity
        estimate of the max value of the CV. Can be determined using find_max_distance in utils

    """
    def __init__(self, num_segs = 10, seg_sim_time=.5 * unit.nanosecond, scan_bias=45,
                 scan_time = 1 * unit.nanosecond,
                 prod_bias=5, num_cycles=1,
                 **kwargs):

        super().__init__(**kwargs)

        #setup init vars
        self.num_segs = num_segs
        self.seg_sim_time = seg_sim_time
        self.scan_bias = scan_bias
        self.scan_time = scan_time
        self.prod_bias = prod_bias
        self.num_cycles = num_cycles

        if self.CV_list[0][0]!='Distance':
            raise ValueError('Segment Map Sim where the first CV is not distance not yet supported')

        if self.scan_bias < self.prod_bias:
            print('WARNING: scan bias should be high (40-50) and prod bias should be low (5-10)')

        #find unbinding distance algorithmically
        lig_atom_index = select_atoms(self.parmed_structure, keyword_selection='ligand')
        prot_atom_index = select_atoms(self.parmed_structure, keyword_selection='protein')
        lig_positions = np.array(self.positions.value_in_unit(unit.nanometer))[lig_atom_index]
        prot_positions = np.array(self.positions.value_in_unit(unit.nanometer))[prot_atom_index]

        #flat bottom function is designed to find max protein radius around ligand that could be important
        #for sampling. Hard code the scale factor though, since if it's too big the scan will run for forever
        self.unbound_distance = find_flat_bottom_radius(lig_positions, prot_positions, 1.15)
        print('using the following value for unbound distance {}'.format(self.unbound_distance))

    def run(self):
        """
        Run the segment mapping protocol defined by input variables.

        :return:
        """

        #run initial run with initial biasfactor
        self.bias_factor = self.scan_bias
        self._build_sim()
        self._build_custom_forces()

        nsteps = int(self.scan_time / self.step_length)

        self.traj_interval = .01 * unit.nanosecond

        self.fes_interval = (.01 * unit.nanosecond/self.step_length)

        self._add_reporters(nsteps)
        self._add_FESReporter()

        print('running initial scan')
        self.metaD.step(self.simulation, nsteps)
        self.update_parmed()

        #continually run .5ns runs until distance CV exceeds unbound_distance
        with open(os.path.join(self.cwd, 'CV_values.pickle'), 'rb') as handle:
            CVs = pickle.load(handle)

        distances = np.array(CVs)[:, 0]

        print('CV distances {}'.format(distances))

        while all(distances < self.unbound_distance):
            print('failed to unbind, scanning for another .5 ns')
            print('CV distances {}'.format(distances))
            nsteps = int(.5 * unit.nanosecond / self.step_length)

            self.metaD.step(self.simulation, nsteps)

            with open(os.path.join(self.cwd,'CV_values.pickle'), 'rb') as handle:
                CVs = pickle.load(handle)

            distances = np.array(CVs)[:, 0]
        else:
            print('ligand reached unbinding distance, proceeding with forced sampling')

        print('distances from scan: {}'.format(distances))

        self.simulation.reporters.clear()

        #find traj frames where the CV is evenly spaced along num_seg segments
        segment_targets = np.linspace(np.min(distances), self.unbound_distance, self.num_segs)

        sorted_distances = distances.sort()

        segment_frames = []
        for target in segment_targets:
            idx = (np.abs(distances - target)).argmin()
            #if idx is already in the list, try 100 times to choose another with similar value
            counter=0
            while idx in segment_frames and counter<100:
                counter+=1
                target+=random.randint(-100,100)* .01
                idx = (np.abs(distances - target)).argmin()
            segment_frames.append(idx)
            print('choosing CV value', distances[idx])

        copyfile(os.path.join(self.cwd,self.traj_out), 'temp_traj.h5')

        #load trajectory and slice for chosen frames
        traj = mdtraj.load_hdf5('temp_traj.h5')
        segment_coords = traj.xyz[segment_frames]


        #now we have the coordinates we use for seeding, get the seg steps and delete the bias file
        pattern = re.compile('bias(.*)\.npy')
        matches = [pattern.match(filename) for filename in os.listdir(self.cwd) if pattern.match(filename)!=None]
        bias_file = os.path.join(self.cwd, matches[-1].string)
        os.remove(bias_file)


        seg_steps = int(self.seg_sim_time / self.step_length)

        self.bias_factor = self.prod_bias
        self.simulation.reporters.clear()
        del self.simulation
        del self.metaD

        self._build_sim()
        self._build_custom_forces()


        self.fes_interval = (.1 * unit.nanosecond / self.step_length)

        self._add_reporters()
        self._add_FESReporter()

        #set number of times to loop across binding pathway
        for k,cycle in enumerate(range(self.num_cycles)):
            print('starting cycle {}'.format(k+1))
             #loop across the chosen frames running short sims and writing to the bias
            for i,frame in enumerate(segment_coords):
                print('swapping in coordinates from frame {}'.format(segment_frames[i]))
                self.simulation.context.setPositions(frame * unit.nanometers)

                self.metaD.step(self.simulation, seg_steps)
        self.simulation.reporters.clear()

        self.update_parmed()
        return self.parmed_structure