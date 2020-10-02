#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 12:03:18 2020

@author: ljia
"""

import multiprocessing
import numpy as np
import networkx as nx
import os
from gklearn.preimage import RandomPreimageGenerator
from gklearn.preimage.utils import compute_k_dis
from gklearn.utils import Dataset, compute_distance_matrix
from gklearn.utils.utils import get_graph_kernel_by_name


def test_random_preimage_generator():
	"""
	Experiment similar to the one in Bakir's paper. A test to check if RandomPreimageGenerator class works correctly.

	Returns
	-------
	None.

	"""
	# create graphs.
	g_s = nx.Graph() # the small graph.
	g_s.add_node(0, label='C')
	g_s.add_node(1, label='O')
	g_s.add_node(2, label='C')
	g_s.add_edges_from([(0, 1), (1, 2)])
	g_l = nx.Graph() # the large graph.
	g_l.add_node(0, label='C')
	g_l.add_node(1, label='O')
	g_l.add_node(2, label='C')
	g_l.add_node(3, label='O')
	g_l.add_node(4, label='C')
	g_l.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
	g_m = nx.Graph() # the middle graph.
	g_m.add_node(0, label='C')
	g_m.add_node(1, label='O')
	g_m.add_node(2, label='C')
	g_m.add_node(3, label='O')
	g_m.add_edges_from([(0, 1), (1, 2), (2, 3)])
	# create dataset.
	dataset = Dataset()
	dataset.load_graphs([g_s, g_l, g_m], targets=None)
	dataset.set_labels(node_labels=['label'])
	
	# set parameters.
# 	alphas = [0.5, 0.5]
	rpg_options = {'k': 5,
				   'r_max': 10, #
				   'l': 500,
				   'alphas': None,
				   'parallel': True,
				   'verbose': 2}
# 	# Path kernel, naive, h = 5
# 	kernel_options = {'name': 'PathUpToH',
# 					  'depth': 5, #
# 					  'k_func': None, #
# 					  'compute_method': 'naive',
#  					  # 'parallel': 'imap_unordered', 
#                       'parallel': None, 
# 					  'n_jobs': multiprocessing.cpu_count(),
# 					  'normalize': True,
# 					  'verbose': 0}
# 	# Path kernel, naive, h = 1
# 	kernel_options = {'name': 'PathUpToH',
# 					  'depth': 1, #
# 					  'k_func': None, #
# 					  'compute_method': 'naive',
#  					  # 'parallel': 'imap_unordered', 
#                       'parallel': None, 
# 					  'n_jobs': multiprocessing.cpu_count(),
# 					  'normalize': True,
# 					  'verbose': 0}
# 	# Path kernel, MinMax, h = 5
# 	kernel_options = {'name': 'PathUpToH',
#  					  'depth': 5, #
#  					  'k_func': 'MinMax', #
#  					  'compute_method': 'trie',
#  					  # 'parallel': 'imap_unordered', 
#                       'parallel': None, 
#  					  'n_jobs': multiprocessing.cpu_count(),
#  					  'normalize': True,
#  					  'verbose': 0}	
# 	# Marginalized kernel, itr = 7
# 	kernel_options = {'name': 'Marginalized',
# 					  'p_quit': 0.8, #
# 					  'n_iteration': 7, #
# 					  'remove_totters': False,
#  					  # 'parallel': 'imap_unordered', 
#                       'parallel': None, 
# 					  'n_jobs': multiprocessing.cpu_count(),
# 					  'normalize': True,
# 					  'verbose': 0}
	# Marginalized kernel, itr = 1
	kernel_options = {'name': 'Marginalized',
					  'p_quit': 0.8, #
					  'n_iteration': 1, #
					  'remove_totters': False,
 					  # 'parallel': 'imap_unordered', 
                      'parallel': None, 
					  'n_jobs': multiprocessing.cpu_count(),
					  'normalize': True,
					  'verbose': 0}		

	# compute the Gram matrix.
	graph_kernel = get_graph_kernel_by_name(kernel_options['name'], 
					  node_labels=['label'], edge_labels=[], 
					  node_attrs=[], edge_attrs=[],
					  ds_infos=dataset.get_dataset_infos(keys=['directed']),
					  kernel_options=kernel_options)	
	gram_matrix, run_time = graph_kernel.compute(dataset.graphs, **kernel_options)
	gram_matrix_unnorm = graph_kernel.gram_matrix_unnorm
	
	dis_all = {}
	# use unnormalized Gram matrix.
	# compute distance between true meiddle graph and each graph in the dataset.
	dis_k_list = []
	for idx, g in enumerate(dataset.graphs):
		dis_k_list.append(compute_k_dis(idx, range(0, len(gram_matrix_unnorm) - 1), [0.5, 0.5], gram_matrix_unnorm, withterm3=False))
	dis_all['dis_k'] = dis_k_list
		
	# compute SOD in kernel spaces.
	dis_mat, _, _, _ = compute_distance_matrix(gram_matrix_unnorm)
	sod_k_list = []
	for idx, g in enumerate(dataset.graphs):
		sod_k_list.append(dis_mat[idx, 0] + dis_mat[idx, 1])
	dis_all['SOD_k'] = sod_k_list
	
	# use normalized Gram matrix.	
	# compute distance between true meiddle graph and each graph in the dataset.
	dis_k_list = []
	for idx, g in enumerate(dataset.graphs):
		dis_k_list.append(compute_k_dis(idx, range(0, len(gram_matrix) - 1), [0.5, 0.5], gram_matrix, withterm3=False))
	dis_all['dis_k (norm)'] = dis_k_list
		
	# compute SOD in kernel spaces.
	dis_mat, _, _, _ = compute_distance_matrix(gram_matrix)
	sod_k_list = []
	for idx, g in enumerate(dataset.graphs):
		sod_k_list.append(dis_mat[idx, 0] + dis_mat[idx, 1])
	dis_all['SOD_k (norm)'] = sod_k_list
		
	return dis_all
	
# 	alpha1_list = np.linspace(0, 1, 11)
# 	k_dis_datasets = []
# 	k_dis_preimages = []
# 	preimages = []
# 	bests_from_dataset = []
# 	for alpha1 in alpha1_list:
# 		print('alpha1 =', alpha1, ':\n')
# 	
# 	


# 		
# 		# 2. initialize rpg and setting parameters.
# 		print('2. initializing rpg and setting parameters...')
# 		nb_graphs = len(dataset_all.graphs) - 2
# 		rpg_options['alphas'] = [alpha1, 1 - alpha1] + [0] * nb_graphs
# 		rpg = RandomPreimageGenerator()
# 		rpg.dataset = dataset_all
# 		rpg.set_options(**rpg_options.copy())
# 		rpg.kernel_options = kernel_options.copy()
# 	
# 		# 3. compute preimage.
# 		print('3. computing preimage...')
# 		rpg.run()
# 		results = rpg.get_results()
# 		k_dis_datasets.append(results['k_dis_dataset'])
# 		k_dis_preimages.append(results['k_dis_preimage'])
# 		bests_from_dataset.append(rpg.best_from_dataset)
# 		preimages.append(rpg.preimage)

# 	print('\ncomplete.\n')
# 	
# 	return k_dis_datasets, k_dis_preimages, bests_from_dataset, preimages


if __name__ == '__main__':
# 	k_dis_datasets, k_dis_preimages, bests_from_dataset, preimages = test_random_preimage_generator()
	dis_all = test_random_preimage_generator()