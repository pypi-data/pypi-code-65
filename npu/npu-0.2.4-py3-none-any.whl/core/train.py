import base64

import dill
import requests

from .Dataset import Dataset
from .Task import Task
from .common import getToken, checkData, add_kwargs_to_params, checkModel, determine_data, validate_model, \
    check_model_type, check_data_type
from .web.urls import TRAIN_URL


def train(model, training_data, test_data, batch_size, epochs, optimiser, loss, trained_model_name, asynchronous, callback, **kwargs):
    checkModel(model)
    # if isinstance(model, Task):
    #     cached_model = model.cache["model"]
    #     if not isinstance(training_data, (str, Dataset, dict)):
    #         validate_model(cached_model, training_data[0])
    #     if not isinstance(test_data, (str, Dataset, dict)) and test_data is not None:
    #         validate_model(cached_model, test_data[0])
    training_data = checkData(training_data)
    test_data = checkData(test_data)
    task_id = model.task_id if isinstance(model, Task) else ""
    task = Task(trainApi(model, training_data, test_data, optimiser, loss, batch_size, epochs, trained_model_name, task_id, **kwargs).json(),
                callback)
    if not asynchronous:
        task.wait(show_progress=True)
        print("Model finished training")
    return task


def trainApi(model, train_data, test_data, optimiser, loss, batch_size, epochs, trained_model_name, task_id="", **kwargs):
    if not isinstance(trained_model_name, str):
        raise ValueError("Name given is not valid. Please supply a string.")
    train_data, train_name, train_start, train_end = determine_data(train_data)
    test_data, test_name, test_start, test_end = determine_data(test_data)
    if callable(loss):
        print("Using custom loss function...")
        loss = base64.urlsafe_b64encode(dill.dumps(loss))
    params = { "loss": loss,
              "token": getToken(), "batch_size": batch_size, "epochs": epochs, "task_id": task_id, "train_start": train_start,
              "train_end": train_end, "test_start": test_start, "test_end": test_end, "train_name": train_name,
              "test_name": test_name, "trained_model_name": trained_model_name}
    check_model_type(model, params)
    check_data_type(train_data, "train", params)
    check_data_type(test_data, "test", params)
    params = add_kwargs_to_params(params, **kwargs)
    response = requests.get(TRAIN_URL, params=params, json=optimiser)
    if response.status_code != 200:
        raise ValueError(response.text)
    return response


