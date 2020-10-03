import asyncio

from cleo import Command

import isilon


class EndpointsCommand(Command):
    """
    Endpoints.

    endpoints
    """

    def handle(self):
        resp = asyncio.run(isilon.endpoints())
        self.line(f"{resp}")
