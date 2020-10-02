from abc import ABC

import wrapt
import copy

from wafec_wrapt_custom.managers import DataEvent, DataManagerAdapter

_simple_types = (str, int, type(None), bool, float)


class WrapperTest(wrapt.ObjectProxy, ABC):
    def __init__(self, wrapped, wrapper_data=None):
        super(WrapperTest, self).__init__(WrapperTest.unwrap(wrapped))
        self._validate_type()
        self._self_wrapper_data = wrapper_data

    def _validate_type(self):
        if isinstance(self.__wrapped__, _simple_types):
            raise TypeError('Cannot be simple')

    def __getitem__(self, item):
        value = super(WrapperTest, self).__getitem__(item)
        wrapper_data = self.notify_external(item, 'getitem', value)
        return WrapperTest.will_wrap(value, wrapper_data=wrapper_data)

    def __setitem__(self, item, value):
        if isinstance(value, WrapperTest):
            super(WrapperTest, self).__setitem__(item, value.__wrapped__)
        else:
            super(WrapperTest, self).__setitem__(item, value)

    def __getattr__(self, name):
        value = super(WrapperTest, self).__getattr__(name)
        wrapper_data = self.notify_external(name, 'getattr', value)
        return WrapperTest.will_wrap(value, wrapper_data=wrapper_data)

    def __setattr__(self, name, value):
        if isinstance(value, WrapperTest):
            super(WrapperTest, self).__setattr__(name, value.__wrapped__)
        else:
            super(WrapperTest, self).__setattr__(name, value)

    def __copy__(self):
        return WrapperTest.will_wrap(copy.copy(self.__wrapped__))

    def __deepcopy__(self, memodict={}):
        return WrapperTest.will_wrap(copy.deepcopy(self.__wrapped__, memodict))

    def __iter__(self):
        self._self_iter_idx = 0
        self._self_iter = iter(self.__wrapped__)
        return self

    def __next__(self):
        value = next(self._self_iter)
        wrapper_data = self.notify_external(self._self_iter_idx, 'iter', value)
        self._self_iter_idx += 1
        return WrapperTest.will_wrap(value, wrapper_data=wrapper_data)

    def notify_external(self, signature, event_name, value):
        is_callable = False
        data_type = 'undefined'
        if value is not None:
            if isinstance(value, WrapperTest):
                value = value.__wrapped__
            is_callable = callable(value)
            data_type = type(value)

        if self._self_wrapper_data:
            wrapper_data = WrapperData.of(signature, self._self_wrapper_data)
            self._self_wrapper_data.manager.notify(DataEvent(wrapper_data.signature, event_name, value, data_type,
                                                             is_callable))
            return wrapper_data
        return self._self_wrapper_data

    @staticmethod
    def wrap_kwargs(kwargs, wrapper_data=None):
        for argname, argvalue in kwargs.items():
            kwargs[argname] = WrapperTest.will_wrap(argvalue, wrapper_data=WrapperData.of(argname, wrapper_data))
        return kwargs

    @staticmethod
    def unwrap(obj):
        if obj is not None and isinstance(obj, WrapperTest):
            return obj.__wrapped__
        return obj

    @staticmethod
    def will_wrap(obj, wrapper_data=None):
        if isinstance(obj, _simple_types):
            return obj
        return WrapperTest(obj, wrapper_data=wrapper_data)

    def __call__(self, *args, **kwargs):
        value = self.__wrapped__(*args, **kwargs)
        wrapper_data = self.notify_external(None, 'return', value)
        return WrapperTest.will_wrap(value, wrapper_data=wrapper_data)


class WrapperData(object):
    def __init__(self, manager, signature):
        self.manager = manager
        self.signature = signature

    @staticmethod
    def of(signature, wrapper_data):
        if not wrapper_data:
            return WrapperData(DataManagerAdapter(), WrapperData.get_signature_from_obj(signature, '?'))
        if wrapper_data.signature is not None:
            if signature is not None:
                signature = WrapperData.signature_join(wrapper_data.signature, signature)
            else:
                signature = WrapperData.get_signature_from_obj(wrapper_data.signature)
        else:
            signature = WrapperData.get_signature_from_obj(signature, '?')
        manager = wrapper_data.manager if wrapper_data.manager is not None else DataManagerAdapter()
        return WrapperData(manager, signature)

    @staticmethod
    def get_signature_from_obj(obj, default=None):
        signature = default
        if obj is not None:
            if isinstance(obj, _simple_types):
                signature = str(obj)
            else:
                signature = type(obj).__name__
        return signature

    @staticmethod
    def signature_join(*args):
        signature_list = []
        for arg in args:
            if arg is not None:
                signature_list.append(WrapperData.get_signature_from_obj(arg))
        if len(signature_list) == 0:
            return None
        else:
            return ' '.join(signature_list)
