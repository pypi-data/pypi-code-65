import json
from abc import ABC, abstractmethod
from aito.schema import AitoTableSchema, AitoAnalyzerSchema, AitoDelimiterAnalyzerSchema
import logging
import pandas as pd
from jsonschema import Draft7Validator, validate, Draft6Validator, Draft4Validator, Draft3Validator
from typing import TypeVar, Generic, Optional, overload


# class SomeType:
#     def __init__(self):
#         self.some = 'type'
#
#
# class AnotherType:
#     def __init__(self):
#         self.another = 'type'
#
#
# NewType = TypeVar('NewType', bound=SomeType)
#
#

class C1(ABC):
    @property
    @abstractmethod
    def first(self) -> str:
        pass

    def print(self):
        print(self.first)

C3 = type('C3', (C1,), {'first': 3, 'second': 6})
C4 = type('C3', (C1,), {'first': 4, 'second': 8})

c = C3()
c.print()




# validate(
#     instance={'third': 1},
#     schema={
#         'type': 'object',
#         'properties': {
#             'first': {'type': 'string'}, 'third': {}, 'second': {}
#         },
#         'oneOf': [
#             {'required': ['first']},
#             {'required': ['second']}
#         ],
#         'additionalProperties': False
#     }
# )

# logging.basicConfig(level=logging.DEBUG)
# instance = {
#     "type": "table",
#     "columns": {
#         "col1": {"type": "Text", "analyzer": {"type": "delimiter"}}
#     }
# }

# validator = Draft7Validator(AitoTableSchema.json_schema)
# for error in validator.iter_errors(instance):
#     print(error)


# schema = AitoTableSchema.from_deserialized_object({
#     "type": "table",
#     "columns": {
#         "col1": {
#             "type": "Text",
#             "analyzer": {'delimiter': ':', 'trimWhiteSpace': True, 'type': 'delimiter'}
#         }
#     }
# })
#