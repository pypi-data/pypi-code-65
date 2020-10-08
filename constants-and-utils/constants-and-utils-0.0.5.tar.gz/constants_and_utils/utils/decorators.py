import json


def result_to_json(func):
    """Convert result into json from a function.

    Args:
        func: Function to execute.

    Returns:
        Result json dumps.

    Examples:
        Decorate function.

        >>> @result_to_json
        ... def hello():
        ...     return {'message': 'hi'}
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, tuple) and isinstance(result[0], dict):
            result = list(result)
            result[0] = json.dumps(result[0])
            result = tuple(result)
        elif isinstance(result, dict):
            result = json.dumps(result)
        return result
    return wrapper


def debugger_handle(func):
    """Use debugger_handle decorator to show received data and response data.

    Args:
        func: Function to execute.

    Returns:
        Result handle.

    Examples:
        Decorate function.

        >>> @debugger_handle
        ... def handle():
        ...     return {'message': 'hi'}
    """

    def wrapper(self, *args, **kwargs):
        self._debugger('kwargs: {}'.format(kwargs))
        self._debugger('args: {}'.format(args))
        result = func(self, *args, **kwargs)
        self._debugger(result.__json__())
        return result
    wrapper.__doc__ = func.__doc__
    return wrapper
