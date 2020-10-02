# -*- coding: utf-8 -*-
import logging

from struct import unpack
from scapy.config import conf
from scapy.fields import Field, StrField
from scapy.layers.inet import TCP
from scapy.packet import Packet, bind_layers, bind_bottom_up
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.protocol.TCompactProtocol import TCompactProtocol
from thrift.protocol.TJSONProtocol import TJSONProtocol
from thrift.transport import TTransport
from thrift.Thrift import TMessageType

from .thrift_struct import ThriftStruct

if "thrift" not in conf.contribs:
  conf.contribs["thrift"] = {
    "transport": None,      # thrift transport: framed, buffered. None for auto detect
    "protocol": None,       # thrift protocol: binary, compact or json. None for auto detect
    "finagle": False,       # finagle-thrift traffic (i.e.: with request headers)
    "idl_file": None,       # thrift idl object to resolve types
    "read_values": True,    # should get values from thrift message
    "max_fields": 1000,
    "max_lists": 1000000,
    "max_maps": 1000000,
    "max_sets": 1000000,
  }


class ThriftMessage(Packet):
  fields_desc = [
    Field("type", None),
    Field("method", None),
    Field("seqid", None),
    Field('header', None),
    Field('args', None),
    StrField("load", ""),
  ]

  def __init__(self, pkt=b"", mtype=None, method=None, seqid=None, args=None, header=None):
    Packet.__init__(self, pkt)
    self.setfieldval('type', mtype)
    self.setfieldval('method', method)
    self.setfieldval('seqid', seqid)
    self.setfieldval('header', header)
    self.setfieldval('args', args)
    self.setfieldval('load', pkt)
    if args and not isinstance(args, ThriftStruct):
      raise ValueError('args must be a ThriftStruct instance')
    if header and not isinstance(header, ThriftStruct):
      raise ValueError('header must be a ThriftStruct instance')

  def hashret(self):
    # The only field both Call and Reply have in common
    return self.method

  def __str__(self):
    header = ', header=%s' % self.header if self.header else ''
    field = ', fields=%s' % self.args if self.args else ''
    return 'type=%s, method=%s, seqid=%s%s%s' % (
      self.type, self.method, self.seqid, header, field)

  @property
  def as_dict(self):
    return {
      'type': self.type,
      'method': self.method,
      'seqid': self.seqid,
      'header': self.header.as_dict if self.header else None,
      'args': self.args.as_dict if self.args else None,
      'length': len(self.load),
    }


class ThriftCall(ThriftMessage):
  name = "thrift call"

  def __init__(self, pkt=b"", method=None, seqid=None, args=None, header=None):
    ThriftMessage.__init__(self, pkt, 'Call', method, seqid, args, header)


class ThriftReply(ThriftMessage):
  name = "thrift reply"

  def __init__(self, pkt=b"", method=None, seqid=None, args=None, header=None):
    ThriftMessage.__init__(self, pkt, 'Reply', method, seqid, args, header)

  def answers(self, other):
    return ThriftCall in other


class ThriftException(ThriftMessage):
  name = "thrift exception"

  def __init__(self, pkt=b"", method=None, seqid=None, args=None, header=None):
    ThriftMessage.__init__(self, pkt, 'Exception', method, seqid, args, header)


class ThriftOneway(ThriftMessage):
  name = "thrift oneway"

  def __init__(self, pkt=b"", method=None, seqid=None, args=None, header=None):
    ThriftMessage.__init__(self, pkt, 'Oneway', method, seqid, args, header)


class Thrift(Packet):
  name = "Thrift"
  fields_desc = []
  show_indent = 0

  MIN_MESSAGE_SIZE = 8
  MAX_METHOD_LENGTH = 70
  COMPACT_PROTOCOL_ID = 0x82
  BINARY_PROTOCOL_VERSION_MASK = -65536  # 0xffff0000
  BINARY_PROTOCOL_VERSION_VAL = -2147418112  # 0x80010000

  # tcp_reassemble is used by TCPSession in session.py
  @classmethod
  def tcp_reassemble(cls, data, _metadata):
    def detect_protocol(payload, proto_name, trans_framed, throw_error):
      """ TODO: support fbthrift, finagle-thrift, finagle-mux, CORBA """

      def error(msg):
        if throw_error:
          logging.error("Thrift message reassemble error: %s" % msg)
          raise ValueError(msg)
        return None

      def is_compact_protocol():
        val = unpack('!B', payload[:1])[0]
        return val == cls.COMPACT_PROTOCOL_ID

      def is_binary_protocol():
        val = unpack('!i', payload[0:4])[0]
        return (val & cls.BINARY_PROTOCOL_VERSION_MASK) == cls.BINARY_PROTOCOL_VERSION_VAL

      def is_json_protocol():
        # FIXME: more elaborate parsing would make this more robust
        return payload.startswith(b'[1')

      if trans_framed:
        size = unpack('!i', payload[:4])[0] if len(payload) >= 4 else -1
        if size < cls.MIN_MESSAGE_SIZE:
          return error('Invalid framed size: %d' % size)
        elif len(payload) < size + 4:
          return error('Not enough framed data: %d of %d' % (len(payload), size + 4))
        payload = payload[4:]
      else:
        if len(payload) < cls.MIN_MESSAGE_SIZE:
          return error('Not enough buffered data: %d' % len(payload))

      if proto_name == 'compact' and is_compact_protocol():
        return TCompactProtocol, payload
      elif proto_name == 'binary' and is_binary_protocol():
        return TBinaryProtocol, payload
      elif proto_name == 'json' and is_json_protocol():
        return TJSONProtocol, payload
      elif is_compact_protocol():
        return TCompactProtocol, payload
      elif is_binary_protocol():
        return TBinaryProtocol, payload
      elif is_json_protocol():
        return TJSONProtocol, payload
      else:
        error('Unknown protocol')

    try:
      # get protocol and transport
      config = conf.contribs['thrift']
      trans = config['transport']
      proto = config['protocol']
      finagle = config['finagle']
      max_fields = config['max_fields']
      max_lists = config['max_lists']
      max_maps = config['max_maps']
      max_sets = config['max_sets']
      read_values = config['read_values']
      idl_file = config['idl_file']
      if trans == 'buffered':
        proto, data = detect_protocol(data, proto, False, True)
      elif trans == 'framed':
        proto, data = detect_protocol(data, proto, True, True)
      else:
        proto, data = detect_protocol(data, proto, False, False) or \
                      detect_protocol(data, proto, True, True)

      # get header for finagle-thrift
      protocol = proto(TTransport.TMemoryBuffer(data))
      header = None
      if finagle:
        try:
          header = ThriftStruct.read(protocol, max_fields, max_lists, max_maps, max_sets, read_values)
        except ValueError:
          # reset stream, maybe it's not finagle-thrift
          protocol = proto(TTransport.TMemoryBuffer(data))

      # unpack the message
      method, mtype, seqid = protocol.readMessageBegin()
      if len(method) == 0 or method.isspace() or method.startswith(' '):
        raise ValueError('Empty method name')
      if len(method) > cls.MAX_METHOD_LENGTH:
        raise ValueError('Method name too long')
      if any(ord(char) not in range(33, 127) for char in method):
        raise ValueError('Invalid method name "%s"' % method)

      args = ThriftStruct.read(protocol, max_fields, max_lists, max_maps, max_sets, read_values)

      protocol.readMessageEnd()

      if idl_file:
        try:
          idl_function = conf.contribs["thrift"]["idl_file"].get_function(method)
          args = idl_function.get_args(mtype, args) if idl_function else args
        except Exception as ex:
          logging.error("Thrift message parse error: %s" % ex)

      if mtype == TMessageType.CALL:
        return ThriftCall(data, method, seqid, args, header)
      elif mtype == TMessageType.REPLY:
        return ThriftReply(data, method, seqid, args, header)
      elif mtype == TMessageType.EXCEPTION:
        return ThriftException(data, method, seqid, args, header)
      elif mtype == TMessageType.ONEWAY:
        return ThriftOneway(data, method, seqid, args, header)
      else:
        return None
    except ValueError:
      return None


# Bindings


bind_bottom_up(TCP, Thrift, sport=9090)
bind_bottom_up(TCP, Thrift, dport=9090)
bind_layers(TCP, Thrift, sport=9090, dport=9090)
