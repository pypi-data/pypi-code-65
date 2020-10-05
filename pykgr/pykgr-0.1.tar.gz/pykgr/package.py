from pykgr.shell import Shell
import pykgr

class Package(object):
    build_directory = None
    code_directory = None
    name = None
    shell = None
    version = None

    def __build__(self):
        self.fetch()
        self.prepare()
        self.make()
        self.install()

    def __init__(self, **kwargs):
        self.shell = Shell(PWD=pykgr.config.source_directory)
        self.code_directory = "%s/%s" % (
            pykgr.config.source_directory,
            "%s-%s" % (
                self.name,
                self.version
            )
        )
        self.build_directory = "%s/build" % self.code_directory
        self.__initialize__()

    def __initialize__(self):
        pass

    def __str__(self):
        return "<package [%s-%s]>" % (self.name, str(self.version))

    def fetch(self):
        pass

    def install(self):
        pass

    def make(self):
        pass

    def prepare(self):
        pass
