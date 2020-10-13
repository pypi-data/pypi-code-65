from applipy_metrics.registry import MetricsRegistry

try:
    from applipy import Module
except ImportError:
    Module = object


class MetricsModule(Module):

    def configure(self, bind, register):
        bind(MetricsRegistry)
