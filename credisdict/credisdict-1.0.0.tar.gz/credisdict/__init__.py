"""
Created on June 16 2020

@author: Joan Hérisson
"""

from brs_utils  import print_OK, print_FAILED
from credisdict.CRedisDict import CRedisDict, wait_for_redis

__all__ = ('CRedisDict', 'wait_for_redis', 'print_OK', 'print_FAILED')
