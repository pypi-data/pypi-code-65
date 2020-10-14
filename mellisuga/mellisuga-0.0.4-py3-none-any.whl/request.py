import json
import base64


class Request(object):
    """The request from API gateway."""
    def __init__(self, data=None, params=None, route=None, headers=None, context=None, auth=None):
        """  Route could be path or action """
        self.params = params or {}
        self.headers = headers or {}
        self.auth = auth or {}
        self._data = data or {}
        self.route = route or ''
        self._json_data = None
        self._raw_data = b''
        self.context = context or {}
        self._is_base64_encoded = False

    def _base64decode(self, encoded):
        if not isinstance(encoded, bytes):
            encoded = encoded.encode('ascii')
        output = base64.b64decode(encoded)
        return output

    @property
    def raw_data(self):
        if not self._raw_data and self._data is not None:
            if self._is_base64_encoded:
                self._raw_data = self._base64decode(self._data)
            elif isinstance(self._data, bytes):
                self._raw_data = self._data.encode('utf-8')
            else:
                self._raw_data = self._data
        return self._raw_data

    @property
    def json_data(self):
        # TODO if self.headers.get('content-type', '').startswith('application/json'):
        if self._json_data is None:
            if isinstance(self._data, dict):
                self._json_data = self.raw_data
            else:
                try:
                    self._json_data = json.loads(self.raw_data)
                except ValueError:
                    return {}
        return self._json_data

    def to_dict(self):
        # Don't copy internal attributes.
        copied = {k: v for k, v in self.__dict__.items()
                  if not k.startswith('_')}
        # We want the output of `to_dict()` to be
        # JSON serializable, so we need to remove the CaseInsensitive dict.
        copied['headers'] = dict(copied['headers'])
        return copied
