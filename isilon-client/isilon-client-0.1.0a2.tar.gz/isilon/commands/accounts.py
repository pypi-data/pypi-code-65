import asyncio

from cleo import Command

import isilon


class AccountsCommand(Command):
    """
    Accounts.

    accounts
        {account : Account name.}
        {--headers=* : HTTP headers.}
        {--s|show : Create or replace object.}
        {--u|update : Create, update or delete account metadata.}
        {--m|metadata : Show account metadata.}
    """

    def handle(self):
        account_name = str(self.argument("account"))
        if self.option("show"):
            resp = asyncio.run(isilon.accounts.show(account_name))
            self.line(f"{resp}")
        elif self.option("update"):
            asyncio.run(isilon.accounts.update(account_name))
            self.line("<options=bold>metadata updated.</>")
        elif self.option("metadata"):
            resp = asyncio.run(isilon.accounts.metadata(account_name))
            for meta_key, meta_value in resp.items():
                self.line(f"<options=bold>{meta_key}</>: {meta_value}")
