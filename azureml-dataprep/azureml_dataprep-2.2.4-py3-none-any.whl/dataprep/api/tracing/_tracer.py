from typing import List, Optional

from ._constants import USER_FACING_NAME
from ._span import Span
from ._span_processor import SpanProcessor
from ._vendored import _execution_context as execution_context


class AmlTracer:
    def __init__(self, span_processors: List[SpanProcessor]):
        self._span_processors = span_processors

    def start_as_current_span(
            self, name: str, parent: Optional[Span] = None, user_facing_name: str = None
    ) -> Span:
        parent = parent or execution_context.get_current_span()
        span = Span(name, parent, self._span_processors)
        self.__class__.decorate_span(span, user_facing_name)
        span.__enter__()
        return span

    def start_span(self, name: str, parent: Optional[Span] = None, user_facing_name: str = None) -> Span:
        span = Span(name, parent, self._span_processors)
        self.__class__.decorate_span(span, user_facing_name)
        return span

    @staticmethod
    def decorate_span(span: Span, user_facing_name: str):
        if user_facing_name:
            span.attributes[USER_FACING_NAME] = user_facing_name


class DefaultTraceProvider:
    def __init__(self, tracer: AmlTracer):
        self._tracer = tracer

    def get_tracer(self, name: str) -> AmlTracer:
        return self._tracer

    def get_current_span(self):
        return execution_context.get_current_span()
