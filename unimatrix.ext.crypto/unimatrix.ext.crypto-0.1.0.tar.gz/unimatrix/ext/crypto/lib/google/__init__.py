"""Implements the :mod:`unimatrix.ext.crypto` interface for Google Cloud
KMS.
"""
from .decrypter import GoogleDecrypter
from .encrypter import GoogleEncrypter
from .signer import GoogleSigner


Decrypter = GoogleDecrypter
Encrypter = GoogleEncrypter
Signer = GoogleSigner
