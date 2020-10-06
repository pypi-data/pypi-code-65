from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes
from builtins import str
from builtins import int
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from future import standard_library
standard_library.install_aliases()
from builtins import object
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from google.cloud.pubsub_v1.subscriber.message import Message


class SubscriberMessage(object):
    def __init__(self, *args           ,
                 **kwargs                )        :
        if 'google_cloud_message' in kwargs: google_cloud_message = kwargs['google_cloud_message']; del kwargs['google_cloud_message']
        else: google_cloud_message =  None
        if google_cloud_message:
            self._message = google_cloud_message
            return
        self._message = Message(*args, **kwargs)

    @staticmethod
    def from_google_cloud(message         )                       :
        return SubscriberMessage(google_cloud_message=message)

    @property
    def google_cloud_message(self)           :
        return self._message

    @property
    def message_id(self)       :  # indirects to a Google protobuff field
        return str(self._message.message_id)

    def __repr__(self)       :
        return repr(self._message)

    @property
    def attributes(self)       :  # Google .ScalarMapContainer
        return self._message.attributes

    @property
    def data(self)         :
        return bytes(self._message.data)

    @property
    def publish_time(self)                     :
        published                    = self._message.publish_time
        return published

    @property
    def ordering_key(self)       :
        return str(self._message.ordering_key)

    @property
    def size(self)       :
        return int(self._message.size)

    @property
    def ack_id(self)       :
        return str(self._message.ack_id)

    @property
    def delivery_attempt(self)                 :
        if self._message.delivery_attempt:
            return int(self._message.delivery_attempt)
        return None

    def ack(self)        :
        self._message.ack()

    def drop(self)        :
        self._message.drop()

    def modify_ack_deadline(self, seconds     )        :
        self._message.modify_ack_deadline(seconds)

    def nack(self)        :
        self._message.nack()
