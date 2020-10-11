# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drf_firebase_token_auth', 'drf_firebase_token_auth.migrations']

package_data = \
{'': ['*']}

install_requires = \
['firebase-admin>=4.4.0,<5.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

setup_kwargs = {
    'name': 'drf-firebase-token-auth',
    'version': '0.2.1',
    'description': 'Firebase token authentication for Django Rest Framework',
    'long_description': "Firebase Token Authentication for Django Rest Framework\n=======================================================\n\nInspired by `garyburgmann/drf-firebase-auth <https://github.com/garyburgmann/drf-firebase-auth>`_\nand based on `Rest Framework's TokenAuthentication <https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication>`_,\n``drf-firebase-token-auth`` should be just what you need to enable client\nauthentication using `Firebase Authentication <https://firebase.google.com/docs/auth>`_.\n\nHow Does It Work\n----------------\n#. For each REST request, a Firebase ID Token is extracted from the\n   Authorization header.\n\n#. The ID Token is verified against Firebase.\n\n#. If the Firebase user is already known (A record with the corresponding UID\n   exists in the `FirebaseUser` table), then the corresponding local `User` is\n   successfully authenticated.\n\n#. Otherwise, the unfamiliar Firebase user is attempted to be matched against\n   a local `User` record by `email` or `username`. If no match exists,\n   then a new `User` is created. Its `username` is assigned either to the\n   Firebase email or UID (in case an email is not available).\n   Finally, the newly created local `User` is successfully authenticated.\n\nInstallation\n------------\n#. Install the pip package:\n\n   .. code-block:: bash\n\n    $ pip install drf-firebase-token-auth\n\n#. Add the application to your project's ``INSTALLED_APPS``:\n\n   .. code-block:: python\n\n    # settings.py\n    INSTALLED_APS = [\n        ...\n        'drf-firebase-token-auth',\n    ]\n\n#. Add ``FirebaseTokenAuthentication`` to Rest Framework's list of default\n   authentication classes:\n\n   .. code-block:: python\n\n    # settings.py\n    REST_FRAMEWORK = {\n        ...\n        'DEFAULT_AUTHENTICATION_CLASSES': [\n            ...\n            'drf_firebase_token_auth.authentication.FirebaseTokenAuthentication',\n        ]\n    }\n\n\n   *Note*: It's perfectly fine to keep other authentication classes as well.\n   For example, you may want to keep ``rest_framework.authentication.SessionAuthentication``\n   to allow access to the browsable API for local users with password.\n\n#. Configure the application:\n\n   .. code-block:: python\n\n    # settings.py\n    DRF_FIREBASE_TOKEN_AUTH = {\n        # REQUIRED SETTINGS:\n\n        # Path to JSON file with firebase secrets\n        'FIREBASE_SERVICE_ACCOUNT_KEY_FILE_PATH': r'/mnt/c/Users/ronhe/Google Drive/ProgramsData/WizWot/paywiz-c4b4f-firebase-adminsdk-ekbjf-9b7776879a.json',\n\n\n        # OPTIONAL SETTINGS:\n\n        # Create new matching local user in db, if no match found.\n        # Otherwise, Firebase user not matching a local user will not\n        # be authenticated.\n        'SHOULD_CREATE_LOCAL_USER': True,\n\n        # Authentication header token keyword (usually 'Token', 'JWT' or 'Bearer')\n        'AUTH_HEADER_TOKEN_KEYWORD': 'Token',\n\n        # Verify that Firebase token has not been revoked.\n        'VERIFY_FIREBASE_TOKEN_NOT_REVOKED': True,\n\n        # Require that Firebase user email_verified is True.\n        # If set to True, non verified email addresses from Firebase are ignored.\n        'IGNORE_FIREBASE_UNVERIFIED_EMAIL': True,\n    }\n\n#. Migrate:\n\n   .. code-block:: bash\n\n    $ python manage.py migrate drf-firebase-token-auth\n\n#. Have your clients adding ``Token <Firebase ID Token>`` in the\n   Authorization Header of their REST requests.",
    'author': 'Ron Heimann',
    'author_email': 'ron.heimann@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ronhe/drf-firebase-token-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
