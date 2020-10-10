"""Implements the :mod:`unimatrix.ext.crypto` interface for Google Cloud
KMS.
"""
import copy

from ..backend import BaseBackend
from .decrypter import GoogleDecrypter
from .encrypter import GoogleEncrypter
from .signer import GoogleSigner
from .symmetric import GoogleSymmetricKey


Decrypter = GoogleDecrypter
Encrypter = GoogleEncrypter
Signer = GoogleSigner


PARAM_KEYRING       = "cloudkms.googleapis.com/keyring"
PARAM_KEY           = "cloudkms.googleapis.com/key"
PARAM_LOCATION      = "cloudkms.googleapis.com/location"
PARAM_PROJECT       = "cloud.google.com/project"
PARAM_RESOURCE_ID   = "cloudkms.googleapis.com/resource-id"
PARAM_VERSION       = "cloudkms.googleapis.com/version"


class Backend(BaseBackend):
    """A cryptographic backend that uses Google Cloud KMS."""
    __module__ = 'unimatrix.ext.crypto.lib.google'

    def __init__(self, params):
        """Initializes a new :class:`unimatrix.ext.crypto.lib.google.Backend`
        instance.

        The fully-qualified path to the encryption or signing key in Google
        Cloud KMS is specified using ``cloudkms.googleapis.com/resource-id``.
        If not specified, then mandatory configuration values for
        :class:`Backend` are:

        - ``cloud.google.com/project`` - The Google Cloud project holding the
          Google Cloud KMS key for this backend.
        - ``cloudkms.googleapis.com/location`` - The location of the keyring.
        - ``cloudkms.googleapis.com/keyring`` - The name of the keyring.
        - ``cloudkms.googleapis.com/key`` - The name of the key.

        For signing keys, there is an additional mandatory value:

        - ``cloudkms.googleapis.com/version`` - The version of the signing key
          to use.

        Args:
            params (:class:`dict`): a mapping with the configuration described
                above.
        """
        self.__params = copy.deepcopy(params)
        if PARAM_VERSION not in params:
            # Assume here that it is then an encryption key.
            self.capabilities.extend([
                'encrypt',
                'encrypt:async',
                'decrypt',
                'decrypt:async'
            ])
        else:
            self.capabilities.extend([
                'sign',
                'verify',
            ])

    def symmetric(self):
        """Return the :class:`~unimatrix.ext.crypto.SymmetricKey`
        implementation for this backend.
        """
        return GoogleSymmetricKey(resource_id=self.__params[PARAM_RESOURCE_ID])\
            if PARAM_RESOURCE_ID in self.__params\
            else GoogleSymmetricKey(
                project=self.__params[PARAM_PROJECT],
                region=self.__params[PARAM_LOCATION],
                keyring=self.__params[PARAM_KEYRING],
                key=self.__params[PARAM_KEY],
            )
