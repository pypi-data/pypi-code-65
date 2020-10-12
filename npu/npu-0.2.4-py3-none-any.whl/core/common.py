import hashlib
import math

import requests
from bson import ObjectId
from progress.bar import ChargingBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from .Model import Model
from .DataLoader import DataLoader
from .Dataset import Dataset
from .Task import Task, bar_suffix
from .saving.saving import save_data, determine_model
from .web.urls import TOKEN_URL, HASH_URL, UPLOAD_DATA_URL

VERBOSITY = 1
MIN_VERBOSITY = 1
MID_VERBOSITY = 2
FULL_VERBOSITY = 3

_token = ""


def api(token_, verbosity):
    global _token
    global VERBOSITY
    _token = token_
    VERBOSITY = verbosity
    if VERBOSITY != MIN_VERBOSITY:
        print("Verbosity level set to {}".format(VERBOSITY))
    params = {"token": _token}
    response = requests.get(TOKEN_URL, params=params)
    if response.status_code == 200:
        print("Token successfully authenticated")
        return response
    else:
        raise ValueError(response.text)
    # "API token not valid"


def getToken():
    return _token


def getVerbosity():
    return VERBOSITY


def getResponse(response):
    try:
        return response.json()
    except Exception as e:
        raise ConnectionError("Invalid response received. Error: {}".format(response.text))


# https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def add_kwargs_to_params(params, **kwargs):
    params = {**params, **kwargs}
    return params


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def checkModel(model):
    from .Task import Task
    from .Model import Model
    if not isinstance(model, Task) and not isinstance(model, str) and not isinstance(model, Model):
        raise ValueError("Model is not a valid format. Please make sure you've compiled it first.")


def check_model_type(model, params):
    if isinstance(model, Model):
        params["model_name"] = model.name
        params["model_attr"] = model.attr
    elif isinstance(model, str) and not ObjectId.is_valid(model):
        params["model_name"] = model
    elif model != "" and not isinstance(model, Task):
        params["modelId"] = model


def check_data_type(data, param_name, params):
    if isinstance(data, Dataset):
        params[param_name + "_name"] = data.id
    elif isinstance(data, str) and not ObjectId.is_valid(data):
        params[param_name + "_name"] = data
    elif data != "" and not isinstance(data, Task):
        params[param_name + "Id"] = data


def checkData(data, name=""):
    if not isinstance(name, str):
        raise ValueError("Name given is not valid. Please supply a string.")
    if isinstance(data, (str, dict)):
        return data
    elif isinstance(data, Dataset):
        return data
    elif isinstance(data, DataLoader):
        response = uploadDataLoader(data, name)
    else:
        response = uploadData(data, name)
    status_code = response.status_code
    if status_code not in (204, 200, 201):
        raise ConnectionAbortedError("Data upload has not worked: {}".format(response.content))
    if status_code != 204:
        response = getResponse(response)
    if isinstance(response, dict) and status_code == 200:
        message = response.get("message")
        print(message)
        response = response["id"]
    return response


def sliceData(data):
    id = data["id"]
    x = data["indexes"]
    y = None
    if isinstance(x, slice):
        y = x.stop
        x = x.start
    return id, x, y


def gen(dl):
    for data_part in dl.numpy():
        yield save_data(data_part)


class UploadBar(ChargingBar):
    suffix = bar_suffix + " || %(index_bytes)s / %(max_bytes)s"

    @property
    def index_bytes(self):
        return convert_size(self.index)

    @property
    def max_bytes(self):
        return convert_size(self.max)


def create_callback(encoder):
    encoder_len = encoder.len
    bar = UploadBar('Uploading', max=encoder_len)

    def callback(monitor):
        bar.goto(monitor.bytes_read)
        if monitor.bytes_read == encoder_len:
            bar.finish()
    return callback


def get_progress_bar_uploader(file):
    encoder = create_upload(file)
    callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, callback)
    return monitor


def create_upload(file):
    return MultipartEncoder({
        'file': ('file', file, 'application/octet-stream', {'Content-Transfer-Encoding': 'binary'}),
    })


def uploadDataLoader(dl, name=""):
    length = len(dl)
    if VERBOSITY >= MID_VERBOSITY:
        print("Hashing data locally...")
    hash, size = dl.hash()
    params = {"token": getToken(), "hash": hash, "collection": 1, "chunked": True, "is_last": False, "size": size,
              "given_name": name, "input_shape": dl.shape}
    # params = {"token": getToken(), "hash": hash, "collection": 1, "size": size, "given_name": name}
    print("Checking if data is on servers...")
    response = requests.get(HASH_URL, params=params)
    if response.status_code == 200:
        if VERBOSITY >= MID_VERBOSITY:
            print("Data already uploaded. Will not reupload.")
        return response
    print("Data not on servers. Starting to upload. Total size of data is {}".format(convert_size(size)))
    if length == 1:
        return uploadData(next(dl.numpy()), name)
    print("{} chunks to upload...".format(length))
    for i, data_part in enumerate(dl.numpy()):
        if VERBOSITY >= MID_VERBOSITY:
            print("Uploading chunk {} out of {}...".format(i + 1, length))
        if i == length - 1:
            params["is_last"] = True
        file = save_data(data_part)
        monitor = get_progress_bar_uploader(file)
        response = requests.post(UPLOAD_DATA_URL, data=monitor,
                                 headers={'Content-Type': monitor.content_type}, params=params)
        # response = requests.post(UPLOAD_DATA_URL, files=files, params=params)
    return response


def uploadData(data, name=""):
    if VERBOSITY >= FULL_VERBOSITY:
        print("Saving data locally...")
    if isinstance(data, str):
        file = open(data, "rb")
    else:
        file = save_data(data)
    if VERBOSITY >= FULL_VERBOSITY:
        print("Hashing...")
    hash = hashlib.md5()
    size = 0
    for piece in read_in_chunks(file):
        size += len(piece)
        hash.update(piece)
    hash = hash.hexdigest()
    print("Checking if data is on servers...")
    params = {"token": getToken(), "hash": hash, "collection": 1, "given_name": name}
    response = requests.get(HASH_URL, params=params)
    if response.status_code == 200:
        if VERBOSITY >= MID_VERBOSITY:
            print("Data already on servers. Returning result...")
        file.close()
        return response
    print("Data not found on servers. Total size of data is {}. Uploading now...".format(convert_size(size)))
    file.seek(0)
    # files = {'file': file}

    monitor = get_progress_bar_uploader(file)
    response = requests.post(UPLOAD_DATA_URL, data=monitor,
                             headers={'Content-Type': monitor.content_type}, params=params)
    # response = requests.post(UPLOAD_DATA_URL, files=files, params=params)
    if isinstance(data, str):
        file.close()
    return response


def hashData(data):
    pass


def validate_model(model, data):
    library = determine_model(model)
    if isinstance(data, str):
        return
    # data = convert_to_numpy(data)
    if library == "pytorch":
        from torch import ones
    elif library == "mxnet":
        from mxnet import nd
        ones = nd.ones
    elif library == "TF":
        from numpy import ones
    else:
        return
        # raise ValueError("Cannot validate library: {} .".format(library))
    placeholder_data = ones(data.shape)
    model(placeholder_data)


def determine_data(data):
    start = end = None
    name = ""
    if isinstance(data, dict):
        data, start, end = sliceData(data)
    if isinstance(data, Dataset):
        name = data.id
        data = data
    return data, name, start, end
