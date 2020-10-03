import asyncio
import json

from cleo import Command

import isilon


class DiscoverabilityCommand(Command):
    """
    Discoverability.

    discoverability
    """

    def handle(self):
        resp = asyncio.run(isilon.discoverability.info())
        self.line(f"{json.dumps(resp, indent=4, sort_keys=True)}")
