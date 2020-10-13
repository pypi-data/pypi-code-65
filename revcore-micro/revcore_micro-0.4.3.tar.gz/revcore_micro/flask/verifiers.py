from revcore_micro.ddb.exceptions import InstanceNotFound
from jwcrypto.jwk import JWK
from revcore_micro.flask import exceptions
import boto3
import jwt
import requests
import json


class BaseVerifier:
    def __init__(self, client_class, region_name='ap-northeast-1'):
        self.client_class = client_class
        self.region_name = region_name

    def verify(self, *args, **kwargs):
        raise NotImplementedError('verify')


class ClientVerifier(BaseVerifier):
    def verify(self, client_id, **kwargs):
        try:
            return self.client_class.get(id=client_id), None
        except InstanceNotFound:
            raise exceptions.PermissionDenied


class ClientSecretVerifier(BaseVerifier):
    region_name = 'ap-northeast-1'

    def verify(self, client_secret, **kwargs):
        try:
            client = boto3.client('apigateway', region_name=self.region_name)
            client_id = client.get_api_key(apiKey=client_secret)['name']
            return self.client_class.get(id=client_id), None
        except:
            raise exceptions.PermissionDenied


class JWTVerifier(BaseVerifier):
    def get_public_key(self, kid):
        resp = requests.get('https://keys.revtel-api.com/pub.json').json()
        key = [key for key in resp if key['kid'] == kid][0]
        key = JWK.from_json(json.dumps(key))
        return key.export_to_pem()

    def verify(self, token, **kwargs):
        try:
            header = jwt.get_unverified_header(token)
            client = header['kid']
            pub = self.get_public_key(client)
            user = jwt.decode(token, algorithms='RS256', key=pub, verify=True, audience=client)
            client = self.client_class.get(id=client)
            return client, user
        except Exception as e:
            raise exceptions.PermissionDenied
