from .collectors import StreamCollector
from skitai.handlers.collectors import FormCollector
from skitai import counter
from collections import Iterable
from aquests.protocols.grpc.message import decode_message
from skitai.corequest.tasks import Revoke
import struct
import time


class grpc_collector (FormCollector):
	stream_id = counter.counter ()
	def __init__ (self, handler, request, *args):
		super ().__init__ (handler, request, *args)
		self.ch = request.channel
		self.stream_id.inc ()
		self._compressed = None
		self._msg_length = 0
		self.buffer = b""
		self.msgs = []

	def close (self):
		self.handler.continue_request (self.request, self.msgs)

	def start_collect (self):
		self.ch.set_terminator (1)

	def collect_incoming_data (self, data):
		self.buffer += data

	def handle_message (self, msg):
		self.msgs.append (msg)

	def found_terminator (self):
		current_terminator = self.ch.get_terminator ()
		if not self.buffer:
			self.close ()
			return

		buf, self.buffer = self.buffer, b""
		if self._compressed is None:
			self._compressed = struct.unpack ("!B", buf)[0]
			self.ch.set_terminator (4)

		elif self._msg_length == 0:
			self._msg_length = struct.unpack ("!I", buf)[0]
			if self._msg_length:
				self.ch.set_terminator (self._msg_length)
			else:
				self.ch.set_terminator (0)
				self._compressed = None

		else:
			msg = decode_message (buf, self._compressed)
			self._compressed = None
			self._msg_length = 0
			self.handle_message (msg)
			self.ch.set_terminator (b'\r\n\r\n')


class grpc_stream_collector (grpc_collector, StreamCollector):
	stream_id = counter.counter ()
	def __init__ (self, handler, request, *args):
		grpc_collector.__init__ (self, handler, request, *args)
		self.callback = None
		self.closed = False
		self.first_data = True
		self.end_of_data = False
		self.was = None
		self.input_type = None

	def start_collect (self):
		self.ch.set_terminator (b'')

	def set_input_type (self, input_type):
		self.input_type = input_type

	def do_callback (self):
		if self.callback and (self.end_of_data or self.msgs):
			self.callback (self.was, self)
			self.callback = None

		if self.first_data:
			self.first_data = False
			self.handler.continue_request (self.request, self)

	def then (self, func, was = None):
		self.was = was
		if self.end_of_data or self.msgs:
			return func (self.was, self)
		self.callback = func
		return Revoke ()

	def fetch (self):
		if not self.msgs and self.end_of_data:
			return None
		msg = self.msgs.pop (0)
		f = self.input_type [0]()
		f.ParseFromString (msg)
		return f

	def close (self):
		self.end_of_data = True
		StreamCollector.close (self)

	def handle_message (self, msg):
		super ().handle_message (msg)
		self.do_callback ()

	def collect_incoming_data (self, data):
		grpc_collector.collect_incoming_data (self, data)
		self.handle_data ()

	def handle_data (self):
		while len (self.buffer) >= 5:
			_compressed = struct.unpack ("!B", bytes (self.buffer [:1])) [0]
			_msg_length = struct.unpack ("!I", self.buffer [1:5]) [0]
			self.buffer = self.buffer [5:]
			if len (self.buffer) < _msg_length:
				break
			buf, self.buffer = self.buffer [:_msg_length], self.buffer [_msg_length:]
			msg = decode_message (buf, _compressed)
			self.handle_message (msg)

	def found_terminator (self):
		self.do_callback ()
		self.close ()
