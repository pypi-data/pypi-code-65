import numpy as np
import requests
import time
import os
import json
from uuid import uuid4

endpoint = 'https://booste-corporation-v3-flask.zeet.app/'
# Endpoint override for development
if 'BoosteURL' in os.environ:
    print("Dev Mode")
    if os.environ['BoosteURL'] == 'local':
        endpoint = 'http://localhost/'
    else:
        endpoint = os.environ['BoosteURL']
    print("Hitting endpoint:", endpoint)


# identify machine for blind use
cache_path = os.path.abspath(os.path.join(os.path.expanduser('~'),".booste","cache.json"))
if os.path.exists(cache_path):
    with open(cache_path, "r") as file:
        cache = json.load(file)
else:
    cache = {}
    cache['machine_id'] = str(uuid4())
    os.makedirs(os.path.join(os.path.expanduser('~'), ".booste"), exist_ok=True)
    with open(cache_path, "w+") as file:
        json.dump(cache, file)


client_error = {
    "OOB" : "Client error: {}={} is out of bounds.\n\tmin = {}\n\tmax = {}"
}

def gpt2_main(api_key, model_size, in_string, length, temperature, window_max):
    # Make sure request is valid
    global client_error
    if temperature < 0.1 or temperature > 1:
        raise Exception(client_error['OOB'].format("temperature", temperature, "0.1", "1"))
    if window_max < 1 or window_max > 1023:
        raise Exception(client_error['OOB'].format("window_max", window_max,   "1", "1023"))

    global endpoint
    route_start = 'inference/pretrained/gpt2/async/start'
    url_start = endpoint + route_start
    route_check = 'inference/pretrained/gpt2/async/check'
    url_check = endpoint + route_check
    length = int(length)
    # sequence = []

    task_id = gpt2_start(url_start, api_key, model_size, in_string, length, temperature, window_max)

    if task_id == None:
        return None


    # Choose a delay approprate for the call
    if model_size == 'gpt2':
        interval = length * 0.1
        initial_wait = length * .2
    elif model_size == 'gpt2-xl':
        interval = length * 0.2
        initial_wait = length * .4
    else:
        interval = 3
        initial_wait = length * .3
    # Correct for small calls so it's not rediculous
    if interval < 3:
        interval = 3
    time.sleep(initial_wait)
    out = await_async(url_check, task_id, interval)
    return out


def gpt2_start(url, api_key, model_size, in_string, length, temperature, window_max):
    global cache
    # sequence = []
    payload = {
        "string" : in_string,
        "length" : str(length),
        "temperature" : str(temperature),
        "machineID" : cache['machine_id'],
        "apiKey" : api_key,
        "modelSize" : model_size,
        "windowMax" : window_max
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
            response.status_code, response.json()['message']))
    
    try:
        out = response.json()
        task_id = out['TaskID']
        return task_id
    except:
        raise Exception("Server error: Booste inference server returned status code", response.status_code)


def await_async(url, task_id, interval):
    while True:
        # Poll server for completed task
        payload = {"TaskID": task_id}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception("Server error: Booste inference server returned status code {}\n{}".format(
                response.status_code, response.json()['message']))
        try:
            out = response.json()
            if out['Status'] == "Finished":
                return out["Output"]  
            # Catch errors
            if out['Status'] != "PENDING":
                raise Exception("Server error: Booste inference worker failed with status {}".format(out['Status']))
        except:
            raise Exception("Server error: Booste inference server returned status code", response.status_code)

        time.sleep(interval)