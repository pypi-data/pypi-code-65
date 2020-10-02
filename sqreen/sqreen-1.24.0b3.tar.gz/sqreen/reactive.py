# -*- coding: utf-8 -*-
# Copyright (c) 2016 - 2020 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Reactive Engine
"""
import logging
from bisect import bisect
from itertools import chain
from operator import attrgetter
from weakref import WeakSet

from .execute_callbacks import execute_callbacks
from .runtime_storage import runtime
from .utils import viewkeys

LOGGER = logging.getLogger(__name__)


class SpanDisposed(Exception):
    """
    Exception raised when a span is used after it was disposed.
    """


class Span:

    _none = object()

    def __init__(self, queue, storage):
        self.queue = queue
        self.storage = storage
        self._children = WeakSet()
        self._state = {}
        self._callbacks_by_addr = {}

    def create_child(self):
        by_addr = self._callbacks_by_addr
        if by_addr is None:
            raise SpanDisposed
        span = self.__class__(self.queue, self.storage)
        span._callbacks_by_addr = by_addr
        span._state.update(self._state)
        self._children.add(span)
        return span

    def dispose(self):
        """
        Dispose a span and all its children. This method is not thread-safe.
        """
        self._state.clear()
        self._callbacks_by_addr = None
        while len(self._children):
            self._children.pop(0).dispose()

    @property
    def subscribed_addresses(self):
        """
        List all subscribed addresses.
        """
        return viewkeys(self._callbacks_by_addr)

    def _callbacks_for_addresses(self, addresses):
        """
        Return a callbacks interested by addresses. The callbacks
        are sorted by order of priority.
        """
        by_addr = self._callbacks_by_addr
        if by_addr is None:
            raise SpanDisposed
        # Sort callbacks by priority
        it = sorted(chain.from_iterable([by_addr.get(addr, ()) for addr in addresses]),
                    key=attrgetter("priority"))
        prev = None
        for callback in it:
            # Deduplicate callbacks
            if callback is prev:
                continue
            yield callback
            prev = callback

    def _callbacks_for_data(self, data):
        """
        Mutate data to add grouped addresses and return callbacks interested
        by the data.
        """
        for callback in self._callbacks_for_addresses(viewkeys(data)):
            group_addresses = callback.group_addresses
            if group_addresses:
                groups_data = []
                for group in group_addresses:
                    group_data = []
                    for addr in group:
                        value = data.get(addr, self._none)
                        if value is not self._none:
                            self._state[addr] = value
                        else:
                            value = self._state.get(addr, self._none)
                        if value is not self._none:
                            group_data.append((addr, value))
                    if len(group_data) == len(group):
                        groups_data.extend(group_data)
                if groups_data:
                    data.update(groups_data)
                    yield callback
                elif callback.batch_addresses:
                    yield callback
            elif callback.batch_addresses:
                yield callback

    def provide_data(self, data, **kwargs):
        callbacks_data = dict(data)
        callbacks = list(self._callbacks_for_data(callbacks_data))
        if callbacks:
            return execute_callbacks(
                self.queue, callbacks, "handler", None,
                args=(callbacks_data,), kwargs={}, storage=self.storage,
                valid_actions=["raise"], span=self, **kwargs
            )

    def __del__(self):
        self.dispose()


class Engine:
    """
    Reactive Engine dispatches available data to callbacks.

    Data is a mapping between addresses and values. Data is made available on
    a span, describing its lifetime.

    Spans are layed out in a structured tree. A child span cannot outlive its
    parent (once it is disposed all children spans are disposed too).
    """

    def __init__(self, observation_queue, queue, storage=None):
        self.root = Span(queue, storage or runtime)

    def create_span(self, parent=None):
        """
        Create a new span inheriting the given parent state.

        The spans are automatically disposed when there are no more references.
        """
        parent = parent or self.root
        return parent.create_child()

    def provide_data(self, data, span=None, **kwargs):
        """
        Provide data on the given span.

        Note: changes are not propagated to descendant spans.
        """
        span = span or self.root
        return span.provide_data(data, **kwargs)

    def _add_callback(self, callback, addresses):
        for addr in addresses:
            callbacks = self.root._callbacks_by_addr.setdefault(addr, [])
            idx = bisect([c.priority for c in callbacks], callback.priority)
            callbacks.insert(idx, callback)

    def add_callback(self, callback):
        """
        Register a callback to the reactive engine root span.

        Note: the callback will only get called on the root and new children spans.
        """
        addresses = callback.batch_addresses
        authorized_addresses = callback.authorized_addresses
        if addresses:
            not_authorized = addresses.difference(authorized_addresses)
            if not_authorized:
                raise ValueError("Callback {!r} is not authorized to register {!r}"
                                 .format(callback, not_authorized))
        for addresses in callback.group_addresses:
            not_authorized = addresses.difference(authorized_addresses)
            if not_authorized:
                raise ValueError("Callback {!r} is not authorized to register {!r}"
                                 .format(callback, not_authorized))
        if addresses:
            LOGGER.debug("Callback %r subscribes to any of %r", callback, addresses)
            self._add_callback(callback, addresses)
        for addresses in callback.group_addresses:
            LOGGER.debug("Callback %r subscribes to group %r", callback, addresses)
            self._add_callback(callback, addresses)

    def remove_callbacks(self):
        """
        Remove all callbacks from the reactive engine.

        Note: callbacks can still get called on children span until they are disposed.
        """
        self.root._callbacks_by_addr = {}

    @property
    def subscribed_addresses(self):
        """
        List all subscribed addresses.
        """
        return self.root.subscribed_addresses
