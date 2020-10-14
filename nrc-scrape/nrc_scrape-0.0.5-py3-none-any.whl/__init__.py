# make logs accessible from top level module name
from .logs_setup import el, fl, ol, sl

from .definitions.sessions import session_factory

# global session for connecting for urls, multithreaded scraper should use the factory
session = session_factory()