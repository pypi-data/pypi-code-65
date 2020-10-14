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

import builtins
from datetime import datetime
from typing import Union, Dict, Any

__all__ = "CloudEvent",


class CloudEvent:

    __slots__ = "_attributes", "_data", "_has_binary_data"

    NOW = "now"

    def __init__(self, *,
                 type: str,
                 source: str,
                 id: str,
                 specversion="1.0",
                 subject = "",
                 data: Union[str, bytes, Dict[str, Any], list, str, int, float, bool, None] = None,
                 datacontenttype = "",
                 dataschema = "",
                 time: Union[str, datetime] = "",
                 **attributes
                 ):
        attrs = {
            "type": type,
            "source": source,
            "id": id,
            "specversion": specversion,
        }

        if isinstance(time, datetime):
            # if the time has timezone information, convert it directly to isoformat
            if time.tzinfo is not None and time.tzinfo.utcoffset(time) is not None:
                time = time.isoformat()
            else:
                # time is naive, assume it is UTC
                time = "%sZ" % time.isoformat()
        elif isinstance(time, str):
            pass
        elif time:
            raise TypeError("time must be either a string or a datetime.datetime, but it is: %s"
                            % builtins.type(time))

        if subject: attrs["subject"] = subject
        if datacontenttype: attrs["datacontenttype"] = datacontenttype
        if dataschema: attrs["dataschema"] = dataschema
        if time: attrs["time"] = time

        # TODO: validation

        self._attributes = attrs
        self._data = data
        self._attributes.update(attributes)
        self._has_binary_data = isinstance(data, bytes)

    type = property(lambda self: self._attributes.get("type"))
    source = property(lambda self: self._attributes.get("source"))
    id = property(lambda self: self._attributes.get("id"))
    specversion = property(lambda self: self._attributes.get("specversion"))
    data = property(lambda self: self._data)
    datacontenttype = property(lambda self: self._attributes.get("datacontenttype"))
    dataschema = property(lambda self: self._attributes.get("dataschema"))
    subject = property(lambda self: self._attributes.get("subject"))
    time = property(lambda self: self._attributes.get("time"))

    def attribute(self, name):
        return self._attributes.get(name)

    def __str__(self):
        return str(self._attributes)

    def __repr__(self):
        return repr(self._attributes)

    def __eq__(self, other):
        if not isinstance(other, CloudEvent):
            return False
        return self._attributes == other._attributes \
            and self._data == other._data

    def __hash__(self):
        return hash(self._attributes, self._data)