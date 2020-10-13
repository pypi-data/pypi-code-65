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
 UTKFace model training script
"""

# System imports
import os
import sys
import argparse

# Keras imports
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import LearningRateScheduler

# Akida
from cnn2snn import load_quantized_model
from akida_models.utk_face.preprocessing import load_data


def get_rescaled_data_set(x_train, x_test, input_scaling):
    a, b = input_scaling

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')

    x_train = (x_train - b) / a
    x_test = (x_test - b) / a

    return x_train, x_test


def train_model(model,
                x_train,
                y_train,
                x_test,
                y_test,
                epochs=30,
                batch_size=128):

    # Learning rate: be more aggressive at the beginning, and apply decay
    lr_start = 1e-3
    lr_end = 1e-4
    lr_decay = (lr_end / lr_start)**(1. / epochs)

    lr_scheduler = LearningRateScheduler(lambda e: lr_start * lr_decay**e)
    callbacks = [lr_scheduler]

    # Compile model
    model.compile(optimizer='adam', loss='mae')

    history = model.fit(x_train,
                        y_train,
                        batch_size=batch_size,
                        epochs=epochs,
                        verbose=1,
                        validation_data=(x_test, y_test),
                        callbacks=callbacks)


def evaluate_model(model, x_test, y_test):

    # Compile model
    model.compile(optimizer='adam', loss='mae')

    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test score:', score)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-m",
                        "--model",
                        type=str,
                        required=True,
                        help="Model to be trained or tuned")
    parser.add_argument("-s",
                        "--savemodel",
                        type=str,
                        default=None,
                        help="Save model with the specified name")
    parser.add_argument("-e",
                        "--epochs",
                        type=int,
                        default=0,
                        help="The number of training epochs")

    args = parser.parse_args()

    # Load the dataset
    x_train, y_train, x_test, y_test = load_data()
    input_scaling = (127, 127)
    input_shape = x_train.shape[1:]

    # Prepare the dataset (rescale)
    x_train, x_test = get_rescaled_data_set(x_train, x_test, input_scaling)

    # Load the source model
    model = load_quantized_model(args.model)

    # Train model
    if args.epochs > 0:
        train_model(model, x_train, y_train, x_test, y_test, args.epochs)

    # Save model in Keras format (hdf5)
    if args.savemodel:
        model.save(args.savemodel, include_optimizer=False)
        print(f"Trained model saved as {args.savemodel}")

    # Evaluate model accuracy
    evaluate_model(model, x_test, y_test)


if __name__ == "__main__":
    main()