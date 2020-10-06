import json
import requests
from .config import Server



def optimize(data):
    try:
        req = {
            'key': Server.key
        }
        req.update(data)
        solution = json.loads(
            requests.put(Server.url, data=json.dumps(req), headers={"Content-Type": "application/json"}).text)
        return solution
    except Exception as err:
        return {"status": f'error: connecting to server {err}'}
