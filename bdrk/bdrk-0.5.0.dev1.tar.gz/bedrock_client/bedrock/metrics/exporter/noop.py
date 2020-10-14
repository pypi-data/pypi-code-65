from ..context import PredictionContext
from .type import LogExporter


class NoopExporter(LogExporter):
    """Exporter that can be used to disable logging."""

    def emit(self, prediction: PredictionContext):
        pass
