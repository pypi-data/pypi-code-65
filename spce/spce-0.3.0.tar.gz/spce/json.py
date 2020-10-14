# Copyright 2020 Scale Plan Yazılım A.Ş.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from base64 import b64encode, b64decode
from typing import Union, Iterable

from .cloudevents import CloudEvent

__all__ = "Json",


class Json:

    _ENCODER = json.JSONEncoder()

    @classmethod
    def encode(cls, event: Union[CloudEvent, Iterable[CloudEvent]]) -> str:
        if isinstance(event, Iterable):
            encoded = [cls.encode(e) for e in event]
            return "[%s]" % ",".join(encoded)
        elif isinstance(event, CloudEvent):
            kvs = []
            encoder = cls._ENCODER
            for attr, value in event._attributes.items():
                if value:
                    kvs.append('"%s":%s' % (attr, encoder.encode(value)))
            if event._data:
                if event._has_binary_data:
                    kvs.append('"data_base64":%s' % encoder.encode(b64encode(event._data).decode()))
                else:
                    kvs.append('"data":%s' % encoder.encode(event._data))
            return "{%s}" % ",".join(kvs)
        else:
            raise TypeError("JSON.encode cannot encode %s" % type(event))

    @classmethod
    def decode(cls, text: str) -> Union[CloudEvent, Iterable[CloudEvent]]:
        d = json.loads(text)
        if isinstance(d, dict):
            return CloudEvent(**cls._normalize_data(d))
        elif isinstance(d, Iterable):
            return [CloudEvent(**cls._normalize_data(it)) for it in d]
        else:
            raise TypeError("JSON.decode cannot decode %s" % type(d))

    @classmethod
    def _normalize_data(cls, d: dict) -> dict:
        if "data_base64" in d:
            d["data"] = b64decode(d["data_base64"])
            del d["data_base64"]
        return d
