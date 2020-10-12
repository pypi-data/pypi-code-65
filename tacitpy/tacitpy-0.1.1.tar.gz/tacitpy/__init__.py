from functools import *
import copy
from typing import Any

def typeof(value, types):
    if types is Any:
        return True
    if isinstance(types, tuple):
        return some([typeof(value, t) for t in types])
    return type(value) == types

# Automatic currying of functions as they're called.

class Curry(object):
    # Properties:
    # self.λ : Function to curry | None
    # self.__name__ : String, name for the function
    # self.type_string : String with type signature | None
    # self.type_annotation : Parsed type construct | None
    # self.type_context : Context for type variables
    def __init__(self, sig=None):
        self.λ = None
        self.__name__ = "<curry>"
        self.type_string = None
        self.type_annotation = None
        self.type_context = None

        if typeof(sig, self.__class__):
            self.λ = sig.λ
            self.__name__ = sig.__name__
            self.type_string = sig.type_string
            self.type_annotation = sig.type_annotation
            self.type_context = sig.type_context
        elif callable(sig):
            self.λ = sig
            if hasattr(sig, '__name__'):
                self.__name__ = sig.__name__
        else:
            if not typeof(sig, str):
                raise Exception("Type signatre must be passed as a string,"
                    + f" found type of {type(sig).__name__}.")
            self.type_string = sig
            if self.type_string:
                self.type_annotation = _parse_type(self.type_string)

        self.type_context = _TypingContext(self.__name__)

    @property
    def signature():
        return self.type_annotation
    # Currying as each argument is called for.
    def __call__(self, *args):
        def wrapper(λ):
            if self.__name__ == '<curry>' and hasattr(λ, '__name__'):
                self.__name__ = λ.__name__
                self.type_context.name = self.__name__
            def _(*args):
                if typeof(λ, self.__class__):
                    return λ(*args)
                new_λ = partial(λ, *args)
                try:
                    res = new_λ()
                    if self.type_annotation:
                        context = self.type_context.copy()
                        _type_check(
                            _func_resolve(
                                args,
                                self.type_annotation,
                                context),
                            res, context)
                    return res
                except TypeError:
                    new = self.__class__(new_λ)
                    if self.type_annotation:
                        new.__name__ = self.__name__
                        new.type_context = self.type_context.copy()
                        new.type_annotation = _func_resolve(
                            args, self.type_annotation, new.type_context)
                    return new

            return _

        if self.λ:
            return wrapper(self.λ)(*args)

        return wrapper(args[0])()
    # Composition of functions from an array.
    def compose(*fns):
        if len(fns) < 2:
            raise Exception("Can only compose two or more functions.")
        fn_1, fn_2, *fn_rest = fns
        if len(fn_rest) == 0:
            return Curry(lambda x: fn_1(fn_2(x)))
        else:
            fn_1, *fn_rest = fns
            return Curry(lambda x: fn_1(self.__class__.compose(*fn_rest)(x)))
    def __mul__(self, fn):  # Multiplication as composition operator.
        return self.compose(fn)
    def __str__(self):
        return f"<λ {self.__name__}>"
    def __repr__(self):
        return f"<λ `{self.__name__}' of {self.λ}>"

# Useful definitions.
curry = Curry
some = any
every = all
any = Any
NoneType = type(None)

class natural(int):
    def __new__(cls, value):
        natural.__typecheck__(value)
        obj = super(natural, cls).__new__(cls, value)
        return obj
    def __cast__(other):
        if typeof(other, (int, float)):
            return natural(other)
        return None
    def __typecheck__(self):
        if self < 0:
            raise ValueError("Natural number cannot be below zero.")
        if typeof(self, float):
            if not self.is_integer():
                raise ValueError("Natural cannot have fractional part.")
# Type checking and inference.

class TypeCheck(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
    def __str__(self):
        return ('\n[***] TacitPy Type-checking Error:\n'
            + f'   {self.message}')

class _TypingContext(object):
    def __init__(self, name, d=None):
        self.name = name
        self.variables = d or dict()
    def copy(self):
        return self.__class__(self.name, copy.copy(self.variables))
    def __setitem__(self, key, value):
        if typeof(key, _TypeVariable):
            key = key.name
        if key in self.variables.keys() and self[key] != value:
            raise TypeCheck(f"Type-variable `{key}' in function `{self.name}',"
                + f" has been instanced as `{self.variables[key]}`,"
                + f" yet `{value}` was found.")
        self.variables[key] = value
    def __getitem__(self, key):
        if typeof(key, _TypeVariable):
            key = key.name
        if not key in self.variables.keys():
            raise TypeCheck(f"No type-variable {key} has been declared.")
        return self.variables[key]


def _type_infer(value):
    if typeof(value, list):
        return _ListType(_type_infer(value[0]))
    if typeof(value, tuple):
        if len(value) == 0:
            return _TupleType(None, None)
        first_tuple = _TupleType(_type_infer(value[0]), None)
        if len(value) == 1:
            return first_tuple
        if len(value) == 2:
            first_tuple.snd = _type_infer(value[1])
            return first_tuple
        first_tuple.snd = _type_infer(value[1:])
        return first_tuple
    if typeof(value, Curry):
        if value.type_annotation is not None:
            return value.type_annotation
    if typeof(value, type):
        return type
    if callable(value):
        return _FunctionMapping(Any, Any)

    return _Type(type(value))

def _type_check(t, value, context=None):
    if context is None:
        context = _TypingContext()
    pt = _Type(t)
    vt = _Type(type(value))

    if hasattr(value, '__typecheck__'):
        value.__typecheck__()
    if hasattr(t, '__cast__'):
        try:
            value = t.__cast__(value)
            return
        except ValueError:
            pass

    if t == Any:
        return
    if typeof(t, _FunctionMapping):
        if not callable(value):
            raise TypeCheck(f"Expected function {t}, got {vt}.")
    elif typeof(t, _Type):
        _type_check(t.type, value, context)
    elif typeof(t, type):
        if not typeof(value, t):
            if typeof(value, float) and t is int and value.is_integer():
                return
            raise TypeCheck(f"Expected type of {pt}, got {vt}.")
    elif typeof(t, _ListType):
        if not typeof(value, list):
            raise TypeCheck(f"Expected a list ({t}), was provided with {vt} instead.")
        for elem in value:
            _type_check(t.type, elem, context)
    elif typeof(t, _TupleType):
        if not typeof(value, tuple):
            raise TypeCheck(f"Expected tuple {t}, got {vt}.")
        if len(value) == 0:
            if t.fst != None:
                raise TypeCheck(f"Empty tuple does not match type of {t}.")
            return
        _type_check(t.fst, value[0], context)
        if len(value) == 1:
            if t.snd != None:
                raise TypeCheck(f"Singleton tuple does not match type of {t}.")
            return
        if len(value) == 2:
            _type_check(t.snd, value[1], context)
            return
        _type_check(t.snd, value[1:], context)
    elif typeof(t, _TypeVariable):
        context[t] = _type_infer(value)
        return
    else:
        raise TypeCheck(f"Don't know how to typecheck {value} against a {t}.")

def _func_resolve(args, func_type, context=None):
    if len(args) == 0:
        return func_type

    _type_check(func_type.domain, args[0], context)
    return _func_resolve(args[1:], func_type.range, context)

## Parsing type annotations

# Type of a map from two types (a -> b).
class _FunctionMapping(object):
    def __init__(self, kind1, kind2):
        self.domain = kind1
        self.range  = kind2
    def __str__(self):
        return f'({self.domain} -> {self.range})'
    __repr__ = __str__
    def __eq__(self, other):
        if not typeof(other, self.__class__):
            return False
        return (self.domain, self.range) == (other.domain, other.range)

# A normal Python type.
class _Type(object):
    def __init__(self, name):
        self.type = name
        if typeof(name, str):
            self.type = eval(name)
        if not typeof(self.type, type):
            self.type = type(self.type)
    def __str__(self):
        return self.type.__name__
    __repr__ = __str__
    def __eq__(self, other):
        if typeof(other, type):
            other = self.__class__(other)
        if not typeof(other, self.__class__):
            return False
        return self.type is other.type

# Type of a list of a certain type.
class _ListType(object):
    def __init__(self, t):
        self.type = t
    def __str__(self):
        return f'[{self.type}]'
    __repr__ = __str__
    def __eq__(self, other):
        if not typeof(other, self.__class__):
            return False
        return self.type is other.type


# Type of a pair of types.
class _TupleType(object):
    def __init__(self, fst, snd):
        self.fst = fst
        self.snd = snd
    def __str__(self, child=False):
        res = (f'{self.fst}, {self.snd.__str__(True)}'
            if typeof(self.snd, self.__class__)
            else f'{self.fst}, {self.snd}')
        if child:
            return res
        return f'({res})'
    __repr__ = __str__
    def __eq__(self, other):
        if not typeof(other, self.__class__):
            return False
        return (self.fst, self.snd) == (other.fst, other.snd)

# Type variable, type that is resolved depending on how it's used.
class _TypeVariable(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return  f'~{self.name}'
    __repr__ = __str__
    def __eq__(self, other):
        if not typeof(other, self.__class__):
            return False
        raise ValueError("Cannot check for equality between type variables.")

def _match_t_type(rest):
    if len(rest) == 0:
        return None

    len2 = {
        '->': 'MAPPING'
    }.get(rest[:2])

    len1 = {
        ',': 'COMMA',
        '[': 'L_BRACKET',
        ']': 'R_BRACKET',
        '(': 'L_PAREN',
        ')': 'R_PAREN'
    }.get(rest[:1])

    if len2 is not None:
        return (rest[:2], len2)
    if len1 is not None:
        return (rest[:1], len1)
    if rest[0] == ' ':
        return None

    return 'IDENT'

def _lex_annotation(type_string):
    if len(type_string) == 0:
        return None

    offset = 0

    tt = _match_t_type(type_string)
    while tt is None:
        offset += 1
        type_string = type_string[1:]
        if len(type_string) == 0:
            return None
        tt = _match_t_type(type_string)

    if tt != 'IDENT':
        offset += len(tt[0])
        return (tt[0], tt[1], offset)

    old_tt = tt
    span = 0

    while tt == old_tt:
        span += 1;
        old_tt = _match_t_type(type_string[span:])

    sub = type_string[:span]
    return (sub, 'IDENT', offset + span)

def _tokens_iter(string):
    i = 0
    buff = None
    while i < len(string):
        token = _lex_annotation(string[i:])
        if token is None:
            break

        tok = ((token[0], token[1]))
        option = yield tok

        while option == 'back':
            i -= token[2]
            option = yield tok

        if option != None:
            raise Exception(f"Unknonw send: '{option}'!")

        i += token[2]

def peek(gen):
    value = next(gen)
    gen.send('back')
    return value

_TYPE_VARIABLES = list(map(chr, range(ord('a'), ord('z') + 1)))
_EOF_TOKEN = ('EOF', 'EOF')

class SigError(Exception):
    pass

def _expected(expect, tokens):
    closing_token = None
    try:
        closing_token = next(tokens)
    except StopIteration:
        closing_token = _EOF_TOKEN
    if closing_token[0] != expect:
        raise SigError(f"Expected '{expect}', found token '{closing_token[0]}'.")

def _precedence(op): return {
    'MAPPING': 20,
    'R_BRACKET': 0,
    'R_PAREN': 0,
    'COMMA': 10
}.get(op, 99)

_RIGHT   = 'right'
_LEFT    = 'left'
_NEITHER = 'neither'

def _associativity(op): return {
    'MAPPING': _RIGHT,
    'COMMA': _RIGHT
}.get(op, _LEFT)

def _parse_prefix(token, tokens):
    if token[1] == 'L_BRACKET':
        list_type = _parse_signature(tokens)
        _expected(']', tokens)
        return _ListType(list_type)

    if token[1] == 'L_PAREN':
        if peek(tokens)[1] == 'R_PAREN':
            next(tokens)
            return _Type(type(None))
        t = _parse_signature(tokens)
        _expected(')', tokens)
        return t

    if token[1] == 'IDENT':
        name = token[0]
        return (_TypeVariable if name in _TYPE_VARIABLES else _Type)(name)

    raise SigError(f"Unknown prefix token '{token[0]}'.")

def _parse_infix(left, token, tokens):
    p = (_precedence(token[1])
        - (1 if _associativity(token[1]) == _RIGHT else 0))

    if token[1] == 'MAPPING':
        return _FunctionMapping(left, _parse_signature(tokens, p))

    if token[1] == 'COMMA':
        return _TupleType(left, _parse_signature(tokens, p))

    raise SigError(f"Unknown infix operator '{token[0]}'.")

def _parse_signature(tokens, prec=0):
    token = next(tokens)
    left = _parse_prefix(token, tokens)

    try:
        token = peek(tokens)
    except StopIteration:
        return left

    while _precedence(token[1]) > prec:
        token = next(tokens)
        left = _parse_infix(left, token, tokens)

        try:
            token = peek(tokens)
        except StopIteration:
            return left

    return left

def _parse_type(type_string):
    tokens = _tokens_iter(type_string)
    return _parse_signature(tokens)

## Basic utility functions

# id : a -> a
id = Curry(lambda x: x)

const = Curry("a -> b -> a")(lambda x, _: x)

null = Curry("[a] -> bool")(lambda xs: len(xs) == 0)

flip = (Curry("(a -> b -> c) -> (b -> a -> c)")
             (lambda f, x, y: f(y, x)))

minus = Curry(lambda x, y: x - y)
plus  = Curry(lambda x, y: x + y)

# subtract : a -> a -> a, forall a in number
subtract = flip(minus)
add = plus

@Curry("a -> [a] -> [a]")
def cons(x, xs):
    return [x, *xs]

@Curry("(a -> b) -> [a] -> [b]")
def map(f, xs):
    if xs == []:
        return xs
    x, *xs = xs
    return cons(f(x))(map(f)(xs))

@Curry("(a -> a -> a) -> a -> [a] -> a")
def foldr(f, x0, xs):
    if xs == []:
        return x0
    x, *xs = xs
    return f(x, foldr(f, x0, xs))

@Curry("(a -> a -> a) -> a -> [a] -> a")
def foldl(f, x0, xs):
    if xs == []:
        return x0
    x, *xs = xs
    return foldl(f)(f(x0, x))(xs)

@Curry("(a -> a -> a) -> [a] -> a")
def fold(f, xs):
    if len(xs) < 2:
        raise Exception("fold list needs 2 or more arguments.")
    x, *xs = xs
    return foldl(f)(x)(xs)

reduce = fold

@Curry("(a -> bool) -> [a] -> [a]")
def filter(f, xs):
    if xs == []:
        return xs
    x, *xs = xs
    if f(x): return cons(x)(filter(f)(xs))
    else:    return filter(f)(xs)

select = filter
neg = Curry("bool -> bool")(lambda p: not p)
reject = Curry("(a -> bool) -> [a] -> [a]")(lambda f: filter(neg * f))

@Curry("[a] -> [b] -> [(a, b)]")
def zip(xs, ys):
    if xs == [] or ys == []:
        return []
    x, *xs = xs
    y, *ys = ys

    return cons((x, y))(zip(xs)(ys))

@Curry("(a -> b -> c) -> [a] -> [b] -> [c]")
def zip_with(f, xs, ys):
    if xs == [] or ys == []:
        return []
    x, *xs = xs
    y, *ys = ys

    return cons(f(x, y))(zip_with(f)(xs)(ys))

pair = Curry("a -> b -> (a, b)")(lambda x, y: (x, y))
# Hence:
#zip = zip_with(pair)

