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


__all__ = "Avro",


def _make_avro_codec():
    # CloudEvents Avro schema was taken from: https://raw.githubusercontent.com/cloudevents/spec/v1.0/spec.avsc
    # (c) CloudEvents contributors.
    schema_text = '''
    {
      "namespace":"io.cloudevents",
      "type":"record",
      "name":"CloudEvent",
      "version":"1.0",
      "doc":"Avro Event Format for CloudEvents",
      "fields":[
        {
          "name":"attribute",
          "type":{
            "type":"map",
            "values":[
              "null",
              "boolean",
              "int",
              "string",
              "bytes"
            ]
          }
        },
        {
          "name": "data",
          "type": [
            "bytes",
            "null",
            "boolean",
            {
              "type": "map",
              "values": [
                "null",
                "boolean",
                {
                  "type": "record",
                  "name": "CloudEventData",
                  "doc": "Representation of a JSON Value",
                  "fields": [
                    {
                      "name": "value",
                      "type": {
                        "type": "map",
                        "values": [
                          "null",
                          "boolean",
                          { "type": "map", "values": "CloudEventData" },
                          { "type": "array", "items": "CloudEventData" },
                          "double",
                          "string"
                        ]
                      }
                    }
                  ]
                },
                "double",
                "string"
              ]
            },
            { "type": "array", "items": "CloudEventData" },
            "double",
            "string"
          ]
        }
      ]
    }
    '''

    try:
        import avro.schema
        from avro.datafile import DataFileWriter
        from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
    except ImportError:
        return None

    from io import BytesIO
    from .cloudevents import CloudEvent

    schema = avro.schema.parse(schema_text)
    writer = DatumWriter(schema)
    reader = DatumReader(schema)

    class _Avro:

        @classmethod
        def encode_to(cls, event: CloudEvent, file):
            encoder = BinaryEncoder(file)
            writer.write({"attribute": event._attributes, "data": event._data}, encoder)

        @classmethod
        def encode(cls, event: CloudEvent):
            with BytesIO() as bio:
                cls.encode_to(event, bio)
                return bio.getvalue()

        @classmethod
        def decode_from(cls, file) -> CloudEvent:
            decoder = BinaryDecoder(file)
            raw_event = reader.read(decoder)
            attributes = raw_event.get("attribute") or {}
            attributes["data"] = raw_event.get("data") or None
            return CloudEvent(**attributes)

        @classmethod
        def decode(cls, encoded_event: bytes) -> CloudEvent:
            with BytesIO(encoded_event) as f:
                return cls.decode_from(f)

    return _Avro


Avro = _make_avro_codec()