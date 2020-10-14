from math import floor, log10


def int_exp(x): return floor(log10(abs(x)))


def is_positive(x): return x == abs(x)
