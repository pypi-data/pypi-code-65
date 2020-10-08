import numpy as np

from dbnd import pipeline

from .agoda_train import hyper_param_grid_search


@pipeline
def pipeline():
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


# from typing import List
# from dbnd import task, pipeline
# from dbnd._core.parameter.parameter_builder import output
# from targets import Target
#
#
# def save_my_custom_object(path: str, data) -> None:
#     with open(path, 'w') as fd:
#         fd.writelines(data)
#
#
# def load_my_custom_object(path: str) -> List[str]:
#     with open(path, 'r') as fd:
#         return fd.readlines()
#
#
# @task
# def test_read(loc: Target) -> str:
#     data = load_my_custom_object(loc.path)
#     return " ".join(data)
#
#
# # def write(data, res=output.data):
# @task
# def test_write(data, res=output.data.require_local_access):
#     save_my_custom_object(res, data)
#
#
# @pipeline
# def test_read_write(data=["abcd", "zxcvb"]):
#     path = test_write(data)
#     r = test_read(path.res)
#     return r
# local run (by default --env equal local)
# dbnd run dbnd_examples.pipelines.test_fs.test_read_write
# hdfs run (need to configure prod env with hdfs)
# dbnd run dbnd_examples.pipelines.test_fs.test_read_write --env prod
