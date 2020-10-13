# coding: utf-8

import time
import sys
import os
sys.path.append(os.path.abspath('../mlvtk'))

from mlvtk import mlvtk
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from sklearn.preprocessing import label_binarize
(mnist_train, label_train), (mnist_test, label_test) = tfds.as_numpy(tfds.load(
    'mnist',
    split=['train', 'test'],
    batch_size=-1,
    as_supervised=True, data_dir='datasets'
))
label_train_binarized = label_binarize(label_train, classes=np.unique(label_train))
label_test_binarized = label_binarize(label_test, classes=np.unique(label_train))

mnist_train_data = tf.data.Dataset.from_tensors((mnist_train.reshape(mnist_train.shape[0], -1), label_train_binarized)).shuffle(buffer_size=mnist_train.shape[0]).batch(mnist_train.shape[0])
mnist_test_data = tf.data.Dataset.from_tensors((mnist_test.reshape(mnist_test.shape[0], -1), label_test_binarized)).shuffle(buffer_size=mnist_test.shape[0]).batch(mnist_test.shape[0])

def test_gen_model():
    inputs = tf.keras.layers.Input(shape=(None,784))
    dense_1 = tf.keras.layers.Dense(50, activation='relu')(inputs)
    outputs = tf.keras.layers.Dense(np.unique(label_train, axis=0).size, activation='softmax')(dense_1) # hard coded outputs size
    _model = tf.keras.Model(inputs, outputs)
    ml_model = mlvtk.create_model(_model)
    ml_model.overwrite = True
    ml_model.compile(loss=tf.keras.losses.MeanSquaredError())
    hist = ml_model.fit(mnist_train_data, validation_data=mnist_test_data, 
            epochs=10)
    print("Trained model")
    return ml_model
    

def test_calc_loss():
    model = test_gen_model()

    print(time.ctime())
    model._calculate_loss()
    print(time.ctime())
    assert model.loss_df.shape == model.loss_df.shape

