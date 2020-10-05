"""
Serialize and Deserialize in XML format.
"""

from typing import Any, Type

import dicttoxml
import xmltodict

from .core import T
from .de import Deserializer, from_dict
from .se import Serializer, asdict


class XmlSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, **opts) -> str:
        return dicttoxml.dicttoxml(asdict(obj), **opts).decode('utf-8')


class XmlDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return xmltodict.parse(s, postprocessor=cast)


def to_xml(obj: Any, se=XmlSerializer, attr_type=False, **opts) -> str:
    return se.serialize(obj, attr_type=attr_type, **opts)


def from_xml(c: Type[T], s: str, de=XmlDeserializer, **opts) -> T:
    return from_dict(c, de.deserialize(s, **opts)['root'])


def cast(path, key, value):
    if isinstance(value, dict) and '@type' in value:
        print('@type', value['@type'])
        if value['@type'] == 'int':
            return key, int(value['#text'])
        elif value['@type'] == 'str':
            return key, value['#text']
        elif value['@type'] == 'float':
            return key, float(value['#text'])
        elif value['@type'] == 'bool':
            return key, bool(value['#text'])

    print("casting", path, key, value)
    return (key, value)
