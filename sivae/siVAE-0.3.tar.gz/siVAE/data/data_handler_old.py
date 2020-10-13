import os

import math
import numpy as np

import pandas as pd

from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import scale
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import pickle
import re

from siVAE import util


def save_as_npy(dir_data, dir_label):

    dir_data_suffix, filetype = dir_data.rsplit(".",1)

    if filetype == 'csv':
        df_in = pd.read_csv(os.path.join(dir_data), index_col = 0)
        data = df_in.values.transpose().astype('float32')
        labels_gene = np.array(list(df_in.index))
        labels_type = np.array([id.split("_")[0] for id in list(df_in.columns.values)])
    else:
        raise Exception("File type must be csv, not {}".format(filetype))

    if dir_label is not None:
        labels_type = np.array(pd.read_csv(dir_label)).reshape(-1).tolist()

    np.savez(filename, matrix = data, column =  labels_type, index =labels_gene)
    # data = [gene,type]
    assert len(labels_type) == data.shape[0], 'Length of cell label ({}) does not match number of cells ({})'.format(len(labels_type), data.shape[0])


def scale_float64(data, *args, **kwargs):
    """
    Convert the input data to float64 to avoid errors
    """
    dtype = data.dtype
    data_scaled = scale(np.array(data).astype('float64'), *args, **kwargs)
    return data_scaled.astype(dtype)


def index2mask(index, length = None):
    if length is None:
        length = np.max(index) + 1
    return np.array([np.isin(np.arange(length), idx) for idx in index])


def extract_targets_from_labels(targets, labels):
    """
    targets = list of targets
    labels = numpy array of labels
    """
    if targets == ["all"]:
        indices = np.repeat(True, len(labels))
    else:
        indices = np.array([np.any([bool(re.search(target + "(_|\Z)", label)) for target in targets]) for label in labels])
    return indices


def import_labeled_df(dir_data, dir_label = None):
    """ Import data """

    datah = data_handler()
    datah.import_X(dir_data, dir_label)
    data = datah.data
    labels_gene = datah.labels_gene
    labels_cell = datah.labels_cell
    return (data, labels_gene, labels_cell)


def save_mask_gene(filename, matrix, column, index, format = "all"):
    """
    matrix = num_gene x num_pathway
    column: pathway
    index: gene
    """
    np.savez(filename, matrix = matrix, column = column, index = index)


def save_X(matrix, column, index, format = "all"):
    """
    matrix = num_samples x num_genes
    column: gene
    index: celltype
    """
    np.savez(filename, matrix = matrix, column = column, index = index)



def kfold_split(X,y, k_split, random_seed = 1, isPrecompMatrix = False):
    skf = StratifiedKFold(n_splits     = k_split,
                          random_state = random_seed,
                          shuffle      = True)
    if not isPrecompMatrix:
        datasets = [[X[idx_train],
                     X[idx_test],
                     y[idx_train],
                     y[idx_test]] for idx_train, idx_test in skf.split(X, y)]
    else:
        datasets = [[X[idx_train][:,idx_train],
                     X[idx_test][:,idx_train],
                     y[idx_train],
                     y[idx_test]] for idx_train, idx_test in skf.split(X, y)]
    return datasets


class data_handler(object):

    """
    Main Data (X, y, masks)
    Batch split
    Kfold split
    Dataset
    """

    def __init__(self, h_dims = None, X = None, y = None, batch_type = None,
                 masks = None, index_latent_embedding = 0, label = None,
                 idx_selected = np.array([], dtype = 'int'), use_3D = False,
                 masking = False, dir_y = None, scale_feature = True, data = None,
                 iterator = None):

        self.X = X
        self.y = y
        self.masks = masks
        self.label = label
        self.idx_selected = idx_selected
        self.batch_type = batch_type
        self.use_3D = use_3D
        self.masking = masking
        self.dir_y = dir_y
        self.data = None

        self.iterator = iterator

        self.index_latent_embedding = index_latent_embedding
        self.scale_feature = scale_feature

        self.set_h_dims(h_dims)


    def set_batch_type(self, batch_type):
        self.batch_type = batch_type


    def get_batch_mask(self):

        if self.batch_type == 'cell':
            self.batch_mask = self.mask_cell[self.index_cell_use]

        elif self.batch_type == 'gene':
            self.batch_mask = self.mask_gene[self.index_gene_use]

        else:
            raise Exception('Batch type must be either cell or gene')

        return self.batch_mask


    def set_batch_mask(self, batch_mask):
        self.batch_mask = batch_mask


    def get_kfold_index(self, kfold_idx):
        return self.kfold_index_list[kfold_idx]


    def set_use_3D(self, use_3D):
        self.use_3D = use_3D


    def set_use_masking(self, use_masking):
        self.use_masking = use_masking


    def create_dataset(self, kfold_idx = None):
        """
        split_idx: index of the training and test set in X and y data
        """

        if kfold_idx is None:
            split_idx = self.split_idx
        else:
            split_idx = self.get_kfold_index(kfold_idx)
            self.split_idx = split_idx

        data_list = [self.X, self.y]
        self.dataset = split_data(data_list, split_idx)


    def create_masks_batch(self, run_idx = None):
        masks_selected = self.masks[self.idx_selected]
        masks_combined = self.masks + np.any(masks_selected, axis = 0)
        self.masks_batch = masks_combined

        if run_idx is not None:
            self.masks_batch = masks_combined[self.idx_list[run_idx]]


    def create_X_batch(self, masking = False, scale_feature = False, use_3D = False):
        """ """
        if use_3D and not np.all(self.masks_batch.sum(1) == self.masks_batch.sum(1)[0]):
            raise Exception('For use_3D, all masks should contain same number of non-masked value')

        if masking:
            self.X_batch = np.array([self.X])
        else:
            self.X_batch = np.array([self.X[:,mask] for mask in self.masks_batch])

        if scale_feature:
            self.X_batch = [scale_float64(data_masked,0) for data_masked in self.X_batch]

        if not use_3D:
            assert len(data) == 1, "For use_3D is false, length of masks should be 1"
            self.X_batch = self.X_batch[0]


    def extract_batch(self, batch_num, batch_idx):
        idx_all_masks = np.arange(self.masks.shape[0])
        idx_unused = idx_all_masks[np.logical_not(np.isin(idx_all_masks, self.idx_selected))]
        idx_batch = np.array_split(idx_unused, batch_num)[batch_idx]

        self.idx_batch = idx_batch


    def check_rewrite(self, logdir = '', rewrite = False):
        """ """
        num_sel = len(self.idx_selected)

        if rewrite:
            idx_batch_incomplete = self.idx_batch

        else:
            idx_batch_incomplete = []
            for ii in self.idx_batch:
                filename = os.path.join(logdir, "sel-{}_gene-{}.npy".format(num_sel,ii))
                if not os.path.exists(filename):
                    idx_batch_incomplete.append(ii)

        self.idx_batch = np.array(idx_batch_incomplete)


    def prepare_batch(self, batch_num, batch_idx, n_nn, logdir, rewrite = False):
        """
        Prepare list of mask by extracting the (batch_idx) th batch out of
        (batch_num batches) then dividing that so the batches have n_nn masks
        """
        # Prepare idx lists
        self.extract_batch(batch_num, batch_idx)
        self.check_rewrite(logdir = logdir, rewrite = rewrite)

        if len(self.idx_batch) == 0:
            raise Exception('All masks in the batch have been completed.')

        idx_list = np.array_split(self.idx_batch, self.num_loops)

        self.num_loops = int(math.ceil(len(self.idx_batch)*1.0/n_nn))
        self.idx_list = idx_list


    def get_num_batch(self):
        return self.num_loops


    def import_X(self, dir_data, dir_label = None, dir_label_gene = None):
        """ Import data """
        filetype = dir_data.split('.')[-1]

        if filetype == 'npz':

            npz_in = np.load(dir_data, allow_pickle = True)
            data        = npz_in['matrix']
            labels_type = npz_in['index']
            labels_gene = npz_in['column']

        else:
            if filetype == 'csv':
                df_in = pd.read_csv(os.path.join(dir_data), index_col = 0)
                data = df_in.values.transpose().astype('float32')
                labels_gene = np.array(list(df_in.index))
                labels_type = [id.split("_")[0] for id in list(df_in.columns.values)]

            elif filetype == 'npy':
                data = np.load(dir_data, allow_pickle = True).astype('float32')

                if dir_label is None or dir_label_gene is None:
                    raise Exception('If input dir_data is npy format, dir_label must be specified')
            else:
                raise Exception('dir_data ({}) does not have correct format (csv,npy)'.format(dir_data))

            if dir_label is not None:
                labels_type = np.array(pd.read_csv(dir_label)).reshape(-1).tolist()

        assert len(labels_type) == data.shape[0], 'Length of cell label ({}) does not match number of cells ({})'.format(len(labels_type), data.shape[0])

        self.data = data # num_sample x num_gene
        self.labels_gene = labels_gene
        self.labels_cell = labels_type

        if self.output_dim == 0:
            self.set_h_dims(self.h_dims)

        # return (data, labels_gene, labels_type)


    def set_index_cell(self, dir_sample = "None", index_cell = None, targets = None):

        if dir_sample == "None":

            if index_cell is not None:
                self.index_cell = index_cell

            elif targets is not None:
                self.index_cell = []
                self.targets = targets

                # assert  np.all(np.all(np.isin(targets, list(set(self.labels_cell))))) != 0, 'Target ({}) not available in dataset'.format(targets)

                index_cell = extract_targets_from_labels(targets, self.labels_cell)

                if (targets != ['all']):
                    self.index_cell.append(index_cell) # Find indices for targets
                else:
                    self.index_cell.append(index_cell)

            else:
                raise Exception('Either index cell or targets needs to be specified')

        else:
            self.index_cell = np.load(dir_sample, allow_pickle = True)

        self.index_cell = np.array(self.index_cell)
        self.mask_cell = index2mask(self.index_cell, len(self.labels_cell))
        self.num_cell = len(self.index_cell[0])
        self.labels_target = np.zeros([1,self.num_cell])

        self.use_index_cell(index = "all")


    def set_split_idx(self, kk):
        self.split_idx = self.kfold_index_list[kk]


    def create_kfold_index_list(self, k_split, random_seed = 0):

        self.kfold_index_list = split_index(length = self.X.shape[-2],
                                            k_split = k_split,
                                            label =self.labels_target[0],
                                            random_seed = random_seed)


    def set_index_gene(self, index_gene = None, mask_gene = None):
        if index_cell is not None:
            self.index_gene = index_gene
            self.mask_gene = index2mask(self.index_gene)

        elif mask_cell is not None:
            self.index_gene = [np.where(mask) for mask in mask_gene]
            self.mask_gene = mask_gene

        self.use_index_gene('all')


    def use_index_cell(self, index = 'all'):
        if index == 'all':
            self.index_cell_use = np.arange(len(self.index_cell))
        else:
            self.index_cell_use = index
            self.index_cell = self.index_cell[index]


    def use_index_gene(self, index = 'all'):
        if index == 'all':
            self.index_gene_use = np.arange(len(self.index_gene))
        else:
            self.index_gene_use = index


    def filter_cell(self, index_cell = None, scale_feature = None, scale_axis = []):
        # Extract Targets
        self.data_target = []
        self.labels_target = []

        if scale_feature is None:
            scale_feature = self.scale_feature

        if index_cell is None:
            index_cell = self.index_cell

        print("index_cell: {}".format(index_cell.shape))

        # index_cell = index_cell[self.index_cell_use]

        for index in index_cell:
            data_target = self.data[index]
            labels_target = np.array(self.labels_cell)[index]

            # Normalize Target Data
            for ii in scale_axis:
                data_target = scale_float64(data_target, ii)

            if scale_feature:
                data_target = scale_float64(data_target, 0)

            self.data_target.append(data_target)
            self.labels_target.append(labels_target)

        self.data_target = np.array(self.data_target)
        self.label_target = np.array(labels_target)


    def filter_gene(self, mask_gene = None):
        if mask_gene is None:
            print("index_gene: {}".format(self.index_gene.shape))
            print("index_gene_use: {}".format(self.index_gene_use))
            index_gene = self.mask_gene[self.index_gene_use]
            mask_gene = index2mask(index_gene, len(self.labels_gene))
            print("mask_gene: {}".format(self.mask_gene.shape))
            # mask_gene = self.mask_gene[self.index_gene_use]
        print("mask_gene: {}".format(mask_gene.shape))
        print("data_target: {}".format(self.data_target.shape))
        # data_target = np.array([[data_temp.take(index, axis = -1) for index in index_gene] for data_temp in self.data_target])
        data_target = np.array([filter_gene(data_temp, masks = mask_gene, use_3D = self.use_3D, masking = self.masking) for data_temp in self.data_target])

        self.data_target = data_target


    def import_mask_gene(self, dir_pathway, labels_gene = None, match_gene = True, min_size = 10, max_size = 500):
        """ Import and process pathway in matrix form """

        if labels_gene is None:
            labels_gene = self.labels_gene

        if dir_pathway == 'all_genes':
            mat_pathway = np.repeat(True, len(labels_gene)).reshape(1,-1)
            label_pathway = np.array(['all_genes'])

        elif dir_pathway == "single_genes":
            mat_pathway = np.identity(len(labels_gene), dtype = 'bool')
            label_pathway = labels_gene

        else:
            filetype = dir_pathway.split('.')[-1]

            if 'single' in dir_pathway and min_size != 1:
                min_size = 1
                print('For single genes, min_size has been set to 1.')

            if filetype == 'csv':
                df_pathway = pd.read_csv(dir_pathway, index_col = 0)
                pathway_gene = np.array(df_pathway.index)
                label_pathway = df_pathway.columns.values

            elif filetype == 'npz':
                npz_file = np.load(dir_pathway, allow_pickle = True)

                mat_pathway   = npz_file['matrix'].astype('bool') # load n_path x n_index
                label_pathway = npz_file['column']
                pathway_gene  = npz_file['index']

                df_pathway = pd.DataFrame(mat_pathway)
                df_pathway.columns = label_pathway
                df_pathway.index = pathway_gene

            else:
                raise Exception('File type must be either csv, npy, npz or specified as all_genes/single_genes')

            # Filter and reindex genes in the imported mat_pathway to match the expression matrix
            if labels_gene is not None:
                if match_gene and not np.all(np.isin(labels_gene, pathway_gene)):
                    raise Exception('Gene in Expression Matrix and Pathways do not match')
                else:
                    df_pathway = df_pathway.reindex(labels_gene).fillna(0)

            mat_pathway = df_pathway.values.transpose().astype('bool')

            # Filter out pathways that does not meet the min_size
            idx_pathway = np.all([mat_pathway.sum(1) >= min_size, mat_pathway.sum(1) <= max_size], axis = 0)

            num_sizeerror = sum(~idx_pathway)

            if num_sizeerror > 0:
                print('{} / {} did not mean size requirement'.format(num_sizeerror,
                                                                     len(label_pathway)))
                mat_pathway = mat_pathway[idx_pathway]
                label_pathway = label_pathway[idx_pathway]

        # Set outputs
        self.mask_gene = mat_pathway
        self.index_gene = np.array([np.where(mask)[0] for mask in self.mask_gene])
        self.label_geneset = label_pathway
        self.use_index_gene("all")


    def set_batch_index(self, batch_index):
        self.batch_index = batch_index


    def set_h_dims(self, h_dims):
        """ Set h_dims of data_handler object """
        self.h_dims = h_dims

        if self.h_dims[-1] == 0:
            if self.data is not None:
                self.h_dims[-1] = self.data.shape[-1] # set h_dims to be number of genes

        self.output_dim = h_dims[-1]

    def import_y(self, dir_y, index_cell = None, with_std = False, target_specific_PCA = True):
        print("importing from dir_y = {}".format(dir_y))
        if dir_y == 'None':

            kwargs = {"dir_y": dir_y,
                      "y_dim": self.h_dims[-1],
                      "data": self.data,
                      "with_std": with_std,
                      "target_specific_PCA": target_specific_PCA
                      }

            if index_cell is None:
                index_cell = self.index_cell

            self.y = np.array([import_y(index_targets = index, **kwargs) for index in index_cell])

        elif dir_y == 'X':
            self.y = self.X

        else:
            self.y = import_y(dir_y)
            if len(self.y.shape) == 3:
                if self.batch_type == 'cell':
                    self.y = self.y.take(self.batch_index, axis = 0)
                    assert len(self.y) == len(self.index_cell)
            else:
                self.y = np.array([self.y])



    def prepare_for_batch(self, dir_y = None):

        if self.batch_type == 'gene':
            self.filter_cell()
            if dir_y is None:
                dir_y = self.dir_y
            self.import_y(dir_y)


    def prepare_for_CV(self, dir_y):
        if self.batch_type == 'cell':
            self.filter_cell()
            self.import_y(dir_y)


    def prepare_X(self):

        if self.batch_type == 'cell':
            self.filter_cell(self.batch_mask)
            print("Data_target after filter cell - {}".format(self.data_target.shape))
            self.filter_gene()
            print("Data_target after filter gene - {}".format(self.data_target.shape))

        elif self.batch_type == 'gene':
            self.filter_cell()
            print("Data_target after filter cell - {}".format(self.data_target.shape))
            self.filter_gene(self.batch_mask)
            print("Data_target after filter gene - {}".format(self.data_target.shape))

        self.X = self.data_target.reshape(-1, *self.data_target.shape[2:])


    def prepare_y(self, dir_y = None):

        if dir_y is None:
            dir_y = self.dir_y

        print("dir_y = {}".format(dir_y))

        if dir_y == 'X':
            self.y = self.X
        else:
            if self.batch_type == 'cell':
                self.import_y(dir_y, index_cell = self.batch_mask)


    def prepare_CV(idx, masks_in, n_nn):
        datah.set_batch_index(idx)
        datah.set_batch_mask(masks_in)
        datah.n_nn = n_nn
        datah.prepare_X()
        datah.prepare_y()


def preprocess_pca(data, n_pca, whiten = False, verbose = False, random_state = 0, center = True, with_std = False):
    """
    data = [sample,feature]
    """

    # Convert to float64 to avoid numerical error warning
    dtype = data.dtype
    # data_scaled = scale_float64(data,0)
    data_scaled = data

    if data.shape[-1] == n_pca:
        data_pca = data_scaled

    else:
        pca = PCA(n_components=n_pca, whiten = False, random_state = random_state)
        data_pca = pca.fit_transform(data_scaled)

        if center:
            data_pca = scale_float64(data_pca, 0, with_std = with_std)

    if verbose:
        print('Explained Variance: {}'.format(sum(pca.explained_variance_ratio_)))

    return data_pca


def import_y(dir_y, y_dim = None, data = None, index_targets = None, with_std = False, target_specific_PCA = True):
    """
    """
    if dir_y == 'None':

        if data is None or index_targets is None or y_dim is None:
            raise Exception('Data, y_dim, and index_targets required')

        else:
            n_pca = y_dim

            if n_pca == data.shape[-1]:
                data_pca = data[index_targets]

            else:

                if target_specific_PCA:
                    data_pca = preprocess_pca(data[index_targets], n_pca, whiten = False, verbose = True)

                else:
                    data_pca_full = preprocess_pca(data, n_pca, whiten = False, verbose = True)
                    data_pca = data_pca_full[index_targets]

        data_pca = scale_float64(data_pca, 0, with_std = with_std)

    else:
        filetype = dir_y.split('.')[-1]
        if filetype == 'csv':
            data_pca = pd.read_csv(dir_y, header = None).values.astype('float32')
        elif filetype == 'npy':
            data_pca = np.load(dir_y, allow_pickle = True).astype('float32')

        if len(data_pca.shape) == 2:
            data_pca = data_pca.reshape(-1, *data_pca.shape)

        data_pca = np.array([scale_float64(data_loop, 0, with_std = with_std) for data_loop in data_pca])

    return data_pca


def split_index(length, k_split, label = None, random_seed = 0):
    """ Given data and label, split into test/train then give result """
    list_index = []
    X0 = np.arange(length)
    if k_split < 1:
        if label is None:
            label = np.ones(length)
        test_data, train_data, _, _ = train_test_split(pd.DataFrame(X0), label,
                                                       test_size    = k_split,
                                                       stratify     = label,
                                                       random_state = random_seed)
        split_values = (np.array(train_data.index), np.array(test_data.index))
        list_index.append(split_values)

    elif k_split == 1:
        split_values = (X0, X0)
        list_index.append(split_values)

    else:
        skf = StratifiedKFold(n_splits     = int(k_split),
                              random_state = random_seed,
                              shuffle      = True)
        for split_values in skf.split(X0, label):
            list_index.append(split_values)

    return list_index


def filter_gene(data, masks = None, index_gene = None, masking = False, scale_feature = False, use_3D = False):
    """ """
    if masks is None:
        if index_gene is None:
            raise Exception('Eitehr mask or index should be specified')
        else:
            masks = np.array([np.isin(np.arange(data.shape[-1]), index) for index in index_gene])

    if scale_feature is None:
        scale_feature = self.scale_feature

    if len(data.shape) == 3:

        assert masks.shape[0] == 1, "If data is 3D, then masks should only have one mask instead of {}".format(masks.shape[0])

        data = data.take(np.where(masks[0])[0], axis = -1)
        data = np.array([scale_float64(data_temp,0) for data_temp in data])

    else:
        print("mask shape: {}".format(masks.shape))
        if use_3D and not np.all(masks.sum(1) == masks.sum(1)[0]):
            raise Exception('For use_3D, all masks should contain same number of non-masked value')

        if masking:
            data = np.array(data)
        else:
            print(masks.sum())
            print(masks.shape)
            data = np.array([data[:,mask] for mask in masks])

        if scale_feature:
            data = np.array([scale_float64(data_masked,0) for data_masked in data])

        if not use_3D:
            assert len(data) == 1, "For use_3D is false, length of masks should be 1"
            data = data[0]

    return np.array(data)


def split_data(data_list, split_idx, axis_list = None):
    """ Split list of data by train/test index for specificed axis"""
    train_index, test_index = split_idx
    dataset = []
    #
    if axis_list is None:
        axis_list = [-2] * len(data_list)
    #
    for data,axis in zip(data_list, axis_list):
        dataset.append(data.take(train_index, axis))
        dataset.append(data.take(test_index, axis))
    #
    return dataset
