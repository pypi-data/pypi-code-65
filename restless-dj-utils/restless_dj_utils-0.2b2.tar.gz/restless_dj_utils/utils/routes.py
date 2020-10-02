"""
Util to add rutes to restless resources
"""
from copy import deepcopy

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt


def routes(*configs):
    """
    A class decorator that adds extra routes to the resource.

    Usage:

        @routes(('POST', r'url_pattern/$', 'new_method1'),
                ('POST', r'url_pattern/$', 'new_method2'),
                (('GET', 'POST'), r'url_pattern/$', 'new_method2'))
        class MyResource(Resource):
            def new_method1(self):
                pass
            def new_method2(self):
                pass
    """

    def decorator(cls):
        old_init = getattr(cls, "__init__")
        # Copy http_methods to resource subclass
        cls.http_methods = deepcopy(cls.http_methods)

        def __init__(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            for methods, __, target in configs:
                if isinstance(methods, str):
                    methods = (methods,)
                conf = {}
                for method in methods:
                    conf[method] = target
                self.http_methods[target] = conf

        cls.__init__ = __init__

        old_urls = getattr(cls, "urls")

        @classmethod
        def urls(cls, name_prefix=None):
            urls = old_urls(name_prefix=name_prefix)
            for __, path_regex, target in configs:
                name = cls.build_url_name(target, name_prefix)
                view = csrf_exempt(cls.as_view(target))
                urls.insert(0, url(path_regex, view, name=name))
            return urls

        cls.urls = urls

        return cls

    return decorator
