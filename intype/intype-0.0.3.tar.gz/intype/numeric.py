def is_numeric(x):
    if isinstance(x, float): return True
    if isinstance(x, int): return True
    if isinstance(x, str): return is_string_numeric(x)  # x.strip().replace('.', '').isnumeric()
    return False


def is_string_numeric(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
