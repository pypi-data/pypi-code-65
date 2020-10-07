from urllib.parse import urljoin
from dataclasses import dataclass
import requests
import sseclient
import json
import threading
import logging
import time


@dataclass
class Metadata:
    name: str
    type: str
    readonly: bool
    item_uri: str
    item_changed_event_uri: str


class ServerSentEventStream:

    def __init__(self, openhab_item, on_item_changed_callback):
        self.logger = logging.getLogger(openhab_item.metadata.name)
        self.openhab_item = openhab_item
        self.on_item_changed_callback = on_item_changed_callback
        self.is_running = True
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.__listen)
        self.thread.start()

    def __listen(self):
        while self.is_running:
            try:
                self.logger.info("opening sse stream (" + self.openhab_item.metadata.item_changed_event_uri + ")")
                response = requests.get(self.openhab_item.metadata.item_changed_event_uri, stream=True)
                client = sseclient.SSEClient(response)

                # set initial state (if changes are coming sporadically)
                self.on_item_changed_callback(self.openhab_item.state)

                try:
                    for event in client.events():
                        data = json.loads(event.data)
                        payload = json.loads(data['payload'])
                        value = payload['value']
                        self.on_item_changed_callback(value)
                finally:
                    self.logger.info("closing sse stream")
                    client.close()
                    response.close()
            except Exception as e:
                self.logger.error("error occurred consuming sse for " + self.openhab_item.metadata.name + " (" + self.openhab_item.metadata.item_changed_event_uri + ") " + str(e))
                time.sleep(5)

    def stop(self):
        self.is_running = False
        threading.Thread.join(self.thread)


class OpenhabItem:

    def __init__(self, openhab_uri: str, itemname: str):
        self.logger = logging.getLogger(itemname)
        self.__openhab_uri = openhab_uri
        self.__itemname = itemname
        self.__metadata = None

    @property
    def metadata(self) -> Metadata:
        if self.__metadata is None:
            item_uri = urljoin(self.__openhab_uri, '/rest/items/' + self.__itemname)
            resp = requests.get(item_uri)
            resp.raise_for_status()
            data = json.loads(resp.text)
            type = data['type'].lower()
            readonly = False
            item_changed_event_uri = urljoin(self.__openhab_uri, '/rest/events?topics=smarthome/items/' + self.__itemname + '/statechanged')
            self.__metadata = Metadata(self.__itemname, type, readonly, item_uri, item_changed_event_uri)
            resp.close()
            self.logger.info("meta data loaded:  " + str(self.__metadata))
        return self.__metadata

    @property
    def state(self):
        try:
            resp = requests.get(self.metadata.item_uri + '/state')
            resp.raise_for_status()
            value = resp.text
            resp.close()
            self.logger.info("read " + str(value))
            return value
        except requests.exceptions.HTTPError as err:
            self.logger.info("got error by reading. reason: " + resp.text)

    @state.setter
    def state(self, value):
        uri = self.metadata.item_uri + '/state'
        try:
            self.logger.info("writing " + str(value))
            resp = requests.put(uri, data=str(value), headers={'Content-Type': 'text/plain'})
            resp.raise_for_status()
            resp.close()
        except requests.exceptions.HTTPError as err:
            self.logger.error("got error by writing " + str(value) + " using " + uri +  " reason: " + resp.text)

    def new_change_listener(self, on_changed_callback) -> ServerSentEventStream:
        return ServerSentEventStream(self, on_changed_callback)


