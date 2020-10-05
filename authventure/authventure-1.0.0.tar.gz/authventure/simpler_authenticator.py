import jwt


class SimplerAuthenticator:
    def __init__(self, secret: str):
        self.secret = secret

    def create_user_unexpirable_token(self, user_id: str) -> str:
        return jwt.encode(
            {"userId": user_id},
            self.secret,
            algorithm='HS256'
        )

    def get_user_id_from_unexpirable_token(self, token: str) -> str:
        payload = jwt.decode(
            token,
            self.secret,
            algorithms='HS256',
            options={'verify_signature': True, 'verify_exp': False}
        )

        return payload['userId']
