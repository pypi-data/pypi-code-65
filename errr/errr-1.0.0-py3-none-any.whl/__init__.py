from .exception import DetailedException
from .tree import make_tree, exception

__version__ = "1.0.0"

def wrap(type, e, *details, prepend=None, append=None):
    interpolator = type("", *details)
    msg = ""
    if hasattr(interpolator, "interpolate"):
        if prepend is not None:
            msg = interpolator.interpolate(prepend)
        msg += str(e)
        if append is not None:
            msg += interpolator.interpolate(append)
    else:
        if prepend is not None:
            msg = prepend
        msg += str(e)
        if append is not None:
            msg += append
    err = type(msg, *details)
    err.__traceback__ = e.__traceback__
    raise err from None
