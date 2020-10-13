from decimal import Decimal, ROUND_HALF_UP
import urllib.parse as urlparse
from urllib.parse import urlencode


def round(f):
    return Decimal(f'{f}').quantize(0, ROUND_HALF_UP).__int__()


def add_url_query(url, **extra):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(extra)

    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)
