import re

LITERAL = re.compile('[A-Za-z0-9]+')


def is_literal(x): return bool(LITERAL.search(x))


def is_string(x): return isinstance(x, str)


def has_literal(x): return isinstance(x, str) and is_literal(x)

# vec = ['a', 'shakes', 'cyber2077', '5', '_', '...']
# for word in vec:
#     print(word, True if has_literal(word) else False)
