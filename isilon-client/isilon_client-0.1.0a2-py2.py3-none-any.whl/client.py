import os

import attr

from isilon.api import Accounts, Containers, Discoverability, Endpoints, Objects
from isilon.creds import Credentials
from isilon.http import Http


@attr.s
class IsilonClient:
    isilon_addr = attr.ib(
        type=str,
        default=os.getenv("ISILON_ADDRESS", "http://localhost:8080"),
        converter=str,
    )
    account = attr.ib(type=str, default=os.getenv("ISILON_ACCOUNT"), converter=str)
    user = attr.ib(type=str, default=os.getenv("ISILON_USER"), converter=str)
    password = attr.ib(
        type=str, default=os.getenv("ISILON_PASSWORD"), repr=False, converter=str
    )
    http_client = attr.ib(
        repr=False, factory=Http, validator=attr.validators.instance_of(Http)
    )

    def __attrs_post_init__(self):
        self.credentials = Credentials(
            self.http_client, self.account, self.user, self.password
        )
        self.objects = Objects(
            http=self.http_client, url=self.isilon_addr, credentials=self.credentials
        )
        self.discoverability = Discoverability(
            http=self.http_client, url=self.isilon_addr, credentials=self.credentials
        )
        self.containers = Containers(
            http=self.http_client, url=self.isilon_addr, credentials=self.credentials
        )
        self.endpoints = Endpoints(
            http=self.http_client, url=self.isilon_addr, credentials=self.credentials
        )
        self.accounts = Accounts(
            http=self.http_client, url=self.isilon_addr, credentials=self.credentials
        )
