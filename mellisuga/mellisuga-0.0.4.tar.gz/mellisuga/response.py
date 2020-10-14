import json
import base64
import decimal

try:
    # In python 2 there is a base class for the string types that
    # we can check for. It was removed in python 3 so it will cause
    # a name error.
    _ANY_STRING = (basestring, bytes)
except NameError:
    # In python 3 string and bytes are different so we explicitly check
    # for both.
    _ANY_STRING = (str, bytes)


def handle_decimals(obj):
    # Lambda will automatically serialize decimals so we need
    # to support that as well.
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj


class Response(object):
    def __init__(self, data, status_code=200, headers=None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }

    def to_dict(self, binary_types=None):
        data = self.data
        if not isinstance(data, _ANY_STRING):
            data = json.dumps(data, default=handle_decimals)
        response = {
            'statusCode': self.status_code,
            'data': data
        }
        return response

    def data_as_string(self):
        data = self.data
        if not isinstance(data, _ANY_STRING):
            data = json.dumps(data, default=handle_decimals)
        return data

    def _base64encode(self, data):
        if not isinstance(data, bytes):
            raise ValueError('Expected bytes type for body with binary '
                             'Content-Type. Got %s type body instead.'
                             % type(data))
        data = base64.b64encode(data)
        return data.decode('ascii')

    def __call__(self):
        return self.to_dict()
