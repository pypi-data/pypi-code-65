from pushgateway.config import load_config
from pushgateway.webthing import WebthingProperty
from pushgateway.openhab import OpenhabItem
import time
import threading
import logging


class WebThingPropertyToOpenhabItemLink:

    def __init__(self, webthing_property: WebthingProperty, openhab_item: OpenhabItem):
        self.webthing_property = webthing_property
        self.openhab_item = openhab_item
        self.cached_value = None

    def start(self):
        threading.Thread(target=self.__listen).start()

    def __listen(self):
        while True:
            try:
                # listen for values to forwards
                stream = self.webthing_property.new_change_listener(self.__on_changed_callback)
                stream.start()
                time.sleep(10 * 60)
                stream.stop()
            except Exception as e:
                logging.error("error occurred for webthing " + self.webthing_property.metadata.name + ": "+ str(e))
                time.sleep(10)

    def __on_changed_callback(self, new_value):
        item_value = self.__convert(new_value)
        if self.cached_value != item_value:
            self.cached_value = item_value
            self.openhab_item.state = item_value

    def __convert(self, property_value):
        if self.webthing_property.metadata.type == 'boolean':
            if property_value:
                return "ON"
            else:
                return "OFF"
        else:
            return property_value



class OpenhabItemToWebThingPropertyLink:

    def __init__(self, webthing_property: WebthingProperty, openhab_item: OpenhabItem):
        self.webthing_property = webthing_property
        self.openhab_item = openhab_item
        self.cached_value = None

    def start(self):
        threading.Thread(target=self.__listen).start()

    def __listen(self):
        while True:
            try:
                # listen for values to forwards
                stream = self.openhab_item.new_change_listener(self.__on_changed_callback)
                stream.start()
                time.sleep(10 * 60)
                stream.stop()
            except Exception as e:
                logging.error("error occurred for openhab " + self.webthing_property.metadata.name + ": "+ str(e))
                time.sleep(10)

    def __on_changed_callback(self, new_value):
        property_value = self.__convert(new_value)
        if self.cached_value != property_value:
            self.cached_value = property_value
            self.webthing_property.property = property_value

    def __convert(self, value):
        source_type = self.openhab_item.metadata.type
        target_type = self.webthing_property.metadata.type
        if source_type == 'switch':
            return value == 'ON'
        elif target_type == 'number':
            return float(value)
        elif  target_type == 'integer':
            return int(value)
        else:
            return value


class Link:

    def __init__(self, webthing_uri: str, webthing_property: str, openhab_uri: str, itemname: str):
        self.webthing_property = WebthingProperty(webthing_uri, webthing_property)
        self.openhab_item = OpenhabItem(openhab_uri, itemname)
        if self.webthing_property.metadata.readonly:
            logging.info("Backward link openhab item " + self.openhab_item.metadata.name + " <- webthing property " + self.webthing_property.metadata.name + " created")
        else:
            logging.info("Forward  Link openhab item " + self.openhab_item.metadata.name + " -> webthing property " + self.webthing_property.metadata.name + " created")

    def start(self):
        threading.Thread(target=self.__listen).start()

    def __listen(self):
        if self.webthing_property.metadata.readonly:
            webthing_to_openhab_link = WebThingPropertyToOpenhabItemLink(self.webthing_property, self.openhab_item)
            webthing_to_openhab_link.start()
        else:
            openhab_to_webthing_link = OpenhabItemToWebThingPropertyLink(self.webthing_property, self.openhab_item)
            openhab_to_webthing_link.start()

        while True:
            time.sleep(10)


def run(filename: str):
    configs = load_config(filename)
    logging.info("config file " + filename + " loaded. " + str(len(configs)) + " entries found")
    for config in configs:
        Link(config.webthing_root_uri, config.webthing_property_name, config.openhab_root_uri, config.openhab_item_name).start()

    while True:
        time.sleep(60)
