"""Rest Client using requests module"""
import requests


class RestClient:
    """Rest Client"""

    @staticmethod
    def get(url, headers=None, auth=None, query_params=None):
        """Get method"""
        response = ""
        if auth is not None:
            response = requests.get(url, params=query_params, headers=headers,
                                    auth=(auth['user'], auth['password']))
        else:
            response = requests.get(url, params=query_params, headers=headers)
        return response

    @staticmethod
    def post(url, headers=None, auth=None, data=None):
        """Post method"""
        response = ""
        if auth is not None:
            response = requests.post(url, json=data, headers=headers,
                                     auth=(auth['user'], auth['password']))
        else:
            response = requests.post(url, json=data, headers=headers)
        return response

    @staticmethod
    def put(url, headers=None, auth=None, data=None):
        """Put method"""
        response = ""
        if auth is not None:
            response = requests.put(url, json=data, headers=headers,
                                     auth=(auth['user'], auth['password']))
        else:
            response = requests.put(url, json=data, headers=headers)
        return response

