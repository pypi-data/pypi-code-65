import sys
import requests
import json
from json import JSONDecodeError
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Sc:
    def __init__(self, username, password, base_url):
        self.base_url = base_url
        self.session = self._create_session(username, password)
        self.token = self.session['token']
        self.user_id = self.session['user']['id']

    def _create_session(self, username, password):
        payload = {
            'user': {
                'userID': username,
                'password': password,
            }
        }

        try:
            output_json = self._api_call('POST', 'api/sessions', payload, auth=False)

        except JSONDecodeError:
            sys.exit('Failed to authenticate. Please check your Smart Check URL, username and password.')

        return output_json

    def _api_call(self, verb, endpoint, payload='', auth=True, query_params=None):
        headers = {
            'Content-type': 'application/json',
        }

        if auth:
            headers['Authorization'] = f'Bearer {self.token}'

        path = f'{self.base_url}/{endpoint}'
        call_verb = getattr(requests, verb.lower())

        if query_params:
            request_output = call_verb(path, headers=headers, json=payload, verify=False, params=query_params)

        else:
            request_output = call_verb(path, headers=headers, json=payload, verify=False)

        output_json = request_output.json()

        return output_json

    def list_sessions(self):
        output = self._api_call('get', 'api/sessions')

        return json.dumps(output, indent=4, sort_keys=True)

    def list_users(self):
        output = self._api_call('get', 'api/users')

        return json.dumps(output, indent=4, sort_keys=True)

    def list_roles(self):
        output = self._api_call('get', 'api/roles')

        return json.dumps(output, indent=4, sort_keys=True)

    def get_role_id_map(self):
        role_id_map = {}

        get_roles = self.list_roles()
        roles = json.loads(get_roles)

        for role in roles['roles']:
            role_name = role['name']
            role_id = role['id']

            role_id_map[role_name] = role_id

        return role_id_map

    def change_password(self, original_password, new_password):
        payload = {
            'oldPassword': original_password,
            'newPassword': new_password,
            }

        output_json = self._api_call('POST', f'api/users/{self.user_id}/password', payload, auth=True)

        return output_json

    def create_user(self, username, password, role_id, description='', name='', password_change_required=True):
        payload = {
            'userID': username,
            'password': password,
            'passwordChangeRequired': password_change_required,
            'name': name if name else username,
            'description': description,
            'role': role_id,
            }

        output_json = self._api_call('POST', f'api/users', payload, auth=True)

        return output_json

    def create_registry(self, registry_hostname, registry_name, registry_region, registry_description='',
                        insecure_skip_verify='false'):

        payload = {
            'host': registry_hostname,
            'name': registry_name,
            'description': registry_description,
            'insecure_skip_verify': insecure_skip_verify,
            'credentials': {
                'aws': {
                    'region': registry_region,
                }
            }
        }

        query_params = {'scan': 'true'}

        output_json = self._api_call('POST', f'api/registries', payload, auth=True, query_params=query_params)

        return output_json
