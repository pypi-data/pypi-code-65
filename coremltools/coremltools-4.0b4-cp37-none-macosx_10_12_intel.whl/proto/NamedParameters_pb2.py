# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: NamedParameters.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='NamedParameters.proto',
  package='CoreML.Specification',
  syntax='proto3',
  serialized_pb=_b('\n\x15NamedParameters.proto\x12\x14\x43oreML.Specification\"0\n\nInt32Range\x12\x10\n\x08minValue\x18\x01 \x01(\x05\x12\x10\n\x08maxValue\x18\x02 \x01(\x05\"\x1a\n\x08Int32Set\x12\x0e\n\x06values\x18\x01 \x03(\x05\"0\n\nFloatRange\x12\x10\n\x08minValue\x18\x01 \x01(\x02\x12\x10\n\x08maxValue\x18\x02 \x01(\x02\"\x99\x01\n\x0eInt32Parameter\x12\x14\n\x0c\x64\x65\x66\x61ultValue\x18\x01 \x01(\x05\x12\x31\n\x05range\x18\n \x01(\x0b\x32 .CoreML.Specification.Int32RangeH\x00\x12-\n\x03set\x18\x0b \x01(\x0b\x32\x1e.CoreML.Specification.Int32SetH\x00\x42\x0f\n\rAllowedValues\"j\n\x0e\x46loatParameter\x12\x14\n\x0c\x64\x65\x66\x61ultValue\x18\x01 \x01(\x02\x12\x31\n\x05range\x18\n \x01(\x0b\x32 .CoreML.Specification.FloatRangeH\x00\x42\x0f\n\rAllowedValues\"\x93\x01\n\tParameter\x12>\n\x0eint32Parameter\x18\x01 \x01(\x0b\x32$.CoreML.Specification.Int32ParameterH\x00\x12>\n\x0e\x66loatParameter\x18\x02 \x01(\x0b\x32$.CoreML.Specification.FloatParameterH\x00\x42\x06\n\x04Type\"l\n\x0eNamedParameter\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x18\n\x10shortDescription\x18\x02 \x01(\t\x12\x32\n\tparameter\x18\x03 \x01(\x0b\x32\x1f.CoreML.Specification.ParameterB\x02H\x03\x62\x06proto3')
)




_INT32RANGE = _descriptor.Descriptor(
  name='Int32Range',
  full_name='CoreML.Specification.Int32Range',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='minValue', full_name='CoreML.Specification.Int32Range.minValue', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='maxValue', full_name='CoreML.Specification.Int32Range.maxValue', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=47,
  serialized_end=95,
)


_INT32SET = _descriptor.Descriptor(
  name='Int32Set',
  full_name='CoreML.Specification.Int32Set',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='CoreML.Specification.Int32Set.values', index=0,
      number=1, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=97,
  serialized_end=123,
)


_FLOATRANGE = _descriptor.Descriptor(
  name='FloatRange',
  full_name='CoreML.Specification.FloatRange',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='minValue', full_name='CoreML.Specification.FloatRange.minValue', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='maxValue', full_name='CoreML.Specification.FloatRange.maxValue', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=125,
  serialized_end=173,
)


_INT32PARAMETER = _descriptor.Descriptor(
  name='Int32Parameter',
  full_name='CoreML.Specification.Int32Parameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='defaultValue', full_name='CoreML.Specification.Int32Parameter.defaultValue', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='range', full_name='CoreML.Specification.Int32Parameter.range', index=1,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='set', full_name='CoreML.Specification.Int32Parameter.set', index=2,
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
      name='AllowedValues', full_name='CoreML.Specification.Int32Parameter.AllowedValues',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=176,
  serialized_end=329,
)


_FLOATPARAMETER = _descriptor.Descriptor(
  name='FloatParameter',
  full_name='CoreML.Specification.FloatParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='defaultValue', full_name='CoreML.Specification.FloatParameter.defaultValue', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='range', full_name='CoreML.Specification.FloatParameter.range', index=1,
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
      name='AllowedValues', full_name='CoreML.Specification.FloatParameter.AllowedValues',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=331,
  serialized_end=437,
)


_PARAMETER = _descriptor.Descriptor(
  name='Parameter',
  full_name='CoreML.Specification.Parameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='int32Parameter', full_name='CoreML.Specification.Parameter.int32Parameter', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='floatParameter', full_name='CoreML.Specification.Parameter.floatParameter', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
      name='Type', full_name='CoreML.Specification.Parameter.Type',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=440,
  serialized_end=587,
)


_NAMEDPARAMETER = _descriptor.Descriptor(
  name='NamedParameter',
  full_name='CoreML.Specification.NamedParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='CoreML.Specification.NamedParameter.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shortDescription', full_name='CoreML.Specification.NamedParameter.shortDescription', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='parameter', full_name='CoreML.Specification.NamedParameter.parameter', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
  ],
  serialized_start=589,
  serialized_end=697,
)

_INT32PARAMETER.fields_by_name['range'].message_type = _INT32RANGE
_INT32PARAMETER.fields_by_name['set'].message_type = _INT32SET
_INT32PARAMETER.oneofs_by_name['AllowedValues'].fields.append(
  _INT32PARAMETER.fields_by_name['range'])
_INT32PARAMETER.fields_by_name['range'].containing_oneof = _INT32PARAMETER.oneofs_by_name['AllowedValues']
_INT32PARAMETER.oneofs_by_name['AllowedValues'].fields.append(
  _INT32PARAMETER.fields_by_name['set'])
_INT32PARAMETER.fields_by_name['set'].containing_oneof = _INT32PARAMETER.oneofs_by_name['AllowedValues']
_FLOATPARAMETER.fields_by_name['range'].message_type = _FLOATRANGE
_FLOATPARAMETER.oneofs_by_name['AllowedValues'].fields.append(
  _FLOATPARAMETER.fields_by_name['range'])
_FLOATPARAMETER.fields_by_name['range'].containing_oneof = _FLOATPARAMETER.oneofs_by_name['AllowedValues']
_PARAMETER.fields_by_name['int32Parameter'].message_type = _INT32PARAMETER
_PARAMETER.fields_by_name['floatParameter'].message_type = _FLOATPARAMETER
_PARAMETER.oneofs_by_name['Type'].fields.append(
  _PARAMETER.fields_by_name['int32Parameter'])
_PARAMETER.fields_by_name['int32Parameter'].containing_oneof = _PARAMETER.oneofs_by_name['Type']
_PARAMETER.oneofs_by_name['Type'].fields.append(
  _PARAMETER.fields_by_name['floatParameter'])
_PARAMETER.fields_by_name['floatParameter'].containing_oneof = _PARAMETER.oneofs_by_name['Type']
_NAMEDPARAMETER.fields_by_name['parameter'].message_type = _PARAMETER
DESCRIPTOR.message_types_by_name['Int32Range'] = _INT32RANGE
DESCRIPTOR.message_types_by_name['Int32Set'] = _INT32SET
DESCRIPTOR.message_types_by_name['FloatRange'] = _FLOATRANGE
DESCRIPTOR.message_types_by_name['Int32Parameter'] = _INT32PARAMETER
DESCRIPTOR.message_types_by_name['FloatParameter'] = _FLOATPARAMETER
DESCRIPTOR.message_types_by_name['Parameter'] = _PARAMETER
DESCRIPTOR.message_types_by_name['NamedParameter'] = _NAMEDPARAMETER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Int32Range = _reflection.GeneratedProtocolMessageType('Int32Range', (_message.Message,), dict(
  DESCRIPTOR = _INT32RANGE,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.Int32Range)
  ))
_sym_db.RegisterMessage(Int32Range)

Int32Set = _reflection.GeneratedProtocolMessageType('Int32Set', (_message.Message,), dict(
  DESCRIPTOR = _INT32SET,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.Int32Set)
  ))
_sym_db.RegisterMessage(Int32Set)

FloatRange = _reflection.GeneratedProtocolMessageType('FloatRange', (_message.Message,), dict(
  DESCRIPTOR = _FLOATRANGE,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.FloatRange)
  ))
_sym_db.RegisterMessage(FloatRange)

Int32Parameter = _reflection.GeneratedProtocolMessageType('Int32Parameter', (_message.Message,), dict(
  DESCRIPTOR = _INT32PARAMETER,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.Int32Parameter)
  ))
_sym_db.RegisterMessage(Int32Parameter)

FloatParameter = _reflection.GeneratedProtocolMessageType('FloatParameter', (_message.Message,), dict(
  DESCRIPTOR = _FLOATPARAMETER,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.FloatParameter)
  ))
_sym_db.RegisterMessage(FloatParameter)

Parameter = _reflection.GeneratedProtocolMessageType('Parameter', (_message.Message,), dict(
  DESCRIPTOR = _PARAMETER,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.Parameter)
  ))
_sym_db.RegisterMessage(Parameter)

NamedParameter = _reflection.GeneratedProtocolMessageType('NamedParameter', (_message.Message,), dict(
  DESCRIPTOR = _NAMEDPARAMETER,
  __module__ = 'NamedParameters_pb2'
  # @@protoc_insertion_point(class_scope:CoreML.Specification.NamedParameter)
  ))
_sym_db.RegisterMessage(NamedParameter)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('H\003'))
# @@protoc_insertion_point(module_scope)
