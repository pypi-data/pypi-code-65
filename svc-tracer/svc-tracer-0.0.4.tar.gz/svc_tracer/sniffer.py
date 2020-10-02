# -*- coding: utf-8 -*-
import time
import logging
import traceback

from threading import Thread
from scapy.all import sniff, TCPSession
from scapy.layers.inet import TCP
from scapy.packet import bind_bottom_up


class Sniffer(Thread):
  """ A generic & simple packet sniffer """

  def __init__(self, iface, port, printer, **options):
    """A Sniffer that merges packets into a stream

    Params:
        ``iface``           The interface in which to listen
        ``port``            The TCP port that we care about
        ``stream_handler``  The callback for each stream
        ``offline``         Path to a pcap file
        ``ip``              A list of IPs that we care about
    """
    super(Sniffer, self).__init__()
    self.setDaemon(True)

    self._iface = iface
    self._port = port
    self._handlers = [printer] if printer else []
    self._options = options
    self._wants_stop = False

    self.start()

  def add_handler(self, handler):
    if handler and handler not in self._handlers:
      self._handlers.append(handler)

  def run(self):
    try:
      kwargs = {
        'filter': 'port %d' % self._port,
        'store': False,
        'prn': self._handle_packet,
        'iface': self._iface,
        'stop_filter': lambda p: self._wants_stop,
        'session': TCPSession,
      }

      from scapy.config import conf
      level = self._options.get('log_level')
      conf.logLevel = level

      message = self._options.get('message')
      if message == 'thrift':
        from .thrift_parser import Thrift
        from .thrift_idl import parse_idl_file
        if self._options.get('transport'):
          conf.contribs["thrift"]["transport"] = self._options['transport']
        if self._options.get('protocol'):
          conf.contribs["thrift"]["protocol"] = self._options['protocol']
        if self._options.get('finagle'):
          conf.contribs["thrift"]["finagle"] = self._options['finagle']
        if self._options.get('idl_file'):
          conf.contribs["thrift"]["idl_file"] = parse_idl_file(self._options['idl_file'])
        bind_bottom_up(TCP, Thrift, sport=self._port)
        bind_bottom_up(TCP, Thrift, dport=self._port)
      elif message == 'http':
        from scapy.layers.http import HTTP
        bind_bottom_up(TCP, HTTP, sport=self._port)
        bind_bottom_up(TCP, HTTP, dport=self._port)
      else:
        raise ValueError("Invalid message type '%s'" % message)
      self._wants_stop = False
      sniff(**kwargs)
    except Exception as ex:
      logging.error("Sniffer start on '%s' error: %s\n%s" % (self._iface, ex, traceback.format_exc()))

  def stop(self, wait_for_stopped=False):
    self._wants_stop = True
    if wait_for_stopped:
      while self.is_alive():
        time.sleep(0.01)

  def _handle_packet(self, packet):
    for handler in self._handlers:
      try:
        if not handler(packet):
          self.stop()
          break
      except Exception as ex:
        logging.error('Sniffer handler exception: %s\n%s' % (ex, traceback.format_exc()))
