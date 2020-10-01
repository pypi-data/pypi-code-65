from ..interfaces.ILoader import ILoader
from ..types import Credentials
import json


class EnvPasswordCredentialLoader(ILoader):
    """Loads credentials from environment variables."""

    def __init__(self, username_env: str = "", password_env: str = "", token_env: str = ""):
        raise NotImplementedError("This class is still under development.")

    def parse(self) -> Credentials:
        pass


class JsonPasswordCredentialLoader(ILoader):
    """
    Loads credentials from a json file.

    The json file must have the following structure:
    {
      username: "", // Either a string or an integer
      password: "", // Either a string or null
      is_token: <true/false>, // Boolean value
    }
    """

    def __init__(self, json_file: str = "credentials.json"):
        self.credential_file = json_file

    def parse(self) -> Credentials:

        with open(self.credential_file, 'r') as creds:
            credential = json.load(creds)

            assert type(credential['username']) in (str, int), "Username must be a string or integer"
            assert type(credential['password']) in (None, str), "Password must be a string or null"
            assert type(credential['is_token']) is bool, "is_token must be a boolean expresion: true/false."

            return Credentials(username=credential['username'], password=credential['password'],
                               is_token=credential['is_token'])
