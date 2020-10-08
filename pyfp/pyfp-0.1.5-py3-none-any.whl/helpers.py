from functools import wraps, update_wrapper

def min_arguments(num: int):
    fn = None
    def decorator(func):
        global fn
        fn = func
        @wraps(func)
        def inner(*args):
            if len(args) < num:
                raise TypeError(f"{func.__name__} expects at least {num} arguments. Got {len(args)}")
            return func(*args)
        
        return inner

    return update_wrapper(decorator, fn)