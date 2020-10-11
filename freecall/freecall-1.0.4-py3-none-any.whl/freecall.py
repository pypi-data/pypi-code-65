import functools
import json
import logging
import shelve
import sys
import zlib
import dill
import dbm
import traceback

__CACHE_NAME__ = "freecall.shelf"


def set_cache_file(new_cache_file: str) -> None:
    """
    Changes the storage location of the cache. Directly used by shelve.open, and hence has the same possible side-effects of extensions or multiple file creation.
    :param new_cache_file: The new filename for the cache.
    """
    global __CACHE_NAME__
    __CACHE_NAME__ = new_cache_file


def _parameterize_deco(deco_to_replace):
    def deco_replacement(*args, **kwargs):
        def func_replacement(func_to_replace):
            return deco_to_replace(func_to_replace, *args, **kwargs)

        return func_replacement

    return deco_replacement


def _checksum_dump(obj: object):
    return zlib.adler32(dill.dumps(obj))


@_parameterize_deco
def cache(func, force_hot: bool = False, history_limit: int = 5, disable_cache: bool = False) -> callable:
    """
    Automatically memoizes decorated functions to disk in freecall.shelf.
    :param func: Function to memoize.
    :param force_hot: Forces function to always recompute values.
    :param history_limit: Number of function calls to remember. If reduced from a previous run, will truncate history to match new limit.
    :param disable_cache: Disables the cache entirely for this function. Provided for convenience, will simply call the function and return the result.
    :return: Wrapped, memoizing function. Can be manually adjusted with force_hot_, history_limit_, and disable_cache_, corresponding to the decorator parameters.
    """

    @functools.wraps(func)
    def memo_wrapper(*args, force_hot_, history_limit_, disable_cache_=False, **kwargs, ) -> functools.partial:
        if disable_cache_:
            return func(*args, **kwargs)

        None if not force_hot_ else logging.debug(f"Calling [{func.__name__}] forcibly hot")
        func_name = func.__name__
        try:
            shelf = shelve.open(__CACHE_NAME__)
        except dbm.error:
            shelf = shelve.open(__CACHE_NAME__, "r")
            logging.warning(f"{traceback.format_exc()}\nFalling back to read-only mode")
        logging.debug("Loaded cache ")
        if "__meta_history" not in shelf:
            logging.info(f"First run, initializing shelf")
            shelf["__meta_history"] = {}

        meta_history = shelf["__meta_history"]
        if func_name not in meta_history:
            meta_history[func_name] = []

        try:
            call_parts = (func, args, kwargs)
            call_hash = str(zlib.adler32(json.dumps(call_parts, default=_checksum_dump, sort_keys=True).encode('utf-8')) & 0xffffffff)
            logging.debug(f"[{func_name}]Call hash successfully computed: {call_hash}")
            hot = force_hot_ or call_hash not in meta_history[func_name]
        except dill.PicklingError as err:
            logging.warning(f"[{func_name}] Calling cached function with invalid arguments. Defaulting to HOT. Pickle error: \n {err}")
            hot = True
            call_hash = None

        if hot:
            logging.debug(f"[{func_name}] is hot, calling function")
            shelf["__meta_history"] = meta_history
            shelf.close()
            func_result = func(*args, **kwargs)
            shelf = shelve.open(__CACHE_NAME__)
            meta_history = shelf["__meta_history"]
            if call_hash is not None and call_hash not in meta_history[func_name]:
                meta_history[func_name].append(call_hash)
                # Forget old calls
                if len(meta_history[func_name]) > history_limit:
                    for call_to_forget in meta_history[func_name][:-history_limit]:
                        del shelf[call_to_forget]
                # Cache new call
                shelf[call_hash] = func_result
                shelf["__meta_history"] = meta_history
                logging.debug(f"[{func_name}] Saving call with call hash [{call_hash}]")

        else:
            logging.debug(f"[{func_name}] already saved with call hash {call_hash}, loading")
            func_result = shelf[call_hash]

        shelf.close()
        return func_result

    return functools.partial(memo_wrapper, force_hot_=force_hot, history_limit_=history_limit, disable_cache_=disable_cache)


def heat(func: callable) -> functools.partial:
    """
    Convenience method that converts a @cache decorated function to one that always recomputes
    :param func: @cache decorated function
    :return: A @cache decorated function that will always recompute the value
    """
    return functools.partial(func, force_hot_=True)


def no_cache(func: callable) -> functools.partial:
    """
    Convenience method that converts a @cache decorated function into one that bypasses the cache entirely,
    without loading or saving to it.
    :param func: @cache decorated function
    :return: A @cache decorated function that will ignore the cache entirely
    """
    return functools.partial(func, disable_cache_=True)
