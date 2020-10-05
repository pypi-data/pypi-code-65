#!/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2020 yinochaos <pspcxl@163.com>. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import tqdm
from typing import Any, Tuple, List, Dict
import tensorflow as tf
import numpy as np
from model_factory.utils import BeamHypotheses
from model_factory.models.model import Model
from model_factory.losses.loss import seq2seq_cross_entropy_loss
from datasets.utils.common_struct import data_schemas2types, data_schemas2shapes

""" model interface
"""


class Seq2seqModel(Model):
    def __init__(self, optimizer, loss, encoder, decoder, max_decoder_len=16, feature_fields=None, label_fields=None, batch_size=16):
        self.optimizer = optimizer
        self.loss = loss
        self.encoder = encoder
        self.decoder = decoder
        self.hidden_size = encoder.hidden_size
        self.max_decoder_len = max_decoder_len
        self._build_model()
        # self.model.summary()

    def _build_model(self):
        inputs = self.encoder.get_inputs()
        _, enc_hidden = self.encoder(inputs)
        tokens_inputs = tf.keras.layers.Input(shape=(None,), dtype=tf.int32, name='tokens')
        logits, _ = self.decoder([tokens_inputs, enc_hidden])
        self.model = tf.keras.Model([inputs, tokens_inputs], logits)
        #loss1=KL.Lambda(lambda x:custom_loss1(*x),name='loss1')([x,x_in])
        loss = tf.keras.layers.Lambda(lambda x: seq2seq_cross_entropy_loss(x[0], x[1]))([tokens_inputs[1:], logits[:-1]])
        self.model.add_loss(loss)
        self.model.compile(optimizer=self.optimizer)
        """
        assert feature_fields is not None
        assert label_fields is not None
        inputs_signature = [tf.TensorSpec(shape=[batch_size]+[s for s in shape], dtype=type) for shape, type
                            in zip(data_schemas2shapes(feature_fields), data_schemas2types(feature_fields))]
        targets_signature = [tf.TensorSpec(shape=[batch_size]+[s for s in shape], dtype=type) for shape, type
                             in zip(data_schemas2shapes(label_fields), data_schemas2types(label_fields))]
        if len(inputs_signature) == 1:
            inputs_signature = inputs_signature[0]
        if len(targets_signature) == 1:
            targets_signature = targets_signature[0]
        print('inputs', inputs_signature)
        print('targets', targets_signature)
        #self.train_step = tf.function(self.train_one_step, input_signature=(inputs_signature, targets_signature))
        #self.train_step = tf.function(self.train_one_step)
        """

    def predict(self, inputs, bos_token_id=None, eos_token_id=None, token_dict=None):
        def id_to_tokens(ids, token_dict):
            return [token_dict[id] if id in token_dict else '<UNKOWN>' for id in ids]
        results = []
        #attentions = []

        bos_token_id = 1 if bos_token_id is None else bos_token_id
        eos_token_id = 2 if eos_token_id is None else eos_token_id

        _, enc_hidden = self.encoder(inputs)
        dec_input = tf.expand_dims([bos_token_id] * inputs.shape[0], 1)
        dec_input = tf.cast(dec_input, dtype=tf.int64)
        print('dec    inputs', dec_input)
        for _ in range(self.max_decoder_len):
            predictions, _ = self.decoder([dec_input, enc_hidden])# (batch_size, cur_len, vocab_size)
            print('predictions', predictions.shape)
            next_token_logits = predictions[:, -1, :]  # (batch_size, vocab_size)
            next_token_logits = tf.reshape(next_token_logits, [inputs.shape[0], -1])
            print('predictions', next_token_logits.shape)
            next_tokens = tf.argmax(next_token_logits, axis=-1)
            results.append(next_tokens.numpy())
            #print('dec_inputs', dec_input.shape)
            dec_input = tf.concat([dec_input, tf.expand_dims(next_tokens, 1)], axis=-1)
            #input_ids = tf.concat([input_ids, tf.expand_dims(beam_tokens, 1)], axis=-1)
            print('next_token', next_tokens.numpy(), 'dec_input', dec_input.numpy())
        return results

        """
        for input_seq in inputs:
            print('input_seq', input_seq)
            _, enc_hidden = self.encoder([input_seq])

            #attention_plot = []
            token_out = []

            dec_input = tf.expand_dims([bos_token_id], 0)
            #dec_input = tf.expand_dims([bos_token_id] * targets.shape[0], 1)

            for _ in range(self.max_decoder_len):
                predictions, _ = self.decoder([dec_input, enc_hidden])
                # storing the attention weights to plot later on
                #attention_weights = tf.reshape(att_weights, (-1,))
                # attention_plot.append(attention_weights.numpy())

                next_tokens = tf.argmax(predictions[0]).numpy()
                token_out.append(next_tokens)
                if next_tokens == eos_token_id:
                    break
                dec_input = tf.expand_dims([next_tokens], 0)
            if token_dict is None:
                r = token_out
            else:
                r = id_to_tokens(token_out, token_dict)
            results.append(r)
            """
        # attentions.append(attention_plot)

    # here tf.function can fix error: tensorflow.python.framework.errors_impl.UnknownError: CUDNN_STATUS_BAD_PARAM
    # in tensorflow/stream_executor/cuda/cuda_dnn.cc(1521):
    # 'cudnnSetRNNDataDescriptor( data_desc.get(), data_type, layout,
    # max_seq_length, batch_size, data_size, seq_lengths_array,
    # (void*)&padding_fill)' [Op:CudnnRNNV3]

    def train_step(self, inputs, targets):
        return self.model.train_on_batch([inputs, targets], y=None)