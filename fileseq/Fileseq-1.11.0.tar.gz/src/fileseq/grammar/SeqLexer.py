# Generated from Seq.g4 by ANTLR 4.7.2
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\7")
        buf.write(":\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3")
        buf.write("\5\3\6\5\6\37\n\6\3\6\6\6\"\n\6\r\6\16\6#\3\7\5\7\'\n")
        buf.write("\7\3\7\6\7*\n\7\r\7\16\7+\3\7\3\7\3\b\3\b\3\b\5\b\63\n")
        buf.write("\b\3\t\3\t\3\n\3\n\5\n9\n\n\2\2\13\3\3\5\2\7\2\t\2\13")
        buf.write("\2\r\4\17\5\21\6\23\7\3\2\5\4\2C\\c|\3\2\62;\4\2\61\61")
        buf.write("^^\2;\2\3\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2")
        buf.write("\2\2\23\3\2\2\2\3\25\3\2\2\2\5\27\3\2\2\2\7\31\3\2\2\2")
        buf.write("\t\33\3\2\2\2\13\36\3\2\2\2\r&\3\2\2\2\17/\3\2\2\2\21")
        buf.write("\64\3\2\2\2\238\3\2\2\2\25\26\7\60\2\2\26\4\3\2\2\2\27")
        buf.write("\30\t\2\2\2\30\6\3\2\2\2\31\32\t\3\2\2\32\b\3\2\2\2\33")
        buf.write("\34\t\4\2\2\34\n\3\2\2\2\35\37\7/\2\2\36\35\3\2\2\2\36")
        buf.write("\37\3\2\2\2\37!\3\2\2\2 \"\5\7\4\2! \3\2\2\2\"#\3\2\2")
        buf.write("\2#!\3\2\2\2#$\3\2\2\2$\f\3\2\2\2%\'\5\t\5\2&%\3\2\2\2")
        buf.write("&\'\3\2\2\2\')\3\2\2\2(*\5\21\t\2)(\3\2\2\2*+\3\2\2\2")
        buf.write("+)\3\2\2\2+,\3\2\2\2,-\3\2\2\2-.\5\t\5\2.\16\3\2\2\2/")
        buf.write("\62\5\13\6\2\60\61\7/\2\2\61\63\5\13\6\2\62\60\3\2\2\2")
        buf.write("\62\63\3\2\2\2\63\20\3\2\2\2\64\65\n\4\2\2\65\22\3\2\2")
        buf.write("\2\669\5\5\3\2\679\5\7\4\28\66\3\2\2\28\67\3\2\2\29\24")
        buf.write("\3\2\2\2\t\2\36#&+\628\2")
        return buf.getvalue()


class SeqLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    DIRNAME = 2
    FRANGE = 3
    CHAR = 4
    ALNUM = 5

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'.'" ]

    symbolicNames = [ "<INVALID>",
            "DIRNAME", "FRANGE", "CHAR", "ALNUM" ]

    ruleNames = [ "T__0", "LETTER", "DIGIT", "PATHSEP", "INT", "DIRNAME", 
                  "FRANGE", "CHAR", "ALNUM" ]

    grammarFileName = "Seq.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


