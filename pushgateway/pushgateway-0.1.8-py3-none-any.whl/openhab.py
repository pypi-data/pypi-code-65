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

    def __init__(self, item_event_uri: str, itemname: str, on_item_changed_callback):
        self.itemname = itemname
        self.on_item_changed_callback = on_item_changed_callback
        self.item_event_uri = item_event_uri
        self.is_running = True
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.__listen)
        self.thread.start()

    def __listen(self):
        while self.is_running:
            try:
                logging.info("opening openhab item " + self.itemname + " sse stream (" + self.item_event_uri + ")")
                response = requests.get(self.item_event_uri, stream=True)
                client = sseclient.SSEClient(response)
                try:
                    for event in client.events():
                        data = json.loads(event.data)
                        payload = json.loads(data['payload'])
                        value = payload['value']
                        self.on_item_changed_callback(value)
                finally:
                    logging.info("closing openhab item " + self.itemname + " sse stream")
                    client.close()
                    response.close()
            except Exception as e:
                logging.error("error occurred consuming sse for " + self.itemname + " (" + self.item_event_uri + ") " + str(e))
                time.sleep(5)

    def stop(self):
        self.is_running = False
        threading.Thread.join(self.thread)


class OpenhabItem:

    def __init__(self, openhab_uri: str, itemname: str):
        self.openhab_uri = openhab_uri
        self.itemname = itemname
        self.__metadata = None

    def metadata(self) -> Metadata:
        if self.__metadata is None:
            item_uri = urljoin(self.openhab_uri, '/rest/items/' + self.itemname)
            resp = requests.get(item_uri)
            resp.raise_for_status()
            data = json.loads(resp.text)
            type = data['type'].lower()
            readonly = False
            item_changed_event_uri = urljoin(self.openhab_uri, '/rest/events?topics=smarthome/items/' + self.itemname + '/statechanged')
            self.__metadata = Metadata(self.name, type, readonly, item_uri, item_changed_event_uri)
            resp.close()
            logging.info('openhab item ' + self.name + " meta data loaded:  " + str(self.__metadata))
        return self.__metadata

    @property
    def type(self) -> str:
        return self.metadata().type

    @property
    def writeable(self) -> bool:
        return not self.metadata().readonly

    @property
    def name(self) -> str:
        return self.itemname

    @property
    def state(self):
        try:
            resp = requests.get(self.metadata().item_uri + '/state')
            resp.raise_for_status()
            value = resp.text
            resp.close()
            logging.info("openhab item " + self.itemname + " read " + str(value))
            return value
        except requests.exceptions.HTTPError as err:
            logging.info("got error by reading openhab item " + self.itemname + " reason: " + resp.text)

    @state.setter
    def state(self, value):
        uri = self.metadata().item_uri + '/state'
        try:
            logging.info("writing openhab item " + self.itemname + " with " + str(value))
            resp = requests.put(uri, data=str(value), headers={'Content-Type': 'text/plain'})
            resp.raise_for_status()
            resp.close()
        except requests.exceptions.HTTPError as err:
            logging.error("got error by writing openhab item " + self.itemname + " = " + str(value) + " using " + uri +  " reason: " + resp.text)

    def new_change_listener(self, on_changed_callback) -> ServerSentEventStream:
        return ServerSentEventStream(self.metadata().item_changed_event_uri, self.itemname, on_changed_callback)


