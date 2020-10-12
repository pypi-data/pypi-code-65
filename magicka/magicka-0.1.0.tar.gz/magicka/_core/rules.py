from magicka._core.errors import MageLexingError
from ply.lex import TOKEN


class MageRules:
    """ This class defines the regular expressions used to match the tokens and
    classify them to the correct type so they can be parsed effectively. """

    execute_identifier = r'execute'
    number_identifier = r'\d+'
    newline_identifier = r'\n'

    t_ignore = ' \t'

    @TOKEN(number_identifier)
    def t_NUMBER(self, t):
        return t

    @TOKEN(execute_identifier)
    def t_EXECUTE(self, t):
        return t

    @TOKEN(newline_identifier)
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise MageLexingError(f"Illegal character: {repr(t.value[0])}")

        # t.lexer.skip(1)
