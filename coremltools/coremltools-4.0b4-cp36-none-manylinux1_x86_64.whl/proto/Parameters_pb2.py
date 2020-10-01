# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Parameters.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import DataStructures_pb2 as DataStructures__pb2
try:
  FeatureTypes__pb2 = DataStructures__pb2.FeatureTypes__pb2
except AttributeError:
  FeatureTypes__pb2 = DataStructures__pb2.FeatureTypes_pb2

from .DataStructures_pb2 import *

DESCRIPTOR = _descriptor.FileDescriptor(
  name='Parameters.proto',
  package='CoreML.Specification',
  syntax='proto3',
  serialized_pb=_b('\n\x10Parameters.proto\x12\x14\x43oreML.Specification\x1a\x14\x44\x61taStructures.proto\"\x99\x01\n\x0eInt64Parameter\x12\x14\n\x0c\x64\x65\x66\x61ultValue\x18\x01 \x01(\x03\x12\x31\n\x05range\x18\n \x01(\x0b\x32 .CoreML.Specification.Int64RangeH\x00\x12-\n\x03set\x18\x0b \x01(\x0b\x32\x1e.CoreML.Specification.Int64SetH\x00\x42\x0f\n\rAllowedValues\"l\n\x0f\x44oubleParameter\x12\x14\n\x0c\x64\x65\x66\x61ultValue\x18\x01 \x01(\x01\x12\x32\n\x05range\x18\n \x01(\x0b\x32!.CoreML.Specification.DoubleRangeH\x00\x42\x0f\n\rAllowedValues\"\'\n\x0fStringParameter\x12\x14\n\x0c\x64\x65\x66\x61ultValue\x18\x01 \x01(\t\"%\n\rBoolParameter\x12\x14\n\x0c\x64\x65\x66\x61ultValue\x18\x01 \x01(\x08\x42\x02H\x03P\x00\x62\x06proto3')
  ,
  dependencies=[DataStructures__pb2.DESCRIPTOR,],
  public_dependencies=[DataStructures__pb2.DESCRIPTOR,])




_INT64PARAMETER = _descriptor.Descriptor(
  name='Int64Parameter',
  full_name='CoreML.Specification.Int64Parameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='defaultValue', full_name='CoreML.Specification.Int64Parameter.defaultValue', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='range', full_name='CoreML.Specification.Int64Parameter.range', index=1,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='set', full_name='CoreML.Specification.Int64Parameter.set', index=2,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='AllowedValues', full_name='CoreML.Specification.Int64Parameter.AllowedValues',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=65,
  serialized_end=218,
)


_DOUBLEPARAMETER = _descriptor.Descriptor(
  name='DoubleParameter',
  full_name='CoreML.Specification.DoubleParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='defaultValue', full_name='CoreML.Specification.DoubleParameter.defaultValue', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='range', full_name='CoreML.Specification.DoubleParameter.range', index=1,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='AllowedValues', full_name='CoreML.Specification.DoubleParameter.AllowedValues',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=220,
  serialized_end=328,
)


_STRINGPARAMETER = _descriptor.Descriptor(
  name='StringParameter',
  full_name='CoreML.Specification.StringParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='defaultValue', full_name='CoreML.Specification.StringParameter.defaultValue', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=330,
  serialized_end=369,
)


_BOOLPARAMETER = _descriptor.Descriptor(
  name='BoolParameter',
  full_name='CoreML.Specification.BoolParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='defaultValue', full_name='CoreML.Specification.BoolParameter.defaultValue', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=371,
  serialized_end=408,
)

_INT64PARAMETER.fields_by_name['range'].message_type = DataStructures__pb2._INT64RANGE
_INT64PARAMETER.fields_by_name['set'].message_type = DataStructures__pb2._INT64SET
_INT64PARAMETER.oneofs_by_name['AllowedValues'].fields.append(
  _INT64PARAMETER.fields_by_name['range'])
_INT64PARAMETER.fields_by_name['range'].containing_oneof = _INT64PARAMETER.oneofs_by_name['AllowedValues']
_INT64PARAMETER.oneofs_by_name['AllowedValues'].fields.append(
  _INT64PARAMETER.fields_by_name['set'])
_INT64PARAMETER.fields_by_name['set'].containing_oneof = _INT64PARAMETER.oneofs_by_name['AllowedValues']
_DOUBLEPARAMETER.fields_by_name['range'].message_type = DataStructures__pb2._DOUBLERANGE
_DOUBLEPARAMETER.oneofs_by_name['AllowedValues'].fields.append(
  _DOUBLEPARAMETER.fields_by_name['range'])
_DOUBLEPARAMETER.fields_by_name['range'].containing_oneof = _DOUBLEPARAMETER.oneofs_by_name['AllowedValues']
DESCRIPTOR.message_types_by_name['Int64Parameter'] = _INT64PARAMETER
DESCRIPTOR.message_types_by_name['DoubleParameter'] = _DOUBLEPARAMETER
DESCRIPTOR.message_types_by_name['StringParameter'] = _STRINGPARAMETER
DESCRIPTOR.message_types_by_name['BoolParameter'] = _BOOLPARAMETER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Int64Parameter = _reflection.GeneratedProtocolMessageType('Int64Parameter', (_message.Message,), dict(
  DESCRIPTOR = _INT64PARAMETER,
  __module__ = 'Parameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.Int64Parameter)
  ))
_sym_db.RegisterMessage(Int64Parameter)

DoubleParameter = _reflection.GeneratedProtocolMessageType('DoubleParameter', (_message.Message,), dict(
  DESCRIPTOR = _DOUBLEPARAMETER,
  __module__ = 'Parameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.DoubleParameter)
  ))
_sym_db.RegisterMessage(DoubleParameter)

StringParameter = _reflection.GeneratedProtocolMessageType('StringParameter', (_message.Message,), dict(
  DESCRIPTOR = _STRINGPARAMETER,
  __module__ = 'Parameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.StringParameter)
  ))
_sym_db.RegisterMessage(StringParameter)

BoolParameter = _reflection.GeneratedProtocolMessageType('BoolParameter', (_message.Message,), dict(
  DESCRIPTOR = _BOOLPARAMETER,
  __module__ = 'Parameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.BoolParameter)
  ))
_sym_db.RegisterMessage(BoolParameter)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('H\003'))
# @@protoc_insertion_point(module_scope)
