from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from future import standard_library
standard_library.install_aliases()
from builtins import object
import io
import json
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from gcloud.rest.auth import SyncSession  # pylint: disable=no-name-in-module
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module
from gcloud.rest.pubsub.utils import PubsubMessage

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session  # type: ignore[no-redef]


API_ROOT = 'https://pubsub.googleapis.com/v1'
SCOPES = [
    'https://www.googleapis.com/auth/pubsub',
]


PUBSUB_EMULATOR_HOST = os.environ.get('PUBSUB_EMULATOR_HOST')
if PUBSUB_EMULATOR_HOST:
    API_ROOT = 'http://{}/v1'.format((PUBSUB_EMULATOR_HOST))

log = logging.getLogger(__name__)


class PublisherClient(object):
    def __init__(self, **_3to2kwargs)        :
        if 'token' in _3to2kwargs: token = _3to2kwargs['token']; del _3to2kwargs['token']
        else: token =  None
        if 'session' in _3to2kwargs: session = _3to2kwargs['session']; del _3to2kwargs['session']
        else: session =  None
        if 'service_file' in _3to2kwargs: service_file = _3to2kwargs['service_file']; del _3to2kwargs['service_file']
        else: service_file =  None
        self.session = SyncSession(session)
        self.token = token or Token(service_file=service_file, scopes=SCOPES,
                                    session=self.session.session)

    @staticmethod
    def project_path(project     )       :
        return 'projects/{}'.format((project))

    @classmethod
    def subscription_path(cls, project     , subscription     )       :
        return '{}/subscriptions/{}'.format((cls.project_path(project)), (subscription))

    @classmethod
    def topic_path(cls, project     , topic     )       :
        return '{}/topics/{}'.format((cls.project_path(project)), (topic))

    def _headers(self)                  :
        if PUBSUB_EMULATOR_HOST:
            return {}

        token = self.token.get()
        return {
            'Authorization': 'Bearer {}'.format((token)),
        }

    # TODO: implement that various methods from:
    # https://github.com/googleapis/python-pubsub/blob/master/google/cloud/pubsub_v1/gapic/publisher_client.py

    # https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.topics/publish
    def publish(self, topic     , messages                     ,
                      session                    = None,
                      timeout      = 10)                  :
        if not messages:
            return {}

        url = '{}/{}:publish'.format((API_ROOT), (topic))

        body = {'messages': [m.to_repr() for m in messages]}
        payload = json.dumps(body).encode('utf-8')

        headers = self._headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=payload, headers=headers,
                            timeout=timeout)
        data                 = resp.json()
        return data

    def close(self)        :
        self.session.close()

    def __enter__(self)                     :
        return self

    def __exit__(self, *args     )        :
        self.close()
