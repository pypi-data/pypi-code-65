"""Extracts data, trains model and does hyper-search.

Execute `hyper_param_grid_search` to optimize and store optimal model.
 """
import itertools
import os
import shutil

from typing import Any, Callable, Dict, List, Tuple

import tensorflow as tf

from dbnd import parameter, pipeline, task
from targets import Target

assert tf.__version__ == "1.15.2"


@task(result=parameter.output[Tuple[Tuple[Any, Any], Tuple[Any, Any]]])
def load_data(lang: str = "en"):
    """Loads and preprocesses data for training.

    The output of this function is expected to be reused.
    """
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train / 255.0
    x_test = x_test / 255.0
    x_train = x_train[..., None][:15000]
    x_test = x_test[..., None][:5000]
    y_train = y_train[..., None][:15000]
    y_test = y_test[..., None][:5000]
    return (x_train, y_train), (x_test, y_test)


# @task(result=parameter.output.tensor[tf.python.keras.callbacks.History])
@task
def train_model(
    data: Tuple[Tuple[Any, Any], Tuple[Any, Any]],
    model_builder_fn: Callable = None,
    optimizer=None,
    learning_rate: float = 0.001,
    loss=None,
    epochs: int = 3,
    batch_size: int = 128,
):
    """Trains model.

    Args:
      model_builder_fn: A callable that creates non-compiled model.
      optimizer: A config dictionary, string, or instance of
        `tf.keras.optimizers.Optimizer`.
      loss: A callable, string, or instance of `tf.keras.losses.Loss`.

      The rest of arguments are floats and self-explanatory.

    Returns:
      `tf.keras.callbacks.History` instance of the training logs.
    """

    model = (model_builder_fn or model_builder)()

    model.compile(
        optimizer=optimizer or tf.keras.optimizers.SGD(learning_rate),
        loss=loss or "sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    (x, y), validation_data = data
    history = model.fit(
        x, y, validation_data=validation_data, batch_size=batch_size, epochs=epochs
    )

    return history


@pipeline
def hyper_param_grid_search(optimizers: List, losses: List, model_output_dir: str):
    """Hyper param grid search, stores optimal model"""
    models = [model_builder]
    hyper_param_space = list(itertools.product(models, optimizers, losses))
    data = load_data()
    histories = []
    for i, (model_builder_fn, opt, loss) in enumerate(hyper_param_space):
        histories.append(train_model(data, model_builder_fn, opt, loss=loss))

        # store optimal model so far
        store_optimal_model(model_output_dir)

        tf.keras.backend.clear_session()  # clear session for next hyper-set

        if i >= 3:  # limit the number of iteration for speedup
            break

    return histories


@task(result=parameter.output.require_local_access[Target])
def store_optimal_model(model_output_dir: str):
    sess = tf.compat.v1.keras.backend.get_session()
    if os.path.exists(model_output_dir):
        # if model_output_dir.exists():
        shutil.rmtree(model_output_dir)
    builder = tf.compat.v1.saved_model.builder.SavedModelBuilder(model_output_dir)
    builder.add_meta_graph_and_variables(sess, [tf.saved_model.SERVING])
    builder.save()

    return tf


@task(result=parameter.output.require_local_access[tf.keras.models.Model])
def model_builder():
    """Builds simple CNN model for MNIST."""
    inputs = tf.keras.layers.Input((28, 28, 1), dtype=tf.float32, name="inputs")
    res = tf.keras.layers.Conv2D(
        filters=6, kernel_size=(5, 5), strides=(1, 1), activation=tf.nn.relu
    )(inputs)
    res = tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2))(res)
    res = tf.keras.layers.Flatten()(res)
    res = tf.keras.layers.Dense(10, activation=tf.nn.softmax)(res)
    # _ = tf.keras.layers.Lambda(lambda x: tf.math.argmax(x, axis=-1), name='outputs')(res)
    return tf.keras.models.Model(inputs, res)
