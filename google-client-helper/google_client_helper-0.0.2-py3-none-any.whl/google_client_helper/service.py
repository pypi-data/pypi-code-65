import json
from time import sleep
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.http import HttpError
from encrypted_credentials import django_credentials


class GoogleServiceMixin:
    api_name = None
    api_version = None
    scopes = None
    credential_name = None

    def __init__(self, account_email=None):
        self.credentials = None
        self.account_email = account_email
        self.service = self.get_service_account()

    def get_service_account(self):
        json_credentials = json.loads(django_credentials.get_credentials(self.credential_name))
        self.credentials = service_account.Credentials.from_service_account_info(json_credentials, scopes=self.scopes)
        if self.account_email:
            self.credentials = self.credentials.with_subject(self.account_email)
        return discovery.build(self.api_name, self.api_version, credentials=self.credentials, cache_discovery=False)

    @staticmethod
    def google_execute_retry(api_command):
        retry = 1
        while retry < 9:
            try:
                result = api_command.execute()
                return result
            except HttpError:
                sleep(retry)
                retry = 2 * retry
        return api_command.execute()
