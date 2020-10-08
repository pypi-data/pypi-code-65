"""This file does scheduled inference execution by calling
`predict_on_new_data_and_store()`
"""
import os
from typing import Union

import numpy as np
import tensorflow as tf
from dbnd import task, pipeline
from dbnd._core.current import try_get_current_task_run
from targets import Target, FileTarget


@task
def get_new_data():
    """Extracts new data from database that were added after last inference."""
    n_samples = np.random.randint(5, 50)
    x_data = np.random.normal(0, 0.3, (n_samples, 28, 28, 1))

    ids = np.random.randint(10000, 99999, (n_samples,))
    return x_data, ids

# model_dir should be local access
@task
def predict(data, model_dir):
    sess = tf.compat.v1.Session()
    _ = tf.saved_model.load(sess, [tf.saved_model.SERVING], model_dir)
    graph = sess.graph

    inputs = graph.get_tensor_by_name('inputs:0')
    outputs = graph.get_tensor_by_name('metrics/acc/ArgMax:0')

    evaled = sess.run(outputs, {inputs: data})
    return evaled


@pipeline
def inference_pipeline(model_dir):
    new_data, ids = get_new_data()
    # model_dir = download_to_local(model_path, local_dir_basename=model_name)
    predicted = predict(new_data, model_dir)
    # store result in database here
    return predicted, ids


def download_to_local(remote_path: Union[str, Target], local_dir_basename):
    tr = try_get_current_task_run()
    local_path = os.path.join(tr.local_task_run_root, local_dir_basename)
    target = FileTarget(path=remote_path, fs=None)
    target.fs.download(local_path, remote_path)
    return local_path


def weekly_model():
    import numpy as np

    from dbnd import pipeline

    from .agoda_train import hyper_param_grid_search

@pipeline
def weekly_model():
    learning_rates = np.linspace(0.01, 0.001, 4)
    optimizers_names = ["SGD", "Adam"]
    losses = ["sparse_categorical_crossentropy"]
    # model_output_dir = "optimal_model_graph"
    model_output_dir = "hdfs://optimal_model_graph"
    optimizers = []
    for opt_name in optimizers_names:
        for lr in learning_rates:
            config = {"class_name": opt_name, "config": {"learning_rate": lr}}
            optimizers.append(config)
    hyper_param_grid_search(optimizers, losses, model_output_dir)
    inference_pipeline

if __name__ == '__main__':
    inference_pipeline.dbnd_run()
