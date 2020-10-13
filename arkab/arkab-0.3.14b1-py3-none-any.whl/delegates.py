import os


class FileDelegate:
    def __init__(self, parent: str):
        self.parent = parent

    def provide(self, file: str):
        return os.path.join(self.parent, file)
