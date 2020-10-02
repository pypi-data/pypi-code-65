import requests
import json
import logging

LOG = logging.getLogger(__name__)


class DataEvent(object):
    def __init__(self, source, event_name, value, data_type, is_callable):
        self.source = str(source)
        self.event_name = str(event_name)
        self.value = str(value)
        self.data_type = str(data_type)
        self.is_callable = is_callable
        self.process_name = 'unset'

    def to_dict(self):
        return {
            'source': self.source,
            'event_name': self.event_name,
            'value': self.value,
            'is_callable': self.is_callable,
            'data_type': self.data_type,
            'process_name': self.process_name
        }


class DataManagerAdapter(object):
    def notify(self, data_event):
        pass


class DataManager(object):
    def __init__(self, api_uri):
        self._api_uri = api_uri

    def notify(self, data_event):
        try:
            data = data_event.to_dict()
            headers = {
                'Content-Type': 'application/json'
            }
            requests.post(self._api_uri, data=json.dumps(data), headers=headers)
        except Exception as exc:
            LOG.exception(str(exc))
