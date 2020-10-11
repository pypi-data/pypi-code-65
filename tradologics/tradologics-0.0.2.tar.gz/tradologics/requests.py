import requests as _requests

_BASE_URL = "https://api.tradologics.com"
_TOKEN = None
_TIMESTAMP = None
_DEFAULT_TIMEOUT = 5


def set_token(token):
    global _TOKEN
    _TOKEN = token


def _set_timestamp(ts):
    global _TIMESTAMP
    _TIMESTAMP = ts


def _bearer_token():
    if not _TOKEN:
        raise Exception("Please use `set_token(...)` first.")
    return {"Authorization": "Bearer {token}".format(token=_TOKEN)}


def _full_url(slug):
    return "{url}/beta/{slug}".format(url=_BASE_URL, slug=slug.strip("/"))


def _kwargs(kwargs):
    if "timeout" not in kwargs:
        kwargs["timeout"] = _DEFAULT_TIMEOUT
    if "headers" not in kwargs:
        kwargs["headers"] = _bearer_token()
    return kwargs


def get(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _full_url(endpoint), kwargs
    return _requests.get(_full_url(endpoint), **kwargs)


def post(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _requests.post(_full_url(endpoint), **kwargs)


def patch(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _requests.patch(_full_url(endpoint), **kwargs)


def put(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _requests.put(_full_url(endpoint), **kwargs)


def delete(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _requests.delete(_full_url(endpoint), **kwargs)


def options(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _requests.options(_full_url(endpoint), **kwargs)


def head(endpoint, **kwargs):
    kwargs = _kwargs(kwargs)
    return _requests.head(_full_url(endpoint), **kwargs)
