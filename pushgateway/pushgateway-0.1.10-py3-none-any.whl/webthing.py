from urllib.parse import urljoin
from dataclasses import dataclass
import requests
import websocket
import json
import time
import threading
import logging


@dataclass
class Metadata:
    name: str
    type: str
    readonly: bool
    prop_uri: str
    prop_ws_uri: str


class WebSocketStream:

    def __init__(self, webthing_property, on_property_changed_callback):
        self.logger = logging.getLogger(webthing_property.metadata.name)
        self.webthing_property = webthing_property
        self.on_property_changed_callback = on_property_changed_callback
        self.is_running = True
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.__listen)
        self.thread.start()

    def __listen(self):
        while self.is_running:
            try:
                ws = websocket.WebSocket()
                try:
                    ws.connect(self.webthing_property.metadata.prop_ws_uri)
                    self.logger.info('websocket ' + self.webthing_property.metadata.prop_ws_uri + ' connected')

                    # set initial state (if changes are coming sporadically)
                    self.on_property_changed_callback(self.webthing_property.property)

                    while self.is_running:
                        msg = json.loads(ws.recv())
                        if msg['messageType'] == 'propertyStatus':
                            data = msg['data']
                            if self.webthing_property.metadata.name in data.keys():
                                value = data[self.webthing_property.metadata.name]
                                self.on_property_changed_callback(value)
                finally:
                    self.logger.info('websocket ' + self.webthing_property.metadata.prop_ws_uri + ' disconnected')
                    ws.close()
            except Exception as e:
                self.logger.error("error occurred consuming web socket for " + self.webthing_property.metadata.name  + " (" + self.webthing_property.metadata.prop_ws_uri + ") " + str(e))
                time.sleep(5)

    def stop(self):
        self.is_running = False
        threading.Thread.join(self.thread)


class WebthingProperty:

    def __init__(self, webthing_uri: str, webthing_property: str):
        self.logger = logging.getLogger(webthing_property)
        self.__webthing_uri = webthing_uri
        self.__webthing_property = webthing_property
        self.__metadata = None

    @property
    def metadata(self) -> Metadata:
        if self.__metadata is None:
            response = requests.get(self.__webthing_uri)
            webthing_meta = response.json()
            props = webthing_meta['properties'][self.__webthing_property]
            webthing_type = props['type']
            if 'readOnly' in props.keys():
                webthing_readonly = props['readOnly']
            else:
                webthing_readonly = False
            webthing_prop_uri = None
            for link in props['links']:
                if 'rel' in link.keys():
                    if link['rel'] == 'property':
                        webthing_prop_uri = urljoin(self.__webthing_uri, link['href'])
            webthing_prop_ws_uri = None
            for link in webthing_meta['links']:
                if 'rel' in link.keys():
                    if link['rel'] == 'property':
                        webthing_prop_uri = urljoin(self.__webthing_uri, link['href'])
                    elif link['rel'] == 'alternate':
                        webthing_prop_ws_uri = urljoin(self.__webthing_uri, link['href'])
            self.__metadata = Metadata(self.__webthing_property, webthing_type, webthing_readonly, webthing_prop_uri, webthing_prop_ws_uri)
            response.close()
            self.logger.info("meta data loaded: " + str(self.__metadata))
        return self.__metadata

    @property
    def property(self):
        response = requests.get(self.metadata.prop_uri)
        properties = response.json()
        value =  properties[self.metadata.name]
        response.close()
        return value

    @property.setter
    def property(self, value):
        try:
            body = json.dumps({ self.metadata.name: value }, indent=2)
            resp = requests.put(self.metadata.prop_uri, data=body, headers={'Content-Type': 'application/json'})
            resp.raise_for_status()
            resp.close()
        except requests.exceptions.HTTPError as err:
            self.logger.error("got error by writing " + str(value) + " using " + self.metadata.prop_uri + " reason: " + resp.text)

    def new_change_listener(self, on_changed_callback) -> WebSocketStream:
        return WebSocketStream(self, on_changed_callback)
