from urllib.parse import urljoin
from dataclasses import dataclass
import requests
import websocket
import json
import time
import threading


@dataclass
class Metadata:
    name: str
    type: str
    readonly: bool
    prop_uri: str
    prop_ws_uri: str


class WebSocketStream:

    def __init__(self, metadata: Metadata, on_property_changed_callback):
        self.metadata = metadata
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
                    ws.connect(self.metadata.prop_ws_uri)
                    print('webthing property ' + self.metadata.name + ' websocket ' + self.metadata.prop_ws_uri + ' connected')
                    while self.is_running:
                        msg = json.loads(ws.recv())
                        if msg['messageType'] == 'propertyStatus':
                            data = msg['data']
                            if self.metadata.name in data.keys():
                                value = data[self.metadata.name]
                                print("webthing property " + self.metadata.name + " has been updated to " + str(value))
                                self.on_property_changed_callback(value)
                finally:
                    print('websocket ' + self.metadata.prop_ws_uri + ' disconnected')
                    ws.close()
            except Exception as e:
                print("error occurred consuming web socket for " + self.metadata.name + " " + str(e))
                time.sleep(5)

    def stop(self):
        self.is_running = False
        threading.Thread.join(self.thread)


class WebthingProperty:

    def __init__(self, webthing_uri: str, webthing_property: str):
        self.__webthing_uri = webthing_uri
        self.__webthing_property = webthing_property
        self.__metadata = None

    def metadata(self) -> Metadata:
        if self.__metadata is None:
            print('webthing property ' + self.__webthing_property + ' fetching meta data')
            webthing_meta = requests.get(self.__webthing_uri).json()
            webthing_type = webthing_meta['properties'][self.__webthing_property]['type']
            webthing_readonly = webthing_meta['properties'][self.__webthing_property]['readOnly']
            webthing_prop_uri = None
            webthing_prop_ws_uri = None
            for link in webthing_meta['links']:
                if 'rel' in link.keys():
                    if link['rel'] == 'properties':
                        webthing_prop_uri = urljoin(self.__webthing_uri, link['href'])
                    elif link['rel'] == 'alternate':
                        webthing_prop_ws_uri = urljoin(self.__webthing_uri, link['href'])
            self.__metadata = Metadata(self.__webthing_property, webthing_type, webthing_readonly, webthing_prop_uri, webthing_prop_ws_uri)
            print('webthing property ' + self.__webthing_property + " meta data loaded (type: " + self.__metadata.type + ", readonly: " + str(self.__metadata.readonly) + ")")
        return self.__metadata

    @property
    def name(self) -> str:
        return self.metadata().name

    @property
    def type(self) -> str:
        return self.metadata().type

    @property
    def writeable(self) -> bool:
        return not self.metadata().readonly

    @property
    def property(self):
        properties = requests.get(self.metadata().prop_uri).json()
        value =  properties[self.metadata().name]
        print("webthing property " + self.metadata().name + " read " + str(value))
        return value

    @property.setter
    def property(self, value):
        try:
            print("writing webthing property " + self.name + " with " + str(value))
            body = json.dumps({ self.metadata().name: value }, indent=2)
            resp = requests.put(self.metadata().prop_uri, data=body, headers={'Content-Type': 'application/json'})
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("got error by webthing property " + self.name + " = " + str(value) + " reason: " + resp.text)

    def new_change_listener(self, on_changed_callback) -> WebSocketStream:
        return WebSocketStream(self.metadata(), on_changed_callback)
