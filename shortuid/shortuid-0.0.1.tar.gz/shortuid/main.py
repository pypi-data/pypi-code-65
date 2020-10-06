from datetime import datetime
from string import digits, ascii_letters

def _to_base(number: int, base: int):
    """ Converts a number to any base upto base 62
    0-9 => 0-9
    a-z => 10-35
    A-Z => 36 - 61
    """
    scope = (digits + ascii_letters)[:base]
    value = ''
    while number > 0:
        value = scope[number % len(scope)] + value
        number = int(number / len(scope))
    return value

def uid(size, *prefixes):
    """
    Generates a uid based on the current timestamp, and prefixxes with any user
    """
    timestamp = int(float(datetime.now().timestamp() * 1e7))
    return "-".join([str(prefix) for prefix in prefixes]) + _to_base(timestamp, size)

def uid62(*prefixes):
    """
    Generates a UID which is case sensitive using all 62 characters
    """
    return uid(62, *prefixes)

def uid36(*prefixes):
    """
    Generates a UID which is case insensitive using only lower case characters
    """
    return uid(62, *prefixes)


if __name__ == "__main__":
    print(uid(62))