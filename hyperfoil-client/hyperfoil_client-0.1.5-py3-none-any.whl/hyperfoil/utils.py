import requests
import yaml


def extract_response(response: requests.Response) -> dict:
    if 'text/vnd.yaml' in response.headers.get("Content-Type", ""):
        return yaml.load(response.content.decode('utf-8'), Loader=yaml.Loader)
    return response.json()
