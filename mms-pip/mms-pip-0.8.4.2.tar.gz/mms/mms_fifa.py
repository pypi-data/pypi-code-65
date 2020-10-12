import requests
import json
import jwt
from jwt.algorithms import RSAAlgorithm
import time


class Fifa(object):

    def __init__(self,
                 jwk_url="https://auth.mediamarktsaturn.com/.well-known/jwks.json",
                 fifa_token_url="https://auth.mediamarktsaturn.com/oauth/token",
                 max_num_retries=5):

        self.jwk_url = jwk_url
        self.fifa_token_url = fifa_token_url
        self.max_num_retries = max_num_retries
        self.__keys = self.__get_keys()

    def __get_keys_from_api(self):
        try:
            r = requests.get(self.jwk_url)
            if r.status_code != 200:
                raise Exception("status_code={}, content={}".format(r.status_code, r.content.decode('utf-8')))

            jwks = json.loads(r.content.decode('utf-8'))
            public_keys = {}
            for jwk in jwks['keys']:
                kid = jwk['kid']
                public_keys[kid] = RSAAlgorithm.from_jwk(json.dumps(jwk))  # TODO maybe consider other algorithms
            return None, public_keys
        except Exception as exc:
            return "Error while getting jwk from {}: {}".format(self.jwk_url, exc), None

    def __get_keys(self, sleep_start=0.1):
        # Retry block, if i.e. the connection is broken
        for _ in range(self.max_num_retries):
            error, keys = self.__get_keys_from_api()
            if error:
                time.sleep(sleep_start)
                sleep_start = sleep_start*2
                continue  # try again
            else:
                break
        else:
            raise Exception("Error while getting jwk from {}. Max number of retries reached.".format(self.jwk_url))
        return keys

    def verify_jwt_token(self, jwt_token: str, audience):
        """
        Verify if a given jwt_token is valid.

        :param jwt_token: str, jwt token which has to validated
        :param audience: str or tuple of strings with the allowed audience
        :return: tuple(error, payload) -> if no error occurs validation was successful: error=None, payload=dict(...)
                                       -> if error occurs: validation failed: error=str(...), payload=None
        """
        try:
            kid = jwt.get_unverified_header(jwt_token)['kid']
            key = self.__keys.get(kid)
            if key is None:
                # Get potential new keys:
                self.__keys = self.__get_keys()
                key = self.__keys.get(kid)
                if key is None:
                    raise Exception("No public key found for kid: {}.".format(kid))
            payload = jwt.decode(jwt_token, key=key, algorithms=['RS256'], audience=audience)
            return None, payload
        except Exception as exc:
            return "Error while validating jwt: {}".format(exc), None

    def get_jwt_token(self, client_id: str, client_secret: str):
        """
        :param client_id: str
        :param client_secret: str
        :return: tuple (error, bearer_token). If no error: (None, "eyJh334...."). If error: ("Error message", None)
        """
        try:
            data = {'grant_type': 'client_credentials'}
            try:
                access_token_response = requests.post(self.fifa_token_url, data=data, auth=(client_id, client_secret))
            except Exception as ex:
                return 'Get new FIFA bearer token failed: {}'.format(ex), None

            status_code = access_token_response.status_code

            # Check response code
            if status_code != 200:
                return 'FIFA API call not successful: code {}, response {}'.format(status_code, access_token_response.text), None

            result_body = json.loads(access_token_response.content)
            return None,  str(result_body["access_token"])

        except Exception as exc:
            return "Unexpected error: {}".format(exc), None


if __name__ == '__main__':

    # Init fifa handler:
    fifa_handler = Fifa()
    # Optional paramaters (with default values):
    #   - jwk_url="https://auth.mediamarktsaturn.com/.well-known/jwks.json",
    #   - fifa_token_url="https://auth.mediamarktsaturn.com/oauth/token",
    #   - max_num_retries=5

    # Get fifa jwt token: (If error is None -> everything is ok)
    error, token = fifa_handler.get_jwt_token(client_id="...", client_secret="...")
    print(error, token)
    # Verify fifa jwt token: (If error is None -> everything is ok)
    error, payload = fifa_handler.verify_jwt_token(jwt_token=token, audience="...")
    print(error, payload)

