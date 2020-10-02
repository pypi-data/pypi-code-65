# _*_coding:utf-8_*_
#################
# 不再写if else  #
#################
import abc
from functools import wraps


class HandleBaseAbstract(metaclass=abc.ABCMeta):

    def register(self, *args, **kwargs):
        raise NotImplementedError

    def unregister(self, *args, **kwargs):
        raise NotImplementedError

    def invoke(self, *args, **kwargs):
        raise NotImplementedError


class HandleBase(HandleBaseAbstract):

    def __init__(self):
        self.__strategy_handles_mapping = {}

    def register(self, strategy, *register_args, **register_kwargs):
        # print(strategy, register_args, register_kwargs)
        # print(args)
        # print(register_kwargs)

        def _set_register(func):
            # print(func.__name__)
            if strategy in self.__strategy_handles_mapping:
                self.__strategy_handles_mapping[strategy].update({func.__name__: func})
            else:
                self.__strategy_handles_mapping.update({strategy: {func.__name__: func}})

            @wraps(func)
            def wrap(self, *args, **kwargs):
                """
                此处必须要有 *args, **kwargs 不然具名路由或者参数路由会出现问题
                :param self:
                :param args:
                :param kwargs:
                :return:
                """
                # print('register_args, register_kwargs', register_args, register_kwargs)
                # print('args, kwargs', args, kwargs)
                try:
                    # 管理端登录
                    return func(self, *args, **kwargs)

                except Exception as _e:
                    print(_e)

            return wrap
        return _set_register

    def unregister(self, strategy) -> bool:
        if strategy in self.__strategy_handles_mapping:
            self.__strategy_handles_mapping.pop(strategy)
            return True
        return False

    def remove_handle(self, strategy, handle) -> bool:
        if strategy in self.__strategy_handles_mapping[strategy]:
            if handle in self.__strategy_handles_mapping[strategy]:
                self.__strategy_handles_mapping[strategy].pop(handle)
                return True
        return False

    def invoke(self, strategy, handle):
        return self.__strategy_handles_mapping[strategy][handle]

    def __repr__(self):
        return f'{self.__strategy_handles_mapping}'


handle_base = HandleBase()
# print('handle_base:', handle_base)

