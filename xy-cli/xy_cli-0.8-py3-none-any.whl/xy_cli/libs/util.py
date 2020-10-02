import re
from datetime import date, datetime
import decimal

non_url_safe = ['"', '#', '$', '%', '&', '+',
                ',', '/', ':', ';', '=', '?',
                '@', '[', '\\', ']', '^', '`',
                '{', '|', '}', '~', "'"]

translate_table = {ord(char): u'' for char in non_url_safe}
non_url_safe_regex = re.compile(
    r'[{}]'.format(''.join(re.escape(x) for x in non_url_safe)))

def slugify(text):
    text = text.translate(translate_table)
    text = u'_'.join(text.split())
    return text


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError ("Type %s not serializable" % type(obj))