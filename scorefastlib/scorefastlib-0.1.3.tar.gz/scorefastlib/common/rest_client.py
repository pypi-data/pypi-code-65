# -*- coding: utf-8 -*-
import requests


class RestClient(object):
    """ RESTful Client """
    @staticmethod
    def get(url, headers={}, auth={}, query_params={}):
        response = ""
        if len(auth) > 0:
            response = requests.get(url,  params=query_params, headers=headers, auth=(
                auth['user'], auth['password']))
        else:
            response = requests.get(url, params=query_params, headers=headers)
        return response

    @staticmethod
    def post(url, headers={}, auth={}, data={}):
        response = ""
        if len(auth) > 0:
            response = requests.post(url, json=data, headers=headers, auth=(
                auth['user'], auth['password']))
        else:
            response = requests.post(url, json=data, headers=headers)
        return response
