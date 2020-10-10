import webbrowser
from functools import wraps

import attr


@attr.s
class TdxManager(object):
    dispatcher = attr.ib(repr=False, cmp=False)
    __tdx_section__ = None

    def docs(self):
        webbrowser.open_new_tab(
            f"https://app.teamdynamix.com/TDWebApi/Home/section/{self.__tdx_section__}"
        )


def tdx_method(method, url):
    def wrapper(f):
        f.method = method
        f.url = url

        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped

    return wrapper
