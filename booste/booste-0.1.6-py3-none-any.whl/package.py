import requests, os
from uuid import uuid4
import numpy as np
import json
import base64

endpoint = 'https://booste-corporation-v3-flask.zeet.app/'
# Endpoint override for development
if 'BoosteDevMode' in os.environ:
    print("Dev Mode")
    endpoint = 'http://localhost/'


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


def gpt2(api_key, in_string, length = 5, temperature = 0.8, batch_length = 20, window_max = 50, pretrained = True, model_id = None):
    
    # Make sure request is valid
    global client_error
    if temperature < 0.1 or temperature > 1:
        raise Exception(client_error['OOB'].format("temperature", temperature, "0.1", "1"))
    if batch_length < 1 or batch_length > 50:
        raise Exception(client_error['OOB'].format("batch_length", batch_length, "1", "50"))
    if window_max < 1 or window_max > 200:
        raise Exception(client_error['OOB'].format("window_max", window_max,   "1", "200"))

    global endpoint
    route = 'inference/pretrained/gpt2'
    url = endpoint + route
    length = int(length)
    sequence = []

    # Loop batches until requested length is done
    while True:
        # adjust batch size to remainder for final loop
        if len(sequence) + batch_length > length:
            batch_length = length - len(sequence) + 3 # Add 3 for extra buffer so there's not single word calls

        sequence_string = " ".join(sequence) # convert aggrigated output "sequence" into string
        if len(sequence_string) > 0:
            batch_string = in_string + " " + sequence_string # add aggrigated output onto original input
        else: 
            batch_string = in_string

        # Reduce to max window size
        batch_sequence = batch_string.split(" ")
        if len(batch_sequence) >= window_max:
            end_index = len(batch_sequence)+1
            batch_sequence = batch_sequence[end_index-window_max:end_index]
        batch_string = " ".join(batch_sequence)
        batch_out = run_gpt2_batch(url, api_key, batch_string, batch_length, temperature)
        if batch_out == None:
            return None
        for item in batch_out:
            sequence.append(item)

        if len(sequence) >= length:
            break

    return(sequence[0:length]) #Return, and shave off any buffer from the last pass


def run_gpt2_batch(url, api_key, in_string, length, temperature):
    global cache
    sequence = []
    payload = {
        "string" : in_string,
        "length" : str(length),
        "temperature" : str(temperature),
        "machineID" : cache['machine_id'],
        "apiKey" : api_key
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("Error: Booste inference server returned status code", response.status_code)
        print(response.json()['message'])
        return None
    out = response.content.decode()

    # Clean the out into list
    cleaned = str(out[2:len(out)-2])
    offset = 0
    word = ""
    for i in range(len(cleaned)):
        if i+offset < len(cleaned):
            if cleaned[i+offset] == '\\':
                if i+offset+1 < len(cleaned):
                    if cleaned[i+offset+1] == 'n':
                        if word != "" and word != " ":
                            sequence.append(word)
                            word = ""
                        sequence.append("\n")
                        offset += 1
            elif cleaned[i+offset] == " ":
                if word != "" and word != " ":
                    sequence.append(word)
                    word = ""
            else:
                word += cleaned[i+offset]
    if word != "" and word != " ":
        sequence.append(word)
        word = ""

    return sequence






# def yolov3(image_path, owner, model_name, labels, postprocess = True, obj_thresh = 0.5, nms_thresh = 0.5):
#     global endpoint
#     route = 'inference/yolov3'
#     url = os.path.join(endpoint, route)

#     files = {'file': open(image_path, 'rb')}
#     payload = {"owner" : owner,
#     "model_name" : model_name,
#     "labels" : json.dumps(labels),
#     "postprocess" : postprocess,
#     "obj_thresh" : obj_thresh,
#     "nms_thresh" : nms_thresh,
#     "image_name" : image_path}

#     response = requests.post(url, files=files, data=payload)

#     r = response.json()

#     if postprocess:
#         boxes = r['boxes']
#         img_data = base64.b64decode(r['image'])
#         path_out = image_path[:-4] + '_detected' + image_path[-4:]
#         with open(path_out, "wb") as fh:
#             fh.write(img_data)        
#         return boxes

#     else:
#         out1 = np.reshape(a = r['output1'], newshape = r['output1shape'])
#         out2 = np.reshape(a = r['output2'], newshape = r['output2shape'])
#         out3 = np.reshape(a = r['output3'], newshape = r['output3shape'])
#         return {"output_1":out1,"output_2":out2,"output_3":out3}
