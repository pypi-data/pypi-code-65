from functools import wraps

from sym.awslambda.dispatch import register


def sym_action(action):
    """Declare a handler for a Sym action.

    Only one handler is supported per action.
    """

    def decorator(f):
        register(action, f)

        @wraps(f)
        def wrapped(*args, **kwargs):
            f(*args, **kwargs)

    return decorator
