"""
Resource mixin to help with NewRelic intergration
"""
from newrelic import agent


class NewRelicResourceMixin:
    def handle(self, endpoint, *args, **kwargs):
        """
        This is to make sure that for NewRelic transactions we don't get
        _wrapper and we get the method name instead
        :param endpoint:
        :param args:
        :param kwargs:
        :return:
        """

        try:
            method_name = self.http_methods[endpoint][self.request_method()]
            view_method = getattr(self, method_name)
        except KeyError:
            pass
        else:
            name = agent.callable_name(view_method)
            if name.endswith("._wrapper"):
                name = name.replace("._wrapper", method_name)
            agent.set_transaction_name(name)

        return super().handle(endpoint, *args, **kwargs)
