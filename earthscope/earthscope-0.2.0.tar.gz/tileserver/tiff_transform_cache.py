from datetime import datetime
import logging
from typing import Tuple, Callable, Union

from .tiff_io import read_tiff, write_tiff, sniff_tiff

logger = logging.getLogger(__name__)

MAX_CACHE_LEN = 10

# tiff_transform_cache maps from a tuple to a tuple:
# (tiff_path, transform) : (transformedTiffFile, whenTransformed)
tiff_transform_cache = {}

to_key = lambda tiff_path, transform: (tiff_path, transform)

get_oldest_transform = lambda: min(tiff_transform_cache, key=lambda i: i[1])

def get(tiff_path, transform):
    key = to_key(tiff_path, transform)
    try:
        file, when = tiff_transform_cache[key]
        return file.name
    except KeyError:
        return None

def transform(tiff_path, transform_chain: Tuple[Callable]):
    im_data, im_profile = read_tiff(tiff_path)
    
    # Now apply each transform_func, one by one, passing each the
    # output of the previous
    for transform_func in transform_chain:
        im_data, im_profile = transform_func(im_data, im_profile)

    result_tiff_file = write_tiff(im_data, im_profile, source_tiff_path=tiff_path)

    if not result_tiff_file:
        raise Exception("Transform did not return a valid tiff file")

    key = to_key(tiff_path, transform_chain)
    tiff_transform_cache[key] = (result_tiff_file, datetime.now)
    
    # Now drop oldest item from the cache until its small enough
    while len(tiff_transform_cache) > MAX_CACHE_LEN:
        del tiff_transform_cache[get_oldest_transform()]
        
    return result_tiff_file.name

def pretty_print(transform_chain):
    return " | ".join([ transform_func.__name__ for transform_func in transform_chain ])

def transform_if_needed(tiff_path, transform_chain: Tuple[Callable], skip_transform_if: Callable = None):
    if cached_tiff_path := get(tiff_path, transform_chain):
        logger.info(f"CACHE HIT: {tiff_path} | {pretty_print(transform_chain)}")
        return cached_tiff_path

    if skip_transform_if:
        if sniff_tiff(tiff_path, skip_transform_if):
            logger.info(f"CACHE SKIP TRANSFORM: {tiff_path} | {pretty_print(transform_chain)}")
            return tiff_path
        else:
            logger.info(f"CACHE MISS: {tiff_path} | {pretty_print(transform_chain)}")
            return transform(tiff_path, transform_chain)
