"""
fidx: a module for float and custom indexes in Python.
version 1.0.0
MIT LICENSE
© Davide Peressoni 2020

>>> fidx([1,2,3])[.5]
2
>>> l = fidx([1,2,3,4])
>>> l[:.5], l[.5:]
([1, 2], [3, 4])

>>> t = fidx.tuple(i//2 for i in range(0,10))
>>> t[.2:-.2:.2]
(1, 2, 3)
"""

import sys
from typing import Sequence, Optional, Union, Callable, Type, List, Tuple, TypeVar
from collections import defaultdict

Idx = Union[int, float, slice] # Type for indexes

_T, _U = TypeVar('T'), TypeVar('U')
def float_idx(s:Sequence, i:Optional[Union[Idx, _T]], types:Sequence[type] = tuple()) -> Optional[Union[int, _T, _U]]:
  """
  Converts float indexes into integer indexes.
  
  :param s: object on which apply the index.
  :param i: the index to convert.
  :param types: additional types accepted as index by s (optional).
  
  :return: the converted index.
  
  :raises: TypeError if the type of i is not `Idx` or in `types`
  """
  if hasattr(s, '_index_map') and type(i) in s._index_map.keys():
    return s._index_map[type(i)](s, i)
  allowed_types = set((*types, *_global_types))
  if type(i) in allowed_types:
    return _index_map[type(i)](s, i)
  if type(i) ==float:
    if abs(i)<1: return int(i*len(s)) # percentage
    else: return int(i)
  if type(i) == slice:
    return slice(
      float_idx(s, i.start), 
      float_idx(s, i.stop), 
      float_idx(s, i.step)
    )
  raise TypeError(f'Type {type(i)} not allowed as index. Allowed types are: {(type(None), int, float, slice, *allowed_types)}.')

# Global types for indexes to pass as they are or to map
_global_types: List[Type] = [type(None), int]
# Dictionary of index maps
_index_map = defaultdict(lambda:lambda _, x : x)

def set_index_map(t:Type[_T], f:Callable[[Sequence,Optional[_T]],Optional[Union[_T,_U]]], override:bool = False, global_map:bool = False) -> None:
  """
  Set a map for casting indexes.
  If the map is not set for a certain type, the indexes of that type will pass as they are.
  
  :param t: the type to cast from.
  :param f: the function which maps indexes of type `t`. The first argument passed to `f` is the Sequence object, the second the index to map.
  :param override: see :raises: below (default False).
  :param global_map: apply for all types. (default False).
  
  :warning: Setting a map for type T doesn't mean that `float_idx` will accept automatically type T as index: you have to pass T in the `types` argument of `float_idx` when you want to accept T as index or set the `globa_map` flag to True.
  
  :raises: TypeError if you try to override a map for a type in `(int, float, tuple, range, type(None))` without flag `override=True`.
  """
  if not override and t in (int, float, tuple, range, type(None)):
    raise TypeError(f'The map for indexes of type {t} can not be overridden.')
  _index_map[t] = f
  if global_map:
    _global_types.append(t)

# Maps each tuple item with float_idx. 
# (0,)*j creates a tuple of j zeros and allows to access the (j+1)-esim dimension of s.
set_index_map(tuple, lambda s, i : tuple(float_idx(s[(0,)*j], e) for j,e in enumerate(i)), override=True)

def param(*idx:Union[Idx, str], types:Sequence[type] = tuple()):
  """
  Decorator to add `fidx` support to a function.
  The first argument of the function to decorate must be the Sequence object to which the indexes have to apply.
  
  :param idx: list of positional arguments (numbered from 0) on which apply `float_idx`; defaults (1,). You can also specify the name for keyword arguments.
  :param types: additional types accepted as index (optional).
  
  Usage: 
  .. code-block:: python
  
    @fidx.param()
    def myfunction(self, ....): ....

  Example:
  .. code-block:: python
  
    @fidx.param(1, 2)
    def sum(a, i, j): a[i]+a[j]
    
  You could use float indexes as well:
  .. code-block:: python
  
    @fidx.param(.5, .9)
    def sum(a, i, j): a[i]+a[j]
    
  You could use keyword arguments, too:
  .. code-block:: python
  
    @fidx.param(1, 2, 'i', 'j')
    def sum(a, i = 0, j = 0): return a[i]+a[j]
  """
  if len(idx) == 0:
    idx = (1,) # default index list
    
  def g(f:Callable, args, kwargs):
    for i in idx:
      # args[0] is the Sequence object
      if type(i) == str:
        if i in kwargs.keys():
          kwargs[i] = float_idx(args[0], kwargs[i], types)
      elif i < len(args): # discard missing optional arguments
        args[i] = float_idx(args[0], args[i], types)
    return f(*args, **kwargs)
  
  def h(f):
    def l(*args, **kwargs): return g(f, list(args), kwargs)
    # propagate the method name in order to use @add_method
    l.__name__ = f.__name__
    return l  
  
  return h

###############################################################################
######################### Extension of standard types #########################
###############################################################################

class self_type:
  """
  Blank class.
  Can be used in the `types` argument of `add` function as a placeholder to refer to the new extend type itself.
  Example:
  .. code-block:: python

    fidx.add(my_class, types=(tuple, my_class, fidx.self_type))
    
  If `my_class` accepts also `tuples` and itself as index type, we want `fidx.my_class` to accept them and `fidx.my_class` (marked by `fidx.self_type`) as well.
  """
  pass

def _fSequence(cls:Type[Sequence], types:List[type] = tuple()):
  """
  Class which extends a Sequence with fidx support.
  """
  class k(cls):
    _index_map = dict()
    @classmethod
    def set_index_map(cls, t:Type[_T], f:Callable[[Sequence, Optional[_T]],Optional[Union[_T,_U]]], override:bool = False) -> None:
      """
      Set a map for casting indexes.
      If the map is not set for a certain type, the indexes of that type will pass as they are.
      
      :param t: the type to cast from.
      :param f: the function which maps indexes of type `t`. The first argument passed to `f` is the Sequence object, the second the index to map.
      :param override: see :raises: below (default False).
      
      :raises: TypeError if you try to override a map for a type in `(int, float, tuple, range, type(None))` without flag `override=True`.
      """  
      if not override and t in (int, float, tuple, range, type(None)):
        raise TypeError(f'The map for indexes of type {t} can not be overridden.')
      cls._index_map[t] = f
        
    # propagate class name
    __qualname__ = cls.__qualname__ 
  k.__name__ = k.__qualname__
    
  # Finds and replace the self_type placeholder.
  fidx_types = tuple(k if t == self_type else t for t in types) 
  
  # Decorator to add a new method to a class
  def add_method(cls):
    def g(f):
      setattr(cls, f.__name__, f)
    return g
    
  @add_method(k)
  @param(types=fidx_types)
  def __getitem__(self, i):
    return cls.__getitem__(self, i)
  
  @add_method(k)
  @param(types=fidx_types)
  def __delitem__(self, i):
    cls.__delitem__(self, i)
    
  @add_method(k)
  @param(types=fidx_types)
  def insert(self, i, v):
    cls.insert(self, i, v)
    
  @add_method(k)
  @param(types=fidx_types)
  def __setitem__(self, i, v):
    cls.__setitem__(self, i, v)
    
  @add_method(k)
  @param(2,3, types=fidx_types) # (self, e, [start, [end]])
  def index(self, *args):
    return cls.index(self, *args)
    
  return k

# List of pairs (standard type, extended type) for autocast
_types:List[Tuple[Type[Sequence]]] = list()

def fidx (*args, **kwargs):
    """
    Automatically casts an object to the extended version with float indexes.
    The object type must be registered with the `add` function.
    The types `list`, `tuple`, `str`, `bytes` and `bytearray` are already registered.
    Also `array` is automatically registered if its module is loaded before `fidx`.
    For `numpy` see `add_numpy`.
    
    :param: the object to cast followed by optional initialization arguments.
    
    :return: the casted object.
    
    :raises: TypeError if the original type is not registered.
    """
    if len(args) == 0:
      raise ValueError('Missing mandatory argument.')
    e:Sequence = args[0]
    t = type(e)
    for std_t, f_t in _types:
      if t == std_t:
        return f_t(*args, **kwargs)
          
    else: raise TypeError(f'Type {t} not supported in fidx. You can add it using `fidx.add({t.__name__})`.')

class _fidx(sys.modules[__name__].__class__):
  """
  Class for module management.
  """
  class std:pass

  def __call__ (self,*args, **kwargs): return fidx(*args ,**kwargs)
    
def add(t:Type[Sequence], types:Sequence[type] = tuple(), classes:Sequence[type] = tuple(), name:str = None) -> None:
  """
  Registers a Sequence type for use it with float indexes.
  To cast an object to its extended version you could use autocast (see `fidx`) or the classes in `fidx` with the same name of the original ones.
  Original classes are stored into the `std` namespace.
  Example:
  .. code-block:: python
  
    fidx.add(my_class)
    a = fidx(my_class(...))
    b = fidx.my_class(...)
    assert a == b
    assert my_class == fidx.std.my_class
    
  :param t: type to register.
  :param types: additional types accepted as index (optional).
  :param classes: additional classes accepted to cast from (optional).
  :param name: custom name for the extended class (optional).
  """
  tn = t.__name__
  etn = tn if name is None else name
  
  if tn  == 'numpy' or hasattr(t,'__module__') and t.__module__ == 'numpy':
    add_numpy()
    return
  
  if etn[0]=='_':
    raise ValueError(f'Name `{etn}` not accepted.') 
  if etn in _fidx.__dict__.keys():
    raise AttributeError(f'Attribute `{etn}` already exists.')
  
  # save original type in `std`
  setattr(_fidx.std, tn, t)
  # create extended type
  c = _fSequence(t, [*types])
  # save extended type
  setattr(_fidx, etn, c)
  # register pairs for autocast
  # there is also the pair (c, c) to allow creating a new object starting from an extended class
  for k in [t, c, *classes]:
    _types.append((k, c))

# Register standard types.
for t in (list, tuple, str, bytes, bytearray):
  #TODO add support for `range` and `memoryview`
  add(t)  
  
def add_numpy() -> None:
  """
  Adds support for `numpy` `ndarray`s.
  Automatically called if `numpy` is loaded before `fidx`.
  
  :warning: `numpy` `ndarray` extended version is called `fidx.nparray`: note the 'p' instead of the 'd' (NumPy array).
  """
  import numpy as np
  class _nparray(np.ndarray):
    # Due to numpy implementation it is needed to override __new__ in order to get an object of the extended type
    def __new__(cls, arr:np.ndarray = np.array([])): 
      if type(arr) == list:
        arr = np.array(arr)
      return arr.view(_fidx.nparray)
    __qualname__ = 'nparray'
  _nparray.__name__ = _nparray.__qualname__
  add(_nparray, types=(tuple, self_type, np.ndarray, type(...)), classes=(np.ndarray,))

# Register common types if imported.
if 'numpy' in sys.modules: add_numpy()
if 'array' in sys.modules: 
  import array
  add(array.array)

# Add class to module.
sys.modules[__name__].__class__ = _fidx
  
###############################################################################
##################################### Main ####################################
###############################################################################

if __name__ == '__main__':
  import doctest
  doctest.testmod(globs={'fidx':sys.modules[__name__]})
  help(sys.modules[__name__]) 
