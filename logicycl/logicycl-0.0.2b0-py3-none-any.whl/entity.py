"""Classes for generating Arithmetic Express"""


class Arithmetic:

    def __init__(self, name):
        self._value = str(name)

    def __str__(self):
        return self._value

    def __neg__(self):
        return Neg(self)

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __div__(self, other):
        return Div(self, other)

    def __rdiv__(self, other):
        return Div(other, self)

    def __eq__(self, other):
        return f'{self} = {other}'

    def __ne__(self, other):
        return f'{self} != {other}'

    def __gt__(self, other):
        return f'{self} > {other}'

    def __lt__(self, other):
        return f'{self} < {other}'

    def __ge__(self, other):
        return f'{self} >= {other}'

    def __le__(self, other):
        return f'{self} <= {other}'


# Alias for Arithmetic
F = Arithmetic


class Neg(Arithmetic):

    def __init__(self, x):
        self._value = f'-{x}'


class Add(Arithmetic):

    def __init__(self, x, y):

        if isinstance(x, Neg):
            x = f'({x})'
        if isinstance(x, Neg):
            y = f'({y})'
        self._value = f'{x} + {y}'


class Sub(Arithmetic):

    def __init__(self, x, y):

        if isinstance(x, Neg):
            x = f'({x})'
        if isinstance(x, Neg):
            y = f'({y})'
        self._value = f'{x} - {y}'


class Mul(Arithmetic):

    def __init__(self, x, y):

        if isinstance(x, (Neg, Add, Sub)):
            x = f'({x})'
        if isinstance(x, (Neg, Add, Sub)):
            y = f'({y})'
        self._value = f'{x} * {y}'


class Div (Arithmetic):

    def __init__(self, x, y):

        if isinstance(x, (Neg, Add, Sub)):
            x = f'({x})'
        if isinstance(x, (Neg, Add, Sub)):
            y = f'({y})'
        self._value = f'{x} / {y}'
