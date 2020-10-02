# -*- coding: utf-8 -*-
import re
import time
import logging
import pprintpp

from datetime import datetime
from collections import deque, defaultdict, namedtuple


class Message(object):
  def __init__(self, timestamp, src, dst, key, method, is_req, is_res, info, header, data):
    self.timestamp = timestamp
    self.src = src
    self.dst = dst
    self.key = key
    self.method = method
    self.is_req = is_req
    self.is_res = is_res
    self.info = info
    self.header = header
    self.data = data


PrintOptions = namedtuple('PrintOptions', [
  'port',
  'from_ip',
  'to_ip',
  'methods',
  'show_header',
  'show_data',
])
PrintOptions.__new__.__defaults__ = (None,)


def filter_msg(options, src_ip, dst_ip, src_port, dst_port, method, is_req, is_res):
  # filter msg by ip and port
  if is_req:
    if dst_port != options.port:
      return None, None
    elif options.from_ip and src_ip not in options.from_ip:
      return None, None
    elif options.to_ip and dst_ip not in options.to_ip:
      return None, None
  elif is_res:
    if src_port != options.port:
      return None, None
    elif options.from_ip and dst_ip not in options.from_ip:
      return None, None
    elif options.to_ip and src_ip not in options.to_ip:
      return None, None
  else:
    if src_port != options.port and dst_port != options.port:
      return None, None
    elif options.from_ip and src_ip not in options.from_ip and dst_ip not in options.from_ip:
      return None, None
    elif options.to_ip and src_ip not in options.to_ip and dst_ip not in options.to_ip:
      return None, None

  # filter msg by method
  if method and options.methods and all([not re.search(i, method) for i in options.methods]):
    return None, None

  from six.moves import intern
  src = intern('%s:%s' % (src_ip, src_port))
  dst = intern('%s:%s' % (dst_ip, dst_port))
  return src, dst


def parse_msg(options, packet):
  from scapy.packet import Raw
  from scapy.layers.inet import IP
  from scapy.layers.http import HTTPRequest, HTTPResponse
  from .thrift_parser import ThriftMessage

  def to_string(binary, charset='utf-8'):
    try:
      if not binary:
        return ''
      if isinstance(binary, (bytes, bytearray)):
        s = binary.decode(charset) if binary else ''
        return s.encode('utf-8') if str(type(s)).find('unicode') >= 0 else s
      return binary
    except UnicodeDecodeError:
      return binary

  def to_header(fields, skip_names):
    r = {}
    for k, v in fields.items():
      if k not in skip_names:
        if k == "Unknown_Headers":
          r.update(to_header(v, []))
        else:
          r[to_string(k)] = to_string(v)
    return r

  def to_data(raw, content_type):
    m = re.search(r'charset=([^ ;]+)', to_string(content_type))
    return to_string(raw.load, m[1]) if raw and m else raw

  if packet.haslayer(ThriftMessage, True):
    msg = packet.getlayer(ThriftMessage, _subclass=True)
    if msg.type == 'Call':
      is_req, is_res = True, False
    elif msg.type in ['Reply', 'Exception']:
      is_req, is_res = False, True
    else:
      is_req, is_res = False, False
    method = msg.method[len('ThriftXHandler:'):] if msg.method.startswith('ThriftXHandler:') else msg.method
    src, dst = filter_msg(options, packet[IP].src, packet[IP].dst, packet.sport, packet.dport, method, is_req, is_res)
    if src and dst:
      info = "%s %s(seqid=%d)" % (msg.type, msg.method, msg.seqid)
      return Message(packet.time, src, dst, method, method, is_req, is_res, info, msg.header, msg.args)
  elif packet.haslayer(HTTPRequest):
    msg = packet.getlayer(HTTPRequest)
    http_method = to_string(msg.Method)
    http_host = to_string(msg.Host)
    http_path = to_string(msg.Path)
    http_version = to_string(msg.Http_Version)
    method = '%s %s' % (http_method, http_path)
    src, dst = filter_msg(options, packet[IP].src, packet[IP].dst, packet.sport, packet.dport, method, True, False)
    if src and dst:
      info = '%s http://%s%s %s' % (http_method, http_host, http_path, http_version)
      header = to_header(msg.fields, ['Method', 'Path', 'Http_Version'])
      data = to_data(packet.getlayer(Raw), msg.Content_Type)
      return Message(packet.time, src, dst, http_version, method, True, False, info, header, data)
  elif packet.haslayer(HTTPResponse):
    msg = packet.getlayer(HTTPResponse)
    http_version = to_string(msg.Http_Version)
    http_code = to_string(msg.Status_Code)
    http_reason = to_string(msg.Reason_Phrase)
    src, dst = filter_msg(options, packet[IP].src, packet[IP].dst, packet.sport, packet.dport, None, False, True)
    if src and dst:
      info = '%s %s %s' % (http_version, http_code, http_reason)
      header = to_header(msg.fields, ['Http_Version', 'Status_Code', 'Reason_Phrase'])
      data = to_data(packet.getlayer(Raw), msg.Content_Type)
      return Message(packet.time, src, dst, http_version, None, False, True, info, header, data)
  return None


def print_msg(options, msg, prefix='', indent=0):
  indent = ' ' * indent if indent else ''

  if options.show_header and msg.header:
    header = '\n%sheader: %s' % (indent, pprintpp.pformat(msg.header, indent=2, width=80))
  else:
    header = ''

  if options.show_data and msg.data:
    data = '\n%sdata: %s' % (indent, pprintpp.pformat(msg.data, indent=2, width=80))
  else:
    data = ''

  now = datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S:%f')
  return '%s[%s] %s -> %s: %s%s%s' % (prefix, now, msg.src, msg.dst, msg.info, header, data)


def print_pair(options, request, reply):
  output = print_msg(options, request)
  output += "\n" + print_msg(options, reply, prefix='-----> ')
  return output


class MessagePrinter(object):
  """ A simple message printer """

  def __init__(self, options):
    self._options = options

  def __call__(self, packet):
    msg = parse_msg(self._options, packet)
    if msg:
      logging.info(print_msg(self._options, msg))

    return True  # keep the sniffer running


class PairedPrinter(object):
  """ Pairs each request with its reply """

  def __init__(self, options):
    self._options = options

    # msgs by [src/dst/method]
    self._requests = defaultdict(deque)
    self._replies = defaultdict(deque)

  # noinspection DuplicatedCode
  def __call__(self, packet):
    """
    We need to match up each (request, reply) pair. Presumably,
    pcap _shouldn't_ deliver packets out of order, but
    things could get mixed up somewhere withing the
    TCP stream being reassembled and the StreamHandler
    thread. So, we don't assume that a 'reply' implies
    the corresponding 'call' has been seen.

    It could also be that we started sniffing after
    the 'call' message... but there's no easy way to tell
    (given we don't keep the startup time around...)
    """
    msg = parse_msg(self._options, packet)
    if msg and msg.is_req:
      replies = self._replies[(msg.dst, msg.src, msg.key)]
      if len(replies) > 0:
        reply = replies.popleft()
        logging.info(print_pair(self._options, msg, reply))
      else:
        self._requests[(msg.src, msg.dst, msg.key)].append(msg)
    elif msg and msg.is_res:
      requests = self._requests[(msg.dst, msg.src, msg.key)]
      if len(requests) > 0:
        request = requests.popleft()
        logging.info(print_pair(self._options, request, msg))
      else:
        self._replies[(msg.src, msg.dst, msg.key)].append(msg)
    elif msg:
      logging.info(print_msg(self._options, msg))

    return True  # keep the sniffer running

  def timer(self, timeout):
    now = time.time()
    for requests in self._requests.values():
      for request in requests:
        if now - request.timestamp > timeout:
          logging.error('[TIMEOUT] ' + print_msg(self._options, request))
    for replies in self._replies.values():
      removes = []
      for reply in replies:
        if now - reply.timestamp > timeout:
          if reply.method:
            logging.error('[TIMEOUT] ' + print_msg(self._options, reply))
          else:
            removes.append(reply)
      for reply in removes:
        replies.remove(reply)
