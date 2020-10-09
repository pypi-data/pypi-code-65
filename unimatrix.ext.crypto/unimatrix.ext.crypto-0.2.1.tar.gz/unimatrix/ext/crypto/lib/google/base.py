"""Declares :class:`GoogleKMSInvoker`."""
from google.cloud import kms
from gcloud.aio.kms import KMS


class GoogleKMSInvoker:
    """Provides methods to invoke the Google KMS API."""

    # Maps Google algortihm version indicators to PKCS#1 OID.
    _crypto_mapping = {
        # RSA_SIGN_PKCS1_4096_SHA256
        7: "1.2.840.113549.1.1.11"
    }


    def __init__(self, project=None, region=None, keyring=None, key=None, version=None, resource_id=None):
        self._google_kms = kms.KeyManagementServiceClient()
        if resource_id is not None:
            self.__resource_id = resource_id
        else:
            self.__resource_id = None
            self.__project = project
            self.__region = region
            self.__keyring = keyring
            self.__key = key
            self.__version = version

    def _get_async_client(self):
        return KMS(self.__project, self.__keyring, self.__key,
            location=self.__region)

    def _get_resource_id(self):
        if self.__resource_id is not None:
            return self.__resource_id

        if self.__version:
            return self._google_kms.crypto_key_version_path(
                self.__project, self.__region, self.__keyring, self.__key,
                self.__version)
        else:
            return self._google_kms.crypto_key_path(
                self.__project, self.__region, self.__keyring, self.__key)
