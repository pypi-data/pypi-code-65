import asyncio
import json

from cleo import Command

import isilon


class ContainersCommand(Command):
    """
    Containers.

    containers
        {container : Container name.}
        {--headers=* : HTTP headers.}
        {--o|objects : Show container details and list objects.}
        {--c|create : Create container.}
        {--m|metadata : Show container metadata.}
        {--u|update : Create, update or delete container metadata.}
        {--d|delete : Delete container.}
    """

    def handle(self):
        container_name = str(self.argument("container"))
        headers = dict()
        for header in self.option("headers"):
            headers.update(json.loads(header))
        if self.option("objects"):
            resp = asyncio.run(isilon.containers.objects(container_name, headers))
            for obj in resp:
                self.line(f"{obj}")
        elif self.option("create"):
            asyncio.run(isilon.containers.create(container_name, headers))
            self.line(f"<options=bold><comment>{container_name}</comment> created.</>")
        elif self.option("delete"):
            asyncio.run(isilon.containers.delete(container_name, headers))
            self.line(f"<options=bold><comment>{container_name}</comment> deleted.</>")
        elif self.option("metadata"):
            resp = asyncio.run(isilon.containers.show_metadata(container_name, headers))
            for meta_key, meta_value in resp.items():
                self.line(f"<options=bold>{meta_key}</>: {meta_value}")
        elif self.option("update"):
            asyncio.run(isilon.containers.update_metadata(container_name, headers))
            self.line("<options=bold>metadata updated.</>")
