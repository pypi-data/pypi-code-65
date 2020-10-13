import json
import requests


class Environment:

    def __init__(self, api_url_base):
        self._api_url_base = api_url_base

    def get_url_from(self, path):
        return '{0}{1}'.format(self._api_url_base, path)


class Session:

    def __init__(self, env: Environment, api_token: str):
        self._env = env
        self._api_token = api_token

    @property
    def env(self) -> Environment:
        return self._env

    @property
    def api_token(self) -> str:
        return self._api_token


class WebRequester:

    def __init__(self, session: Session):
        self._session = session

    @property
    def env(self):
        return self.session.env

    @property
    def session(self):
        return self._session

    def get(self, sub_path):
        url = self._get_url_from(sub_path)
        headers = self._get_web_headers()

        return requests.get(url, headers=headers, allow_redirects=False)

    def get_with_content(self, sub_path, obj):
        url = self._get_url_from(sub_path)
        headers = self._get_web_headers()

        return requests.get(url, headers=headers, data=json.dumps(obj), allow_redirects=False)

    def delete(self, sub_path):
        url = self._get_url_from(sub_path)
        headers = self._get_web_headers()

        return requests.delete(url, headers=headers, allow_redirects=False)

    def post(self, sub_path, obj):
        url = self._get_url_from(sub_path)
        headers = self._get_web_headers()

        return requests.post(url, headers=headers, data=json.dumps(obj), allow_redirects=False)

    def put(self, sub_path, obj):
        url = self._get_url_from(sub_path)
        headers = self._get_web_headers()

        return requests.put(url, headers=headers, data=json.dumps(obj), allow_redirects=False)

    # private members

    def _get_url_from(self, sub_path):
        return self.env.get_url_from(sub_path)

    def _get_web_headers(self):
        api_token = self.session.api_token
        return {
            'Content-Type': 'application/json',
            'x-api-key': api_token
        }
