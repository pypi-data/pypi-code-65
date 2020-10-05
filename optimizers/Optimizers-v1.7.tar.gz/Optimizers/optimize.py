import json
import requests
from .config import *


def optimize(data, server=SERVER, key=KEY):
    try:
        req = {
            'key': key
        }
        req.update(data)
        solution = json.loads(
            requests.put(server, data=json.dumps(req), headers={"Content-Type": "application/json"}).text)
        return solution
    except Exception as err:
        return {"status": f'error: connecting to server {err}'}
