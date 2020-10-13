#!/usr/bin/env python
# ******************************************************************************
# Copyright 2020 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
"""
This model is an adaptation of the `mobilenet_imagenet` model for edge
applications. It is based on MobileNetBC with top layers replaced by a quantized
spike extractor and a classification layer.

It comes with a `mobilenet_edge_imagenet_pretrained` helper method that loads a
set of pretrained weights on a Mobilenet 0.5 that can be run on Akida hardware.

The following tables describes the expected results using the provided weights:
-----------------------------------------------------
            Model           | Top 1 Acc | Top 5 Acc
-----------------------------------------------------
|  Keras 0.5 MobileNet-224  |   51.5 %  |   76.2 %  |
|  Akida 0.5 MobileNet-224  |   52.0 %  |   76.4 %  |

# Reference

- [MobileNets: Efficient Convolutional Neural Networks for
   Mobile Vision Applications](https://arxiv.org/pdf/1704.04861.pdf))

"""
import os

# Tensorflow/Keras imports
from tensorflow.keras import Model
from tensorflow.keras.utils import get_file
from tensorflow.keras.layers import Reshape, Dropout, Activation

# CNN2SNN imports
from cnn2snn import load_quantized_model

# Local utils
from ..quantization_blocks import separable_conv_block, dense_block

BASE_WEIGHT_PATH = 'http://data.brainchip.com/models/mobilenet_edge/'


def mobilenet_edge_imagenet(base_model, classes):
    """Instantiates a MobileNet-edge architecture.

    Args:
        base_model (str/tf.keras.Model): a mobilenet_imagenet quantized model.
        classes (int) : the number of classes for the edge classifier.

    Returns:
        tf.keras.Model: a Keras Model instance.
    """
    if isinstance(base_model, str):
        base_model = load_quantized_model(base_model)

    input_shape = base_model.input_shape

    try:
        # Identify the last separable, which is the base model classifier
        base_classifier = base_model.get_layer("separable_14")
        # remember the classifier weight bitwidth
        wq = base_classifier.quantizer.bitwidth
    except:
        raise ValueError(
            "The base model is not a quantized Mobilenet/Imagenet model")

    # Recreate a model with all layers up to the classifier
    x = base_classifier.input
    # Add the new end layer with kernel_size (3, 3) instead of (1,1) for
    # hardware compatibility reasons
    x = separable_conv_block(x,
                             filters=2048,
                             kernel_size=(3, 3),
                             padding='same',
                             use_bias=False,
                             add_batchnorm=True,
                             name='spike_generator',
                             weight_quantization=wq,
                             activ_quantization=1)

    # Then add the Akida edge learning layer that will be dropped after
    # NOTE: weight_quantization set to 2 here, to be as close as
    # possible to the Akida native layer that will replace this one,
    # with binary weights.
    x = dense_block(x,
                    classes,
                    name="classification_layer",
                    weight_quantization=2,
                    activ_quantization=None,
                    add_batchnorm=False,
                    use_bias=False)
    x = Activation('softmax', name='act_softmax')(x)
    x = Reshape((classes,), name='reshape_2')(x)

    # Create model
    return Model(inputs=base_model.input,
                 outputs=x,
                 name=f"{base_model.name}_edge")


def mobilenet_edge_imagenet_pretrained():
    model_name = 'mobilenet_imagenet_edge_wq4_aq4.h5'
    model_path = get_file(fname=model_name,
                          origin=BASE_WEIGHT_PATH + model_name,
                          cache_subdir='models')
    return load_quantized_model(model_path)
