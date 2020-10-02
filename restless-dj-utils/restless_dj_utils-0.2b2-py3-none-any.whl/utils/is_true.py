def is_true(value):
    """
    Helper function for getting a bool form a query string.
    """

    if hasattr(value, "lower"):
        return value.lower() not in ("false", "0")
    return bool(value)
