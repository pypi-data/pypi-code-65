import logging
from types import SimpleNamespace
from contextlib import contextmanager

from logchain import formatters


VerbosityToLevel = {
	0: logging.ERROR,
	1: logging.WARNING,
	2: logging.INFO,
	3: logging.DEBUG,
}


class Result(SimpleNamespace):
	"""
	Class for reporting rich errors.
	Where a mere container would have been evaluated True,
	`Result` is evaluated like its `valid` argument.
	Extra information can be added as named arguments.
	"""
	def __init__(self, valid: bool, **kwargs):
		super().__init__(**kwargs)
		self.valid = valid

	def __bool__(self):
		return self.valid


class LogChainer:
	"""
	Entrypoint for initializing the log chain.
	"""

	def __init__(self, **kwargs):
		"""
		@param named args
		"""

		self.verbosity = kwargs.get("verbosity", 0)
		self.stream = kwargs.get("stream", None)
		self.name = kwargs.get("name", None)
		self.formatterCls = kwargs.get("formatterCls", formatters.Basic)

		self.formatter = self.formatterCls(kwargs)

		# Remaining unused args
		# if kwargs:
		# 	raise ValueError('Unrecognised argument(s): %s' % keys)


	def initLogging(self):
		aLevel = VerbosityToLevel.get(self.verbosity, logging.DEBUG)
		#logging.basicConfig(level = aLevel, stream = self.stream)
		#FileHandler(filename, mode)
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(aLevel)
		handler = logging.StreamHandler(self.stream)
		handler.setFormatter(self.formatter)
		self.logger.addHandler(handler)
		return self.logger


	def verify(self, iLogChain):
		"""
		Check the consistency of a log chain with the secret.
		In case of failure, a Result object is returned:
		- evaluates to False
		- prevLine: last consistent line
		- line: first inconsistent line
		"""

		# TODO, verify the last line somehow
		for prevLine, line in zip(iLogChain, iLogChain[1:]):

			isValid = self.formatter.verify(prevLine, line)

			if not isValid:
				return Result(False, prevLine = prevLine, line = line)
		return Result(True)


	def setFields(self, **kwargs):
		"""
		Adds contextual data to the log record in the form of key = value
		Remove a key by setting it to `None`.
		"""
		self.formatter.setFields(**kwargs)

	@contextmanager
	def managedFields(self, **kwargs):
		try:
			previousCtx = self.formatter.setFields(**kwargs)
			yield
		finally:
			self.formatter.context = previousCtx

def stopLogging():
	"""
	Cleanup if needed, inspired from the library source code.
	"""
	logger = logging.getLogger()
	for h in logger.handlers[:]:
		logger.removeHandler(h)
		h.close()
