from flask import request, jsonify
from functools import wraps
from revcore_micro.flask.verifiers import ClientVerifier, JWTVerifier, ClientSecretVerifier

class Authorizer:
    region_name = 'ap-northeast-1'
    client_class = None
    client_verifier_class = ClientVerifier
    jwt_verifier_class = JWTVerifier
    client_secret_verifier_class = ClientSecretVerifier

    @classmethod
    def authorize(cls, with_client=False, with_jwt=False, with_client_secret=False, force_client=True, force_jwt=True, force_secret=True):
        def decorated(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                context = request.environ['lambda.event']['requestContext']
                identity = context.get('identity', {})
                client_id = request.args.get('client_id')
                token = request.args.get('token')
                client_secret = identity.get('apiKeyId', '')
                client = None
                user = None
                verifier_class = None 
                if (with_client and force_client) or (with_client and client_id):
                    verifier_class = cls.client_verifier_class
                elif (with_jwt and force_jwt) or (with_jwt and token):
                    verifier_class = cls.jwt_verifier_class
                elif (with_client_secret and force_secret) or (with_client_secret and client_secret):
                    verifier_class = cls.client_secret_verifier_class
                    
                data = {'client_id': client_id, 'token': token, 'client_secret': client_secret}
                verifier = verifier_class(client_class=cls.client_class, region_name=cls.region_name)
                client, user = verifier.verify(**data)

                kwargs['client'] = client
                kwargs['user'] = user
                return f(*args, **kwargs)

            return wrapped

        return decorated
