import json
import requests

def optimize(data, login):
    try:
        req = {
            'key': login['key']
        }
        req.update(data)
        solution = json.loads(
            requests.put(login['server'], data=json.dumps(req), headers={"Content-Type": "application/json"}).text)
        return solution
    except Exception as err:
        return {"status": f'error: connecting to server {err}'}
