import ply.lex as lex
from magicka._core import rules, tokens


class MageLexer(tokens.MageTokens, rules.MageRules):
    """ The base class which will tokenize the input which will later be consumed
    by the parser. """

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def lex_input(self, data):
        self.lexer.input(data)
