import logging
import os

from isilon.__version__ import __version__
from isilon.api import Accounts, Containers, Discoverability, Endpoints, Objects
from isilon.creds import Credentials
from isilon.http import Http

logging.getLogger("isilon-client").addHandler(logging.NullHandler())


isilon_addr = os.getenv("ISILON_ADDRESS", "http://localhost:8080")
account = os.getenv("ISILON_ACCOUNT", "test")
user = os.getenv("ISILON_USER", "tester")
password = os.getenv("ISILON_PASSWORD", "testing")
http = Http()

credentials = Credentials(http, account, user, password)
objects = Objects(http, isilon_addr, credentials)
discoverability = Discoverability(http, isilon_addr, credentials)
containers = Containers(http, isilon_addr, credentials)
endpoints = Endpoints(http, isilon_addr, credentials)
accounts = Accounts(http, isilon_addr, credentials)
