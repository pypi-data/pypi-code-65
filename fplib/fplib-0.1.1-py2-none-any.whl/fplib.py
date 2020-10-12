# -*- coding: utf-8 -*-
"""
A set of functions to program in python in a more functional style. 

******************************************
*f*\ unctional *p*\ rogramming *lib*\ rary
******************************************

Functions
*********

General-purpose
===============

.. autosummary::
   dictf
   dictfd
   dictfdf
   mapf
   filterf
   comp
   rcomp
   nest
   idf
   constf   

Dictionaries
============

.. autosummary::
   mapdictv
   mapdictk
   mapdictkvkv
   filterdictk
   filterdictv
   flip_dict
   update_dict


List-valued dictionaries
========================

.. autosummary::
   listvaldict
   flip_listvaldict
   listvaldict_eq

Structure
=========

.. autosummary::
   unlist1
   relist1

Function application
====================

.. autosummary::
   npify
   denpify

Selectors
=========

.. autosummary::
   fst
   snd
   thr
   last
   nofirst
   nolast

Predicates
==========

.. autosummary::
   zerolenp

Zipping
=======

.. autosummary::
   zipe
   ezip

Lists
=====

.. autosummary::
   heads
   tails
   sliding_window

Tuples
======

.. autosummary::
   flip
   
Enumerations
============

.. autosummary::
   lenum
   renum
   
Mapping
=======

.. autosummary::
   emap
   deepmap
   cachedmap
   
Filtering
=========

.. autosummary::
   dfilter

Functionalized operations
=========================

.. autosummary::
   sjoin

Curried functions
=================

.. autosummary::
   startswithf
   replacef
   splitf
   fmtf
   hasf
   nothasf

Lookup
======

.. autosummary::
   isinsetf
"""

#%% Modules
import itertools as _it
import collections as _collections
from functools import reduce as _reduce

#%% * General-purpose functions
def idf(x):
  """
  Returns the identity function. 
  
  The identity function returns the element with which the function was applied. 
  
  .. note:: Useful commonly as an identity element of a function composition. 

  Parameters
  ----------  
  x : any
    Element to apply the function with.

  Returns
  -------
  x : any
    The same element as `x`.
  
  Examples
  --------
  
  >>> idf(1)
  1
  >>> idf([])
  []
  """  
  return x


def constf(x):
  """
  Returns a constant function.
  
  Suppose 
    `f` = :code:`constf(x)`.
  
  Then, if `f` is applied with any `y`, it returns `x`. 
  
  Examples
  --------
  
  >>> f = constf(10)  
  >>> f([])
  10
  >>> f(3)
  10
  
  """
  return lambda _: x


def dictf(d):
  """
  Returns a function with the behavior defined by a dictionary.
  
  Suppose a dictionary `d`, and `f` = :code:`dictf(d)`. 
  
  Then, for a given `x`, the `f(x) = d[x]`.
  
  Examples
  --------
  
  Consider a simple dictionary. 
  
  >>> d = {0: False, 1: True}  
  
  We can use it directly to get the values like:
  
  >>> dictf(d)(0)
  False
  
  Furthermore, we can easily combine it with other functions, e.g., 
  with the :func:`map`.
  
  >>> map(dictf(d), [0, 1, 0])  
  [False, True, False]
  
  """
  return lambda x: d[x]


def dictfd(d, default=None):
  """
  Returns a function with the behavior defined by a dictionary, 
  and a default value.

  .. note::
     This function extends :func:`dictf`. 
  
  .. seealso:: 
     :func:`dictfdf` for argument-dependent behavior over non-specified values.
  
  Examples
  --------
  
  Let us define a function `f` that returns 
  ``False`` if the argument is 0, and ``True`` otherwise. 
  
  >>> f = dictfd({0: False}, True)
  
  We can map it over a list like this:  
  
  >>> map(f, [-1, 0, 1, 2])
  [True, False, True, True]
  """
  return lambda x: d.get(x, default)


def dictfdf(d, defaultf=idf):
  """
  Returns a function with the behavior defined by a dictionary, and by a default 
  function. 

  .. note::
     This function extends :func:`dictf`. 

  .. seealso:: 
     :func:`dictfd` for a constant behavior over non-specified values.

  Examples
  --------
  Suppose having a list of colors:
  
  >>> colors = ['red', 'green', 'blue']
  
  Now, imagine you would like to change the color 'green' to 'yellow' 
  in the list:
  
  >>> map(dictfdf({'green': 'yellow'}), colors)
  ['red', 'yellow', 'blue']
  """  
  return lambda x: d[x] if x in d.keys() else defaultf(x)  


def mapf(f):
  """
  Turns a function `f` into a function over 
  lists, applying `f` to each element of the list. 
  
  Arguments
  ---------
  f : function
    The function. 
    
  Returns
  -------
  g : function
    Function that applies `f` over each element of a list. 
  
  Examples
  --------
  
  Define a function `f`:
  
  >>> f = lambda x: x + 1
  
  We apply it over a list in the following way:
  
  >>> mapf(f)([1, 2, 3])
  [2, 3, 4]
  
  """
  return lambda x: map(f, x)


def filterf(predf):
  """
  Returns a function that filters a list by a given predicate.
  
  Parameters
  ----------
  predf: function
    The predicate by which to filter.  
  
  Examples
  --------
  
  Suppose a list of lists as follows:  
  
  >>> l = [[0, 1], [1, 2, 3]]  
  
  Let us retain those elements from each list that are even:

  >>> map(filterf(lambda x: x % 2 == 1), l)  
  [[1], [1, 3]]
  
  """
  return lambda x: filter(predf, x)


def nest(f, n):
  """ 
  Returns a function `f` nested `n` times.
  
  Suppose 
  
    `g` = ``nest(f, n)``,
    
  then,     
  
    `g(x) = f(f( ... f(x) ... ))`, with `f` being applied `n` times. 
  
  Arguments
  ---------
  f : one-argument function  
    The function to nest. 
    
  n : a non-negative number
    The number of applications of `f`.
    
  Returns
  -------
  g : a function of one argument
    
  Examples
  --------

  One can use `nest`, e.g., to navigate in the directory structure.
  
  >>> import os
  >>> d = "/home/user/dir"
  >>> nest(os.path.dirname, 2)(d)
  '/home'
  
  When `n` is zero, the resulting function is the identity function. 
  
  >>> nest(os.path.dirname, 0)(d)
  '/home/user/dir'
  """  
  return _reduce(comp, [f] * n, idf)

#%% * Function composition
def _o(f, g):
  return lambda x: f(g(x))


def _compose(fs):
  return _reduce(_o, fs, idf)
  

def _rcompose(fs):
  return _compose(fs[::-1])
  

def comp(*fs):
  """ 
  Returns the composed function, functions being applied in the usual order 
  (the last one applied first). 

  Suppose `fs` refers to functions 
  
    `f_1`, `f_2`, ..., `f_n`
    
  and consider a function `g` defined as
  
    `g` = comp(`f_1`, `f_2`, ..., `f_n`). 

  Then `g(x)` behaves as follows: 
  
    `g(x) = f_1(f_2( ... (f_n(x)) ... ))`.
  
  Arguments
  ---------
  fs : functions of one argument
    The functions to compose.
  
  Returns
  -------
  g : function of one argument
    The composed function. 
  

  .. note:: If the argument list is empty, returns the identity function. 

  .. seealso:: :func:`rcomp` for composition in the reversed order.
  
  Examples
  --------  
  
  Let us define some functions first:
  
  >>> fa = lambda x: x + 2
  >>> fb = lambda x: x * 2  
  
  Then let us compose them:
  
  >>> g = comp(fa, fb)  
  
  Now we can apply the function `g`:  
  
  >>> g(10) # (10 * 2) + 2
  22

  Note the difference if we compose them in the opposite order:

  >>> h = comp(fb, fa)
  >>> h(10) # (10 + 2) * 2
  24
  """
  return _compose(fs)
  

def rcomp(*fs):
  """
  Returns the compose function, with functions being applied in 
  the `reversed` order (the first one applied first).
  
  .. seealso:: :func:`comp` for composion in the usual order. 
  """
  return _rcompose(fs)

#%% * Dictionaries
def mapdictv(f, d):
  """
  Maps a function over the *values* of a dictionary.
  
  Examples
  --------
  
  Let us define a simple dictionary:

  >>> d = {'a': 0}
  
  Now, we can map over its values:
  
  >>> mapdictv(lambda x: x + 1, d)
  {'a': 1}

  """
  return dict(map(lambda key: (key, f(d[key])), d.keys()))


def mapdictk(f, d):
  """
  Maps a function over the keys of a dictionary.

  .. note:: \
  If `f` maps different keys `k_1, ... k_n` into the same \
  key `k`, the dictionary will contain only one of them. 
  
  Examples
  --------
  
  Let us define a simple dictionary:  
  
  >>> d = {1: 'a'}
  
  >>> mapdictk(lambda x: x + 1, d)
  {2: 'a'}
  
  """
  return dict(map(lambda key: (f(key), d[key]), d.keys()))


def mapdictkvkv(kvfk, kvfv, d):
  """
  Maps two two-argument functions---having key and value 
  as arguments---over the keys and the values of a dictionary.

  Suppose a dictionary 

    `d = {k_1: v_1, ..., k_n: v_n}`.

  The function builds a dictionary `e`, with all the pairs as specified
  for the `k_i` and `v_i`:
  
    `e = { ..., kvfk(k_i, v_i): kvfv(k_i, v_i), ...}`.
  
  Arguments
  ---------
  kvfk : function of two arguments --- key and value
    A function to apply over the key and the value, giving the new `key`.
  
  kvfv : function of two arguments --- key and value
    A function to apply over the key and the value, giving the new `value`.
  
  Examples
  --------  
  
  Consider a dictionary `d`: 
  
  >>> d = {1: 'a', 2: 'b', 3: 'c'}
  
  We can, e.g., rebuild the dictionary as follows: 
  
  >>> md = mapdictkvkv(lambda k, v: k, lambda k, v: v, d)
  >>> md == d
  True
  
  We can, e.g., reverse the dictionary as follows:
  
  >>> rd = mapdictkvkv(lambda k, v: v, lambda k, v: k, d)
  >>> rd == {'a': 1, 'b': 2, 'c': 3}
  True
  """
  return dict(zip(map(npify(kvfk), d.items()), map(npify(kvfv), d.items())))


def filterdictk(f, d):
  """
  Filters a dictionary based on its keys.

  Examples
  --------

  Suppose the following predicate:
  
  >>> is_even = lambda x: x % 2 == 0
  
  Define a dictionary:   

  >>> d = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}  
  
  We can filter the dictionary by its keys:
    
  >>> filterdictk(is_even, d)
  {0: 'a', 2: 'c'}

  """
  return dict(filter(lambda pair: f(fst(pair)), d.items()))
  

def filterdictv(f, d):
  """
  Filters a dictionary based on its values.
  
  .. seealso:: :func:`filterdictk` for filtering based on the keys.
  """
  return dict(filter(lambda pair: f(snd(pair)), d.items()))


def update_dict(d, e, copy=True):
  """
  Returns a new dictionary updated by another dictionary.
  
  Examples
  --------
  
  Consider a dictionary `d` which we want to update:  
  
  >>> d = {0: 'a', 1: 'b'}

  Now consider the dictionary for update:

  >>> e = {1: 'c', 2: 'd'}
  
  We can update the `d` as follows:
  
  >>> f = update_dict(d, e)
  >>> f
  {0: 'a', 1: 'c', 2: 'd'}

  Note that the previous dictionary is unchanged:  
  
  >>> d
  {0: 'a', 1: 'b'}
  """
  if copy:  
    d = d.copy()
  d.update(e)
  return d


def flip_dict(d):
  """
  Flips the keys and the values of a dictionary.
  
  .. note:: \
  If multiple keys `k_1, ..., k_n` with the same value `v` exist, \
  only one (say, `k_i`) will be present (as a value) in the flipped dictionary. 
  
  .. seealso:: \
  For a reversible dictionary, see :func:`listvaldict`. 
  
  Examples
  --------
  >>> d = {0: 'a', 1: 'b', 2: 'c'}
  >>> flip_dict(d) == {'a': 0, 'b': 1, 'c': 2}
  True
  """
  return dict(map(flip, d.items()))


#%% * List-valued dictionaries
def listvaldict(l):
  """
  Creates a list-valued dictionary by aggregating 
  values for the same keys into a list.
  
  Examples
  --------
  >>> l = [(0, 'a'), (0, 'b'), (1, 'c')]
  >>> listvaldict(l)
  {0: ['a', 'b'], 1: ['c']}
  """
  d = dict(map(lambda x: (x, []), map(fst, l)))
  for key, val in l:
    d[key].append(val)
  return d


def flip_listvaldict(lvd):
  """
  Flips keys and values of a list-valued dictionary.
  
  Examples
  --------
  
  Define a list-valued dictionary:
  
  >>> lvd = {0: ['a', 'b'], 1: ['c'], 2: ['a']}
  
  Let's flip it.   
  
  >>> flvd = flip_listvaldict(lvd)
  >>> flvd == {'a': [0, 2], 'b': [0], 'c': [1]}
  True

  If we flip it again, we get the original one, except for the possible 
  differences in the order of the list-values. 

  >>> fflvd = flip_listvaldict(flvd)
  >>> listvaldict_eq(fflvd, lvd)
  True
  """
  fks = set(unlist1(lvd.values()))
  d = dict(map(lambda k: (k, []), fks))
  for k, vs in lvd.items():
    for v in vs:
      d[v].append(k)
  return d
  

def listvaldict_eq(lvda, lvdb):
  """
  Tests whether two list-valued dictionaries are equal (ignoring the list order).
  
  Example
  -------

  Let us define two list-value dictionaries that differ just 
  in the order of elements for particular key(s). 

  >>> lvda = {0: ['a', 'b'], 1: ['c']}
  >>> lvdb = {0: ['b', 'a'], 1: ['c']}
  >>> listvaldict_eq(lvda, lvdb)
  True
  """
  if lvda.keys() != lvdb.keys():
    return False
  counter = _collections.Counter
  return all(map(lambda key: counter(lvda[key]) == counter(lvdb[key]), lvda.keys()))
      
  
#%% * Structure
def unlist1(ll):
  """
  Flattens the outermost structure of inner lists.
  
  Examples
  --------
  
  Let us define a list of inner lists: 
  
  >>> ll = [[0, 1], [2], [], [3, 4]]
  
  Now we can unlist it:  
  
  >>> unlist1(ll)
  [0, 1, 2, 3, 4]
  
  Note that if we had multiple levels of lists, such as in this case, 
  
  >>> lll = [[[0, 1]], [2, 3]]  
  
  only one level of flattening happens. 

  >>> unlist1(lll)
  [[0, 1], 2, 3]
  
  """
  return list(_it.chain(*ll))


def relist1(unlisted, listed):
  """
  Imposes a structure on a list.
  
  Examples
  --------

  Let us define the structure of the list. 

  >>> ll = [[0, 1], [2]]
  
  Let us have an unstructured list, for which we want to 
  impose the structure. 
  
  >>> ul = ['a', 'b', 'c']
  
  Now let us impose the structure of `ll` on `ul`.

  >>> relist1(ul, ll)
  [['a', 'b'], ['c']]
  """
  if not sum(map(len, listed)) == len(unlisted):
    raise ValueError(\
      "The sum of length of listed arrays must be equal to the " \
      "length of the unlisted array.")
  ulit = iter(unlisted)
  return deepmap(lambda _: ulit.next(), listed)
  

#%% * Function application
def npify(f):
  """
  Transforms a function of multiple arguments into a function over a tuple.
	
  Suppose 
  
    `g` = :code:`npify(f)`.
    
  Then `g((arg_1, arg_2, ...)) = f(arg_1, arg_2, ...)`. 
    
  Example
  -------
  
  >>> import math
  >>> math.pow(2, 3)   
  8.0
  
  >>> f = npify(math.pow)
  >>> f((2, 3))
  8.0
  
  """
  return lambda t: f(*t)


def denpify(f):
  """
  Transforms a function over a tuple into a function over arguments.

  Suppose that 
    
    `g` = ``denpify(f)``, 
  
  then 
  
    `g(a_1, a_2, ..., a_n) = f((a_1, a_2, ..., a_n))`.
  
  Examples
  --------
  
  >>> flip((0, 1))
  (1, 0)
  
  >>> f = denpify(flip)
  >>> f(0, 1) # note the the argument is *not* a tuple
  (1, 0)
  """
  return lambda *t: f(t) 


#%% * Selectors
def fst(x):
  """
  Returns the first item of a collection.
  
  Examples
  --------
  >>> fst([0, 1, 2])
  0
  """
  return x[0]


def snd(x):
  """ 
  Returns the second item of a collection.
  
  Examples
  --------
  >>> snd([0, 1, 2])
  1
  """
  return x[1]


def thr(x):
  """
  Returns the third item of a collection.
  
  Examples
  --------
  >>> thr([0, 1, 2])
  2
  """
  return x[2]
  
  
def last(l):
  """
  Returns the last element of a collection.

  .. note::
    Useful when we do not want to have numbers in the code. 
    Furthermore, it can be directly used in the function composition.
  
  Examples
  --------
  
  >>> last([1, 2, 3])
  3
  """
  return l[-1]
  

def nofirst(l):
  """
  Returns a collection without its first element.
  
  Examples
  --------
  >>> nofirst([0, 1, 2])
  [1, 2]
  >>> nofirst([])
  []
  """
  return l[1:]


def nolast(l):
  """
  Returns a collection without its last element.
  
  Examples
  --------
  >>> nolast([0, 1, 2])
  [0, 1]
  >>> nolast([])
  []
  """
  return l[:-1]


#%% * Predicates
def zerolenp(e):
  """
  Tests whether the `len` of an object is 0.
  
  Examples
  --------
  >>> zerolenp([])
  True
  >>> zerolenp('')
  True
  >>> zerolenp([0])
  False
  """
  return len(e) == 0
  

#%% * Zipping
def zipe(l, e):
  """
  Zips an element on the right side of a collection.
  
  Examples
  --------

  Let us define a list `l`:  
  
  >>> l = [0, 1, 2]  
  
  Let us zip an element 'id' on the right side of each element in `l`.
  
  >>> zipe(l, 'id')
  [(0, 'id'), (1, 'id'), (2, 'id')]
  
  .. seealso:: :func:`ezip` for zipping the element from the left side. 
  """
  return map(lambda x: (x, e), l)


def ezip(e, l):
  """
  Zips an element on the left side of a collection.
  
  Examples
  --------
  Let us define a list `l`:
  
  >>> l = [0, 1, 2]
  
  Let us zip an element 'id' for each element of the l.
  
  >>> ezip('id', l)
  [('id', 0), ('id', 1), ('id', 2)]
  
  """
  return map(lambda x: (e, x), l)


#%% * Mapping
def emap(f, l):
  """
  Maps a function over a list, returning both the argument and the result.
  
  Examples
  --------
  >>> f = lambda x: x + 1
  >>> emap(f, [0, 1, 2])
  [(0, 1), (1, 2), (2, 3)]
  """  
  return map(lambda e: (e, f(e)), l)
  

def deepmap(f, dl):
  """
  Performs a deep map over deeply nested list.
  
  Examples
  --------
  
  Let us define a deep list:
  
  >>> dl = [0, 1, [2, [3], 4]]
  
  Now we can apply the function over each leaf of the list:
  
  >>> deepmap(lambda x: x + 1, dl)  
  [1, 2, [3, [4], 5]]
  """
  if isinstance(dl, list):
    return map(lambda x: deepmap(f, x), dl)
  else:
    return f(dl)


def cachedmap(f, xs):
  """
  Caches a function on the unique elements, then maps it over a list.
  
  .. note:: Uses internally :func:`set` to get unique elements. 
  
  Examples
  --------  
  
  >>> def f(x): print("f called with %d" % x); return x

  >>> cachedmap(f, [0, 0, 1, 2])
  f called with 0
  f called with 1
  f called with 2
  [0, 0, 1, 2]
  """
  return map(_precachef(f, xs), xs)


def _precachef(f, xs):
  """
  Returns a function whose results are cached on specified arguments.
  
  Examples
  --------
  
  Let us first define a function with a side effect of 
  printing out about its application:
  
  >>> def f(x): print("f called with %d" % x); return x
  
  Precache the function:  
  
  >>> g = _precachef(f, [0, 1, 2])
  f called with 0
  f called with 1
  f called with 2
  
  Use the function on precached elements: 
  
  >>> map(g, [0, 1])
  [0, 1]
  
  Use the function also on the non-precached elements: 
  
  >>> map(g, [2, 3])
  f called with 3
  [2, 3]
  """
  return dictfdf(dict(emap(f, set(xs))), f)


#%% * Lists
def heads(l):
  """
  Returns all prefixes of a list.
  
  Examples
  --------
  >>> heads([0, 1, 2])
  [[], [0], [0, 1], [0, 1, 2]]
  """
  return map(lambda i: l[:i], range(len(l) + 1))


def tails(l):
  """
  Returns all suffixes of a list.
  
  Examples
  --------
  >>> tails([0, 1, 2])
  [[0, 1, 2], [1, 2], [2], []]
  """
  return map(lambda i: l[i:], range(len(l) + 1))


def sliding_window(l, n):
  """
  Creates a sliding window of given length over a list.
  
  Examples
  --------
  >>> l = range(5)
  >>> sliding_window(l, 2)
  [[0, 1], [1, 2], [2, 3], [3, 4]]
  """
  rngs = range(0, len(l) - n + 1)
  return map(lambda rng: l[rng:rng + n], rngs)  


def dfilter(f, l):
  """
  Splits the list into two sublists depending on the fulfilment of a criterion. 
  
  Examples
  --------

  Define a function which tests whether an argument is even number. 

  >>> is_even = lambda x: x % 2 == 0

  Now we can split the list like this: 

  >>> dfilter(is_even, [0, 1, 2, 3, 4, 5])
  ([0, 2, 4], [1, 3, 5])
  """  
  true  = []
  false = []
  for e in l:
    if f(e):
      true.append(e)
    else:
      false.append(e)
  return (true, false)


#%% Tuples
def flip(tup):
  """
  Flips the elements of a 2-element tuple.
  
  Examples
  --------

  >>> flip((0, 1))
  (1, 0)
  
  """  
  return (snd(tup), fst(tup))


#%% * Enumerations
def lenum(l, start=0):
  """ 
  Indexes a list from the left side. 
  
  Examples
  --------

  >>> lenum(['a', 'b', 'c'])
  [(0, 'a'), (1, 'b'), (2, 'c')]
  """
  return list(enumerate(l, start=start))


def renum(l, start=0):
  """ 
  Indexes a list from the right side.
  
  Examples
  --------
  >>> renum(["a", "b", "c"])
  [('a', 0), ('b', 1), ('c', 2)]
  """
  return map(flip, lenum(l, start=start))



#%% * Functionalized operations
def sjoin(strs, s=''):
  """ 
  Function that joins strings.
  
  Examples
  --------
  
  Consider a list `l` of strings. 
  
  >>> l = ["abc", "def"]
  
  We can join the strings in `l` as:
  
  >>> sjoin(l)  
  'abcdef'
  
  Or with a joiner as:
  
  >>> sjoin(l, " ")
  'abc def'
  """ 
  return s.join(strs)


#%% * Curried functions
def startswithf(prefix):
  """
  Returns a function that tests whether a string starts with a prefix.
  
  Examples
  --------
  
  >>> f = startswithf('__')
  >>> f('abc')
  False
  >>> f('__name__')
  True
  """
  return lambda s: s.startswith(prefix)


def endswithf(suffix):
  """
  Returns a function that tests whether a string ends with a suffix.
  
  Examples
  --------
  
  >>> f = endswithf('.txt')
  >>> f('abc')
  False
  >>> f('abc.txt')
  True
  """
  return lambda s: s.endswith(suffix)


def replacef(s, r=''):
  """
  Returns a function that replaces substrings with a replacement.
  
  Examples
  --------
  >>> f = replacef('inside', 'outside')
  >>> f('Thankfully, I have spent the day inside.')
  'Thankfully, I have spent the day outside.'
  """
  return lambda e: e.replace(s, r)


def splitf(delim):
  """ 
  Returns a function that splits string with a given delimiter.
  
  Examples
  --------
  >>> f = splitf(", ")
  >>> f('apples, pears, oranges')  
  ['apples', 'pears', 'oranges']
  """
  return lambda x: x.split(delim)


def fmtf(format):
  """
  Returns a function that formats strings.
  
  >>> f = fmtf("%.2f")
  >>> f(0.5)
  '0.50'
  """
  return lambda x: format % x


def hasf(e):
  """
  Returns a function which if applied with `x` tests whether `x` has `e`.
  
  Examples
  --------
  >>> filter(hasf("."), ['statement', 'A sentence.'])
  ['A sentence.']
  """
  return lambda x: e in x


def nothasf(e):
  """
  Returns a function which if applied with `x` tests where 'x' does
  *not* have `e`. 

  .. seealso:: :func:`hasf`.
  
  Examples
  --------  
  >>> filter(nothasf("."), ['statement', 'A sentence.'])
  ['statement']
  """  
  return lambda x: not e in x

#%% * Lookup
def isinsetf(s):
  """
  Returns a function which tests whether an element is in a set `s`.
  
  Examples
  --------  
  >>> colors = ['red', 'green', 'blue']
  >>> f = isinsetf(colors)
  >>> map(f, ['yellow', 'green'])
  [False, True]
  """
  s = set(s)
  return lambda e: e in s

#%% __main__
if __name__ == '__main__':
  import doctest
  doctest.testmod(verbose=False)
