import datetime
from .f import F
from .dbtypes import DB_PGSQL, DB_SQLITE3
import json

def toval (s, engine = DB_PGSQL):
	from .sql import SQLComposer

	if isinstance (s, dict):
		assert engine == DB_PGSQL, "JSON not supported"
		s = json.dumps (s)

	if isinstance (s, datetime.datetime):
		if engine == DB_PGSQL:
			return "TIMESTAMP '" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"
		else:
			return "'" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"

	if isinstance (s, datetime.date):
		if engine == DB_PGSQL:
			return "TIMESTAMP '" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"
		else:
			return "'" + s.strftime ("%Y-%m-%d %H:%M:%S") + "'"

	if s is None:
		return "NULL"

	if isinstance (s, bool):
		return s == True and 'true' or 'false'

	if isinstance (s, (SQLComposer,)):
		return "({})".format (str (s))

	if isinstance (s, (float, int, F)):
		return str (s)

	return "'" + s.replace ("'", "''") + "'"

class D:
	def __init__ (self, **data):
		self._feed = data
		self._columns = list (self._feed.keys ())
		self._encoded = False

	def encode (self, engine = DB_PGSQL):
		if self._encoded:
			return
		_data = {}
		for k, v in self._feed.items ():
			_data [k] = toval (v, engine)
		self._feed = _data
		self._encoded = True
		return self

	@property
	def columns (self):
		return ", ".join (self._columns)

	@property
	def values (self):
		return ", ".join ([self._feed [c] for c in self._columns])

	@property
	def pairs (self):
		return ", ".join (["{} = {}".format (c, self._feed [c]) for c in self._columns])
