import json
from urllib import request

def get(url, headers=None):
    kwargs = {
        'url': url,
        'headers': headers or {}
    }

    req = request.Request(**kwargs)                    
    response = request.urlopen(req)
    return response.read().decode('utf8')

def post(url, headers=None, data=None):
    kwargs = {
        'url': url,
        'headers': headers or {}
    }

    if data:
        kwargs['data'] = json.dumps(data)
        kwargs['headers']['Content-Type'] = 'application/json'

    req = request.Request(**kwargs)                    
    response = request.urlopen(req)
    return response.read().decode('utf8')