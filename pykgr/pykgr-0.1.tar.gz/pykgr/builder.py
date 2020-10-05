import os

class Builder:
    data = None

    def __init__(self, **kwargs):
        self.data = BuilderData(**kwargs)

        if not self.data.directory:
            raise Exception("What can we do without a directory?")

        if not os.path.exists(self.data.directory):
            os.mkdir(self.data.directory)

    def build(self, package_class):
        package_to_build = package_class()
        package_to_build.__build__()

class BuilderData:
    def __init__(self, **kwargs):
        self.directory = None

        self_keys = [row for row in dir(self) if "__" not in row and not callable(getattr(self, row))]
        for key in kwargs:
            if key in self_keys:
                setattr(self, key, kwargs.get(key))