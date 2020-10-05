class BaseFlowProcessor(object):
    def initialize(self, *args, **kwargs):
        raise NotImplemented()

    def execute(self, *args, **kwargs):
        raise NotImplemented()
