from magicka._core.lexer import MageLexer


class MageTestLexer(MageLexer):

    def _test(self, data):
        self.lex_input(data)

    def input_and_return(self, data):
        self._test(data)
        yield from self.lexer

    def test_input(self, data):
        self._test(data)
        for token in self.lexer:
            print(token)


if __name__ == "__main__":  # pragma: no cover
    m = MageTestLexer()
    m.test_input('3 4 execute')
    m.test_input('wrong-error')
