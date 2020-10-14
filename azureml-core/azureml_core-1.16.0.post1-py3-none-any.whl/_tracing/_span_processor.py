# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import ABC, abstractmethod

from ._constants import USER_FACING_NAME, AML_DEV_ATTR_PREFIX


class SpanProcessor(ABC):
    def on_start(self, span):
        pass

    @abstractmethod
    def on_end(self, span):
        pass

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=30000):
        return True


class _ChainedSpanProcessor(SpanProcessor):
    def __init__(self, span_processor):
        self._next_processor = span_processor

    def on_start(self, span):
        self._next_processor.on_start(span)

    def on_end(self, span):
        self._next_processor.on_end(span)

    def shutdown(self):
        self._next_processor.shutdown()

    def force_flush(self, timeout_millis=30000):
        return self._next_processor.force_flush(timeout_millis)


class ExporterSpanProcessor(SpanProcessor):
    def __init__(self, span_exporter, logger=None):
        self._span_exporter = span_exporter
        self._logger = logger or logging.getLogger(__name__)

    def on_end(self, span):
        try:
            self._span_exporter.export((span,))
        except Exception as e:
            self._logger.error('Exception of type {} while exporting spans.'.format(type(e).__name__))

    def shutdown(self):
        self._span_exporter.shutdown()


class UserFacingSpanProcessor(_ChainedSpanProcessor):
    def __init__(self, span_processor):
        super().__init__(span_processor)

    def on_end(self, span):
        if USER_FACING_NAME not in span.attributes:
            return

        span = _clone_span(span)
        _remove_dev_attributes(span.attributes)
        for event in span.events:
            _remove_dev_attributes(event.attributes)

        super().on_end(span)


class AmlContextSpanProcessor(_ChainedSpanProcessor):
    def __init__(self, span_processor):
        from azureml._base_sdk_common import _ClientSessionId

        super().__init__(span_processor)

        self._run_id = None
        self._session_id = _ClientSessionId

    def on_end(self, span):
        self._add_aml_context(span)
        super().on_end(span)

    def _add_aml_context(self, span):
        span.set_user_facing_attribute('session_id', self._session_id)
        span.set_user_facing_attribute('run_id', self._get_run_id())

    def _get_run_id(self):
        from azureml.core import Run

        if not self._run_id:
            try:
                self._run_id = Run.get_context().id
            except:
                self._run_id = '[Unavailable]'
        return self._run_id


def _clone_span(span):
    from ._span import Span
    from ._event import Event

    def clone_event(event):
        return Event(event.name, event.timestamp, event.attributes.copy())

    cloned = Span(span.name, span.parent, span._span_processors)
    cloned._trace_id = span.trace_id
    cloned._span_id = span.span_id
    cloned._start_time = span.start_time
    cloned._end_time = span.end_time
    cloned._attributes = span.attributes.copy()
    cloned._events = [clone_event(event) for event in span.events]
    cloned._status = span.status
    return cloned


def _remove_dev_attributes(attributes):
    for key in attributes:
        if key.startswith(AML_DEV_ATTR_PREFIX + '.'):
            del attributes[key]
