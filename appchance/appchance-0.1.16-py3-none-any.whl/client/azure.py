from azure.storage.file import FileService
from azure.storage.file.models import FilePermissions
from django.conf import settings
from django.utils import timezone

read_permission = FilePermissions(read=True)

class ClientAFS:
    """ Manage files on Azure File Storage.
        Default expiry time of SAS signature is set to one hour.
    """

    def __init__(self, account_name, account_key, expiry=3600):
        self.account_name = account_name
        self.client = FileService(account_name=account_name, account_key=account_key)
        self.expiry = expiry

    def get_file_sas(self, share_name, file_name):
        """ Fetch token for temporary public file read access.
        """
        return self.client.generate_file_shared_access_signature(
            share_name=share_name,
            file_name=file_name,
            permission=read_permission,
            expiry=timezone.now()+timezone.timedelta(seconds=self.expiry)
        )

    def public_file_link(self, share_name, file_name):
        return (f"https://{self.account_name}.file.core.windows.net/"
                f"{file_name}?{self.get_file_sas(share_name, file_name)}")
