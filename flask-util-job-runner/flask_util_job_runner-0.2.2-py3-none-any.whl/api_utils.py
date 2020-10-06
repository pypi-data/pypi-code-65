import copy
import json
import os
import uuid

import requests
from flask import request, Response, jsonify
import logging
import traceback


def handle(method_name, version, uuid_str, data_json):
    url = 'http://' + method_name + '.' + version
    error_message = str({'message': 'Error while calling ' + method_name, 'uuid_str': uuid_str})
    try:
        resp = requests.post(url, json=data_json)
        if not resp.ok:
            logging.error(method_name + error_message)
            return jsonify(error_message), 500
        res = resp.json()
        res['uuid_str'] = uuid_str
        return jsonify(res), 200
    except requests.exceptions.ConnectionError as e:
        message = 'Cannot send POST request to ' + url
        message += str(e) + ' Is the webservice running?'
        log_error_message = {'message': message, 'uuid_str': uuid_str}
        logging.error(method_name + str(log_error_message))
        return jsonify(error_message), 500
    except:
        logging.error(method_name + str({'traceback': traceback.format_exc()}))
        return jsonify(error_message), 500


def with_request_params(mandatory):
    def get_request_param(key):
        try:
            return request.json[key]
        except KeyError:
            return None

    def call_with_params(f):
        def wrapper():
            params = {}
            for key in mandatory:
                params[key] = get_request_param(key)
                if not params[key]:
                    return ErrorSecuredWithToken('Missing expected parameter {}'.format(key)).response()
            uuid_str = str(uuid.uuid4())
            params['uuid_str'] = uuid_str
            params_logged = copy.deepcopy(params)
            if 'data' in params_logged:
                params_logged['len_data'] = len(params_logged['data'])
                del params_logged['data']
            logging.info(f.__name__ + ' ' + str(params_logged))
            return f(**params)

        wrapper.__name__ = f.__name__
        return wrapper

    return call_with_params


def secured_with_token():
    try:
        expected_api_key = os.environ['token']
    except KeyError:
        expected_api_key = None
    api_key_header = 'Token'

    def get_token_from_request():
        return request.headers.get(api_key_header)

    def secured_call(f):
        def wrapper(*args, **kwargs):
            if expected_api_key is None or (get_token_from_request() == expected_api_key):
                try:
                    return f(*args, **kwargs)
                except Exception as ex:
                    message = 'Unhandled exception occurred : {}'.format(traceback.format_exc())
                    logging.error(message)
                    return ErrorSecuredWithToken(message).response()
            else:
                return ErrorSecuredWithToken('Could not validate credentials ', http_status=403).response()

        wrapper.__name__ = f.__name__
        return wrapper

    return secured_call


class ErrorSecuredWithToken:
    def __init__(self, details, http_status=400):
        self._status = http_status
        self._details = details
        self._http_status = http_status

    def response(self):
        response = {
            'status': self._status,
            'details': self._details if self._details is not None else ''
        }
        return Response(json.dumps(response), status=self._http_status, mimetype='application/json')
