import os
import time
import logging

# Tensorflow
import tensorflow as tf
import tensorflow_probability as tfp

import numpy as np
import pandas as pd
import math

from .layer import layer
from .layer import KL_divergence_normal
from .layer import create_variance
from .layer import Distribution
from .util import batch_handler
from . import VAE
from .analysis import run_FI

from siVAE import FeatureImportance as FI
from siVAE import util

import scanpy as sc


def create_placeholder_W(VAE_sample):
    """
    Input: self.VAE_sample
    Return: placeholder (matrix of zeros) with
    """

    preW = VAE_sample.W
    preW_shape = [int(s) for s in preW.shape]
    preW_placeholder = np.zeros(preW.shape).transpose()

    return preW_placeholder


def setup_siVAE(datah_in, datah_in_transpose, graph_args1, graph_args2, graph_args3,
                graph = None, rs = 1):
    """ Set up siVAE """

    times = {}
    duration = {}
    times['start'] = time.time()

    if graph is None:
        graph = tf.get_default_graph()

    VAE_sample = VAE.AutoEncoder(data_handler = datah_in,
                                 random_seed  = rs,
                                 isVAE        = True,
                                 name         = 'VAE_sample',
                                 **graph_args1)
    VAE_sample.build_model(reset_graph = False, graph = graph)
    times['VAE_sample_build'] = time.time()
    ## Set datah_in_transpose for VAE_feature
    preW = VAE_sample.W
    preW_shape = [int(s) for s in preW.shape]
    preW_placeholder = np.zeros(preW.shape).transpose()

    datah_in_transpose.y = sc.AnnData(preW_placeholder)
    k_split = 1
    datah_in_transpose.create_split_index_list(k_split, random_seed = rs)
    ks = 0
    datah_in_transpose.create_dataset(kfold_idx = ks)

    ## Create VAE_feature
    VAE_feature = VAE.AutoEncoder(data_handler = datah_in_transpose,
                           random_seed = rs, isVAE = True,
                           name = 'VAE_feature', **graph_args2)

    VAE_feature.build_model(reset_graph = False, graph = graph)
    times['VAE_feature_build'] = time.time()

    VAE_dict = {'sample' : VAE_sample,
                'feature': VAE_feature}

    ## Create siVAE
    model = combinedVAE(random_seed = rs, name = 'combinedModel', **graph_args3)
    model.combine_models(VAE_dict)
    times['VAE_feature_build'] = time.time()

    return model, VAE_sample, VAE_feature


def run(datah_in, datah_in_transpose, graph_args1, graph_args2, graph_args3,
        rs = 1, do_pretrain = True,
        sample_input = None, do_FA = False, method_DE = [], kwargs_FI = {}):

    """ run """

    start_time = time.time()
    times = {}
    times['start'] = time.time()

    if datah_in.iterator is None:
        tf.reset_default_graph()
    graph = tf.get_default_graph()

    config = graph_args1['config']

    with tf.Session(config = config) as sess:

        with FI.DeepExplain(session=sess) as de:

            model, VAE_sample, VAE_feature = setup_siVAE(datah_in, datah_in_transpose,
                                            graph_args1, graph_args2, graph_args3,
                                            rs = rs, graph = graph)

            times['build_model'] = time.time()

            ## Train
            results1 = None
            results2 = None

            logdir_tf = graph_args1['logdir_tf']

            ## Initialize
            tf.set_random_seed(VAE_sample.random_seed)
            tf.logging.set_verbosity(tf.logging.FATAL)
            sess.run(tf.global_variables_initializer())

            var_init = sess.run([VAE_sample.X_dist.var, VAE_sample.z_dist.var],
                                feed_dict = {VAE_sample.X: VAE_sample.data_handler.X.X})

            ## Initialize tensorboard
            logdir_train = os.path.join(logdir_tf,'train')
            logdir_test  = os.path.join(logdir_tf,'test')
            train_writer = tf.summary.FileWriter(logdir_train, sess.graph)
            test_writer  = tf.summary.FileWriter(logdir_test, sess.graph)

            if do_pretrain:

                ## Train VAE_sample
                logging.info("Pre-train sample-wise encoder and decoder")
                results1 = VAE_sample.train(sess = sess,
                                            initialize = False,
                                            train_writer = train_writer,
                                            test_writer = test_writer,
                                            close_writer = False)

                times['train_VAE_sample'] = time.time()
                VAE_sample.sess  = sess

                ## Train VAE_feature
                logging.info("Pre-train feature-wise encoder and decoder")
                preW = results1['W'].transpose()
                VAE_feature.data_handler.y = sc.AnnData(preW)
                ks = 0
                VAE_feature.data_handler.create_dataset(kfold_idx = ks)

                results2 = VAE_feature.train(sess = sess,
                                             initialize = False,
                                             train_writer = train_writer,
                                             test_writer = test_writer,
                                             close_writer = False)
                times['train_VAE_feature'] = time.time()
                VAE_feature.sess = sess

            else:
                VAE_sample.sess  = sess
                VAE_feature.sess = sess
                times['train_VAE_sample']  = time.time()
                times['train_VAE_feature'] = time.time()

            ## Train model
            results = model.train(sess = sess, initialize = False, close_writer = True,
                                  train_writer = train_writer, test_writer = test_writer,
                                  pretrain = True)
            results = model.train(sess = sess, initialize = False, close_writer = True,
                                  train_writer = train_writer, test_writer = test_writer,
                                  pretrain = False)

            times['train_combined'] = time.time()

            results['duration'] = time.time() - start_time
            results['time']     = times

            ## Additional Analysis
            if sample_input is not None:

                sample_dict = {}

                ## Grid inputs -------------------------------------------------
                grids_list = []
                n_LE = int(model.VAE_sample.z_mu.shape[1])

                for ii in range(n_LE):
                    n_sample = 100
                    grids = np.zeros([n_sample,n_LE])
                    grids[:,ii] = np.arange(-1,1,0.02)
                    grids_list.append(grids)
                grids = np.concatenate(grids_list)
                X_dummy = np.zeros([len(grids),int(model.VAE_sample.X_target.shape[1])])

                feed_dict_full = {model.VAE_sample.X  : X_dummy,
                                  model.z_sample      : grids,
                                  model.X_target      : X_dummy,
                                  model.VAE_feature.X : model.VAE_dict['feature'].data_handler.X.X}

                sample_output = np.array(model.reconstruct_X(feed_dict_full))

                sample_dict['grid'] = sample_output

                ## Calculate components with sample input ----------------------
                feed_dict_full = {model.VAE_sample.X  : sample_input,
                                  model.X_target      : sample_input,
                                  model.VAE_feature.X : model.VAE_dict['feature'].data_handler.X.X}

                z_mu          = model.VAE_sample.calculate_z_mu(feed_dict_full)
                sample_output = np.array(model.reconstruct_X(feed_dict_full))

                sample_dict["input"]  = sample_input
                sample_dict["output"] = sample_output

                sampled_outputs = np.array([model.reconstruct_X(feed_dict_full)])
                sampled_outputs = np.swapaxes(sampled_outputs,0,1) # swap 0:Sample 1: Image


                ## Decoder layers ----------------------------------------------

                decoder_layers_list = []
                for ii in range(len(sampled_outputs)):

                    sampled_output = sampled_outputs[ii,]

                    feed_dict_full = {model.VAE_sample.X        : sampled_output,
                                      model.VAE_sample.X_target : sampled_output,
                                      model.VAE_feature.X       : model.VAE_dict['feature'].data_handler.X.X}

                    z_mu = model.VAE_sample.calculate_z_mu(feed_dict_full)
                    X_mu = np.array(model.reconstruct_X(feed_dict_full)) # Don't sample X
                    decoder_layers     = model.VAE_sample.calculate_decoder_layers(feed_dict_full)
                    decoder_layers     = [z_mu] + decoder_layers
                    decoder_layers[-1] = X_mu
                    decoder_layers_list.append(decoder_layers)

                sample_dict['decoder_layers'] = decoder_layers_list

                ## Feature Attribution -----------------------------------------

                if do_FA and len(method_DE) > 0:

                    logging.info('Perform feature attribution')

                    feed_dict_full = {model.VAE_sample.X        : sample_input,
                                      model.VAE_sample.X_target : sample_input,
                                      model.VAE_feature.X       : model.VAE_dict['feature'].data_handler.X.X}

                    sample_z = model.VAE_sample.calculate_z_mu(feed_dict_full)

                    feed_dict_base = {model.VAE_sample.X_target : sample_input,
                                      model.VAE_feature.X       : model.VAE_dict['feature'].data_handler.X.X}

                    attributions_dict_all = {}

                    ## Encoder
                    attributions_dict = run_FI(input     = model.VAE_sample.X,
                                               target    = model.VAE_sample.z_mu,
                                               sample_DE = sample_input,
                                               de        = de,
                                               sess      = sess,
                                               method_DE = method_DE,
                                               feed_dict = feed_dict_base,
                                               kwargs_FI = kwargs_FI,
                                               mode      = 'reverse')

                    attributions_dict_all['encoder'] = attributions_dict

                    ## Decoder
                    kwargs_FI2 = dict(kwargs_FI)
                    _ = kwargs_FI2.pop('baseline',None)
                    attributions_dict = run_FI(input     = model.VAE_sample.z_sample,
                                               target    = model.X_dist.mu,
                                               sample_DE = sample_z,
                                               de        = de,
                                               sess      = sess,
                                               method_DE = method_DE,
                                               feed_dict = feed_dict_base,
                                               kwargs_FI = kwargs_FI2,
                                               mode      = 'forward')

                    attributions_dict_all['decoder'] = attributions_dict

                    sample_dict['attributions_samples'] = attributions_dict_all

                results['sample_dict'] = sample_dict

    return results, results1, results2, model


class combinedVAE(object):

    def __init__(self, logdir_tf = ".", data_handler = None, iter = 5000,
                 h_dims = None, LE_dim = None, architecture = None,
                 mb_size = 1000, learning_rate = 1e-3, l2_scale = 0.0, l1_scale = 0.0,
                 early_stopping = 0, tolerance = 0, min_early_stopping = 0,
                 activation_fun = tf.nn.relu, random_seed = 0,
                 log_frequency = 100, batch_norm = False, keep_prob = None, masking = False,
                 dataAPI = False, tensorboard = False, metadata = False, permute_axis = -2,
                 custom = False, config = None, validation_split = 0,
                 decay_rate=1, decay_steps = 1000, save_recon = True, save_LE = True,
                 decoder_var='scalar', save_W=True, set_y_logvar=False, decoder_activation = None,
                 name="", var_dependency=True, optimizer_type=tf.compat.v1.train.AdamOptimizer,
                 kernel_initializer=tf.contrib.layers.xavier_initializer(uniform = False), X_mu_use_bias=True,
                 zv_recon_scale=None, hl_recon_scale=None):

        self.decoder_var = decoder_var
        self.custom = custom
        self.var_dependency = var_dependency
        self.X_mu_use_bias = X_mu_use_bias
        self.decoder_activation = decoder_activation

        ## Recalculate h_dims if h_dims = 0
        self.save_LE = save_LE
        self.save_W = save_W
        self.set_y_logvar = set_y_logvar
        self.save_recon = save_recon

        ## Variable scope name
        self.name = name

        ## Set activation function
        self.activation_fun = activation_fun

        ## Training Parameters
        self.mb_size = mb_size
        self.iter = iter
        self.keep_prob = keep_prob

        ## Hyperparameters
        self.random_seed = random_seed

        # learning rate
        self.learning_rate = learning_rate
        self.decay_steps = decay_steps
        self.decay_rate = decay_rate

        # Regularization
        self.l1_scale = l1_scale
        self.l2_scale = l2_scale
        self.batch_norm = batch_norm
        self.placeholder_reg = {}

        ## Early stopping
        self.validation_split = validation_split
        self.tolerance = tolerance
        self.early_stopping = early_stopping
        self.min_early_stopping = min_early_stopping
        self.iter_min_early_stopping = self.iter * self.min_early_stopping

        ## Tensorboard
        self.tensorboard = tensorboard
        self.logdir_tf = logdir_tf
        self.metadata = metadata
        self.summary_list = []

        self.feed_dict = {}

        if self.metadata and not self.tensorboard:
            logging.info("Tensorboard has been switched to true as metadata requires tensorboard")
            self.tensorboard = True

        self.log_frequency = log_frequency
        self.permute_axis = permute_axis
        self.dataAPI = dataAPI
        self.config = config


    def combine_models(self, VAE_dict):
        """

        """

        self.VAE_dict = VAE_dict

        assert all(VAE_type in list(VAE_dict.keys())  for VAE_type in ['sample', 'feature']), 'VAE_dict must contain both cell and gene type'

        self.VAE_sample  = self.VAE_dict['sample']
        self.VAE_feature = self.VAE_dict['feature']
        self.y_var_type  = self.VAE_sample.y_var_type
        self.do_sample   = self.VAE_sample.do_sample
        self.X_target    = self.VAE_sample.X_target
        self.decoder_var = self.VAE_sample.decoder_var
        self.isVAE       = self.VAE_sample.isVAE

        with tf.variable_scope(self.name, reuse = tf.AUTO_REUSE):

            self.v_sample = self.VAE_feature.z_sample
            self.v_mu     = self.VAE_feature.z_mu
            self.v_sample = self.v_mu

            self.z_sample_pre = self.VAE_sample.z_sample
            self.z_mu_pre     = self.VAE_sample.z_mu


            ## Combine with feature embeddings, v_sample
            self.feature_weights = tf.get_variable(name = 'feature_weights',
                                                   shape = [int(self.VAE_sample.X.shape[-1]),int(self.v_sample.shape[-1])],
                                                   dtype = tf.float32,
                                                   initializer = tf.keras.initializers.RandomNormal(),
                                                   trainable = True)

            self.summary_list.append(tf.summary.histogram('Feature Weights',self.feature_weights))
            self.summary_list.append(tf.summary.histogram('Feature Weights',self.feature_weights))
            self.summary_list.append(tf.summary.histogram('Feature Weights',self.feature_weights))

            self.weighted_v = self.feature_weights * self.v_sample
            self.weighted_v_sum = tf.math.reduce_mean(self.weighted_v,axis=0) + 1

            self.z_sample = self.z_sample_pre * self.weighted_v_sum
        print('VAE_sample decoder variable scope')
        print(self.VAE_sample.decoder_variable_scope)
        with tf.variable_scope(self.VAE_sample.decoder_variable_scope, reuse = True):

            self.build_decoder(h_temp   = self.z_sample,
                               h_dims   = self.VAE_sample.h_dims_decoder,
                               l1_scale = self.VAE_sample.l1_scale,
                               l2_scale = self.VAE_sample.l2_scale,
                               variable_scope = 'Decoder',
                               kernel_initializer = self.VAE_sample.kernel_initializer)

        self.create_decoder_loss()
        self.create_loss()

        self.summary_list += self.VAE_sample.summary_list


    def build_decoder(self, h_dims, h_temp, l1_scale, l2_scale, kernel_initializer, variable_scope = 'decoder'):
        """
        Build decoder
        """
        logging.info("Building " + variable_scope + "with dims {}".format(h_dims))

        self.decoder_layers = []
        self.hidden_layers  = []

        with tf.variable_scope(variable_scope, reuse = tf.AUTO_REUSE):

            self.decoder_variable_scope = tf.get_variable_scope().name

            for ii, h_dim in enumerate(h_dims):

                with tf.variable_scope("hidden_layer_{}".format(ii)):

                    if ii < len(h_dims) - 2:

                        ## Hidden layers
                        fun = self.activation_fun

                        h_temp,_,_ = layer(h = h_temp, dim = h_dim, fun = fun,
                                           l2_scale = l2_scale, l1_scale = l1_scale,
                                           kernel_initializer = kernel_initializer)

                    elif ii == len(h_dims) - 2:
                        ## Last layer before final layer

                        prob_layer  = Distribution(h   = h_temp,
                                                   dim = h_dim,
                                                   fun = None,
                                                   var_type = self.y_var_type,
                                                   l2_scale = l2_scale,
                                                   l1_scale = l1_scale)

                        self.y_dist = prob_layer
                        self.y_sample, self.y_mu, self.y_var, self.y_logvar, self.y_eps = prob_layer.get_tensors()
                        h_temp = self.y_sample

                    elif ii == len(h_dims) - 1:

                        ## If there is no y layer, set y to z
                        if len(h_dims) == 1:
                            self.y_dist = self.z_dist
                            self.y_sample = self.z_sample
                            self.y_mu = self.z_mu
                            self.y_var = self.z_var
                            self.y_logvar = self.z_logvar
                            self.y_eps    = self.z_eps

                        with tf.variable_scope('output', reuse = tf.AUTO_REUSE):

                            self.output_variable_scope = tf.get_variable_scope().name

                            prob_layer,W,b = self.build_output_layer(h_temp, h_dim = h_dim,
                                                                     fun = self.activation_fun,
                                                                     var_type = self.decoder_var,
                                                                     var_dependency = self.var_dependency,
                                                                     l2_scale = l2_scale,
                                                                     l1_scale = l1_scale,
                                                                     use_bias = self.X_mu_use_bias)

                        self.X_dist = prob_layer
                        self.X_sample, self.X_mu, self.X_var, self.X_logvar, self.X_eps = prob_layer.get_tensors()
                        self.X_sample = tf.cond(self.do_sample, lambda: self.X_sample, lambda: self.X_mu, 'X_sample_cond')
                        self.W = W
                        self.b = b
                        h_temp = self.X_mu

                self.decoder_layers.append(h_temp)
                self.hidden_layers.append(h_temp)
                self.summary_list.append(tf.summary.histogram("hidden_layer_{}", h_temp))


        return prob_layer


    def build_output_layer(self, h_temp, fun, var_type, var_dependency, l2_scale, l1_scale, use_bias,
                           h_dim = None, W = None, b = None, h_mu = None, h_std = None, custom = False, **kwargs):
        """"""

        h_mu, W, b = layer(h_temp, h_dim, fun = None,
                           name = "{}_{}".format('X','mu'),
                           l1_scale = l1_scale, l2_scale = l2_scale,
                           custom = custom, use_bias = use_bias,
                           W = W, b = b, **kwargs)

        with tf.variable_scope('Distribution'):
            prob_layer  = Distribution(h = h_temp,
                                       h_mu = h_mu,
                                       h_std = h_std,
                                       dim = h_dim,
                                       fun = None,
                                       var_type = var_type,
                                       var_dependency = var_dependency,
                                       l2_scale = l2_scale,
                                       l1_scale = l1_scale,
                                       **kwargs)

        return prob_layer, W, b


    def mean_squared_error(self, target, reconstruction):
        """ calculate mean squared error between target and reconstruction """
        return tf.square(target - reconstruction)


    def create_decoder_loss(self):
        """ Create decoder loss """

        with tf.name_scope('mean_squared_error'):
            self.recon_loss_ae = self.mean_squared_error(self.X_mu, self.X_target)

        with tf.name_scope('log_likelihood'):
            if self.isVAE and self.decoder_var != 'deterministic':
                self.decoder_loss_old        = self.X_logvar / 2 + self.recon_loss_ae / self.X_var / 2 + tf.constant(0.5 * np.log(2. * np.pi), dtype = self.X_var.dtype)
                self.decoder_loss_mse        = tf.square(self.X_mu - self.X_target)
                self.decoder_loss_mse_scaled = self.recon_loss_ae / self.X_var / 2
                self.decoder_loss_logvar     = self.decoder_loss_mse * 0 + self.X_logvar / 2
                self.decoder_loss            = -self.X_dist.dist.log_prob(self.X_target)
            else:
                self.decoder_loss = tf.reduce_sum(self.recon_loss_ae,-1)


    def create_loss(self):
        """
        Crate losses
        """

        ## l2_loss
        self.reg_loss = tf.reduce_sum(tf.losses.get_regularization_losses(scope = self.name))
        logging.info(" ")
        logging.info("reg_loss: {}".format(self.reg_loss.shape))
        logging.info(self.reg_loss)
        logging.info(tf.losses.get_regularization_losses(scope = self.name))

        ## recon_loss
        self.recon_loss_scalar = tf.reduce_mean(tf.reduce_sum(self.recon_loss_ae,-1))
        logging.info("recon_loss_scalar: {}".format(self.recon_loss_scalar.shape))
        logging.info(self.recon_loss_scalar)
        logging.info(self.recon_loss_ae)

        ## decoder_loss
        self.decoder_loss_scalar = tf.reduce_mean(self.decoder_loss)
        tf.losses.add_loss(self.decoder_loss_scalar)
        logging.info("decoder_loss_scalar: {}".format(self.decoder_loss_scalar.shape))
        logging.info(self.decoder_loss_scalar)
        logging.info(self.decoder_loss)

        ## Total loss consists of KL
        self.total_loss = self.VAE_sample.KL_loss_scalar + \
                          self.VAE_feature.KL_loss_scalar + \
                          self.decoder_loss_scalar + \
                          self.VAE_sample.reg_loss + \
                          self.VAE_feature.reg_loss + \
                          self.reg_loss

        self.losses = [self.total_loss,
                       self.decoder_loss_scalar,
                       self.recon_loss_scalar,
                       self.VAE_sample.reg_loss,
                       self.VAE_feature.reg_loss,
                       self.VAE_sample.KL_loss_scalar,
                       self.VAE_feature.KL_loss_scalar,
                       self.reg_loss]

        self.losses_name = ['total loss',
                            'decoder_loss',
                            'recon_loss',
                            'reg_loss sample',
                            'reg_loss feature',
                            'latent loss sample',
                            'latent loss feature',
                            'reg_loss']

        for loss_name, loss in zip(self.losses_name, self.losses):
            self.summary_list.append(tf.summary.scalar(loss_name, loss))

        ## Optimizer
        # Variables to Train
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS, scope=self.name)
        self.theta = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope = self.name)
        # self.theta += self.VAE_sample.theta + self.VAE_feature.theta
        # self.theta += self.VAE_sample.theta

        self.theta2 = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope = self.name)
        self.theta += self.VAE_sample.theta + self.VAE_feature.theta
        # self.theta2 += self.VAE_sample.theta

        ## Set up optimizer
        with tf.name_scope("global_steps"):

            self.global_step = tf.Variable(0, name='global_step', trainable=False)

            self.decayed_learning_rate = tf.train.exponential_decay(learning_rate = self.learning_rate,
                                                                    global_step   = self.global_step,
                                                                    decay_steps   = self.decay_steps,
                                                                    decay_rate    = self.decay_rate,
                                                                    staircase     = False)

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        var_list = self.theta

        logging.info("Build train_op optimizing:")
        logging.info(var_list)

        with tf.name_scope("train_op"):
            self.optimizer = tf.train.AdamOptimizer(self.decayed_learning_rate)

            with tf.control_dependencies(update_ops):
                optimizer = self.optimizer.minimize(loss = self.total_loss,
                                                    global_step = self.global_step,
                                                    var_list = var_list)
                self.train_op = optimizer

        var_list = self.theta2
        with tf.name_scope("train_op2"):
            self.optimizer2 = tf.train.AdamOptimizer(self.decayed_learning_rate)

            with tf.control_dependencies(update_ops):
                optimizer = self.optimizer2.minimize(loss = self.total_loss,
                                                    global_step = self.global_step,
                                                    var_list = var_list)
                self.train_op2 = optimizer


        logging.info("train_op:")
        logging.info(self.train_op)

        if self.tensorboard:
            self.merge = tf.summary.merge(self.summary_list)
            self.losses.insert(0,self.merge)


    def start_tensorboard(self, train_writer = None, test_writer = None):
        """ Start tensorboard """

        if train_writer is not None and test_writer is not None:
            self.train_writer = train_writer
            self.test_writer  = test_writer
        else:
            logdir_train = os.path.join(self.logdir_tf,self.name,'train')
            logdir_test  = os.path.join(self.logdir_tf,self.name,'test')
            self.train_writer = tf.summary.FileWriter(logdir_train, self.sess.graph)
            self.test_writer = tf.summary.FileWriter(logdir_test, self.sess.graph)
            logging.info("Starting Tensorboard: {}".format(logdir_train))


    def train(self, sess, dataset = None, initialize = True, train_writer = None, test_writer = None, close_writer = True, pretrain = False):
        """ Train the model """

        start_time = time.time()

        self.sess = sess

        # Set random seed
        if initialize:
            tf.set_random_seed(self.random_seed)
            tf.logging.set_verbosity(tf.logging.FATAL)
            sess.run(tf.global_variables_initializer())

        dataset_sample = self.VAE_dict['sample'].data_handler.dataset
        train_data_full, test_data, y_train_full, y_test = dataset_sample
        dataset_feature = self.VAE_dict['feature'].data_handler.dataset

        # Split into validation
        if self.validation_split == 0:
            train_data = train_data_full
            y_train = y_train_full
            validation_data = test_data
            y_validation = y_test

        else:
            len_train = int(train_data.shape[self.permute_axis])
            len_validate = int(len_train * self.validation_split)
            validation_data = train_data_full.swapaxes(0,self.permute_axis)[:len_validate].swapaxes(0,self.permute_axis)
            train_data      = train_data_full.swapaxes(0,self.permute_axis)[len_validate:].swapaxes(0,self.permute_axis)
            y_validation    = y_train.swapaxes(0,self.permute_axis)[:len_validate].swapaxes(0,self.permute_axis)
            y_train         = y_train.swapaxes(0,self.permute_axis)[len_validate:].swapaxes(0,self.permute_axis)

        logging.info("======================== Data Split =============================")
        logging.info("validation_data: " + str(validation_data.shape))
        logging.info("y_validation: " + str(y_validation.shape))
        logging.info("train_data: " + str(train_data.shape))
        logging.info("y_train: " + str(y_train.shape))
        logging.info("test_data: " + str(test_data.shape))
        logging.info("y_test: " + str(y_test.shape))
        logging.info('')

        logging.info("======================== losses =============================")
        logging.info(self.losses)
        logging.info(self.losses_name)

        if self.tensorboard:
            "Starting Tensorboard "
            self.start_tensorboard(train_writer = train_writer, test_writer=  test_writer)

        feed_dict = {}
        feed_dict[self.VAE_feature.X] = dataset_feature[0]

        # Set up for early stopping
        it_tb = -1
        it_test = 0
        it_min = 0
        min_loss = float("inf")
        result = None

        feed_dict_train = {self.VAE_sample.X: train_data,
                           self.VAE_sample.X_target: y_train,
                           self.VAE_feature.X: dataset_feature[0]}

        feed_dict_test = {self.VAE_sample.X: validation_data,
                          self.VAE_sample.X_target: y_validation,
                          self.VAE_feature.X: dataset_feature[0]}

        iter = self.iter

        for VAE_in in self.VAE_dict.values():
            if VAE_in.keep_prob is not None:
                feed_dict[VAE_in.prob] = VAE_in.keep_prob

        ## Set minibatch size
        if self.mb_size <= 1:
            mb_size = int(int(train_data.shape[self.permute_axis]) * self.mb_size)
        else:
            mb_size = int(self.mb_size)

        train_data_size = int(train_data.shape[self.permute_axis])

        # if self.VAE_sample.iterator is None:
        batch = batch_handler(train_data_size, mb_size)

        # Set up batch
        if pretrain:
            self.solvers = [self.train_op2]
        else:
            self.solvers = [self.train_op]

        for it in range(iter):
            ## Separate counters for tensorboard and early stopping
            it_tb += 1
            it_test += 1

            idx_out = batch.next_batch()

            if self.VAE_sample.iterator is None:
                feed_dict[self.VAE_sample.X]        = train_data.take(idx_out, axis = -2)
                feed_dict[self.VAE_sample.X_target] = y_train.take(idx_out, axis = -2)

            ## Train a batch
            results = self.sess.run(self.solvers + self.losses, feed_dict = feed_dict)

            # Log train/test results
            if (it_tb % self.log_frequency == 0) or (it_tb == iter - 1):
                logging.info('')
                logging.info('Iter: {}, time: {:.4}s'.format(it, time.time()- start_time))

                ## Batch Loss
                zipped = zip(self.losses_name, results[-len(self.losses_name):])
                format_args = [item for pack in zipped for item in pack]
                str_report = "Batch: {}={:.4}" + ", {}={:.4}" * (len(self.losses_name)-1)
                logging.info(str_report.format(*format_args))

                ## Train Loss
                results = sess.run(self.losses, feed_dict = feed_dict_train)
                results_train = results

                # Write to Summary (writing train data)
                if self.tensorboard:
                    summary = results.pop(0)
                    self.train_writer.add_summary(summary, str(it_tb))

                zipped = zip(self.losses_name,results[-len(self.losses_name):])
                format_args = [item for pack in zipped for item in pack]
                str_report = "Train: {}={:.4}" + ", {}={:.4}" * (len(self.losses_name)-1)
                logging.info(str_report.format(*format_args))

                ## Validation loss

                if self.tensorboard:
                    run_args = {}

                    if self.metadata:
                        run_args["options"] = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
                        run_args['run_metadata'] = tf.RunMetadata()

                    results = self.sess.run(self.losses,
                                       feed_dict = feed_dict_test, **run_args)

                    summary = results.pop(0)

                    if self.metadata:
                        self.test_writer.add_run_metadata(run_args["run_metadata"], str(it_tb))

                    self.test_writer.add_summary(summary, str(it_tb))

                    zipped = zip(self.losses_name,results[-len(self.losses_name):])
                    format_args = [item for pack in zipped for item in pack]
                    str_report = "Test: {}={:.4}" + ", {}={:.4}" * (len(self.losses_name)-1)
                    logging.info(str_report.format(*format_args))

                else:
                    results = sess.run(self.losses, feed_dict = feed_dict_test)
                    zipped = zip(self.losses_name,results[-len(self.losses_name):])
                    format_args = [item for pack in zipped for item in pack]
                    str_report = "Test: {}={:.4}" + ", {}={:.4}" * (len(self.losses_name)-1)
                    logging.info(str_report.format(*format_args))

                results_test = results

                if self.early_stopping > 0:
                    logging.info("new min loss: {} vs old {}".format(results[-3], min_loss))
                    delta = min_loss - results[-3]
                    if delta > self.tolerance:
                        it_min = it
                        it_test = 0
                        min_loss =  results[-3]

                    elif it_test > self.early_stopping:
                        break

        if self.tensorboard and close_writer:
            self.train_writer.close()
            self.test_writer.close()

        result = {}

        output = {'model_evaluation': result}
        output['iter'] = it
        output['losses'] = {'train': results_train,
                            'test' : results_test,
                            'name' : self.losses_name}

        #### Calculate layers for full data and save results
        output['split_index'] = self.VAE_dict['sample'].data_handler.split_idx
        output['labels']      = np.array(self.VAE_dict['sample'].data_handler.X.obs['Labels'])

        feed_dict_full = {self.VAE_sample.X        : self.VAE_dict['sample'].data_handler.X.X,
                          self.VAE_sample.X_target : self.VAE_dict['sample'].data_handler.y.X,
                          self.VAE_feature.X       : self.VAE_dict['feature'].data_handler.X.X}

        y_full    = self.VAE_dict['sample'].data_handler.y.X
        full_data = self.VAE_dict['sample'].data_handler.X.X

        if self.save_recon:

            logging.info("y_full: {}".format(y_full.shape))

            y_reconstruct = np.array(self.reconstruct_X(feed_dict_full))

            y_residual = y_full - y_reconstruct

            y_result = np.array([y_full, y_reconstruct])

            output['reconstruction'] = y_result

        if self.save_LE:

            bottleneck = {}
            for VAE_type, VAE_in in self.VAE_dict.items():
                bottleneck[VAE_type] = np.array(self.calculate_latent_embedding(VAE_in, feed_dict_full))

            output['latent_embedding'] = bottleneck

            bottleneck_var = {}
            for VAE_type, VAE_in in self.VAE_dict.items():
                bottleneck_var[VAE_type] = np.array(self.calculate_latent_variance(VAE_in, feed_dict_full))

            output['latent_embedding_var'] = bottleneck_var

        if self.save_W:
            W = self.get_W(feed_dict_full)
            output['W_mu'] = W
            y_mu = self.VAE_sample.calculate_y_mu(feed_dict_full)
            output['y_mu'] = y_mu

            weighted_v = self.get_feature_weights(feed_dict_full)
            output['feature_weights'] = weighted_v

            ## Decoder layers
            decoder_layers_dict = {'sample' : self.VAE_sample.calculate_decoder_layers(feed_dict_full),
                                   'feature': self.VAE_feature.calculate_decoder_layers(feed_dict_full)}
            output['decoder_layers'] = decoder_layers_dict

        return output


    def calculate_X_reconstruct(self, feed_dict_in):
        """ Reconstruct X from input data """

        y_reconstruct = np.array(self.sess.run(self.X_dist.mu, feed_dict = feed_dict_in))

        return y_reconstruct


    def calculate_latent_embedding(self, VAE_in, feed_dict_in):
        """ Calculate bottleneck layer from input data"""

        bottleneck = np.array(self.sess.run(VAE_in.latent_embedding, feed_dict = feed_dict_in))

        return bottleneck


    def reconstruct_X(self, feed_dict_in):
        """
        Calculate the X_reconstruct from the mean of the latent variables rather than sampled
        y_reconstruct = [cell, gene]
        """

        z_sample = self.calculate_latent_embedding(self.VAE_sample,feed_dict_in)
        v_sample = self.calculate_latent_embedding(self.VAE_feature,feed_dict_in)

        feed_dict_Wy = {self.v_sample: v_sample, self.z_sample_pre: z_sample}

        X_reconstruct = np.array(self.sess.run(self.X_dist.mu, feed_dict = feed_dict_Wy))

        return X_reconstruct


    def calculate_latent_variance(self, VAE_in, feed_dict_in):
        """ Calculate latent variance of VAE_in """
        bottleneck = np.array(self.sess.run(VAE_in.z_var, feed_dict = feed_dict_in))

        return bottleneck


    def calculate_decoder_variance(self, test_data):
        """ Calculate decoder variance """
        var = np.array(self.sess.run(self.X_var, feed_dict = {self.X: test_data}))

        return var


    def get_W(self, feed_dict = {}):
        """ Get W"""
        W = np.array(self.sess.run(self.W, feed_dict=feed_dict))

        return W


    def get_feature_weights(self, feed_dict = {}):
        """ Get W"""
        W = np.array(self.sess.run(self.feature_weights, feed_dict=feed_dict))

        return W
