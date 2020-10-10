"""The :mod:`unimatrix.ext.crypto` package provides an interface to encrypt,
decrypt, sign and verify using various cryptographic backends.


Integration with Django
=======================
The :mod:`unimatrix.ext.crypto` package is a Django application. It is
installed by adding ``unimatrix.ext.crypto`` to the Django ``INSTALLED_APPS``
setting.

The application recognizes the following settings:

- ``CRYPTO_BACKENDS` - The dictionary of cryptographic backends that are
  configured for the Django application. The keys are strings specifying the
  internal names; the values mappings of configuration options. Structure is
  documented below.

The ``CRYPTO_BACKENDS`` setting members support:

- ``backend`` - (Required) The qualified name of the Python package providing
  a cryptographic backend. Valid options are ``unimatrix.ext.crypto.lib.null``,
  ``unimatrix.ext.crypto.lib.google``, ``unimatrix.ext.crypto.lib.aes``.
- ``options`` - (Required) The options to initialize the cryptographic backend
  with. The required keys depend on the backend.


Configuration examples
----------------------
The sections below describe the various Django configurations for specific
cryptographic backends.

Google Cloud KMS
++++++++++++++++

.. code:: python

    INSTALLED_APPS = [
        "unimatrix.ext.crypto",
        # ... other apps
    ]

    CRYPTO_BACKENDS = {
        'default': {
            'backend': "unimatrix.ext.crypto.lib.google",
            'options': {
                'cloud.google.com/project': "myproject",
                'cloudkms.googleapis.com/location': "europe-west4",
                'cloudkms.googleapis.com/keyring': "mykeyring",
                'cloudkms.googleapis.com/key': "mykey",

                # This option is only required for signing backends.
                'cloudkms.googleapis.com/version': 1
            }
        }
    }
"""
from .ciphertext import CipherText
from .provider import BackendProvider


__all__ = [
    'backends'
]
backends = BackendProvider()
default_app_config = 'unimatrix.ext.crypto.apps.ApplicationConfig'
