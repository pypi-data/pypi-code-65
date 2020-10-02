from functools import wraps

from ratelimit import ALL, UNSAFE
from ratelimit.exceptions import Ratelimited
from ratelimit.utils import is_ratelimited


def restless_ratelimit(group=None, key=None, rate=None, method=ALL, block=False):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(*args, **kw):
            """
            Work as restless API entry point decorator

            Example of usage
            class DummyResource(BaseResource):
                @restless_ratelimit(key='ip', rate='100/h')
                def list(self):
                    # Some logic that is needed to be ratelimited
                    return

            """
            request = args[0].request  # Get request Resource object attribute
            request.limited = getattr(request, "limited", False)
            ratelimited = is_ratelimited(
                request=request,
                group=group,
                fn=fn,
                key=key,
                rate=rate,
                method=method,
                increment=True,
            )
            if ratelimited and block:
                raise Ratelimited()
            return fn(*args, **kw)

        return _wrapped

    return decorator


restless_ratelimit.ALL = ALL
restless_ratelimit.UNSAFE = UNSAFE


def is_user_ratelimited(request, user_value, **kwargs):
    """
    Helper function to validate if user is ratelimited. Wraps `is_ratelimited`
    of Django's ratelimit lib
    :param request: The request object
    :param user_value: Unique value. E.g.: email, phone, uuid
    :return: True or false
    """

    def get_user_value(*args):
        return user_value

    return is_ratelimited(request=request, key=get_user_value, **kwargs)
