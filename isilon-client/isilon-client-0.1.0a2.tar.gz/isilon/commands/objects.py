import asyncio

from cleo import Command

import isilon


class ObjectsCommand(Command):
    """
    Objects.

    objects
        {container : Container name.}
        {object : Object name.}
        {--headers=* : HTTP headers.}
        {--data=? : Object data.}
        {--c|create : Create or replace object.}
        {--m|metadata : Show object metadata.}
        {--u|update : Create or update object metadata.}
        {--d|delete : Delete object.}
    """

    def handle(self):
        container_name = str(self.argument("container"))
        object_name = str(self.argument("object"))
        if self.option("create"):
            data = self.option("data")
            if not data:
                self.line("<error>Please, provides a valid object data.</>")
                raise SystemExit(1)
            asyncio.run(isilon.objects.create_large(container_name, object_name, data))
            self.line(f"\n<options=bold><comment>{object_name}</comment> created.</>")
        elif self.option("metadata"):
            resp = asyncio.run(
                isilon.objects.show_metadata(container_name, object_name)
            )
            for meta_key, meta_value in resp.items():
                self.line(f"<options=bold>{meta_key}</>: {meta_value}")
        elif self.option("update"):
            asyncio.run(isilon.objects.update_metadata(container_name, object_name))
            self.line("<options=bold>metadata updated.</>")
        elif self.option("delete"):
            asyncio.run(isilon.objects.delete(container_name, object_name))
            self.line(f"<options=bold><comment>{object_name}</comment> deleted.</>")
        else:
            asyncio.run(
                isilon.objects.get_large(container_name, object_name, object_name)
            )
            self.line(f"<options=bold><comment>{object_name}</comment> saved.</>")
